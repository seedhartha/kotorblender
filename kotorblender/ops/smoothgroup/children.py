import bpy

from ... import kb_utils


class KB_OT_children_smoothgroup(bpy.types.Operator):
    bl_idname = "kb.children_smoothgroup"
    bl_label = "Smoothgroup settings on descendants"
    bl_options = {'UNDO'}

    action : bpy.props.StringProperty()

    def execute(self, context):
        descendants = kb_utils.search_node_all(
            context.object, lambda o: o.type == 'MESH'
        )
        for d in descendants:
            d.nvb.smoothgroup = self.action
        return {'FINISHED'}