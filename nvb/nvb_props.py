import bpy
from mathutils import Color

from . import nvb_def, nvb_light, nvb_txi, nvb_utils


def KB_anim_root_obj_poll(self, object):
    return nvb_utils.ancestor_node(object, nvb_utils.is_root_dummy) is not None


def nvb_update_light_power(self, context):
    if context.object and context.object.type == 'LIGHT':
        nvb_light.calc_light_power(context.object)


def nvb_update_shadow_prop(self, context):
    """
    Set the lights shadow to match the Aurora shadow property
    """
    if context.object and context.object.type == 'LIGHT':
        context.object.data.use_shadow = self.shadow != 0


class FlarePropertyGroup(bpy.types.PropertyGroup):
    """
    Properties for a single flare in the flare list
    """

    texture : bpy.props.StringProperty(name = 'Texture',
                                       description = 'Texture name',
                                       default = nvb_def.null)
    size : bpy.props.FloatProperty(name = 'Size',
                                 description = 'Flare size',
                                 default = 1)
    position : bpy.props.FloatProperty(name = 'Position',
                                       description = 'Flare position',
                                       default = 1)
    colorshift : bpy.props.FloatVectorProperty( name = 'Colorshift',
                                                description = 'Colorshift',
                                                subtype = 'COLOR_GAMMA',
                                                default = (0.0, 0.0, 0.0),
                                                min = -1.0, max = 1.0,
                                                soft_min = 0.0, soft_max = 1.0)


class TexturePropertyGroup(bpy.types.PropertyGroup):
    """
    This class defines all additional properties needed by the txi file
    format. It hold the properties for image textures.
    """

    class PropListItem(bpy.types.PropertyGroup):
        name : bpy.props.StringProperty(name='Property Name')

    # Metaproperties,
    # list of properties edited, these are the ones that will be exported
    modified_properties : bpy.props.CollectionProperty(type=PropListItem)
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
        for tok in nvb_txi.tokens:
            attr_def = TexturePropertyGroup.__annotations__[tok][1]
            default_value = attr_def['default']
            if tok == 'specularcolor':
                default_value = Color(default_value)
            if getattr(self, tok) != default_value:
                self.modified_properties.add().name = tok

    # TXI props
    blending : bpy.props.EnumProperty(items=[
        ('none', '', ''),
        ('additive', 'additive', 'additive'),
        ('punchthrough', 'punchthrough', 'punchthrough'),
    ], default='none', update=prop_update)
    proceduretype : bpy.props.EnumProperty(items=[
        ('none', '', ''),
        ('dirty', 'dirty', 'dirty'),
        ('dirty2', 'dirty2', 'dirty2'),
        ('dirty3', 'dirty3', 'dirty3'),
        ('water', 'water', 'water'),
        ('life', 'life', 'life'),
        ('perlin', 'perlin', 'perlin'),
        ('arturo', 'arturo', 'arturo'),
        ('wave', 'wave', 'wave'),
        ('cycle', 'cycle', 'cycle'),
        ('random', 'random', 'random'),
        ('ringtexdistort', 'ringtexdistort', 'ringtexdistort'),
    ], default='none', update=prop_update)
    filter : bpy.props.EnumProperty(items=[
        ('none', '', ''),
        ('nearest', 'nearest', 'nearest'),
        ('linear', 'linear', 'linear'),
    ], default='none', update=prop_update)
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


def nvb_update_emitter_prop(self, context):
    obj = context.object
    if not obj:
        return
    if obj.nvb.update == 'Lightning':
        obj.nvb.birthrate = pow(2, obj.nvb.lightningsubdiv) + 1
        obj.nvb.lifeexp = 1
        obj.nvb.render_emitter = 'Linked'
    if obj.nvb.update != 'Explosion':
        obj.nvb.loop = False
    if not nvb_utils.is_null(obj.nvb.chunkName):
        obj.nvb.render_emitter = 'Normal'
        obj.nvb.blend = 'Normal'
    if obj.nvb.p2p_type == 'Bezier':
        obj.nvb.p2p_sel = 1
    elif obj.nvb.p2p_type == 'Gravity':
        obj.nvb.p2p_sel = 0


