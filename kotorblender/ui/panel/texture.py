import bpy


class KB_PT_texture(bpy.types.Panel):
    """Texture properties panel, mostly for managing TXI files"""
    bl_label = "Odyssey Texture Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "texture"

    @classmethod
    def poll(cls, context):
        try:
            # yes for image textures
            return context.texture.image
        except:
            return False

    def draw_summ_prop(self, texture, layout, propname):
        """UI Summary prop entries which include default-reset control"""
        row = layout.row(align=True)
        row.prop(texture.nvb, propname)
        prop_names = [o.name for o in texture.nvb.modified_properties]
        if propname in prop_names:
            row.label(icon='FILE_TICK')
            op = row.operator("kb.texture_info_ops", text="", icon='X', emboss=False)
            op.action = "RESET"
            op.propname = propname
        else:
            row.label(icon='RADIOBUT_OFF')

    def draw_box_header(self, texture, layout, boxname, text):
        """UI Title and visibility toggle for texture property sub-groups"""
        row = layout.row()
        row.alignment = 'LEFT'
        state = getattr(texture.nvb, "box_visible_" + boxname)
        if not state:
            row.operator("kb.texture_info_box_ops", text=text, icon='TRIA_RIGHT', emboss=False).boxname = boxname
            return False
        else:
            row.operator("kb.texture_info_box_ops", text=text, icon='TRIA_DOWN', emboss=False).boxname = boxname
            return True

    def draw(self, context):
        layout = self.layout
        texture = context.texture

        # TXI file operations
        row = layout.row(align=True)
        row.operator("kb.texture_info_io", text=" Import", icon='IMPORT').action = "LOAD"
        row.operator("kb.texture_info_io", text=" Export", icon='EXPORT').action = "SAVE"

        # Texture type
        if len(texture.nvb.modified_properties):
            box = layout.row().box()
            if self.draw_box_header(texture, box, "summary", "TXI File Summary"):
                for propname in texture.nvb.modified_properties:
                    self.draw_summ_prop(texture, box, propname.name)

        box = layout.row().box()
        if self.draw_box_header(texture, box, "textures", "Shader Textures"):
            box.prop(texture.nvb, "envmaptexture")
            box.prop(texture.nvb, "bumpmaptexture")
            box.prop(texture.nvb, "bumpyshinytexture")

        box = layout.row().box()
        if self.draw_box_header(texture, box, "procedural", "Procedural Properties"):
            box.prop(texture.nvb, "proceduretype")
            if texture.nvb.proceduretype == "water":
                box.label(text="Water Settings")
                box.prop(texture.nvb, "wateralpha")
                box.prop(texture.nvb, "waterwidth")
                box.prop(texture.nvb, "waterheight")
            elif texture.nvb.proceduretype == "arturo":
                box.label(text="Arturo Settings")
                box.prop(texture.nvb, "arturowidth")
                box.prop(texture.nvb, "arturoheight")
            elif texture.nvb.proceduretype == "cycle":
                box.label(text="Cycle Settings")
                box.prop(texture.nvb, "defaultwidth")
                box.prop(texture.nvb, "defaultheight")
                box.prop(texture.nvb, "numx")
                box.prop(texture.nvb, "numy")
                box.prop(texture.nvb, "fps")
                box.prop(texture.nvb, "filerange")
            box.separator()
            box.prop(texture.nvb, "forcecyclespeed")
            box.prop(texture.nvb, "anglecyclespeed")
            box.prop(texture.nvb, "channelscale0")
            box.prop(texture.nvb, "channelscale1")
            box.prop(texture.nvb, "channelscale2")
            box.prop(texture.nvb, "channelscale3")
            box.prop(texture.nvb, "channeltranslate0")
            box.prop(texture.nvb, "channeltranslate1")
            box.prop(texture.nvb, "channeltranslate2")
            box.prop(texture.nvb, "channeltranslate3")
            box.prop(texture.nvb, "distort")
            box.prop(texture.nvb, "distortangle")
            box.prop(texture.nvb, "distortionamplitude")
            box.prop(texture.nvb, "speed")

        box = layout.row().box()
        if self.draw_box_header(texture, box, "bumpmap", "Bumpmap Properties"):
            box.prop(texture.nvb, "isbumpmap")
            box.prop(texture.nvb, "isdiffusebumpmap")
            box.prop(texture.nvb, "isspecularbumpmap")
            box.prop(texture.nvb, "bumpmapscaling")
            box.prop(texture.nvb, "bumpintensity")
            box.prop(texture.nvb, "diffusebumpintensity")
            box.prop(texture.nvb, "specularbumpintensity")
            box.prop(texture.nvb, "specularcolor")

        box = layout.row().box()
        if self.draw_box_header(texture, box, "envmap", "Environment Map Properties"):
            box.prop(texture.nvb, "isenvironmentmapped")
            box.prop(texture.nvb, "envmapalpha")

        box = layout.row().box()
        if self.draw_box_header(texture, box, "general", "General Properties"):
            box.prop(texture.nvb, "blending")
            box.prop(texture.nvb, "clamp")
            box.prop(texture.nvb, "downsamplemin")
            box.prop(texture.nvb, "downsamplemax")
            box.prop(texture.nvb, "compresstexture")
            box.prop(texture.nvb, "filter")
            box.prop(texture.nvb, "mipmap")
            box.prop(texture.nvb, "maptexelstopixels")
            box.prop(texture.nvb, "gamma")
            box.prop(texture.nvb, "alphamean")
            box.prop(texture.nvb, "cube")
            box.prop(texture.nvb, "islightmap")
            box.prop(texture.nvb, "renderbmlmtype")
            box.prop(texture.nvb, "temporary")
            box.prop(texture.nvb, "useglobalalpha")
            box.prop(texture.nvb, "decal")

        box = layout.row().box()
        if self.draw_box_header(texture, box, "font", "Font Properties"):
            box.prop(texture.nvb, "numchars")
            box.prop(texture.nvb, "fontheight")
            box.prop(texture.nvb, "baselineheight")
            box.prop(texture.nvb, "texturewidth")
            box.prop(texture.nvb, "spacingR")
            box.prop(texture.nvb, "spacingB")