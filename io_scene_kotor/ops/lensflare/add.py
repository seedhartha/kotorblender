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

from ... import defines


class KB_OT_add_lens_flare(bpy.types.Operator):
    bl_idname = "kb.add_lens_flare"
    bl_label = "Add lens flare to the list"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'LIGHT' and obj.kb.lensflares

    def execute(self, context):
        flare = context.object.kb.flare_list.add()
        flare.texture = defines.NULL

        return{'FINISHED'}
