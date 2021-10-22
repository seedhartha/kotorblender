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
        row.prop(texture.kb, propname)
        prop_names = [o.name for o in texture.kb.modified_properties]
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
        state = getattr(texture.kb, "box_visible_" + boxname)
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
        if len(texture.kb.modified_properties):
            box = layout.row().box()
            if self.draw_box_header(texture, box, "summary", "TXI File Summary"):
                for propname in texture.kb.modified_properties:
                    self.draw_summ_prop(texture, box, propname.name)

        box = layout.row().box()
        if self.draw_box_header(texture, box, "textures", "Shader Textures"):
            box.prop(texture.kb, "envmaptexture")
            box.prop(texture.kb, "bumpmaptexture")
            box.prop(texture.kb, "bumpyshinytexture")

        box = layout.row().box()
        if self.draw_box_header(texture, box, "procedural", "Procedural Properties"):
            box.prop(texture.kb, "proceduretype")
            if texture.kb.proceduretype == "water":
                box.label(text="Water Settings")
                box.prop(texture.kb, "wateralpha")
                box.prop(texture.kb, "waterwidth")
                box.prop(texture.kb, "waterheight")
            elif texture.kb.proceduretype == "arturo":
                box.label(text="Arturo Settings")
                box.prop(texture.kb, "arturowidth")
                box.prop(texture.kb, "arturoheight")
            elif texture.kb.proceduretype == "cycle":
                box.label(text="Cycle Settings")
                box.prop(texture.kb, "defaultwidth")
                box.prop(texture.kb, "defaultheight")
                box.prop(texture.kb, "numx")
                box.prop(texture.kb, "numy")
                box.prop(texture.kb, "fps")
                box.prop(texture.kb, "filerange")
            box.separator()
            box.prop(texture.kb, "forcecyclespeed")
            box.prop(texture.kb, "anglecyclespeed")
            box.prop(texture.kb, "channelscale0")
            box.prop(texture.kb, "channelscale1")
            box.prop(texture.kb, "channelscale2")
            box.prop(texture.kb, "channelscale3")
            box.prop(texture.kb, "channeltranslate0")
            box.prop(texture.kb, "channeltranslate1")
            box.prop(texture.kb, "channeltranslate2")
            box.prop(texture.kb, "channeltranslate3")
            box.prop(texture.kb, "distort")
            box.prop(texture.kb, "distortangle")
            box.prop(texture.kb, "distortionamplitude")
            box.prop(texture.kb, "speed")

        box = layout.row().box()
        if self.draw_box_header(texture, box, "bumpmap", "Bumpmap Properties"):
            box.prop(texture.kb, "isbumpmap")
            box.prop(texture.kb, "isdiffusebumpmap")
            box.prop(texture.kb, "isspecularbumpmap")
            box.prop(texture.kb, "bumpmapscaling")
            box.prop(texture.kb, "bumpintensity")
            box.prop(texture.kb, "diffusebumpintensity")
            box.prop(texture.kb, "specularbumpintensity")
            box.prop(texture.kb, "specularcolor")

        box = layout.row().box()
        if self.draw_box_header(texture, box, "envmap", "Environment Map Properties"):
            box.prop(texture.kb, "isenvironmentmapped")
            box.prop(texture.kb, "envmapalpha")

        box = layout.row().box()
        if self.draw_box_header(texture, box, "general", "General Properties"):
            box.prop(texture.kb, "blending")
            box.prop(texture.kb, "clamp")
            box.prop(texture.kb, "downsamplemin")
            box.prop(texture.kb, "downsamplemax")
            box.prop(texture.kb, "compresstexture")
            box.prop(texture.kb, "filter")
            box.prop(texture.kb, "mipmap")
            box.prop(texture.kb, "maptexelstopixels")
            box.prop(texture.kb, "gamma")
            box.prop(texture.kb, "alphamean")
            box.prop(texture.kb, "cube")
            box.prop(texture.kb, "islightmap")
            box.prop(texture.kb, "renderbmlmtype")
            box.prop(texture.kb, "temporary")
            box.prop(texture.kb, "useglobalalpha")
            box.prop(texture.kb, "decal")

        box = layout.row().box()
        if self.draw_box_header(texture, box, "font", "Font Properties"):
            box.prop(texture.kb, "numchars")
            box.prop(texture.kb, "fontheight")
            box.prop(texture.kb, "baselineheight")
            box.prop(texture.kb, "texturewidth")
            box.prop(texture.kb, "spacingR")
            box.prop(texture.kb, "spacingB")