class AnimEventPropertyGroup(bpy.types.PropertyGroup):
    """Properties for a single event in the even list."""

    name : bpy.props.StringProperty(name='Name', default='unnamed',
                                    description='Name for this event',
                                    options=set())
    frame : bpy.props.IntProperty(
        name='Frame', default=1,
        description='Frame at which the event should fire',
        options=set())


class AnimPropertyGroup(bpy.types.PropertyGroup):
    """Properties for a single animation in the animation list."""

    name : bpy.props.StringProperty(name='Name',
                                    description='Name of this animation',
                                    default='unnamed', options=set())
    ttime : bpy.props.FloatProperty(
        name='Transitiontime', subtype='TIME', options=set(),
        description='Blending time between animations in seconds',
        default=0.25, min=0.0, soft_max=60.0)
    transtime : bpy.props.FloatProperty(
        name='Transitiontime', subtype='TIME', options=set(),
        description='Blending time between animations in frames',
        default=7.5, min=0.0, soft_max=60.0)
    root : bpy.props.StringProperty(name='Root', default='', options=set(),
                                    description='Entry point of the animation')
    root_obj : bpy.props.StringProperty(
        name='Root', description='Entry point of the animation',
        default='unnamed', options=set())
    mute : bpy.props.BoolProperty(name='Export', default=False, options=set(),
                                  description='Export animation to MDL')
    frameStart : bpy.props.IntProperty(name='Start', default=0, options=set(),
                                       description='Animation Start', min=0)
    frameEnd : bpy.props.IntProperty(name='End', default=0, options=set(),
                                     description='Animation End', min=0)

    eventList : bpy.props.CollectionProperty(type=AnimEventPropertyGroup)
    eventListIdx : bpy.props.IntProperty(name='Index for event List',
                                         default=0, options=set())


