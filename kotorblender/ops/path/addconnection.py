import bpy

from ... import utils


class KB_OT_add_connection(bpy.types.Operator):
    bl_idname = "kb.add_path_connection"
    bl_label = "Add Odyssey Path Connection"

    @classmethod
    def poll(cls, context):
        return utils.is_path_point(context.object)

    def execute(self, context):
        context.object.kb.path_connections.add()
        return {'FINISHED'}