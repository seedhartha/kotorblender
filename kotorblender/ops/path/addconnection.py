import bpy

from ... import kb_utils


class KB_OT_add_connection(bpy.types.Operator):
    bl_idname = "kb.add_path_connection"
    bl_label = "Add Odyssey Path Connection"

    @classmethod
    def poll(cls, context):
        return kb_utils.is_path_point(context.object)

    def execute(self, context):
        context.object.nvb.path_connections.add()
        return {'FINISHED'}