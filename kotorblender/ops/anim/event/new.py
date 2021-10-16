import bpy

from .... import kb_utils


class KB_OT_anim_event_new(bpy.types.Operator):
    """Add a new item to the event list"""

    bl_idname = "kb.anim_event_new"
    bl_label = "Add a new event to an animation"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        """Enable only if there is an animation."""
        mdl_base = kb_utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            anim_list = mdl_base.nvb.animList
            anim_list_idx = mdl_base.nvb.animListIdx
            return (anim_list_idx >= 0) and len(anim_list) > anim_list_idx
        return False

    def execute(self, context):
        """Add the new item."""
        mdl_base = kb_utils.get_mdl_root_from_object(context.object)
        anim = mdl_base.nvb.animList[mdl_base.nvb.animListIdx]

        eventList = anim.eventList
        newEvent = eventList.add()
        if anim.frameStart <= bpy.context.scene.frame_current <= anim.frameEnd:
            newEvent.frame = bpy.context.scene.frame_current
        else:
            newEvent.frame = anim.frameStart

        return {'FINISHED'}