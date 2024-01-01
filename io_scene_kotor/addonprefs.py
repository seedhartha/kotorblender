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

from bpy.types import AddonPreferences
from bpy.props import StringProperty

from .constants import PACKAGE_NAME

DEF_TEXTURE_SEARCH_PATHS = "textures;../textures;../texturepacks/swpc_tex_tpa"
DEF_LIGHTMAP_SEARCH_PATHS = "lightmaps;../lightmaps"


class KotorBlenderAddonPreferences(AddonPreferences):
    bl_idname = PACKAGE_NAME

    texture_search_paths: StringProperty(
        name="Texture Search Paths",
        description="Semicolon-separated list of paths. Can be relative to the imported layout or absolute.",
        default=DEF_TEXTURE_SEARCH_PATHS,
    )

    lightmap_search_paths: StringProperty(
        name="Lightmap Search Paths",
        description="Semicolon-separated list of paths. Can be relative to the imported layout or absolute.",
        default=DEF_LIGHTMAP_SEARCH_PATHS,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "texture_search_paths")
        layout.prop(self, "lightmap_search_paths")
