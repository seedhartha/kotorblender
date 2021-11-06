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

from ... import defines, utils


class KB_PT_emitter(bpy.types.Panel):
    """
    Property panel for additional properties needed for the mdl file
    format. This is only available for particle systems.
    It is located under the particle panel in the properties window
    """
    bl_label = "Odyssey Emitter Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        try:
            return context.object and \
                context.object.type == 'MESH' and \
                context.object.kb.meshtype == defines.Meshtype.EMITTER
        except:
            return False

    def draw(self, context):
        obj = context.object

        layout = self.layout

        row = layout.row()
        row.prop(obj.kb, "meshtype", text="Type")
        row = layout.row()
        row.prop(obj.kb, "node_number")
        row = layout.row()
        row.prop(obj.kb, "export_order")

        layout.separator()

        box = layout.row().box()
        row = box.row()
        row.prop(obj.kb, "update")
        row = box.row()
        row.prop(obj.kb, "render_emitter")
        if obj.kb.update == "Lightning" or \
           not utils.is_null(obj.kb.chunk_name):
            row.enabled = False
        row = box.row()
        row.prop(obj.kb, "blend")
        if not utils.is_null(obj.kb.chunk_name):
            row.enabled = False
        row = box.row()
        row.prop(obj.kb, "spawntype")
        if obj.kb.update != "Fountain" or \
           not utils.is_null(obj.kb.chunk_name):
            row.enabled = False

        box.separator()

        row = box.row()
        row.label(text="Emitter Size (cm)")
        row = box.row(align=True)
        row.prop(obj.kb, "xsize")
        row.prop(obj.kb, "ysize")

        box.separator()

        # Inheritance
        row = box.row()
        row.label(text="Inheritance")
        row = box.row()
        row.prop(obj.kb, "inherit")
        row.prop(obj.kb, "inherit_local")
        row = box.row()
        row.prop(obj.kb, "inheritvel")
        if obj.kb.update == "Lightning":
            row.enabled = False
        row.prop(obj.kb, "inherit_part")

        box.separator()

        row = box.row()
        row.label(text="Miscellaneous")
        row = box.row()
        row.prop(obj.kb, "num_branches")
        row = box.row()
        row.prop(obj.kb, "renderorder")
        row = box.row()
        row.prop(obj.kb, "threshold")

        row = box.row()
        box.label(text="Blur")
        row = box.row()
        row.prop(obj.kb, "combinetime")
        row = box.row()
        row.prop(obj.kb, "deadspace")

        box = layout.row().box()
        row = box.row()
        row.label(text="Particles", icon='PARTICLE_DATA')
        row = box.row()
        row.label(text="")
        row.label(text="Start")
        row.label(text="Mid")
        row.label(text="End")
        row = box.row()
        row.label(text="Percent")
        row.prop(obj.kb, "percentstart", text="")
        row.prop(obj.kb, "percentmid", text="")
        row.prop(obj.kb, "percentend", text="")
        row = box.row()
        row.label(text="Color")
        row.prop(obj.kb, "colorstart", text="")
        row.prop(obj.kb, "colormid", text="")
        row.prop(obj.kb, "colorend", text="")
        row = box.row()
        row.label(text="Alpha")
        row.prop(obj.kb, "alphastart", text="")
        row.prop(obj.kb, "alphamid", text="")
        row.prop(obj.kb, "alphaend", text="")
        row = box.row()
        row.label(text="Size X")
        row.prop(obj.kb, "sizestart", text="")
        row.prop(obj.kb, "sizemid", text="")
        row.prop(obj.kb, "sizeend", text="")
        row = box.row()
        row.label(text="Size Y")
        row.prop(obj.kb, "sizestart_y", text="")
        row.prop(obj.kb, "sizemid_y", text="")
        row.prop(obj.kb, "sizeend_y", text="")

        box.separator()

        row = box.row()
        row.label(text="Birthrate")
        row = box.row()
        col = row.column()
        col.prop(obj.kb, "birthrate", text="")
        if obj.kb.update == "Lightning":
            col.enabled = False
        col = row.column()
        col.prop(obj.kb, "randombirthrate", text="Random")
        if obj.kb.update == "Lightning":
            col.enabled = False
        row = box.row()
        col = row.column()
        col.prop(obj.kb, "lifeexp")
        if obj.kb.update == "Lightning":
            col.enabled = False
        col = row.column()
        col.prop(obj.kb, "mass")
        if obj.kb.update == "Lightning":
            col.enabled = False
        row = box.row()
        col = row.column()
        col.prop(obj.kb, "spread")
        if obj.kb.update == "Lightning":
            col.enabled = False
        col = row.column()
        col.prop(obj.kb, "particlerot")
        if obj.kb.update == "Lightning":
            col.enabled = False
        row = box.row()
        col = row.column()
        col.prop(obj.kb, "velocity")
        if obj.kb.update == "Lightning":
            col.enabled = False
        col = row.column()
        col.prop(obj.kb, "randvel")
        if obj.kb.update == "Lightning":
            col.enabled = False
        row = box.row()
        row.prop(obj.kb, "blurlength")
        row = box.row()
        row.prop(obj.kb, "targetsize")
        row = box.row()
        row.label(text="Tangent")
        row = box.row()
        row.prop(obj.kb, "tangentspread", text="Spread")
        row.prop(obj.kb, "tangentlength", text="Length")
        # detonate
        row = box.row()
        col = row.column()
        col.prop(obj.kb, "bounce")
        if obj.kb.update == "Lightning":
            col.enabled = False
        col = row.column()
        col.prop(obj.kb, "bounce_co")
        if obj.kb.update == "Lightning":
            col.enabled = False
        row = box.row()
        col = row.column()
        col.prop(obj.kb, "loop")
        if obj.kb.update != "Single" and \
           obj.kb.update != "Explosion":
            col.enabled = False
        col = row.column()
        col.prop(obj.kb, "splat")
        row = box.row()
        row.prop(obj.kb, "affected_by_wind")
        if obj.kb.update == "Lightning":
            row.enabled = False
        row = box.row()
        row.prop(obj.kb, "tinted")

        box = layout.row().box()
        row = box.row()
        row.label(text="Texture / Chunk", icon='TEXTURE')
        row = box.row()
        row.prop(obj.kb, "texture")
        if not utils.is_null(obj.kb.chunk_name):
            row.enabled = False
        row = box.row()
        row.prop(obj.kb, "twosidedtex")
        if not utils.is_null(obj.kb.chunk_name):
            row.enabled = False

        box.separator()

        row = box.row()
        row.label(text="Texture Animation")
        row = box.row()
        row.label(text="Grid")
        row.prop(obj.kb, "xgrid", text="X")
        row.prop(obj.kb, "ygrid", text="Y")
        if not utils.is_null(obj.kb.chunk_name):
            row.enabled = False
        row = box.row()
        row.prop(obj.kb, "fps")
        row = box.row()
        row.prop(obj.kb, "framestart")
        row.prop(obj.kb, "frameend")
        row = box.row()
        row.prop(obj.kb, "frame_blending")
        row = box.row()
        row.prop(obj.kb, "random")

        box.separator()

        row = box.row()
        row.label(text="Depth Texture")
        row = box.row()
        row.prop(obj.kb, "depth_texture")
        row = box.row()
        row.prop(obj.kb, "depth_texture_name", text="")

        box.separator()

        row = box.row()
        row.label(text="Chunk Model")
        row = box.row()
        row.prop(obj.kb, "chunk_name", text="")

        box = layout.row().box()
        row = box.row()
        row.label(text="Advanced", icon='PREFERENCES')

        # Lightning
        parent_box = box
        box = box.row().box()
        if obj.kb.update != "Lightning":
            box.enabled = False
        row = box.row()
        row.label(text="Lightning")
        row = box.row()
        row.prop(obj.kb, "lightningdelay")
        row = box.row()
        row.prop(obj.kb, "lightningradius")
        row = box.row()
        row.prop(obj.kb, "lightningsubdiv")
        row = box.row()
        row.prop(obj.kb, "lightningscale")
        row = box.row()
        row.prop(obj.kb, "lightningzigzag")
        box = parent_box

        box.separator()

        # Blast props
        parent_box = box
        box = box.row().box()
        row = box.row()
        row.label(text="Blast")
        row = box.row()
        row.prop(obj.kb, "blastradius")
        row = box.row()
        row.prop(obj.kb, "blastlength")
        box = parent_box

        box.separator()

        # p2p settings
        parent_box = box
        box = box.row().box()
        if obj.kb.update != "Fountain" and\
           obj.kb.update != "Single":
            box.enabled = False
        row = box.row()
        row.label(text="P2P Settings")
        row = box.row()
        row.prop(obj.kb, "p2p")
        row = box.row()
        row.prop(obj.kb, "p2p_type")
        if not obj.kb.p2p:
            row.enabled = False
        if not obj.kb.p2p:
            row.enabled = False
        row = box.row()
        row.prop(obj.kb, "p2p_bezier2")
        if not obj.kb.p2p or \
           obj.kb.p2p_type == "Gravity":
            row.enabled = False
        row = box.row()
        row.prop(obj.kb, "p2p_bezier3")
        if not obj.kb.p2p or \
           obj.kb.p2p_type == "Gravity":
            row.enabled = False
        row = box.row()
        row.prop(obj.kb, "grav")
        if not obj.kb.p2p or \
           obj.kb.p2p_type == "Bezier":
            row.enabled = False
        row = box.row()
        row.prop(obj.kb, "drag")
        if not obj.kb.p2p or \
           obj.kb.p2p_type == "Bezier":
            row.enabled = False
        box = parent_box

        box.separator()

        parent_box = box
        box = box.row().box()
        row = box.row()
        row.label(text="Control Points")
        row = box.row()
        row.prop(obj.kb, "numcontrolpts")
        row = box.row()
        row.prop(obj.kb, "controlptradius")
        row = box.row()
        row.prop(obj.kb, "controlptdelay")
        row = box.row()
        row.prop(obj.kb, "controlptsmoothing")
        box = parent_box
