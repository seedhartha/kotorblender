import bpy

from ... import kb_utils


class KB_OT_remove_connection(bpy.types.Operator):
    bl_idname = "kb.remove_path_connection"
    bl_label = "Remove Odyssey Path Connection"

    @classmethod
    def poll(cls, context):
        return kb_utils.is_path_point(context.object) and (len(context.object.nvb.path_connections) > 0)

    def execute(self, context):
        context.object.nvb.path_connections.remove(context.object.nvb.active_path_connection)
        return {'FINISHED'}