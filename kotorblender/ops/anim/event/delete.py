# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

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
            anim_list = mdl_base.kb.animList
            anim_list_idx = mdl_base.kb.animListIdx
            if (anim_list_idx >= 0) and len(anim_list) > anim_list_idx:
                anim = anim_list[anim_list_idx]
                ev_list = anim.eventList
                ev_list_idx = anim.eventListIdx
                return ev_list_idx >= 0 and len(ev_list) > ev_list_idx
        return False

    def execute(self, context):
        mdl_base = utils.get_mdl_root_from_object(context.object)
        anim = mdl_base.kb.animList[mdl_base.kb.animListIdx]
        eventList = anim.eventList
        eventIdx = anim.eventListIdx

        eventList.remove(eventIdx)
        if eventIdx > 0:
            eventIdx = eventIdx - 1

        return {'FINISHED'}
