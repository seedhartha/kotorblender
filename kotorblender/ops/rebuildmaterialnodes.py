import bpy

from .. import (defines, material)


class KB_OT_rebuild_material_nodes(bpy.types.Operator):
    """Rebuild material node tree of this object."""

    bl_idname = "kb.rebuild_material_nodes"
    bl_label = "Rebuild Material Nodes"

    def execute(self, context):
        obj = context.object
        if obj and (obj.type == 'MESH') and (obj.nvb.meshtype != defines.Meshtype.EMITTER):
            material.rebuild_material(obj)

        return {'FINISHED'}