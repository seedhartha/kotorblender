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


class KB_PT_path_point(bpy.types.Panel):
    bl_label = "KotOR Path Point"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return utils.is_path_point(context.object)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        row = layout.row()
        box = row.box()
        box.label(text="Connections")
        row = box.row()
        row.template_list("KB_UL_path_points", "path_points", context.object.kb, "path_connection_list", context.object.kb, "path_connection_idx")
        col = row.column(align=True)
        col.operator("kb.add_path_connection", icon='ADD', text="")
        col.operator("kb.remove_path_connection", icon='REMOVE', text="")
