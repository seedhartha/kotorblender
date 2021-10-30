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
    """Move an item in the animation list, without affecting keyframes"""

    bl_idname = "kb.anim_move"
    bl_label = "Move an animation in the list, without affecting keyframes"
    bl_options = {'UNDO'}

    direction : bpy.props.EnumProperty(items=(("UP", "Up", ""),
                                              ("DOWN", "Down", "")))

    @classmethod
    def poll(self, context):
        """Prevent execution if animation list has less than 2 elements."""
        mdl_base = utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            return (len(mdl_base.kb.anim_list) > 1)
        return False

    def execute(self, context):
        """Move an item in the animation list."""
        mdl_base = utils.get_mdl_root_from_object(context.object)
        anim_list = mdl_base.kb.anim_list

        current_idx = mdl_base.kb.anim_list_idx
        new_idx = 0
        max_idx = len(anim_list) - 1
        if self.direction == "DOWN":
            new_idx = current_idx + 1
        elif self.direction == "UP":
            new_idx = current_idx - 1
        else:
            return {'CANCELLED'}

        new_idx = max(0, min(new_idx, max_idx))
        if new_idx == current_idx:
            return {'CANCELLED'}
        anim_list.move(current_idx, new_idx)
        mdl_base.kb.anim_list_idx = new_idx
        return {'FINISHED'}
