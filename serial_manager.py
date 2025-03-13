import bpy
import threading
import serial
import serial.tools.list_ports

class SerialManager:
    def __init__(self, timeout=1):
        """Initialize the SerialManager"""
        self.timeout = timeout
        self.ports = {}  # Dictionary to store ports
        self.connections = {}  # Dictionary to store serial connections
        self.threads = {}  # Dictionary to store threads
        self.running = {}  # Dic]tionary to track active ports
        self.last_sent_values = {}

    def get_available_ports(self):
        """Returns a list of unique serial ports from the Blender scene"""
        unique_ports = list({
            triplet.serial_port
            for triplet in bpy.context.scene.n2048_triplets
            if triplet.serial_port != "None" and triplet.has_serial_stream
        })
        return unique_ports

    def _write_to_port(self, port_name):
        """Thread function: Continuously send data to the serial port"""
        serial_connection = self.connections[port_name]

        while self.running.get(port_name, False): 
            try:
                if serial_connection.is_open:
                    triplets = list({triplet for triplet in bpy.context.scene.n2048_triplets if triplet.serial_port == port_name and triplet.has_serial_stream})
                    for triplet in triplets:
                        obj = triplet.object
                        prop = triplet.transform_property
                        attr, sub_attr = prop.split(".")
                        value = getattr(getattr(obj, attr), sub_attr)*triplet.scale_factor

                        key = (obj.name, prop)

                        if key not in self.last_sent_values or self.last_sent_values[key] != value:
                            message = f"{obj.name}|{prop}|{float(value):.2f}\n"
                            serial_connection.write(message.encode())
                            serial_connection.flush()
                            self.last_sent_values[key] = value  # ✅ Store last sent value

                        #time.sleep(0.1)  # Maintain refresh rate
                
            except serial.SerialException as e:
                break

    def start(self):
        """Starts serial connections in separate threads"""
        self.ports = self.get_available_ports()

        for port_name in self.ports:
            if port_name in self.running and self.running[port_name]:
                continue  # ✅ Prevent duplicate threads

            try:
                baudrate = bpy.context.scene.n2048_baud_rate
                self.connections[port_name] = serial.Serial(port_name, baudrate, timeout=self.timeout)
                self.running[port_name] = True
                self.threads[port_name] = threading.Thread(target=self._write_to_port, args=(port_name,), daemon=True)  # ✅ Corrected tuple formatx
                self.threads[port_name].start()
            except serial.SerialException as e:
                ...

    def stop(self):
        """Stops all serial connections and their threads"""

        for port_name in list(self.running.keys()):
            self.running[port_name] = False  # ✅ Ensure thread exits gracefully

        # Wait for threads to stop
        for port_name in list(self.threads.keys()):
            if self.threads[port_name].is_alive():
                self.threads[port_name].join(timeout=2)
            del self.threads[port_name]
        
        # Close connections
        for port_name in list(self.connections.keys()):
            if self.connections[port_name].is_open:
                self.connections[port_name].close()
            del self.connections[port_name]

        self.running.clear()  # ✅ Ensure clean state

# Register Panel
def register():
    bpy.types.Scene.serial_manager = SerialManager()

def unregister():
    del bpy.types.Scene.serial_manager
