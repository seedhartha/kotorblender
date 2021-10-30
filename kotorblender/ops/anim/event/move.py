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
        mdl_base = utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            anim_list = mdl_base.kb.anim_list
            anim_list_idx = mdl_base.kb.anim_list_idx
            if (anim_list_idx >= 0) and len(anim_list) > anim_list_idx:
                anim = anim_list[anim_list_idx]
                ev_list = anim.event_list
                ev_list_idx = anim.event_list_idx
                return ev_list_idx >= 0 and len(ev_list) > ev_list_idx
        return False

    def execute(self, context):
        mdl_base = utils.get_mdl_root_from_object(context.object)
        anim = mdl_base.kb.anim_list[mdl_base.kb.anim_list_idx]
        event_list = anim.event_list

        current_idx = anim.event_list_idx
        new_idx = 0
        max_idx = len(event_list) - 1
        if self.direction == "DOWN":
            new_idx = current_idx + 1
        elif self.direction == "UP":
            new_idx = current_idx - 1
        else:
            return {'CANCELLED'}

        new_idx = max(0, min(new_idx, max_idx))
        event_list.move(current_idx, new_idx)
        anim.event_list_idx = new_idx
        return {'FINISHED'}
