import bpy

from ... import kb_utils


class KB_OT_anim_move(bpy.types.Operator):
    """Move an item in the animation list, without affecting keyframes"""

    bl_idname = "kb.anim_move"
    bl_label = "Move an animation in the list, without affecting keyframes"
    bl_options = {'UNDO'}

    direction : bpy.props.EnumProperty(items=(("UP", "Up", ""),
                                              ("DOWN", "Down", "")))

    @classmethod
    def poll(self, context):
        """Prevent execution if animation list has less than 2 elements."""
        mdl_base = kb_utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            return (len(mdl_base.nvb.animList) > 1)
        return False

    def execute(self, context):
        """Move an item in the animation list."""
        mdl_base = kb_utils.get_mdl_root_from_object(context.object)
        anim_list = mdl_base.nvb.animList

        currentIdx = mdl_base.nvb.animListIdx
        new_idx = 0
        max_idx = len(anim_list) - 1
        if self.direction == "DOWN":
            new_idx = currentIdx + 1
        elif self.direction == "UP":
            new_idx = currentIdx - 1
        else:
            return {'CANCELLED'}

        new_idx = max(0, min(new_idx, max_idx))
        if new_idx == currentIdx:
            return {'CANCELLED'}
        anim_list.move(currentIdx, new_idx)
        mdl_base.nvb.animListIdx = new_idx
        return {'FINISHED'}