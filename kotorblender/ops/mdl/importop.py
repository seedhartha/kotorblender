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

from bpy_extras.io_utils import ImportHelper

from ...defines import NormalsAlgorithm

from ...io import mdl


class KB_OT_import_mdl(bpy.types.Operator, ImportHelper):
    bl_idname = "kb.mdlimport"
    bl_label = "Import Odyssey MDL"
    bl_options = {'UNDO'}

    filename_ext = ".mdl"

    filter_glob: bpy.props.StringProperty(
        default="*.mdl",
        options={'HIDDEN'})

    import_geometry: bpy.props.BoolProperty(
        name="Import Geometry",
        description="Untick to import animations from supermodel",
        default=True)

    import_animations: bpy.props.BoolProperty(
        name="Import Animations",
        default=True)

    import_walkmeshes: bpy.props.BoolProperty(
        name="Import Walkmeshes",
        description="Import area, door and placeable walkmeshes",
        default=True)

    build_materials: bpy.props.BoolProperty(
        name="Build Materials",
        description="Build object materials",
        default=True)

    build_armature: bpy.props.BoolProperty(
        name="Build Armature",
        description="Build armature from MDL root",
        default=False)

    normals_algorithm: bpy.props.EnumProperty(
        items=[
            (NormalsAlgorithm.NONE, "None", "Ignore normals", 0),
            (NormalsAlgorithm.CUSTOM, "Custom", "Import as Custom Split Normals and enable Auto Smooth", 1),
            (NormalsAlgorithm.SHARP_EDGES, "Sharp Edges", "Merge similar vertices, mark sharp edges and add Edge Split modifier", 2)
        ],
        name="Normals Algorithm",
        description="How to import vertex normals and/or sharp edges",
        default=NormalsAlgorithm.CUSTOM)

    sharp_edge_angle: bpy.props.FloatProperty(
        name="Sharp Edge Angle",
        description="When merging similar vertices, mark edges with an angle higher than this as sharp",
        default=10.0,
        min=0.0,
        max=90.0)

    texture_search_recursive: bpy.props.BoolProperty(
        name="Recursive Texture Search",
        description="Search for textures in subdirectories",
        default=False)

    def execute(self, context):
        mdl.load_mdl(**self.as_keywords(ignore=("filter_glob",)))
        return {'FINISHED'}
