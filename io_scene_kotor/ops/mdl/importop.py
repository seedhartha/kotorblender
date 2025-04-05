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

import os

import bpy

from bpy_extras.io_utils import ImportHelper

from ...constants import PACKAGE_NAME, ImportOptions
from ...io import mdl
from ...utils import logger, semicolon_separated_to_absolute_paths


class KB_OT_import_mdl(bpy.types.Operator, ImportHelper):
    bl_idname = "kb.mdlimport"
    bl_label = "Import KotOR MDL"
    bl_options = {"UNDO"}

    filename_ext = ".mdl"

    filter_glob: bpy.props.StringProperty(default="*.mdl", options={"HIDDEN"})

    import_geometry: bpy.props.BoolProperty(
        name="Import Geometry",
        description="Untick to import animations from supermodel",
        default=True,
    )

    import_animations: bpy.props.BoolProperty(name="Import Animations", default=True)

    import_walkmeshes: bpy.props.BoolProperty(
        name="Import Walkmeshes",
        description="Import area, door and placeable walkmeshes",
        default=True,
    )

    build_materials: bpy.props.BoolProperty(
        name="Build Materials", description="Build object materials", default=True
    )

    build_armature: bpy.props.BoolProperty(
        name="Build Armature", description="Build armature from MDL root"
    )

    def execute(self, context):
        options = ImportOptions()
        options.import_geometry = self.import_geometry
        options.import_animations = self.import_animations
        options.import_walkmeshes = self.import_walkmeshes
        options.build_materials = self.build_materials
        options.build_armature = self.build_armature

        preferences = context.preferences
        addon_preferences = preferences.addons[PACKAGE_NAME].preferences
        options.texture_search_paths = semicolon_separated_to_absolute_paths(
            addon_preferences.texture_search_paths, os.path.dirname(self.filepath)
        )
        options.lightmap_search_paths = semicolon_separated_to_absolute_paths(
            addon_preferences.lightmap_search_paths, os.path.dirname(self.filepath)
        )

        try:
            mdl.load_mdl(self, self.filepath, options)
        except Exception as ex:
            logger().exception(f"Error loading MDL file [{self.filepath}]")
            self.report({"ERROR"}, str(ex))

        return {"FINISHED"}
