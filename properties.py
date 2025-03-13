import bpy
import serial.tools.list_ports


SERIAL_BAUD_RATES = [
    ("300", "300", ""),
    ("1200", "1200", ""),
    ("2400", "2400", ""),
    ("4800", "4800", ""),
    ("9600", "9600", ""),
    ("19200", "19200", ""),
    ("38400", "38400", ""),
    ("57600", "57600", ""),
    ("74880", "74880", ""),
    ("115200", "115200", ""),
    ("230400", "230400", ""),
    ("250000", "250000", ""),
    ("500000", "500000", ""),
    ("1000000", "1000000", ""),
    ("2000000", "2000000", ""),
]

# Function to get available serial ports
def get_serial_ports(self, context):
    ports = serial.tools.list_ports.comports()
    port_list = [(port.device, port.device, "") for port in ports]

    # Ensure "None" is always present as a default option
    if not port_list:
        port_list.append(("None", "No Ports Available", ""))

    return [("None", "None", "")] + port_list  # Always prepend "None" as an option

# Define available transform properties
TRANSFORM_ITEMS = [
    ("location.x", "Location X", ""),
    ("location.y", "Location Y", ""),
    ("location.z", "Location Z", ""),
    ("rotation_euler.x", "Rotation X", ""),
    ("rotation_euler.y", "Rotation Y", ""),
    ("rotation_euler.z", "Rotation Z", ""),
    ("scale.x", "Scale X", ""),
    ("scale.y", "Scale Y", ""),
    ("scale.z", "Scale Z", ""),
]


# Triplet property group
class N2048_TripletProperty(bpy.types.PropertyGroup):
    object: bpy.props.PointerProperty(name="Object", type=bpy.types.Object)
    serial_port: bpy.props.EnumProperty(name="Serial Port", description="Select a serial port", items=get_serial_ports)
    transform_property: bpy.props.EnumProperty(name="Property", description="Transform property", items=TRANSFORM_ITEMS)
    scale_factor: bpy.props.FloatProperty(name="Scale Factor", description="Scale factor", default=1.0)
    has_serial_stream: bpy.props.BoolProperty(name="Enable Serial Stream", default=False)
    
# Register Properties
def register():
    bpy.utils.register_class(N2048_TripletProperty)
    bpy.types.Scene.n2048_triplets = bpy.props.CollectionProperty(type=N2048_TripletProperty)
    bpy.types.Scene.n2048_index = bpy.props.IntProperty(name="Index", default=0)
    bpy.types.Scene.n2048_baud_rate = bpy.props.EnumProperty(
        name="Baud Rate",
        description="Select the baud rate for serial communication",
        items=SERIAL_BAUD_RATES,
        default="115200"
    )
def unregister():
    del bpy.types.Scene.n2048_triplets
    del bpy.types.Scene.n2048_index
    del bpy.types.Scene.n2048_baud_rate
    bpy.utils.unregister_class(N2048_TripletProperty)
