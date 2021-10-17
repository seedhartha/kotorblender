import bpy
from mathutils import Color

from .. import kb_txi

from .listitem import ListItemPropertyGroup


class TexturePropertyGroup(bpy.types.PropertyGroup):
    """
    This class defines all additional properties needed by the txi file
    format. It hold the properties for image textures.
    """

    # Metaproperties,
    # list of properties edited, these are the ones that will be exported
    modified_properties : bpy.props.CollectionProperty(type=ListItemPropertyGroup)
    # visible UI boxes
    box_visible_summary    : bpy.props.BoolProperty(default=True)
    box_visible_textures   : bpy.props.BoolProperty(default=True)
    box_visible_bumpmap    : bpy.props.BoolProperty(default=False)
    box_visible_envmap     : bpy.props.BoolProperty(default=False)
    box_visible_procedural : bpy.props.BoolProperty(default=False)
    box_visible_general    : bpy.props.BoolProperty(default=False)
    box_visible_font       : bpy.props.BoolProperty(default=False)

    def prop_update(self, context):
        """
        Update list of modified TXI properties
        by testing against default values
        """
        self.modified_properties.clear()
        for tok in kb_txi.tokens:
            attr_def = TexturePropertyGroup.__annotations__[tok][1]
            default_value = attr_def["default"]
            if tok == "specularcolor":
                default_value = Color(default_value)
            if getattr(self, tok) != default_value:
                self.modified_properties.add().name = tok

    # TXI props
    blending : bpy.props.EnumProperty(items=[
        ("none", "", ""),
        ("additive", "additive", "additive"),
        ("punchthrough", "punchthrough", "punchthrough"),
    ], default="none", update=prop_update)
    proceduretype : bpy.props.EnumProperty(items=[
        ("none", "", ""),
        ("dirty", "dirty", "dirty"),
        ("dirty2", "dirty2", "dirty2"),
        ("dirty3", "dirty3", "dirty3"),
        ("water", "water", "water"),
        ("life", "life", "life"),
        ("perlin", "perlin", "perlin"),
        ("arturo", "arturo", "arturo"),
        ("wave", "wave", "wave"),
        ("cycle", "cycle", "cycle"),
        ("random", "random", "random"),
        ("ringtexdistort", "ringtexdistort", "ringtexdistort"),
    ], default="none", update=prop_update)
    filter : bpy.props.EnumProperty(items=[
        ("none", "", ""),
        ("nearest", "nearest", "nearest"),
        ("linear", "linear", "linear"),
    ], default="none", update=prop_update)
    filerange : bpy.props.IntProperty(default=0, update=prop_update)
    defaultwidth : bpy.props.IntProperty(default=0, update=prop_update)
    defaultheight : bpy.props.IntProperty(default=0, update=prop_update)
    downsamplemax : bpy.props.IntProperty(default=15, update=prop_update)
    downsamplemin : bpy.props.IntProperty(default=0, update=prop_update)
    mipmap : bpy.props.BoolProperty(default=True, update=prop_update)
    maptexelstopixels : bpy.props.BoolProperty(default=False, update=prop_update)
    gamma : bpy.props.FloatProperty(default=1.0, update=prop_update)
    isbumpmap : bpy.props.BoolProperty(default=False, update=prop_update)
    clamp : bpy.props.IntProperty(default=1, update=prop_update)
    alphamean : bpy.props.FloatProperty(default=0.0, update=prop_update)
    isdiffusebumpmap : bpy.props.BoolProperty(default=False, update=prop_update)
    isspecularbumpmap : bpy.props.BoolProperty(default=False, update=prop_update)
    bumpmapscaling : bpy.props.FloatProperty(default=0.0, update=prop_update)
    specularcolor : bpy.props.FloatVectorProperty(default=(1.0, 1.0, 1.0), subtype='COLOR', min=0.0, max=1.0, update=prop_update)
    islightmap : bpy.props.BoolProperty(default=False, update=prop_update) # found
    compresstexture : bpy.props.BoolProperty(default=False, update=prop_update) # found
    numx : bpy.props.IntProperty(default=1, update=prop_update)
    numy : bpy.props.IntProperty(default=1, update=prop_update)
    cube : bpy.props.BoolProperty(default=False, update=prop_update)
    bumpintensity : bpy.props.FloatProperty(default=0.0, update=prop_update)
    temporary : bpy.props.BoolProperty(default=False, update=prop_update)
    useglobalalpha : bpy.props.BoolProperty(default=False, update=prop_update)
    isenvironmentmapped : bpy.props.BoolProperty(default=False, update=prop_update)
    envmapalpha : bpy.props.FloatProperty(default=0.0, update=prop_update)
    diffusebumpintensity : bpy.props.FloatProperty(default=0.0, update=prop_update)
    specularbumpintensity : bpy.props.FloatProperty(default=0.0, update=prop_update)
    bumpmaptexture : bpy.props.StringProperty(default="", update=prop_update)
    bumpyshinytexture : bpy.props.StringProperty(default="", update=prop_update)
    envmaptexture : bpy.props.StringProperty(default="", update=prop_update)
    decal : bpy.props.BoolProperty(default=False, update=prop_update)
    renderbmlmtype : bpy.props.BoolProperty(default=False, update=prop_update)
    wateralpha : bpy.props.FloatProperty(default=0.0, update=prop_update)
    arturowidth : bpy.props.IntProperty(default=15, update=prop_update)
    arturoheight : bpy.props.IntProperty(default=15, update=prop_update)
    forcecyclespeed : bpy.props.FloatProperty(default=0.0, update=prop_update)
    anglecyclespeed : bpy.props.FloatProperty(default=0.0, update=prop_update)
    waterwidth : bpy.props.IntProperty(default=0, update=prop_update)
    waterheight : bpy.props.IntProperty(default=0, update=prop_update)
    channelscale : bpy.props.IntProperty(default=4, update=prop_update)
    channeltranslate : bpy.props.IntProperty(default=4, update=prop_update)
    distort : bpy.props.BoolProperty(default=False, update=prop_update)
    distortangle : bpy.props.BoolProperty(default=False, update=prop_update)
    distortionamplitude : bpy.props.FloatProperty(default=0.0, update=prop_update)
    speed : bpy.props.FloatProperty(default=1.0, update=prop_update)
    fps : bpy.props.FloatProperty(default=1.0, update=prop_update)
    channelscale0 : bpy.props.FloatProperty(default=0.0, update=prop_update)
    channelscale1 : bpy.props.FloatProperty(default=0.0, update=prop_update)
    channelscale2 : bpy.props.FloatProperty(default=0.0, update=prop_update)
    channelscale3 : bpy.props.FloatProperty(default=0.0, update=prop_update)
    channeltranslate0 : bpy.props.FloatProperty(default=0.0, update=prop_update)
    channeltranslate1 : bpy.props.FloatProperty(default=0.0, update=prop_update)
    channeltranslate2 : bpy.props.FloatProperty(default=0.0, update=prop_update)
    channeltranslate3 : bpy.props.FloatProperty(default=0.0, update=prop_update)

    numchars : bpy.props.BoolProperty(default=False, update=prop_update)
    fontheight : bpy.props.FloatProperty(default=0.0, update=prop_update)
    baselineheight : bpy.props.FloatProperty(default=0.0, update=prop_update)
    texturewidth : bpy.props.FloatProperty(default=0.0, update=prop_update)
    spacingR : bpy.props.FloatProperty(default=0.0, update=prop_update)
    spacingB : bpy.props.FloatProperty(default=0.0, update=prop_update)
    upperleftcoords : bpy.props.StringProperty(default="", update=prop_update)
    lowerrightcoords : bpy.props.StringProperty(default="", update=prop_update)