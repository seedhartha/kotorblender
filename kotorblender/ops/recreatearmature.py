import bpy

from .. import (kb_armature, kb_utils)


class KB_OT_recreate_armature(bpy.types.Operator):
    """Recreate an armature from bone nodes."""

    bl_idname = "kb.recreate_armature"
    bl_label = "Recreate Armature"

    def execute(self, context):
        obj = context.object
        if kb_utils.is_root_dummy(obj):
            armature_object = kb_armature.recreate_armature(obj)
            if armature_object:
                kb_armature.create_armature_animations(obj, armature_object)

        return {'FINISHED'}
