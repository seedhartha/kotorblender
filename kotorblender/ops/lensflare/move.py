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


class KB_OT_move_lens_flare(bpy.types.Operator):
    bl_idname = "kb.move_lens_flare"
    bl_label = "Move lens flare within the list"

    direction: bpy.props.EnumProperty(items=(("UP", "Up", ""),
                                             ("DOWN", "Down", "")))

    @classmethod
    def poll(cls, context):
        obj = context.object
        if not obj or obj.type != 'LIGHT' or not obj.kb.lensflares:
            return False

        flare_list = obj.kb.flare_list
        flare_list_idx = obj.kb.flare_list_idx
        num_flares = len(flare_list)

        return flare_list_idx >= 0 and flare_list_idx < num_flares and num_flares >= 2

    def move_index(self, context):
        obj = context.object
        flare_list = obj.kb.flare_list
        flare_list_idx = obj.kb.flare_list_idx

        listLength = len(flare_list) - 1
        new_idx = 0
        if self.direction == "UP":
            new_idx = flare_list_idx - 1
        elif self.direction == "DOWN":
            new_idx = flare_list_idx + 1

        new_idx = max(0, min(new_idx, listLength))
        obj.kb.flare_list_idx = new_idx

    def execute(self, context):
        obj = context.object
        flare_list = obj.kb.flare_list
        flare_list_idx = obj.kb.flare_list_idx

        if self.direction == "DOWN":
            neighbour = flare_list_idx + 1
            flare_list.move(flare_list_idx, neighbour)
            self.move_index(context)
        elif self.direction == "UP":
            neighbour = flare_list_idx - 1
            flare_list.move(neighbour, flare_list_idx)
            self.move_index(context)
        else:
            return{'CANCELLED'}

        return{'FINISHED'}
