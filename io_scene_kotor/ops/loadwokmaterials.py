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

from ..scene.material import rebuild_walkmesh_materials


class KB_OT_load_wok_materials(bpy.types.Operator):
    bl_idname = "kb.load_wok_mats"
    bl_label = "Load Walkmesh Materials"

    def execute(self, context):
        if (context.object) and (context.object.type == "MESH"):
            rebuild_walkmesh_materials(context.object)
        else:
            self.report({"INFO"}, "A mesh must be selected")
            return {"CANCELLED"}

        return {"FINISHED"}
