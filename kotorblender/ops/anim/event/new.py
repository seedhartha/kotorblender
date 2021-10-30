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


class KB_OT_anim_event_new(bpy.types.Operator):
    """Add a new item to the event list"""

    bl_idname = "kb.anim_event_new"
    bl_label = "Add a new event to an animation"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        """Enable only if there is an animation."""
        mdl_base = utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            anim_list = mdl_base.kb.anim_list
            anim_list_idx = mdl_base.kb.anim_list_idx
            return (anim_list_idx >= 0) and len(anim_list) > anim_list_idx
        return False

    def execute(self, context):
        """Add the new item."""
        mdl_base = utils.get_mdl_root_from_object(context.object)
        anim = mdl_base.kb.anim_list[mdl_base.kb.anim_list_idx]

        event_list = anim.event_list
        new_event = event_list.add()
        if anim.frame_start <= bpy.context.scene.frame_current <= anim.frame_end:
            new_event.frame = bpy.context.scene.frame_current
        else:
            new_event.frame = anim.frame_start

        return {'FINISHED'}
