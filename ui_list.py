import bpy

class N2048_UL_TripletList(bpy.types.UIList):
    bl_idname = "N2048_UL_TripletList"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "object", text="", icon='OBJECT_DATA')
            # row.prop(item, "serial_port", text="")
            row.prop(item, "serial_port", text="")

            row.prop(item, "transform_property", text="")
            row.prop(item, "scale_factor", text="")
            row.prop(item, "offset", text="")
            row.prop(item, "learn_mode", text="")
            row.prop(item, "has_serial_stream", text="")
            row.operator("n2048.remove_triplet", text="", icon="X").index = index

# Register UI List
def register():
    bpy.utils.register_class(N2048_UL_TripletList)

def unregister():
    bpy.utils.unregister_class(N2048_UL_TripletList)
