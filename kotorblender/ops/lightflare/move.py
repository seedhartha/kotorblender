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
    """ Move an item in the flare list """

    bl_idname = "kb.lightflare_move"
    bl_label  = "Move an item in the flare list"

    direction : bpy.props.EnumProperty(items=(("UP", "Up", ""), ("DOWN", "Down", "")))

    @classmethod
    def poll(self, context):
        return len(context.object.kb.flareList) > 0

    def move_index(self, context):
        flareList = context.object.kb.flareList
        flareIdx  = context.object.kb.flareListIdx

        listLength = len(flareList) - 1 # (index starts at 0)
        newIdx = 0
        if self.direction == "UP":
            newIdx = flareIdx - 1
        elif self.direction == "DOWN":
            newIdx = flareIdx + 1

        newIdx   = max(0, min(newIdx, listLength))
        context.object.kb.flareListIdx = newIdx

    def execute(self, context):
        flareList = context.object.kb.flareList
        flareIdx  = context.object.kb.flareListIdx

        if self.direction == "DOWN":
            neighbour = flareIdx + 1
            flareList.move(flareIdx, neighbour)
            self.move_index(context)
        elif self.direction == "UP":
            neighbour = flareIdx - 1
            flareList.move(neighbour, flareIdx)
            self.move_index(context)
        else:
            return{'CANCELLED'}

        return{'FINISHED'}
