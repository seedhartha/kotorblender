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


class KB_OT_delete_lightflare(bpy.types.Operator):
    """ Delete the selected item from the flare list """

    bl_idname = "kb.lightflare_delete"
    bl_label = "Deletes a flare from the light"

    @classmethod
    def poll(cls, context):
        return len(context.object.kb.flare_list) > 0

    def execute(self, context):
        obj = context.object
        flare_list = obj.kb.flare_list
        flare_idx = obj.kb.flare_listIdx

        if flare_idx == len(flare_list) - 1 and flare_idx > 0:
            obj.kb.flare_listIdx = flare_idx - 1

        flare_list.remove(flare_idx)

        return{"FINISHED"}
