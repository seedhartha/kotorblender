import bpy

from .... import kb_utils


class KB_OT_anim_event_move(bpy.types.Operator):
    """Move an item in the event list"""

    bl_idname = "kb.anim_event_move"
    bl_label = "Move an item in the event  list"
    bl_options = {'UNDO'}

    direction : bpy.props.EnumProperty(items=(("UP", "Up", ""),
                                              ("DOWN", "Down", "")))

    @classmethod
    def poll(self, context):
        """Enable only if the list isn't empty."""
        mdl_base = kb_utils.get_mdl_root_from_object(context.object)
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
        mdl_base = kb_utils.get_mdl_root_from_object(context.object)
        anim = mdl_base.nvb.animList[mdl_base.nvb.animListIdx]
        eventList = anim.eventList

        currentIdx = anim.eventListIdx
        newIdx = 0
        maxIdx = len(eventList) - 1
        if self.direction == "DOWN":
            newIdx = currentIdx + 1
        elif self.direction == "UP":
            newIdx = currentIdx - 1
        else:
            return {'CANCELLED'}

        newIdx = max(0, min(newIdx, maxIdx))
        eventList.move(currentIdx, newIdx)
        anim.eventListIdx = newIdx
        return {'FINISHED'}