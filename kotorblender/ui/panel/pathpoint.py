import bpy

from ... import kb_utils


class KB_PT_path_point(bpy.types.Panel):
    bl_label = "Odyssey Path Point"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return kb_utils.is_path_point(context.object)

    def draw(self, context):
        row = self.layout.row()
        box = row.box()
        box.label(text="Connections")
        row = box.row()
        row.template_list("KB_UL_path_points", "", context.object.nvb, "path_connections", context.object.nvb, "active_path_connection")
        col = row.column(align=True)
        col.operator("kb.add_path_connection", icon='ADD', text="")
        col.operator("kb.remove_path_connection", icon='REMOVE', text="")