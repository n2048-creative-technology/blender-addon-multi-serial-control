import bpy
import threading
import serial
import serial.tools.list_ports

class SerialManager:
    def __init__(self, timeout=1):
        self.timeout = timeout
        self.ports = {}
        self.connections = {}
        self.threads = {}
        self.running = {}
        self.last_sent_values = {}
        self.data_queue = {}  # Queue for data updates

    def get_available_ports(self):
        unique_ports = list({
            triplet.serial_port
            for triplet in bpy.context.scene.n2048_triplets
            if triplet.serial_port != "None" and triplet.has_serial_stream
        })
        return unique_ports

    def _update_object_attribute(self, obj_name, attr, sub_attr, value):
        """Safely update Blender object attributes from the main thread."""
        obj = bpy.data.objects.get(obj_name)
        if obj:
            try:
                setattr(getattr(obj, attr), sub_attr, value)
                bpy.context.view_layer.update()
            except Exception as e:
                print(f"Failed to update {obj_name}.{attr}.{sub_attr}: {e}")

    def _process_queue(self):
        """Main thread function to update Blender attributes."""
        for key, (obj_name, attr, sub_attr, value) in list(self.data_queue.items()):
            self._update_object_attribute(obj_name, attr, sub_attr, value)
            del self.data_queue[key]  # Remove processed item

        # Schedule the next update
        return 0.1  # Run every 0.1 seconds

    def _write_to_port(self, port_name):
        serial_connection = self.connections[port_name]

        while self.running.get(port_name, False):
            try:
                if serial_connection.is_open:
                    triplets = list({
                        triplet for triplet in bpy.context.scene.n2048_triplets
                        if triplet.serial_port == port_name and triplet.has_serial_stream
                    })
                    for triplet in triplets:
                        obj = triplet.object
                        prop = triplet.transform_property
                        attr, sub_attr = prop.split(".")
                        key = (obj.name, prop)

                        if triplet.learn_mode:
                            message = f"{obj.name}|learn_mode|1\n"
                            serial_connection.write(message.encode())
                            while True:
                                line = serial_connection.readline().decode('utf-8').strip()
                                if line:
                                    try:
                                        received_value = float(line)
                                        if received_value:
                                            value = (received_value - triplet.offset) / triplet.scale_factor
                                            # Store the value in the queue to update on the main thread
                                            self.data_queue[key] = (obj.name, attr, sub_attr, value)
                                            break
                                    except ValueError:
                                        pass
                        else:
                            value = getattr(getattr(obj, attr), sub_attr) * triplet.scale_factor + triplet.offset
                            if key not in self.last_sent_values or self.last_sent_values[key] != value:
                                message = f"{obj.name}|{prop}|{float(value):.2f}\n"
                                serial_connection.write(message.encode())
                                serial_connection.flush()
                                self.last_sent_values[key] = value

            except serial.SerialException:
                break

    def start(self):
        self.ports = self.get_available_ports()

        # Schedule the main thread update function
        bpy.app.timers.register(self._process_queue)

        for port_name in self.ports:
            if port_name in self.running and self.running[port_name]:
                continue

            try:
                baudrate = bpy.context.scene.n2048_baud_rate
                self.connections[port_name] = serial.Serial(port_name, baudrate, timeout=self.timeout)
                self.running[port_name] = True
                self.threads[port_name] = threading.Thread(target=self._write_to_port, args=(port_name,), daemon=True)
                self.threads[port_name].start()
            except serial.SerialException:
                pass

    def stop(self):
        for port_name in list(self.running.keys()):
            self.running[port_name] = False

        for port_name in list(self.threads.keys()):
            if self.threads[port_name].is_alive():
                self.threads[port_name].join(timeout=2)
            del self.threads[port_name]

        for port_name in list(self.connections.keys()):
            if self.connections[port_name].is_open:
                self.connections[port_name].close()
            del self.connections[port_name]

        self.running.clear()

# Register Panel
def register():
    bpy.types.Scene.serial_manager = SerialManager()

def unregister():
    del bpy.types.Scene.serial_manager