class ObjectPropertyGroup(bpy.types.PropertyGroup):
    """
    This class defines all additional properties needed by the mdl file
    format. It hold the properties for meshes, lights and empties.
    """

    # For all objects
    wirecolor : bpy.props.FloatVectorProperty(name = 'Wirecolor',
                                              description = 'Color of the wireframe',
                                              subtype = 'COLOR_GAMMA',
                                              default = (1.0, 1.0, 1.0),
                                              min = 0.0, max = 1.0,
                                              soft_min = 0.0, soft_max = 1.0)

    # Helper properties to store additional values. Cannot be edited.
    restrot : bpy.props.FloatVectorProperty(name='Rest Pose Rotation',
                                            size=4,
                                            default=(0.0, 0.0, 0.0, 0.0),
                                            options=set())
    restloc : bpy.props.FloatVectorProperty(name='Rest Pose Location',
                                            size=3,
                                            default=(0.0, 0.0, 0.0),
                                            options=set())
    restscl : bpy.props.FloatProperty(name='Rest Pose Scale',
                                      default=0.0,
                                      options=set())

    imporder : bpy.props.IntProperty(name = "Order of Import", default = 0)

    # For all emptys
    dummytype  : bpy.props.EnumProperty(name = 'Type',
                                        items = [(nvb_def.Dummytype.NONE,      'None',                'Simple dummy object',                                        0), \
                                                 (nvb_def.Dummytype.DWKROOT,   'DWK Rootdummy',       'All children are considered part of a door walkmesh',        1), \
                                                 (nvb_def.Dummytype.MDLROOT,   'MDL Rootdummy',       'All children are considered part of a mdl',                  2), \
                                                 (nvb_def.Dummytype.PWKROOT,   'PWK Rootdummy',       'All children are considered part of a placeable walkmesh',   3), \
                                                 (nvb_def.Dummytype.REFERENCE, 'Reference node',      'Used in spells. Points to "fx_ref" by default',              4), \
                                                 (nvb_def.Dummytype.PATCH,     'Patch node',          'Used in spells. Unknown purpose. ',                          5), \
                                                 (nvb_def.Dummytype.PATHPOINT, 'Path point',          'Used when exporting paths',                                  6)],
                                        default = nvb_def.Dummytype.NONE)
    # For MDL Rootdummy
    supermodel     : bpy.props.StringProperty(name = 'Supermodel', description = 'Name of the model to inherit animations from', default = nvb_def.null)
    classification : bpy.props.EnumProperty(name  = 'Classification',
                                            items = [ (nvb_def.Classification.UNKNOWN,   'Other',     'Unknown classification',              0), \
                                                      (nvb_def.Classification.EFFECT,    'Effect',    'Effects',                             1), \
                                                      (nvb_def.Classification.TILE,      'Tile',      'Tiles for a tileset',                 2), \
                                                      (nvb_def.Classification.CHARACTER, 'Character', 'Creatures, characters or placeables', 4), \
                                                      (nvb_def.Classification.DOOR,      'Door',      'Doors',                               8), \
                                                      (nvb_def.Classification.SABER,     'Lightsaber','Lightsaber weapon',                   16), \
                                                      (nvb_def.Classification.ITEM,      'Placeable', 'Items or placeables',                 32), \
                                                      (nvb_def.Classification.FLYER,     'Flyer',     'Non-interactive scene elements',      64) ],
                                            default = nvb_def.Classification.UNKNOWN)
    unknownC1      : bpy.props.IntProperty(name = 'Unknown', description = 'Unknown byte-2 in the classification bytes section of the model header', default = 0)
    ignorefog      : bpy.props.BoolProperty(name = 'Ignore Fog', description = 'If true, model will not be occluded by area fog in-game', default = False)
    compress_quats : bpy.props.BoolProperty(name = 'Use Compressed Quaternions', description = 'If true, model will use compressed quaternions in animations', default = False)
    headlink       : bpy.props.BoolProperty(name = 'Head Model', description = 'If true, this model is a Head', default = False)
    dummysubtype   : bpy.props.EnumProperty(name = 'Subtype',
                                            items = [('NONE', 'None',            'Simple dummy object',                     0), \
                                                     ('HAND', 'Hand',            'Hand node for spells and effects. \n (for door and placeable models)',        1), \
                                                     ('HEAD', 'Head',            'Head node for spells and effects. \n (for door and placeable models)',        2), \
                                                     ('HHIT', 'Head hit',        'Head hit node for spells and effects. \n (for door and placeable models)',    3), \
                                                     ('IMPC', 'Impact',          'Impact node for spells and effects. \n (for door and placeable models)',      4), \
                                                     ('GRND', 'Ground',          'Ground node for spells and effects. \n (for door and placeable models)',      5), \
                                                     ('USE1', 'PWK: Use 1',      '1st node for "Use" animation',            6), \
                                                     ('USE2', 'PWK: Use 2',      '2nd node for "Use" animation',            7), \
                                                     ('O101', 'DWK: Open 1 1st', 'Open 1 State, 1st node for "Use" anim',   8), \
                                                     ('O102', 'DWK: Open 1 2nd', 'Open 1 State, 2nd node for "Use" anim',   9), \
                                                     ('O201', 'DWK: Open 2 1st', 'Open 2 State, 1st node for "Use" anim',  10), \
                                                     ('O202', 'DWK: Open 2 2nd', 'Open 2 State, 2nd node for "Use" anim',  11), \
                                                     ('CL01', 'DWK: Closed 1st', 'Closed State, 1st node for "Use" anim',  12), \
                                                     ('CL02', 'DWK: Closed 2nd', 'Closed State, 2nd node for "Use" anim',  13) ],
                                            default = 'NONE')
    animscale   : bpy.props.FloatProperty(name = 'Animationscale', description = 'Animation scale for all animations', default = 1.00, min = 0.0)
    # Animation Data (for separation)
    animList : bpy.props.CollectionProperty(type=AnimPropertyGroup)
    animListIdx : bpy.props.IntProperty(name='Index for anim List',
                                        default=0, options=set())
    # For reference emptys
    refmodel     : bpy.props.StringProperty(name = 'Reference Model', description = 'Name of another mdl file', default = 'fx_ref')
    reattachable : bpy.props.BoolProperty(name = 'Reattachable', default = False)
    # Minimap generation
    minimapzoffset : bpy.props.FloatProperty(name = 'Minimap Z Offset', default = 0.00, min = 0.00)
    minimapsize    : bpy.props.IntProperty(name = 'Size', default = 512, min = 16)

    # For mesh objects
    meshtype   : bpy.props.EnumProperty(name = 'Type',
                                        items = [ (nvb_def.Meshtype.TRIMESH, 'Trimesh', 'Triangle mesh', 0), \
                                                  (nvb_def.Meshtype.DANGLYMESH, 'Danglymesh', 'Triangle mesh with dangly parts', 1), \
                                                  (nvb_def.Meshtype.SKIN, 'Skinmesh', 'Triangle mesh with weighted deformation', 2), \
                                                  (nvb_def.Meshtype.AABB, 'AABB Walkmesh', 'Axis Aligned Bounding Box Walkmesh, for collision detection', 3), \
                                                  (nvb_def.Meshtype.EMITTER, 'Emitter', 'Particle emitter', 4), \
                                                  (nvb_def.Meshtype.LIGHTSABER, 'Lightsaber', 'Saber mesh (blade plane)', 5)],
                                        default = nvb_def.Meshtype.TRIMESH)
    smoothgroup    : bpy.props.EnumProperty(name = 'Smoothgroup',
                                            items = [   ('SEPR', 'Separate', 'All faces have their own smoothgroup',   0),
                                                        ('SING', 'Single', 'All Faces belong to the same smoothgroup', 1),
                                                        ('AUTO', 'Auto',   'Generate smoothgroups either from edges marked as sharp or edge angles when no sharp edges are present',  2),
                                                        ('DRCT', 'Direct', 'Use imported and directly defined smoothgroups, select smoothgroups for geometry with unset smoothgroups by using Auto algorithm', 3)
                                                         ],
                                            default = 'AUTO')

    bitmap           : bpy.props.StringProperty(name = 'Diffuse map')
    bitmap2          : bpy.props.StringProperty(name = 'Lightmap')
    alpha            : bpy.props.FloatProperty(name = 'Alpha', default = 1.0, min = 0.0, max = 1.0)
    shadow           : bpy.props.BoolProperty(name = 'Shadow', description = 'Whether to cast shadows', default = True, update=nvb_update_shadow_prop)
    render           : bpy.props.BoolProperty(name = 'Render', description = 'Whether to render this object in the scene', default = True)
    lightmapped      : bpy.props.BoolProperty(name = 'Lightmapped', description = 'Whether this object has shading baked into a lightmap', default = False)
    beaming          : bpy.props.BoolProperty(name = 'beaming', description = 'Object casts beams (?)', default = False)
    tangentspace     : bpy.props.BoolProperty(name = 'tangentspace', description = 'Allow Normal Mapping', default = False)
    inheritcolor     : bpy.props.BoolProperty(name = 'Inheritcolor', description = 'Unused (?)', default = False)
    rotatetexture    : bpy.props.BoolProperty(name = 'Rotatetexture', description = 'Automatically rotates texture to prevent seams', default = False)
    m_bIsBackgroundGeometry : bpy.props.BoolProperty(name='Background Geometry', description="Lower detail or fewer mipmaps (?)", default=False, options=set())
    dirt_enabled     : bpy.props.BoolProperty(name="Dirt", description="Dirt enabled (KotOR 2:TSL ONLY)", default=False, options=set())
    dirt_texture     : bpy.props.IntProperty(name="Dirt Texture", description="Dirt texture, values from walkmesh materials?", default=1, options=set())
    dirt_worldspace  : bpy.props.IntProperty(name="Dirt Worldspace", description="Dirt world space, some kind of mapping?", default=1, options=set())
    hologram_donotdraw : bpy.props.BoolProperty(name="Hologram Hide", description="Prevent node from being drawn in hologram mode, useful for tongues and other internal parts (KotOR 2:TSL ONLY)", default=False, options=set())
    animateuv        : bpy.props.BoolProperty(name="Animate UVs", description="Enable UV animation for texture-only/surface animation", default=False, options=set())
    uvdirectionx     : bpy.props.FloatProperty(name="X Direction", description="UV animation vector X component", default=1.0, options=set())
    uvdirectiony     : bpy.props.FloatProperty(name="Y Direction", description="UV animation vector Y component", default=1.0, options=set())
    uvjitter         : bpy.props.FloatProperty(name="Jitter Amount", description="UV animation jitter quantity", default=0.0, options=set())
    uvjitterspeed    : bpy.props.FloatProperty(name="Jitter Speed", description="UV animation jitter speed", default=0.0, options=set())
    transparencyhint : bpy.props.IntProperty(name = 'Transparency Hint', default = 0, min = 0, max = 32)
    selfillumcolor   : bpy.props.FloatVectorProperty(name = 'Self-illum. color',
                                                     description = 'Makes the object seem to glow but does not emit light',
                                                     subtype = 'COLOR_GAMMA',
                                                     default = (0.0, 0.0, 0.0),
                                                     min = 0.0, max = 1.0,
                                                     soft_min = 0.0, soft_max = 1.0)
    diffuse          : bpy.props.FloatVectorProperty(name = 'Diffuse color',
                                                     subtype = 'COLOR_GAMMA',
                                                     default = (1.0, 1.0, 1.0),
                                                     min = 0.0, max = 1.0,
                                                     soft_min = 0.0, soft_max = 1.0)
    ambient          : bpy.props.FloatVectorProperty(name = 'Ambient color',
                                                     subtype = 'COLOR_GAMMA',
                                                     default = (1.0, 1.0, 1.0),
                                                     min = 0.0, max = 1.0,
                                                     soft_min = 0.0, soft_max = 1.0)
    lytposition      : bpy.props.FloatVectorProperty(name = 'LYT Position',
                                                     description = 'Room position in LYT file.',
                                                     subtype = 'XYZ',
                                                     default = (0.0, 0.0, 0.0))

    # For danglymeshes
    period       : bpy.props.FloatProperty(name = 'Period', default = 1.0, min = 0.0, max = 32.0)
    tightness    : bpy.props.FloatProperty(name = 'Tightness', default = 1.0, min = 0.0, max = 32.0)
    displacement : bpy.props.FloatProperty(name = 'Displacement', default = 0.5, min = 0.0, max = 32.0)
    constraints  : bpy.props.StringProperty(name = 'Danglegroup', description = 'Name of the vertex group to use for the danglymesh', default = '')

    # For skingroups
    skingroup_obj : bpy.props.StringProperty(name = 'Bone', description = 'Name of the bone to create the skingroup for', default = '')

    # For lights
    lighttype     : bpy.props.EnumProperty(name = 'Type', items=[('NONE', 'None', 'Simple light', 0), ('MAINLIGHT1', 'Mainlight 1', 'Mainlight for Tiles (Editable in toolset)', 1), ('MAINLIGHT2', 'Mainlight 2', 'Mainlight for Tiles (Editable in toolset)', 2), ('SOURCELIGHT1', 'Sourcelight 1', 'Editable in toolset', 3), ('SOURCELIGHT2', 'Sourcelight 2', 'Editable in toolset', 4)], default = 'NONE')
    ambientonly   : bpy.props.BoolProperty(name = 'Ambient Only', default = False)
    lightpriority : bpy.props.IntProperty(name = 'Lightpriority', default = 3, min = 1, max = 5)
    fadinglight   : bpy.props.BoolProperty(name = 'Fading light', default = False)
    isdynamic     : bpy.props.IntProperty(name = 'Dynamic Type', description="0 - ???\n1 - Light affects area geometry AND dynamic objects\n2 - Light affects ONLY dynamic objects", default = 0, min = 0, max = 2)
    affectdynamic : bpy.props.BoolProperty(name = 'Affect Dynamic', description = 'Affect dynamic objects', default = False)
    negativelight : bpy.props.BoolProperty(name = 'Negative Light', default = False)
    lensflares    : bpy.props.BoolProperty(name = 'Lensflares', default = False)
    flareradius   : bpy.props.FloatProperty(name = 'Flare Radius', default = 0.0, min = 0.0, max = 100.0)
    flareList     : bpy.props.CollectionProperty(type = FlarePropertyGroup)
    flareListIdx  : bpy.props.IntProperty(name = "Index for flare list", default = 0)

    # Point lights in Eevee do not have equivalent for Aurora light multiplier and radius
    radius : bpy.props.FloatProperty(name = 'Radius', default = 0.0, min = 0.0, max = 10000.0, update = nvb_update_light_power)
    multiplier : bpy.props.FloatProperty(name = 'Multiplier', default = 1.0, min = 0.0, max = 10.0, update = nvb_update_light_power)

    rawascii : bpy.props.StringProperty(name = 'Text node', description = 'Name of the raw text node', default = '')

    # For emitters

    # update rules:
    # if update == lightning, birthrate = 2^subdiv + 1, render = lightning, lifeExp = 1
    # if chunk text != '' and text != 'null'/NULL, render = Normal, blend = Normal
    # if p2p_type, set p2p_sel

    # Controllers, in numeric order, these should ALL be animatable
    alphaend : bpy.props.FloatProperty(name="Alpha end", description="Alpha end", default=1.0, min=0.0, max=1.0)
    alphastart : bpy.props.FloatProperty(name="Alpha start", description="Alpha start", default=1.0, min=0.0, max=1.0)
    birthrate : bpy.props.IntProperty(name="Birthrate", description="Birthrate", default=10, min=0)
    bounce_co : bpy.props.FloatProperty(name="Coefficient", description="Bounce coefficient", default=0.0, min=0.0)
    combinetime : bpy.props.FloatProperty(name="Combinetime", description="Combinetime", default=0.0)
    drag : bpy.props.FloatProperty(name="Drag", description="Drag (m/s²)", default=0.0, unit='ACCELERATION')
    fps : bpy.props.IntProperty(name="Frames/s", description="Frames per second", default=24, min=0)
    frameend : bpy.props.IntProperty(name="End Frame", description="Frame End", default=0)
    framestart : bpy.props.IntProperty(name="Start Frame", description="Frame Start", default=0)
    grav : bpy.props.FloatProperty(name="Gravity", description="Gravity (m/s²)", default=0.0, min=0.0, unit='ACCELERATION')
    lifeexp : bpy.props.FloatProperty(name="Lifetime", description="Life Expectancy", default=1.0, min=-1.0)
    mass : bpy.props.FloatProperty(name="Mass", description="Mass", default=1.0, min=0.0)
    p2p_bezier2 : bpy.props.FloatProperty(name="Bezier 2", description="???", default=0.0)
    p2p_bezier3 : bpy.props.FloatProperty(name="Bezier 3", description="???", default=0.0)
    particlerot : bpy.props.FloatProperty(name="Rotation", description="Particle Rotation (degrees)", default=0.0, min=-360.0, max=360.0)
    randvel :  bpy.props.FloatProperty(name="Random Velocity", description="Random Velocity", default=0.0)
    sizestart : bpy.props.FloatProperty(name="Size start", description="x size start", default=1.0, min=0.0)
    sizeend : bpy.props.FloatProperty(name="Size end", description="x size end", default=1.0, min=0.0)
    sizestart_y : bpy.props.FloatProperty(name="Sizestart_y", description="y size start", default=0.0, min=0.0)
    sizeend_y : bpy.props.FloatProperty(name="Sizeend_y", description="y size end", default=0.0, min=0.0)
    spread : bpy.props.FloatProperty(name="Spread", description="Spread", default=0.0, min=0.0)
    threshold : bpy.props.FloatProperty(name="Threshold", description="Threshold", default=0.0)
    velocity :  bpy.props.FloatProperty(name="Velocity", description="Particle Velocity", default=0.0)
    xsize : bpy.props.IntProperty(name="Size X", description="Size X", default=0)
    ysize : bpy.props.IntProperty(name="Size Y", description="Size Y", default=0)
    blurlength : bpy.props.FloatProperty(name="Blur Length", description="Blur Length", default=10.0)
    # Lighting props
    lightningdelay  : bpy.props.FloatProperty(name="Delay", description="Lightning Delay (seconds)", default=0.0, min=0.0, max=1000.0)
    lightningradius : bpy.props.FloatProperty(name="Radius", description="Lightning Radius (meters)", default=0.0, min=0.0, max=1000.0)
    lightningsubdiv : bpy.props.IntProperty(name="Subdivisions", description="Lightning Subdivisions", default=0, min=0, max=12, update=nvb_update_emitter_prop)
    lightningscale  : bpy.props.FloatProperty(name="Scale", description="Lightning Scale", default=1.0, min=0.0, max=1.0)
    lightningzigzag : bpy.props.IntProperty(name="ZigZag", description="Lightning Zig-Zag", default=0, min=0, max=30)
    alphamid : bpy.props.FloatProperty(name="Alpha mid", description="Alpha mid", default=1.0, min=-1.0, max=1.0)
    percentstart : bpy.props.FloatProperty(name="Percent start", description="Percent start", default = 1.0, min=0.0, max=1.0)
    percentmid : bpy.props.FloatProperty(name="Percent mid", description="Percent mid", default=1.0, min=0.0, max=1.0)
    percentend : bpy.props.FloatProperty(name="Percent end", description="Percent end", default=1.0, min=0.0, max=1.0)
    sizemid : bpy.props.FloatProperty(name='sizeMid', description = 'x size mid', default=1.0, min=0.0)
    sizemid_y : bpy.props.FloatProperty(name='sizeMid_y', description = 'y size mid', default=0.0, min=0.0)
    m_frandombirthrate : bpy.props.IntProperty(name = 'Random Birthrate', description = 'Random Birthrate', default=10, min=0)
    targetsize : bpy.props.IntProperty(name="Target Size", description="Target Size", default=1, min=0)
    numcontrolpts : bpy.props.IntProperty(name="# of Control Points", description="Number of Control Points", default=0, min=0)
    controlptradius : bpy.props.FloatProperty(name="Control Point Radius", description="Control Point Radius", default=0.0, min=0.0)
    controlptdelay : bpy.props.IntProperty(name="Control Point Delay", description="Control Point Delay", default=0, min=0)
    tangentspread : bpy.props.IntProperty(name="Tangent Spread", description="Tangent Spread (degrees)", default=0, min=0)
    tangentlength : bpy.props.FloatProperty(name="Tangent Length", description="Tangent Length", default=0.0, min=0.0)
    colormid : bpy.props.FloatVectorProperty(name = 'Color mid',
                                             description = 'Color mid',
                                             subtype = 'COLOR_GAMMA',
                                             default = (1.0, 1.0, 1.0),
                                             min=0.0, max=1.0,
                                             soft_min=0.0, soft_max=1.0)
    colorend : bpy.props.FloatVectorProperty(name = 'Color end',
                                             description = 'Color end',
                                             subtype = 'COLOR_GAMMA',
                                             default = (1.0, 1.0, 1.0),
                                             min=0.0, max=1.0,
                                             soft_min=0.0, soft_max=1.0)
    colorstart : bpy.props.FloatVectorProperty(name = 'Color start',
                                               description = 'Color start',
                                               subtype = 'COLOR_GAMMA',
                                               default = (1.0, 1.0, 1.0),
                                               min = 0.0, max = 1.0,
                                               soft_min = 0.0, soft_max = 1.0)

    # Emitter sub-header properties
    deadspace : bpy.props.FloatProperty(name="Dead space", description="Dead space", default = 0.0, min = 0.0, options=set())
    blastradius : bpy.props.FloatProperty(name="Radius", description="Blast Radius (meters)", default = 0.0, min = 0.0, unit='LENGTH', options=set())
    blastlength : bpy.props.FloatProperty(name="Length", description="Blast Length (seconds)", default = 0.0, min = 0.0, unit='TIME', options=set())
    numBranches : bpy.props.IntProperty(name="# of Branches", description="Number of Branches", default=0, options=set())
    controlptsmoothing : bpy.props.IntProperty(name="Control Point Smoothing", description="Control Point Smoothing", default=0, options=set())
    xgrid : bpy.props.IntProperty(name="X Grid", description="X Grid", default=0, options=set())
    ygrid : bpy.props.IntProperty(name="Y Grid", description="Y Grid", default=0, options=set())
    spawntype : bpy.props.EnumProperty(
        name="Spawn", description="Spawn type",
        items = [('NONE', "", "", 0),
                 ('Normal', "Normal", "Normal", 1),
                 ('Trail', "Trail", "Trail", 2)],
        default='NONE', options=set())
    update : bpy.props.EnumProperty(
        name ="Update", description="Update type",
        items = [('NONE', "", "", 0),
                 ('Fountain', "Fountain", "Fountain", 1),
                 ('Single', "Single", "Single", 2),
                 ('Explosion', "Explosion", "Explosion", 3),
                 ('Lightning', "Lightning", "Lightning", 4)],
        default='NONE', options=set(), update=nvb_update_emitter_prop)
    render_emitter : bpy.props.EnumProperty(
        name="Render", description="Render type",
        items = [('NONE', "", "", 0),
                 ('Normal', "Normal", "Normal", 1),
                 ('Linked', "Linked", "Linked", 2),
                 ('Billboard_to_Local_Z', "Billboard to local Z", "Billboard to local Z", 3),
                 ('Billboard_to_World_Z', "Billboard to world Z", "Billboard to world Z", 4),
                 ('Aligned_to_World_Z', "Aligned to world Z", "Aligned  to world Z", 5),
                 ('Aligned_to_Particle_Dir', "Aligned to particle dir.", "Aligned to particle direction", 6),
                 ('Motion_Blur', "Motion Blur", "Motion Blur", 7)],
        default='NONE', options=set())
    blend : bpy.props.EnumProperty(
        name ="Blend", description="Blending Mode",
        items = [('NONE', "", "", 0),
                 ('Normal', "Normal", "Normal", 1),
                 ('Punch-Through', "Punch-Through", "Punch-Through", 2),
                 ('Lighten', "Lighten", "Lighten", 3)],
        default='NONE', options=set())
    texture : bpy.props.StringProperty(name="Texture", description="Texture", maxlen=32, options=set())
    chunkName : bpy.props.StringProperty(name="Chunk Name", description="Chunk Name", maxlen=16, default='', options=set(), update=nvb_update_emitter_prop)
    twosidedtex : bpy.props.BoolProperty(name="Two-Sided Texture", description="Textures visible from front and back", default=False, options=set())
    loop : bpy.props.BoolProperty(name="Loop", description="Loop", default = False, options=set())
    renderorder : bpy.props.IntProperty(name="Render order", description="Render Order", default = 0, min = 0, options=set())
    m_bFrameBlending : bpy.props.BoolProperty(name="Frame Blending", default=False, options=set())
    m_sDepthTextureName : bpy.props.StringProperty(name="Depth Texture Name", description="Depth Texture Name", default=nvb_def.null, maxlen=32, options=set())

    # Emitter flags
    p2p         : bpy.props.BoolProperty(name="p2p", description="Use Point to Point settings", default = False, options=set())
    p2p_sel     : bpy.props.BoolProperty(name="p2p_sel", description="???", default = False, options=set())
    p2p_type    : bpy.props.EnumProperty(
        name="Type", description="???",
        items = [('NONE', "", "", 0),
                 ('Bezier', "Bezier", "Bezier", 1),
                 ('Gravity', "Gravity", "Gravity", 2)],
        default='NONE', options=set(), update=nvb_update_emitter_prop)
    affectedByWind : bpy.props.BoolProperty(name="Affected By Wind", description="Particles are affected by area wind", default = False, options=set())
    m_isTinted : bpy.props.BoolProperty(name="Tinted", description="Tint texture with start, mid, and end color", default = False, options=set())
    bounce : bpy.props.BoolProperty(name="Bounce", description="Bounce On/Off", default = False, options=set())
    random : bpy.props.BoolProperty(name="Random", description="Random", default = False, options=set())
    inherit : bpy.props.BoolProperty(name="Inherit", description="Inherit", default = False, options=set())
    inheritvel : bpy.props.BoolProperty(name="Velocity", description="Inherit Velocity", default = False, options=set())
    inherit_local : bpy.props.BoolProperty(name="Local", description="???", default = False, options=set())
    splat : bpy.props.BoolProperty(name="Splat", description="Splat", default = False, options=set())
    inherit_part : bpy.props.BoolProperty(name="Part", description="???", default = False, options=set())
    depth_texture : bpy.props.BoolProperty(name="Use Depth Texture", description="Use Depth Texture", default = False, options=set())

    # Path points

    class PathConnection(bpy.types.PropertyGroup):
        point : bpy.props.StringProperty(name='Point')

    path_connections : bpy.props.CollectionProperty(type=PathConnection)
    active_path_connection : bpy.props.IntProperty()
