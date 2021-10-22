import bpy

from ... import utils


class KB_OT_anim_focus(bpy.types.Operator):
    """Set the Start and end frames of the timeline"""

    bl_idname = "kb.anim_focus"
    bl_label = "Set start and end frame of the timeline to the animation"

    @classmethod
    def poll(self, context):
        """Prevent execution if animation list is empty."""
        mdl_base = utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            return (len(mdl_base.kb.animList) > 0)
        return False

    def execute(self, context):
        """Set the timeline to this animation."""
        mdl_base = utils.get_mdl_root_from_object(context.object)
        utils.toggle_anim_focus(context.scene, mdl_base)
        return {'FINISHED'}