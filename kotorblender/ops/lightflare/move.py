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


class KB_OT_move_lightflare(bpy.types.Operator):
    bl_idname = "kb.lightflare_move"
    bl_label = "Move an item in the flare list"

    direction: bpy.props.EnumProperty(items=(("UP", "Up", ""), ("DOWN", "Down", "")))

    @classmethod
    def poll(cls, context):
        return len(context.object.kb.flare_list) > 0

    def move_index(self, context):
        flare_list = context.object.kb.flare_list
        flare_idx = context.object.kb.flare_listIdx

        listLength = len(flare_list) - 1  # (index starts at 0)
        new_idx = 0
        if self.direction == "UP":
            new_idx = flare_idx - 1
        elif self.direction == "DOWN":
            new_idx = flare_idx + 1

        new_idx = max(0, min(new_idx, listLength))
        context.object.kb.flare_listIdx = new_idx

    def execute(self, context):
        flare_list = context.object.kb.flare_list
        flare_idx = context.object.kb.flare_listIdx

        if self.direction == "DOWN":
            neighbour = flare_idx + 1
            flare_list.move(flare_idx, neighbour)
            self.move_index(context)
        elif self.direction == "UP":
            neighbour = flare_idx - 1
            flare_list.move(neighbour, flare_idx)
            self.move_index(context)
        else:
            return{'CANCELLED'}

        return{'FINISHED'}
