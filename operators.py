import bpy

class N2048_OT_AddTriplet(bpy.types.Operator):
    bl_idname = "n2048.add_triplet"
    bl_label = "Add Triplet"
    
    def execute(self, context):
        triplet = context.scene.n2048_triplets.add()
        triplet.object = None  # Default to no object selected

        # Ensure we assign a valid serial port
        available_ports = [port[0] for port in triplet.bl_rna.properties['serial_port'].enum_items]
        triplet.serial_port = available_ports[0] if available_ports else "None"

        triplet.transform_property = "location.x"
        triplet.has_serial_stream = False
        context.scene.n2048_index = len(context.scene.n2048_triplets) - 1
        return {'FINISHED'}


class N2048_OT_RemoveTriplet(bpy.types.Operator):
    bl_idname = "n2048.remove_triplet"
    bl_label = "Remove Triplet"
    
    index: bpy.props.IntProperty()  # ✅ Correctly defines the index property

    def execute(self, context):
        scene = context.scene
        if 0 <= self.index < len(scene.n2048_triplets):
            scene.n2048_triplets.remove(self.index)
            scene.n2048_index = max(0, self.index - 1)  # Prevents out-of-range errors
        return {'FINISHED'}


class N2048_OT_Run(bpy.types.Operator):
    bl_idname = "n2048.run"
    bl_label = "Run"

    def execute(self, context):                    
        # Connect to selected serial Port
        serial_manager = context.scene.serial_manager
        serial_manager.start()
            
        return {'FINISHED'}


class N2048_OT_Stop(bpy.types.Operator):
    bl_idname = "n2048.stop"
    bl_label = "Stop"

    def execute(self, context):
        serial_manager = context.scene.serial_manager
        serial_manager.stop()
        
        return {'FINISHED'}


class N2048_OT_GetUniqueSerialPorts(bpy.types.Operator):
    """Get list of unique serial ports used in triplets"""
    """call from console :  bpy.ops.n2048.get_unique_serial_ports() """
    bl_idname = "n2048.get_unique_serial_ports"
    bl_label = "Get Unique Serial Ports"

    def execute(self, context):
        scene = context.scene
        unique_ports = {triplet.serial_port for triplet in scene.n2048_triplets if triplet.serial_port != "None" and triplet.has_serial_stream}

        if unique_ports:
            print("Unique Selected Serial Ports:", unique_ports)
        else:
            print("No Serial Ports Selected")

        return {'FINISHED'}


# Register Operators
def register():
    bpy.utils.register_class(N2048_OT_AddTriplet)
    bpy.utils.register_class(N2048_OT_RemoveTriplet)
    bpy.utils.register_class(N2048_OT_Stop)
    bpy.utils.register_class(N2048_OT_Run)
    bpy.utils.register_class(N2048_OT_GetUniqueSerialPorts)
    

def unregister():
    bpy.utils.unregister_class(N2048_OT_RemoveTriplet)
    bpy.utils.unregister_class(N2048_OT_AddTriplet)
    bpy.utils.unregister_class(N2048_OT_Stop)
    bpy.utils.unregister_class(N2048_OT_Run)
    bpy.utils.unregister_class(N2048_OT_GetUniqueSerialPorts)

