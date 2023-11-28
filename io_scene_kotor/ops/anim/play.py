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

from ... import utils


class KB_OT_play_animation(bpy.types.Operator):
    bl_idname = "kb.play_animation"
    bl_label = "Set start and end frame of the scene to this animation"

    @classmethod
    def poll(cls, context):
        obj = context.object
        if not utils.is_mdl_root(obj):
            return False

        anim_list = obj.kb.anim_list
        anim_list_idx = obj.kb.anim_list_idx

        return anim_list_idx >= 0 and anim_list_idx < len(anim_list)

    def execute(self, context):
        mdl_root = context.object
        anim_list = mdl_root.kb.anim_list
        anim_list_idx = mdl_root.kb.anim_list_idx

        scene = context.scene
        scene.frame_current = anim_list[anim_list_idx].frame_start
        scene.frame_start = anim_list[anim_list_idx].frame_start
        scene.frame_end = anim_list[anim_list_idx].frame_end

        return {'FINISHED'}
