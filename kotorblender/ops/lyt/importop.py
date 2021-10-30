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


class KB_OT_import_lyt(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Odyssey Engine layout (.lyt)"""

    bl_idname = "kb.lytimport"
    bl_label = "Import Odyssey LYT"
    bl_options = {'UNDO'}

    filename_ext = ".lyt"

    filter_glob : bpy.props.StringProperty(
        default="*.lyt",
        options={'HIDDEN'})

    importGeometry : bpy.props.BoolProperty(
        name = "Import Geometry",
        description = "Disable if only animations are needed",
        default = True)

    importMaterials : bpy.props.BoolProperty(
        name = "Import Materials",
        description = "Import materials",
        default = True)

    importAnim : bpy.props.BoolProperty(
        name = "Import Animations",
        description = "Import animations",
        default = True)

    importWalkmesh : bpy.props.BoolProperty(
        name = "Import Walkmesh",
        description = "Attempt to load placeable and door walkmeshes",
        default = True)

    textureSearch : bpy.props.BoolProperty(
        name="Image search",
        description="Search for images in subdirectories" \
                " (Warning, may be slow)",
        default=False)

    def execute(self, context):
        return io.load_lyt(self, context, **self.as_keywords(ignore=("filter_glob",)))