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
import traceback

from math import radians

import bpy

from bpy_extras.io_utils import ImportHelper

from ...defines import ImportOptions, NormalsAlgorithm

from ...io import mdl


class KB_OT_import_mdl(bpy.types.Operator, ImportHelper):
    bl_idname = "kb.mdlimport"
    bl_label = "Import KotOR MDL"
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
        description="Build armature from MDL root")

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
        default=radians(10.0), min=0.0, max=radians(90.0),
        subtype='ANGLE')

    texture_search_recursive: bpy.props.BoolProperty(
        name="Recursive Texture Search",
        description="Search for textures in subdirectories")

    def execute(self, context):
        options = ImportOptions()
        options.import_geometry = self.import_geometry
        options.import_animations = self.import_animations
        options.import_walkmeshes = self.import_walkmeshes
        options.build_materials = self.build_materials
        options.build_armature = self.build_armature
        options.normals_algorithm = self.normals_algorithm
        options.sharp_edge_angle = self.sharp_edge_angle
        options.texture_path = os.path.dirname(self.filepath)
        options.texture_search_recursive = self.texture_search_recursive

        try:
            mdl.load_mdl(self, self.filepath, options)
        except Exception as e:
            print(traceback.format_exc())
            self.report({'ERROR'}, str(e))

        return {'FINISHED'}
