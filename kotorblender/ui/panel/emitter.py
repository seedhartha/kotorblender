import bpy

from ... import (defines, utils)


class KB_PT_emitter(bpy.types.Panel):
    """
    Property panel for additional properties needed for the mdl file
    format. This is only available for particle systems.
    It is located under the particle panel in the properties window
    """
    bl_label       = "Odyssey Emitter Properties"
    bl_space_type  = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        try:
            return context.object and \
                   context.object.type == 'MESH' and \
                   context.object.nvb.meshtype == defines.Meshtype.EMITTER
        except:
            return False

    def draw(self, context):
        obj = context.object

        layout = self.layout

        row = layout.row()
        row.prop(obj.nvb, "meshtype", text="Type")

        layout.separator()

        box = layout.row().box()
        row = box.row()
        row.prop(obj.nvb, "update")
        row = box.row()
        row.prop(obj.nvb, "render_emitter")
        if obj.nvb.update == "Lightning" or \
           not utils.is_null(obj.nvb.chunkName):
            row.enabled = False
        row = box.row()
        row.prop(obj.nvb, "blend")
        if not utils.is_null(obj.nvb.chunkName):
            row.enabled = False
        row = box.row()
        row.prop(obj.nvb, "spawntype")
        if obj.nvb.update != "Fountain" or \
           not utils.is_null(obj.nvb.chunkName):
            row.enabled = False

        box.separator()

        row = box.row()
        row.label(text="Emitter Size (cm)")
        row = box.row(align=True)
        row.prop(obj.nvb, "xsize")
        row.prop(obj.nvb, "ysize")

        box.separator()

        # Inheritance
        row = box.row()
        row.label(text="Inheritance")
        row = box.row()
        row.prop(obj.nvb, "inherit")
        row.prop(obj.nvb, "inherit_local")
        row = box.row()
        row.prop(obj.nvb, "inheritvel")
        if obj.nvb.update == "Lightning":
            row.enabled = False
        row.prop(obj.nvb, "inherit_part")

        box.separator()

        row = box.row()
        row.label(text="Miscellaneous")
        row = box.row()
        row.prop(obj.nvb, "numBranches")
        row = box.row()
        row.prop(obj.nvb, "renderorder")
        row = box.row()
        row.prop(obj.nvb, "threshold")

        row = box.row()
        box.label(text="Blur")
        row = box.row()
        row.prop(obj.nvb, "combinetime")
        row = box.row()
        row.prop(obj.nvb, "deadspace")

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
        row.prop(obj.nvb, "percentstart", text="")
        row.prop(obj.nvb, "percentmid", text="")
        row.prop(obj.nvb, "percentend", text="")
        row = box.row()
        row.label(text="Color")
        row.prop(obj.nvb, "colorstart", text="")
        row.prop(obj.nvb, "colormid", text="")
        row.prop(obj.nvb, "colorend", text="")
        row = box.row()
        row.label(text="Alpha")
        row.prop(obj.nvb, "alphastart", text="")
        row.prop(obj.nvb, "alphamid", text="")
        row.prop(obj.nvb, "alphaend", text="")
        row = box.row()
        row.label(text="Size X")
        row.prop(obj.nvb, "sizestart", text="")
        row.prop(obj.nvb, "sizemid", text="")
        row.prop(obj.nvb, "sizeend", text="")
        row = box.row()
        row.label(text="Size Y")
        row.prop(obj.nvb, "sizestart_y", text="")
        row.prop(obj.nvb, "sizemid_y", text="")
        row.prop(obj.nvb, "sizeend_y", text="")

        box.separator()

        row = box.row()
        row.label(text="Birthrate")
        row = box.row()
        col = row.column()
        col.prop(obj.nvb, "birthrate", text="")
        if obj.nvb.update == "Lightning":
            col.enabled = False
        col = row.column()
        col.prop(obj.nvb, "m_frandombirthrate", text="Random")
        if obj.nvb.update == "Lightning":
            col.enabled = False
        row = box.row()
        col = row.column()
        col.prop(obj.nvb, "lifeexp")
        if obj.nvb.update == "Lightning":
            col.enabled = False
        col = row.column()
        col.prop(obj.nvb, "mass")
        if obj.nvb.update == "Lightning":
            col.enabled = False
        row = box.row()
        col = row.column()
        col.prop(obj.nvb, "spread")
        if obj.nvb.update == "Lightning":
            col.enabled = False
        col = row.column()
        col.prop(obj.nvb, "particlerot")
        if obj.nvb.update == "Lightning":
            col.enabled = False
        row = box.row()
        col = row.column()
        col.prop(obj.nvb, "velocity")
        if obj.nvb.update == "Lightning":
            col.enabled = False
        col = row.column()
        col.prop(obj.nvb, "randvel")
        if obj.nvb.update == "Lightning":
            col.enabled = False
        row = box.row()
        row.prop(obj.nvb, "blurlength")
        row = box.row()
        row.prop(obj.nvb, "targetsize")
        row = box.row()
        row.label(text="Tangent")
        row = box.row()
        row.prop(obj.nvb, "tangentspread", text="Spread")
        row.prop(obj.nvb, "tangentlength", text="Length")
        # detonate
        row = box.row()
        col = row.column()
        col.prop(obj.nvb, "bounce")
        if obj.nvb.update == "Lightning":
            col.enabled = False
        col = row.column()
        col.prop(obj.nvb, "bounce_co")
        if obj.nvb.update == "Lightning":
            col.enabled = False
        row = box.row()
        col = row.column()
        col.prop(obj.nvb, "loop")
        if obj.nvb.update != "Single" and \
           obj.nvb.update != "Explosion":
            col.enabled = False
        col = row.column()
        col.prop(obj.nvb, "splat")
        row = box.row()
        row.prop(obj.nvb, "affectedByWind")
        if obj.nvb.update == "Lightning":
            row.enabled = False
        row = box.row()
        row.prop(obj.nvb, "m_isTinted")

        box = layout.row().box()
        row = box.row()
        row.label(text="Texture / Chunk", icon='TEXTURE')
        row = box.row()
        row.prop(obj.nvb, "texture")
        if not utils.is_null(obj.nvb.chunkName):
            row.enabled = False
        row = box.row()
        row.prop(obj.nvb, "twosidedtex")
        if not utils.is_null(obj.nvb.chunkName):
            row.enabled = False

        box.separator()

        row = box.row()
        row.label(text="Texture Animation")
        row = box.row()
        row.label(text="Grid")
        row.prop(obj.nvb, "xgrid", text="X")
        row.prop(obj.nvb, "ygrid", text="Y")
        if not utils.is_null(obj.nvb.chunkName):
            row.enabled = False
        row = box.row()
        row.prop(obj.nvb, "fps")
        row = box.row()
        row.prop(obj.nvb, "framestart")
        row.prop(obj.nvb, "frameend")
        row = box.row()
        row.prop(obj.nvb, "m_bFrameBlending")
        row = box.row()
        row.prop(obj.nvb, "random")

        box.separator()

        row = box.row()
        row.label(text="Depth Texture")
        row = box.row()
        row.prop(obj.nvb, "depth_texture")
        row = box.row()
        row.prop(obj.nvb, "m_sDepthTextureName", text="")

        box.separator()

        row = box.row()
        row.label(text="Chunk Model")
        row = box.row()
        row.prop(obj.nvb, "chunkName", text="")

        box = layout.row().box()
        row = box.row()
        row.label(text="Advanced", icon='PREFERENCES')

        # Lightning
        parent_box = box
        box = box.row().box()
        if obj.nvb.update != "Lightning":
            box.enabled = False
        row = box.row()
        row.label(text="Lightning")
        row = box.row()
        row.prop(obj.nvb, "lightningdelay")
        row = box.row()
        row.prop(obj.nvb, "lightningradius")
        row = box.row()
        row.prop(obj.nvb, "lightningsubdiv")
        row = box.row()
        row.prop(obj.nvb, "lightningscale")
        row = box.row()
        row.prop(obj.nvb, "lightningzigzag")
        box = parent_box

        box.separator()

        # Blast props
        parent_box = box
        box = box.row().box()
        row =  box.row()
        row.label(text="Blast")
        row =  box.row()
        row.prop(obj.nvb, "blastradius")
        row =  box.row()
        row.prop(obj.nvb, "blastlength")
        box = parent_box

        box.separator()

        # p2p settings
        parent_box = box
        box = box.row().box()
        if obj.nvb.update != "Fountain" and\
           obj.nvb.update != "Single":
            box.enabled = False
        row = box.row()
        row.label(text="P2P Settings")
        row = box.row()
        row.prop(obj.nvb, "p2p")
        row = box.row()
        row.prop(obj.nvb, "p2p_type")
        if not obj.nvb.p2p:
            row.enabled = False
        if not obj.nvb.p2p:
            row.enabled = False
        row = box.row()
        row.prop(obj.nvb, "p2p_bezier2")
        if not obj.nvb.p2p or \
           obj.nvb.p2p_type == "Gravity":
            row.enabled = False
        row = box.row()
        row.prop(obj.nvb, "p2p_bezier3")
        if not obj.nvb.p2p or \
           obj.nvb.p2p_type == "Gravity":
            row.enabled = False
        row = box.row()
        row.prop(obj.nvb, "grav")
        if not obj.nvb.p2p or \
           obj.nvb.p2p_type == "Bezier":
            row.enabled = False
        row = box.row()
        row.prop(obj.nvb, "drag")
        if not obj.nvb.p2p or \
           obj.nvb.p2p_type == "Bezier":
            row.enabled = False
        box = parent_box

        box.separator()

        parent_box = box
        box = box.row().box()
        row = box.row()
        row.label(text="Control Points")
        row = box.row()
        row.prop(obj.nvb, "numcontrolpts")
        row = box.row()
        row.prop(obj.nvb, "controlptradius")
        row = box.row()
        row.prop(obj.nvb, "controlptdelay")
        row = box.row()
        row.prop(obj.nvb, "controlptsmoothing")
        box = parent_box