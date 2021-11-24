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

import traceback

import bpy

from bpy_extras.io_utils import ExportHelper

from ...defines import ExportOptions
from ...io import mdl


class KB_OT_export_mdl(bpy.types.Operator, ExportHelper):
    bl_idname = "kb.mdlexport"
    bl_label = "Export KotOR MDL"

    filename_ext = ".mdl"

    filter_glob: bpy.props.StringProperty(
        default="*.mdl",
        options={'HIDDEN'})

    export_for_tsl: bpy.props.BoolProperty(
        name="Export for TSL",
        description="Use The Sith Lords MDL format")

    export_for_xbox: bpy.props.BoolProperty(
        name="Export for Xbox",
        description="Use Xbox MDL format")

    export_animations: bpy.props.BoolProperty(
        name="Export Animations",
        default=True)

    export_walkmeshes: bpy.props.BoolProperty(
        name="Export Walkmeshes",
        description="Import area, door and placeable walkmeshes",
        default=True)

    export_custom_normals: bpy.props.BoolProperty(
        name="Export Custom Normals",
        description="Export previously imported normals, if any",
        default=True)

    def execute(self, context):
        options = ExportOptions()
        options.export_for_tsl = self.export_for_tsl
        options.export_for_xbox = self.export_for_xbox
        options.export_animations = self.export_animations
        options.export_walkmeshes = self.export_walkmeshes
        options.export_custom_normals = self.export_custom_normals

        try:
            mdl.save_mdl(self, self.filepath, options)
        except Exception as e:
            print(traceback.format_exc())
            self.report({'ERROR'}, str(e))

        return {'FINISHED'}
