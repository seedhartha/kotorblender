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
import bpy_extras

from ... import io


class KB_OT_import_mdl(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Odyssey Engine model (.mdl)"""

    bl_idname = "kb.mdlimport"
    bl_label = "Import Odyssey MDL"
    bl_options = {'UNDO'}

    filename_ext = ".mdl"

    filter_glob : bpy.props.StringProperty(
        default = "*.mdl",
        options = {'HIDDEN'})

    importAnimations : bpy.props.BoolProperty(
        name = "Import Animations",
        default = True)

    importWalkmeshes : bpy.props.BoolProperty(
        name = "Import Walkmeshes",
        description = "Import area, placeable and door walkmeshes",
        default = True)

    importMaterials : bpy.props.BoolProperty(
        name = "Import Materials",
        default = True)

    importArmatures : bpy.props.BoolProperty(
        name = "Import Armatures",
        description = "Create an animated armature from model nodes",
        default = True)

    textureSearchRecursive : bpy.props.BoolProperty(
        name="Image search",
        description="Search for textures in subdirectories",
        default=False)

    def execute(self, context):
        return io.load_mdl(**self.as_keywords(ignore=("filter_glob",)))
