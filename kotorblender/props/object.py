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

from ..scene import light

from .. import defines, utils

from .anim import AnimPropertyGroup
from .flare import FlarePropertyGroup
from .pathconnection import PathConnectionPropertyGroup


def update_light_power(self, context):
    if context.object and context.object.type == 'LIGHT':
        light.calc_light_power(context.object)


def update_shadow_prop(self, context):
    """
    Set the lights shadow to match the Aurora shadow property
    """
    if context.object and context.object.type == 'LIGHT':
        context.object.data.use_shadow = self.shadow != 0


def update_emitter_prop(self, context):
    obj = context.object
    if not obj:
        return
    if obj.kb.update == "Lightning":
        obj.kb.birthrate = pow(2, obj.kb.lightningsubdiv) + 1
        obj.kb.lifeexp = 1
        obj.kb.render_emitter = "Linked"
    if obj.kb.update != "Explosion":
        obj.kb.loop = False
    if not utils.is_null(obj.kb.chunk_name):
        obj.kb.render_emitter = "Normal"
        obj.kb.blend = "Normal"
    if obj.kb.p2p_type == "Bezier":
        obj.kb.p2p_sel = 1
    elif obj.kb.p2p_type == "Gravity":
        obj.kb.p2p_sel = 0


class ObjectPropertyGroup(bpy.types.PropertyGroup):
    """
    This class defines all additional properties needed by the mdl file
    format. It hold the properties for meshes, lights and empties.
    """

    # For all objects
    node_number: bpy.props.IntProperty(name="Node Number", description="Node number must be equal to this nodes number in supermodel", default=0, min=0, max=1000)
    export_order: bpy.props.IntProperty(name="Export Order", description="Export order relative to parent", default=0, min=0, max=1000)

    # For all emptys
    dummytype: bpy.props.EnumProperty(name="Type",
                                      items=[(defines.Dummytype.NONE,      "None",                "Simple dummy object",                                        0),
                                             (defines.Dummytype.DWKROOT,   "DWK Rootdummy",       "All children are considered part of a door walkmesh",        1),
                                             (defines.Dummytype.MDLROOT,   "MDL Rootdummy",       "All children are considered part of a mdl",                  2),
                                             (defines.Dummytype.PWKROOT,   "PWK Rootdummy",       "All children are considered part of a placeable walkmesh",   3),
                                             (defines.Dummytype.REFERENCE, "Reference node",      "Used in spells. Points to 'fx_ref' by default",              4),
                                             (defines.Dummytype.PATHPOINT, "Path point",          "Used when exporting paths",                                  6),
                                             (defines.Dummytype.PTHROOT,   "PTH Rootdummy",       "All children are considered path points",                    7)],
                                      default=defines.Dummytype.NONE)
    # For MDL Rootdummy
    supermodel: bpy.props.StringProperty(name="Supermodel", description="Name of the model to inherit animations from", default=defines.NULL)
    classification: bpy.props.EnumProperty(name="Classification",
                                           items=[(defines.Classification.UNKNOWN,   "Other",     "Unknown classification",              0),
                                                  (defines.Classification.EFFECT,    "Effect",    "Effects",                             1),
                                                  (defines.Classification.TILE,      "Tile",      "Tiles for a tileset",                 2),
                                                  (defines.Classification.CHARACTER, "Character", "Creatures, characters or placeables", 4),
                                                  (defines.Classification.DOOR,      "Door",      "Doors",                               8),
                                                  (defines.Classification.SABER,     "Lightsaber", "Lightsaber weapon",                   16),
                                                  (defines.Classification.ITEM,      "Placeable", "Items or placeables",                 32),
                                                  (defines.Classification.FLYER,     "Flyer",     "Non-interactive scene elements",      64)],
                                           default=defines.Classification.UNKNOWN)
    subclassification: bpy.props.IntProperty(name="Unknown", description="Unknown byte-2 in the classification bytes section of the model header", default=0)
    ignorefog: bpy.props.BoolProperty(name="Ignore Fog", description="If true, model will not be occluded by area fog in-game", default=False)
    dummysubtype: bpy.props.EnumProperty(name="Subtype",
                                         items=[("NONE", "None", "Simple dummy object", 0),
                                                ("USE1", "Use 1", "1st node for 'Use' animation", 1),
                                                ("USE2", "Use 2", "2nd node for 'Use' animation", 2)],
                                         default="NONE")
    animroot: bpy.props.StringProperty(name="Animation Root", description="Root node to apply animations from", default=defines.NULL)
    animscale: bpy.props.FloatProperty(name="Animation Scale", description="Animation scale for all animations", default=1.00, min=0.0)
    # Animation Data (for separation)
    anim_list: bpy.props.CollectionProperty(type=AnimPropertyGroup)
    anim_list_idx: bpy.props.IntProperty(name="Index for anim List",
                                         default=0, options=set())
    # For reference emptys
    refmodel: bpy.props.StringProperty(name="Reference Model", description="Name of another mdl file", default="fx_ref")
    reattachable: bpy.props.BoolProperty(name="Reattachable", default=False)

    # For mesh objects
    meshtype: bpy.props.EnumProperty(name="Type",
                                     items=[(defines.Meshtype.TRIMESH, "Trimesh", "Triangle mesh", 0),
                                            (defines.Meshtype.DANGLYMESH, "Danglymesh", "Triangle mesh with dangly parts", 1),
                                            (defines.Meshtype.SKIN, "Skinmesh", "Triangle mesh with weighted deformation", 2),
                                            (defines.Meshtype.AABB, "AABB Walkmesh", "Axis Aligned Bounding Box Walkmesh, for collision detection", 3),
                                            (defines.Meshtype.EMITTER, "Emitter", "Particle emitter", 4),
                                            (defines.Meshtype.LIGHTSABER, "Lightsaber", "Saber mesh (blade plane)", 5)],
                                     default=defines.Meshtype.TRIMESH)

    bitmap: bpy.props.StringProperty(name="Diffuse map")
    bitmap2: bpy.props.StringProperty(name="Lightmap")
    alpha: bpy.props.FloatProperty(name="Alpha", default=1.0, min=0.0, max=1.0)
    shadow: bpy.props.BoolProperty(name="Shadow", description="Whether to cast shadows", default=True, update=update_shadow_prop)
    render: bpy.props.BoolProperty(name="Render", description="Whether to render this object in the scene", default=True)
    lightmapped: bpy.props.BoolProperty(name="Lightmapped", description="Whether this object has shading baked into a lightmap", default=False)
    beaming: bpy.props.BoolProperty(name="beaming", description="Object casts beams (?)", default=False)
    tangentspace: bpy.props.BoolProperty(name="tangentspace", description="Allow Normal Mapping", default=False)
    inheritcolor: bpy.props.BoolProperty(name="Inheritcolor", description="Unused (?)", default=False)
    rotatetexture: bpy.props.BoolProperty(name="Rotatetexture", description="Automatically rotates texture to prevent seams", default=False)
    background_geometry: bpy.props.BoolProperty(name="Background Geometry", description="Lower detail or fewer mipmaps (?)", default=False, options=set())
    dirt_enabled: bpy.props.BoolProperty(name="Dirt", description="Dirt enabled (KotOR 2:TSL ONLY)", default=False, options=set())
    dirt_texture: bpy.props.IntProperty(name="Dirt Texture", description="Dirt texture, values from walkmesh materials?", default=1, options=set())
    dirt_worldspace: bpy.props.IntProperty(name="Dirt Worldspace", description="Dirt world space, some kind of mapping?", default=1, options=set())
    hologram_donotdraw: bpy.props.BoolProperty(name="Hologram Hide", description="Prevent node from being drawn in hologram mode, useful for tongues and other internal parts (KotOR 2:TSL ONLY)", default=False, options=set())
    animateuv: bpy.props.BoolProperty(name="Animate UVs", description="Enable UV animation for texture-only/surface animation", default=False, options=set())
    uvdirectionx: bpy.props.FloatProperty(name="X Direction", description="UV animation vector X component", default=1.0, options=set())
    uvdirectiony: bpy.props.FloatProperty(name="Y Direction", description="UV animation vector Y component", default=1.0, options=set())
    uvjitter: bpy.props.FloatProperty(name="Jitter Amount", description="UV animation jitter quantity", default=0.0, options=set())
    uvjitterspeed: bpy.props.FloatProperty(name="Jitter Speed", description="UV animation jitter speed", default=0.0, options=set())
    transparencyhint: bpy.props.IntProperty(name="Transparency Hint", default=0, min=0, max=32)
    selfillumcolor: bpy.props.FloatVectorProperty(name="Self-illum. color",
                                                  description="Makes the object seem to glow but does not emit light",
                                                  subtype='COLOR_GAMMA',
                                                  default=(0.0, 0.0, 0.0),
                                                  min=0.0, max=1.0,
                                                  soft_min=0.0, soft_max=1.0)
    diffuse: bpy.props.FloatVectorProperty(name="Diffuse color",
                                           subtype='COLOR_GAMMA',
                                           default=(1.0, 1.0, 1.0),
                                           min=0.0, max=1.0,
                                           soft_min=0.0, soft_max=1.0)
    ambient: bpy.props.FloatVectorProperty(name="Ambient color",
                                           subtype='COLOR_GAMMA',
                                           default=(1.0, 1.0, 1.0),
                                           min=0.0, max=1.0,
                                           soft_min=0.0, soft_max=1.0)
    bwmposition: bpy.props.FloatVectorProperty(name="BWM Position",
                                               description="Walkmesh position in BWM file",
                                               subtype='XYZ',
                                               default=(0.0, 0.0, 0.0))
    lytposition: bpy.props.FloatVectorProperty(name="LYT Position",
                                               description="Room position in LYT file",
                                               subtype='XYZ',
                                               default=(0.0, 0.0, 0.0))

    # For danglymeshes
    period: bpy.props.FloatProperty(name="Period", default=1.0, min=0.0, max=32.0)
    tightness: bpy.props.FloatProperty(name="Tightness", default=1.0, min=0.0, max=32.0)
    displacement: bpy.props.FloatProperty(name="Displacement", default=0.5, min=0.0, max=32.0)
    constraints: bpy.props.StringProperty(name="Danglegroup", description="Name of the vertex group to use for the danglymesh", default="")

    # For skingroups
    skingroup_obj: bpy.props.StringProperty(name="Bone", description="Name of the bone to create the skingroup for", default="")

    # For lights
    ambientonly: bpy.props.BoolProperty(name="Ambient Only", default=False)
    lightpriority: bpy.props.IntProperty(name="Lightpriority", default=3, min=1, max=5)
    fadinglight: bpy.props.BoolProperty(name="Fading light", default=False)
    isdynamic: bpy.props.IntProperty(name="Dynamic Type", description="0 - ???\n1 - Light affects area geometry AND dynamic objects\n2 - Light affects ONLY dynamic objects", default=0, min=0, max=2)
    affectdynamic: bpy.props.BoolProperty(name="Affect Dynamic", description="Affect dynamic objects", default=False)
    negativelight: bpy.props.BoolProperty(name="Negative Light", default=False)
    lensflares: bpy.props.BoolProperty(name="Lensflares", default=False)
    flareradius: bpy.props.FloatProperty(name="Flare Radius", default=0.0, min=0.0, max=1000000.0)
    flare_list: bpy.props.CollectionProperty(type=FlarePropertyGroup)
    flare_listIdx: bpy.props.IntProperty(name="Index for flare list", default=0)
    shadowradius: bpy.props.FloatProperty(name="Shadow Radius", default=0.0, min=0.0, max=100.0)
    verticaldisplacement: bpy.props.FloatProperty(name="Vertical Displacement", default=0.0, min=0.0, max=10.0)

    # Point lights in Eevee do not have equivalent for Aurora light multiplier and radius
    radius: bpy.props.FloatProperty(name="Radius", default=0.0, min=0.0, max=10000.0, update=update_light_power)
    multiplier: bpy.props.FloatProperty(name="Multiplier", default=1.0, min=0.0, max=10.0, update=update_light_power)

    # For emitters

    # update rules:
    # if update == lightning, birthrate = 2^subdiv + 1, render = lightning, lifeExp = 1
    # if chunk text != '' and text != 'null'/NULL, render = Normal, blend = Normal
    # if p2p_type, set p2p_sel

    # Controllers, in numeric order, these should ALL be animatable
    alphaend: bpy.props.FloatProperty(name="Alpha end", description="Alpha end", default=1.0, min=0.0, max=1.0)
    alphastart: bpy.props.FloatProperty(name="Alpha start", description="Alpha start", default=1.0, min=0.0, max=1.0)
    birthrate: bpy.props.FloatProperty(name="Birthrate", description="Birthrate", default=10.0, min=0.0)
    bounce_co: bpy.props.FloatProperty(name="Coefficient", description="Bounce coefficient", default=0.0, min=0.0)
    combinetime: bpy.props.FloatProperty(name="Combinetime", description="Combinetime", default=0.0)
    drag: bpy.props.FloatProperty(name="Drag", description="Drag (m/s²)", default=0.0, unit='ACCELERATION')
    fps: bpy.props.IntProperty(name="Frames/s", description="Frames per second", default=24, min=0)
    frameend: bpy.props.IntProperty(name="End Frame", description="Frame End", default=0)
    framestart: bpy.props.IntProperty(name="Start Frame", description="Frame Start", default=0)
    grav: bpy.props.FloatProperty(name="Gravity", description="Gravity (m/s²)", default=0.0, min=0.0, unit='ACCELERATION')
    lifeexp: bpy.props.FloatProperty(name="Lifetime", description="Life Expectancy", default=1.0, min=-1.0)
    mass: bpy.props.FloatProperty(name="Mass", description="Mass", default=1.0, min=0.0)
    p2p_bezier2: bpy.props.FloatProperty(name="Bezier 2", description="???", default=0.0)
    p2p_bezier3: bpy.props.FloatProperty(name="Bezier 3", description="???", default=0.0)
    particlerot: bpy.props.FloatProperty(name="Rotation", description="Particle Rotation (degrees)", default=0.0, min=-360.0, max=360.0)
    randvel:  bpy.props.FloatProperty(name="Random Velocity", description="Random Velocity", default=0.0)
    sizestart: bpy.props.FloatProperty(name="Size start", description="x size start", default=1.0, min=0.0)
    sizeend: bpy.props.FloatProperty(name="Size end", description="x size end", default=1.0, min=0.0)
    sizestart_y: bpy.props.FloatProperty(name="Sizestart_y", description="y size start", default=0.0, min=0.0)
    sizeend_y: bpy.props.FloatProperty(name="Sizeend_y", description="y size end", default=0.0, min=0.0)
    spread: bpy.props.FloatProperty(name="Spread", description="Spread", default=0.0, min=0.0)
    threshold: bpy.props.FloatProperty(name="Threshold", description="Threshold", default=0.0)
    velocity:  bpy.props.FloatProperty(name="Velocity", description="Particle Velocity", default=0.0)
    xsize: bpy.props.IntProperty(name="Size X", description="Size X", default=0)
    ysize: bpy.props.IntProperty(name="Size Y", description="Size Y", default=0)
    blurlength: bpy.props.FloatProperty(name="Blur Length", description="Blur Length", default=10.0)
    # Lighting props
    lightningdelay: bpy.props.FloatProperty(name="Delay", description="Lightning Delay (seconds)", default=0.0, min=0.0, max=1000.0)
    lightningradius: bpy.props.FloatProperty(name="Radius", description="Lightning Radius (meters)", default=0.0, min=0.0, max=1000.0)
    lightningsubdiv: bpy.props.IntProperty(name="Subdivisions", description="Lightning Subdivisions", default=0, min=0, max=12, update=update_emitter_prop)
    lightningscale: bpy.props.FloatProperty(name="Scale", description="Lightning Scale", default=1.0, min=0.0, max=1.0)
    lightningzigzag: bpy.props.IntProperty(name="ZigZag", description="Lightning Zig-Zag", default=0, min=0, max=30)
    alphamid: bpy.props.FloatProperty(name="Alpha mid", description="Alpha mid", default=1.0, min=-1.0, max=1.0)
    percentstart: bpy.props.FloatProperty(name="Percent start", description="Percent start", default=1.0, min=0.0, max=1.0)
    percentmid: bpy.props.FloatProperty(name="Percent mid", description="Percent mid", default=1.0, min=0.0, max=1.0)
    percentend: bpy.props.FloatProperty(name="Percent end", description="Percent end", default=1.0, min=0.0, max=1.0)
    sizemid: bpy.props.FloatProperty(name="sizeMid", description="x size mid", default=1.0, min=0.0)
    sizemid_y: bpy.props.FloatProperty(name="sizeMid_y", description="y size mid", default=0.0, min=0.0)
    random_birth_rate: bpy.props.FloatProperty(name="Random Birthrate", description="Random Birthrate", default=10.0, min=0.0)
    targetsize: bpy.props.IntProperty(name="Target Size", description="Target Size", default=1, min=0)
    numcontrolpts: bpy.props.IntProperty(name="# of Control Points", description="Number of Control Points", default=0, min=0)
    controlptradius: bpy.props.FloatProperty(name="Control Point Radius", description="Control Point Radius", default=0.0, min=0.0)
    controlptdelay: bpy.props.IntProperty(name="Control Point Delay", description="Control Point Delay", default=0, min=0)
    tangentspread: bpy.props.IntProperty(name="Tangent Spread", description="Tangent Spread (degrees)", default=0, min=0)
    tangentlength: bpy.props.FloatProperty(name="Tangent Length", description="Tangent Length", default=0.0, min=0.0)
    colormid: bpy.props.FloatVectorProperty(name="Color mid",
                                            description="Color mid",
                                            subtype='COLOR_GAMMA',
                                            default=(1.0, 1.0, 1.0),
                                            min=0.0, max=1.0,
                                            soft_min=0.0, soft_max=1.0)
    colorend: bpy.props.FloatVectorProperty(name="Color end",
                                            description="Color end",
                                            subtype='COLOR_GAMMA',
                                            default=(1.0, 1.0, 1.0),
                                            min=0.0, max=1.0,
                                            soft_min=0.0, soft_max=1.0)
    colorstart: bpy.props.FloatVectorProperty(name="Color start",
                                              description="Color start",
                                              subtype='COLOR_GAMMA',
                                              default=(1.0, 1.0, 1.0),
                                              min=0.0, max=1.0,
                                              soft_min=0.0, soft_max=1.0)

    # Emitter sub-header properties
    deadspace: bpy.props.FloatProperty(name="Dead space", description="Dead space", default=0.0, min=0.0, options=set())
    blastradius: bpy.props.FloatProperty(name="Radius", description="Blast Radius (meters)", default=0.0, min=0.0, unit='LENGTH', options=set())
    blastlength: bpy.props.FloatProperty(name="Length", description="Blast Length (seconds)", default=0.0, min=0.0, unit='TIME', options=set())
    num_branches: bpy.props.IntProperty(name="# of Branches", description="Number of Branches", default=0, options=set())
    controlptsmoothing: bpy.props.IntProperty(name="Control Point Smoothing", description="Control Point Smoothing", default=0, options=set())
    xgrid: bpy.props.IntProperty(name="X Grid", description="X Grid", default=0, options=set())
    ygrid: bpy.props.IntProperty(name="Y Grid", description="Y Grid", default=0, options=set())
    spawntype: bpy.props.EnumProperty(
        name="Spawn", description="Spawn type",
        items=[("NONE", "", "", 0),
               ("Normal", "Normal", "Normal", 1),
               ("Trail", "Trail", "Trail", 2)],
        default="NONE", options=set())
    update: bpy.props.EnumProperty(
        name="Update", description="Update type",
        items=[("NONE", "", "", 0),
               ("Fountain", "Fountain", "Fountain", 1),
               ("Single", "Single", "Single", 2),
               ("Explosion", "Explosion", "Explosion", 3),
               ("Lightning", "Lightning", "Lightning", 4)],
        default="NONE", options=set(), update=update_emitter_prop)
    render_emitter: bpy.props.EnumProperty(
        name="Render", description="Render type",
        items=[("NONE", "", "", 0),
               ("Normal", "Normal", "Normal", 1),
               ("Linked", "Linked", "Linked", 2),
               ("Billboard_to_Local_Z", "Billboard to local Z", "Billboard to local Z", 3),
               ("Billboard_to_World_Z", "Billboard to world Z", "Billboard to world Z", 4),
               ("Aligned_to_World_Z", "Aligned to world Z", "Aligned  to world Z", 5),
               ("Aligned_to_Particle_Dir", "Aligned to particle dir.", "Aligned to particle direction", 6),
               ("Motion_Blur", "Motion Blur", "Motion Blur", 7)],
        default="NONE", options=set())
    blend: bpy.props.EnumProperty(
        name="Blend", description="Blending Mode",
        items=[("NONE", "", "", 0),
               ("Normal", "Normal", "Normal", 1),
               ("Punch-Through", "Punch-Through", "Punch-Through", 2),
               ("Lighten", "Lighten", "Lighten", 3)],
        default="NONE", options=set())
    texture: bpy.props.StringProperty(name="Texture", description="Texture", maxlen=32, options=set())
    chunk_name: bpy.props.StringProperty(name="Chunk Name", description="Chunk Name", maxlen=16, default="", options=set(), update=update_emitter_prop)
    twosidedtex: bpy.props.BoolProperty(name="Two-Sided Texture", description="Textures visible from front and back", default=False, options=set())
    loop: bpy.props.BoolProperty(name="Loop", description="Loop", default=False, options=set())
    renderorder: bpy.props.IntProperty(name="Render order", description="Render Order", default=0, min=0, options=set())
    frame_blending: bpy.props.BoolProperty(name="Frame Blending", default=False, options=set())
    depth_texture_name: bpy.props.StringProperty(name="Depth Texture Name", description="Depth Texture Name", default=defines.NULL, maxlen=32, options=set())

    # Emitter flags
    p2p: bpy.props.BoolProperty(name="p2p", description="Use Point to Point settings", default=False, options=set())
    p2p_sel: bpy.props.BoolProperty(name="p2p_sel", description="???", default=False, options=set())
    p2p_type: bpy.props.EnumProperty(
        name="Type", description="???",
        items=[("NONE", "", "", 0),
               ("Bezier", "Bezier", "Bezier", 1),
               ("Gravity", "Gravity", "Gravity", 2)],
        default="NONE", options=set(), update=update_emitter_prop)
    affected_by_wind: bpy.props.BoolProperty(name="Affected By Wind", description="Particles are affected by area wind", default=False, options=set())
    tinted: bpy.props.BoolProperty(name="Tinted", description="Tint texture with start, mid, and end color", default=False, options=set())
    bounce: bpy.props.BoolProperty(name="Bounce", description="Bounce On/Off", default=False, options=set())
    random: bpy.props.BoolProperty(name="Random", description="Random", default=False, options=set())
    inherit: bpy.props.BoolProperty(name="Inherit", description="Inherit", default=False, options=set())
    inheritvel: bpy.props.BoolProperty(name="Velocity", description="Inherit Velocity", default=False, options=set())
    inherit_local: bpy.props.BoolProperty(name="Local", description="???", default=False, options=set())
    splat: bpy.props.BoolProperty(name="Splat", description="Splat", default=False, options=set())
    inherit_part: bpy.props.BoolProperty(name="Part", description="???", default=False, options=set())
    depth_texture: bpy.props.BoolProperty(name="Use Depth Texture", description="Use Depth Texture", default=False, options=set())

    # Path connections
    path_connections: bpy.props.CollectionProperty(type=PathConnectionPropertyGroup)
    active_path_connection: bpy.props.IntProperty()
