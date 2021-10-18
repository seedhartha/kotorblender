import bpy

from .... import utils


class KB_OT_anim_event_delete(bpy.types.Operator):
    """Delete the selected item from the event list"""

    bl_idname = "kb.anim_event_delete"
    bl_label = "Deletes an event from an animation"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        """Enable only if the list isn't empty."""
        mdl_base = utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            anim_list = mdl_base.nvb.animList
            anim_list_idx = mdl_base.nvb.animListIdx
            if (anim_list_idx >= 0) and len(anim_list) > anim_list_idx:
                anim = anim_list[anim_list_idx]
                ev_list = anim.eventList
                ev_list_idx = anim.eventListIdx
                return ev_list_idx >= 0 and len(ev_list) > ev_list_idx
        return False

    def execute(self, context):
        mdl_base = utils.get_mdl_root_from_object(context.object)
        anim = mdl_base.nvb.animList[mdl_base.nvb.animListIdx]
        eventList = anim.eventList
        eventIdx = anim.eventListIdx

        eventList.remove(eventIdx)
        if eventIdx > 0:
            eventIdx = eventIdx - 1

        return {'FINISHED'}