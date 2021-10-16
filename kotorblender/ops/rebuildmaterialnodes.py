import bpy

from .. import (kb_def, kb_material)


class KB_OT_rebuild_material_nodes(bpy.types.Operator):
    """Rebuild material node tree of this object."""

    bl_idname = "kb.rebuild_material_nodes"
    bl_label = "Rebuild Material Nodes"

    def execute(self, context):
        obj = context.object
        if obj and (obj.type == 'MESH') and (obj.nvb.meshtype != kb_def.Meshtype.EMITTER):
            kb_material.rebuild_material(obj)

        return {'FINISHED'}