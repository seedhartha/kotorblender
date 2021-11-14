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

from ....defines import MeshType

from .... import utils


class KB_PT_emitter(bpy.types.Panel):
    bl_label = "Emitter"
    bl_parent_id = "KB_PT_modelnode"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return utils.is_mesh_type(context.object, MeshType.EMITTER)

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.use_property_split = True

        row = layout.row()
        row.prop(obj.kb, "update")
        row = layout.row()
        row.prop(obj.kb, "emitter_render")
        row = layout.row()
        row.prop(obj.kb, "blend")
        row = layout.row()
        row.prop(obj.kb, "spawntype")

        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "xsize", text="Size X")
        col.prop(obj.kb, "ysize", text="Y")

        row = layout.row()
        row.prop(obj.kb, "texture")

        if obj.kb.depth_texture:
            row = layout.row()
            row.prop(obj.kb, "depth_texture_name", text="Depth Texture")

        row = layout.row()
        row.prop(obj.kb, "chunk_name", text="Chunk")

        row = layout.row()
        row.prop(obj.kb, "num_branches")
        row = layout.row()
        row.prop(obj.kb, "renderorder")
        row = layout.row()
        row.prop(obj.kb, "threshold")

        row = layout.row()
        row.prop(obj.kb, "combinetime")
        row = layout.row()
        row.prop(obj.kb, "deadspace")

        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "twosidedtex")
        col.prop(obj.kb, "depth_texture")
        col.prop(obj.kb, "p2p")

        row = layout.row()
        col = row.column(align=True, heading="Inheritance")
        col.prop(obj.kb, "inherit", text="Inherit")
        col.prop(obj.kb, "inherit_local", text="Local")
        col.prop(obj.kb, "inheritvel", text="Velocity")
        col.prop(obj.kb, "inherit_part", text="Particle")


class KB_PT_emitter_particles(bpy.types.Panel):
    bl_label = "Particles"
    bl_parent_id = "KB_PT_emitter"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return utils.is_mesh_type(context.object, MeshType.EMITTER)

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.use_property_split = True

        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "percentstart", text="Percent Start")
        col.prop(obj.kb, "percentmid", text="Mid")
        col.prop(obj.kb, "percentend", text="End")

        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "colorstart", text="Color Start")
        col.prop(obj.kb, "colormid", text="Mid")
        col.prop(obj.kb, "colorend", text="End")

        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "alphastart", text="Alpha Start")
        col.prop(obj.kb, "alphamid", text="Mid")
        col.prop(obj.kb, "alphaend", text="End")

        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "sizestart", text="Size Start")
        col.prop(obj.kb, "sizemid", text="Mid")
        col.prop(obj.kb, "sizeend", text="End")

        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "sizestart_y", text="Y Size Start")
        col.prop(obj.kb, "sizemid_y", text="Mid")
        col.prop(obj.kb, "sizeend_y", text="End")

        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "birthrate", text="Birthrate")
        col.prop(obj.kb, "randombirthrate", text="Random")

        row = layout.row()
        row.prop(obj.kb, "lifeexp")
        row = layout.row()
        row.prop(obj.kb, "mass")
        row = layout.row()
        row.prop(obj.kb, "spread")
        row = layout.row()
        row.prop(obj.kb, "particlerot", text="Rotation")

        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "velocity", text="Velocity")
        col.prop(obj.kb, "randvel", text="Random")

        row = layout.row()
        row.prop(obj.kb, "blurlength")
        row = layout.row()
        row.prop(obj.kb, "targetsize")

        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "tangentspread", text="Tangent Spread")
        col.prop(obj.kb, "tangentlength", text="Length")

        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "blastradius", text="Blast Radius")
        col.prop(obj.kb, "blastlength", text="Length")

        if obj.kb.bounce:
            row = layout.row()
            row.prop(obj.kb, "bounce_co")

        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "bounce")
        col.prop(obj.kb, "loop")
        col.prop(obj.kb, "splat")
        col.prop(obj.kb, "affected_by_wind")
        col.prop(obj.kb, "tinted")


class KB_PT_emitter_texture_anim(bpy.types.Panel):
    bl_label = "Texture Animation"
    bl_parent_id = "KB_PT_emitter"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return utils.is_mesh_type(context.object, MeshType.EMITTER)

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.use_property_split = True

        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "xgrid", text="Grid X")
        col.prop(obj.kb, "ygrid", text="Y")

        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "framestart", text="Frame Start")
        col.prop(obj.kb, "frameend", text="End")

        row = layout.row()
        row.prop(obj.kb, "fps")

        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "frame_blending")
        col.prop(obj.kb, "random")


class KB_PT_emitter_lighting(bpy.types.Panel):
    bl_label = "Lighting"
    bl_parent_id = "KB_PT_emitter"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return utils.is_mesh_type(obj, MeshType.EMITTER) and obj.kb.update == "Lightning"

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.use_property_split = True

        row = layout.row()
        row.prop(obj.kb, "lightningdelay", text="Delay")
        row = layout.row()
        row.prop(obj.kb, "lightningradius", text="Radius")
        row = layout.row()
        row.prop(obj.kb, "lightningsubdiv", text="Subdivisions")
        row = layout.row()
        row.prop(obj.kb, "lightningscale", text="Scale")
        row = layout.row()
        row.prop(obj.kb, "lightningzigzag", text="Zig-Zag")


class KB_PT_emitter_p2p(bpy.types.Panel):
    bl_label = "P2P"
    bl_parent_id = "KB_PT_emitter"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return utils.is_mesh_type(obj, MeshType.EMITTER) and obj.kb.p2p

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.use_property_split = True

        row = layout.row()
        row.prop(obj.kb, "p2p_type")

        if obj.kb.p2p_type == "Bezier":
            row = layout.row()
            row.prop(obj.kb, "p2p_bezier2")
            row = layout.row()
            row.prop(obj.kb, "p2p_bezier3")
        elif obj.kb.p2p_type == "Gravity":
            row = layout.row()
            row.prop(obj.kb, "grav")
            row = layout.row()
            row.prop(obj.kb, "drag")


class KB_PT_emitter_control_points(bpy.types.Panel):
    bl_label = "Control Points"
    bl_parent_id = "KB_PT_emitter"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return utils.is_mesh_type(obj, MeshType.EMITTER)

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.use_property_split = True

        row = layout.row()
        row.prop(obj.kb, "numcontrolpts", text="Number of Points")
        row = layout.row()
        row.prop(obj.kb, "controlptradius", text="Radius")
        row = layout.row()
        row.prop(obj.kb, "controlptdelay", text="Delay")
        row = layout.row()
        row.prop(obj.kb, "controlptsmoothing", text="Smoothing")
