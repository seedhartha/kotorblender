import bpy

from .. import (armature, utils)


class KB_OT_recreate_armature(bpy.types.Operator):
    """Recreate an armature from bone nodes."""

    bl_idname = "kb.recreate_armature"
    bl_label = "Recreate Armature"

    def execute(self, context):
        obj = context.object
        if utils.is_root_dummy(obj):
            armature_object = armature.recreate_armature(obj)
            if armature_object:
                armature.create_armature_animations(obj, armature_object)

        return {'FINISHED'}
