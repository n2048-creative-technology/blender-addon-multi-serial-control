import bpy

class N2048_PT_Panel(bpy.types.Panel):
    bl_label = "N2048"
    bl_idname = "N2048_PT_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "N2048"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Triplets:")

        # Triplet List
        layout.template_list("N2048_UL_TripletList", "", scene, "n2048_triplets", scene, "n2048_index")


        # Baud Rate Dropdown
        layout.label(text="Baud Rate:")
        layout.prop(scene, "n2048_baud_rate", text="")
        
        layout.operator("n2048.add_triplet", icon="ADD", text="Add")

        row = layout.row()
        col = row.column()
        col.operator("n2048.connect", text="Connect")

        col = row.column()
        col.operator("n2048.disconnect", text="Disonnect")

        row = layout.row()
        col = row.column()
        col.operator("n2048.run", text="Run")

        col = row.column()
        col.operator("n2048.stop", text="Stop")


# Register Panel
def register():
    bpy.utils.register_class(N2048_PT_Panel)

def unregister():
    bpy.utils.unregister_class(N2048_PT_Panel)
