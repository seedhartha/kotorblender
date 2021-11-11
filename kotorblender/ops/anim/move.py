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


class KB_OT_anim_move(bpy.types.Operator):
    bl_idname = "kb.anim_move"
    bl_label = "Move an animation in the list, without affecting keyframes"
    bl_options = {'UNDO'}

    direction: bpy.props.EnumProperty(items=(("UP", "Up", ""),
                                             ("DOWN", "Down", "")))

    @classmethod
    def poll(cls, context):
        if not utils.is_mdl_root(context.object):
            return False

        mdl_root = context.object
        anim_list = mdl_root.kb.anim_list
        anim_list_idx = mdl_root.kb.anim_list_idx
        num_anims = len(anim_list)

        return anim_list_idx >= 0 and anim_list_idx < len(anim_list) and num_anims >= 2

    def execute(self, context):
        mdl_root = context.object
        anim_list = mdl_root.kb.anim_list
        prev_idx = mdl_root.kb.anim_list_idx

        if self.direction == 'DOWN':
            new_idx = min(len(anim_list) - 1, prev_idx + 1)
        elif self.direction == 'UP':
            new_idx = max(0, prev_idx - 1)
        else:
            return {'CANCELLED'}

        if new_idx == prev_idx:
            return {'CANCELLED'}

        anim_list.move(prev_idx, new_idx)
        mdl_root.kb.anim_list_idx = new_idx

        return {'FINISHED'}
