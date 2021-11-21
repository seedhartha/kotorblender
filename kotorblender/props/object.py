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

from ..defines import Classification, DummyType, MeshType
from ..scene.modelnode.light import LightNode

from .. import defines

from .anim import AnimPropertyGroup
from .lensflare import LensFlarePropertyGroup
from .pathconnection import PathConnectionPropertyGroup


def on_update_light_power(self, context):
    obj = context.object
    if obj and obj.type == 'LIGHT':
        LightNode.calc_light_power(obj)


class ObjectPropertyGroup(bpy.types.PropertyGroup):
    # Model Node
    node_number: bpy.props.IntProperty(name="Node Number", description="Must be unique per model and equal to this node number in supermodel", min=0, max=1000)
    export_order: bpy.props.IntProperty(name="Export Order", description="Export order relative to parent", min=0, max=1000)

    # Model
    supermodel: bpy.props.StringProperty(name="Supermodel", description="Name of the model to inherit animations from", default=defines.NULL)
    classification: bpy.props.EnumProperty(name="Classification",
                                           items=[(Classification.OTHER,      "Other",      "Unknown",                        0),
                                                  (Classification.EFFECT,     "Effect",     "",                               1),
                                                  (Classification.TILE,       "Tile",       "",                               2),
                                                  (Classification.CHARACTER,  "Character",  "Creatures and placeables",       3),
                                                  (Classification.DOOR,       "Door",       "",                               4),
                                                  (Classification.LIGHTSABER, "Lightsaber", "",                               5),
                                                  (Classification.PLACEABLE,  "Placeable",  "Placeables and items",           6),
                                                  (Classification.FLYER,      "Flyer",      "Non-interactive scene elements", 7)],
                                           default=Classification.OTHER)
    subclassification: bpy.props.IntProperty(name="Subclassification")
    affected_by_fog: bpy.props.BoolProperty(name="Affected by Fog", description="This model should be affected by area fog", default=True)
    animroot: bpy.props.StringProperty(name="Animation Root", description="Animations should only affect children of selected object", default=defines.NULL)
    animscale: bpy.props.FloatProperty(name="Animation Scale", description="Scale of this model relative to its supermodel", default=1.0, min=0.0)

    # Animations
    anim_list: bpy.props.CollectionProperty(type=AnimPropertyGroup)
    anim_list_idx: bpy.props.IntProperty()

    # Dummy Node
    dummytype: bpy.props.EnumProperty(name="Type",
                                      items=[(DummyType.NONE,      "None",           "",                            0),
                                             (DummyType.MDLROOT,   "MDL Root",       "Root of MDL model",           1),
                                             (DummyType.DWKROOT,   "DWK Root",       "Root of door walkmesh",       2),
                                             (DummyType.PWKROOT,   "PWK Root",       "Root of placeable walkmesh",  3),
                                             (DummyType.PTHROOT,   "PTH Root",       "",                            4),
                                             (DummyType.REFERENCE, "Reference",      "",                            5),
                                             (DummyType.PATHPOINT, "Path Point",     "",                            6),
                                             (DummyType.USE1,      "Walkmesh: Use 1", "'Use 1' animation position", 7),
                                             (DummyType.USE2,      "Walkmesh: Use 2", "'Use 2' animation position", 8)],
                                      default=DummyType.NONE)

    # Reference Node
    refmodel: bpy.props.StringProperty(name="Reference Model", description="Name of another model", default="fx_ref")
    reattachable: bpy.props.BoolProperty(name="Reattachable")

    # Mesh Node
    meshtype: bpy.props.EnumProperty(name="Type",
                                     items=[(MeshType.TRIMESH,    "Trimesh",    "", 0),
                                            (MeshType.DANGLYMESH, "Danglymesh", "", 1),
                                            (MeshType.SKIN,       "Skinmesh",   "", 2),
                                            (MeshType.AABB,       "AABB",       "", 3),
                                            (MeshType.EMITTER,    "Emitter",    "", 4),
                                            (MeshType.LIGHTSABER, "Lightsaber", "", 5)],
                                     default=MeshType.TRIMESH)
    bitmap: bpy.props.StringProperty(name="Diffuse Map")
    bitmap2: bpy.props.StringProperty(name="Lightmap")
    alpha: bpy.props.FloatProperty(name="Alpha", default=1.0, min=0.0, max=1.0)
    render: bpy.props.BoolProperty(name="Render", description="This object should be rendered", default=True)
    shadow: bpy.props.BoolProperty(name="Shadow", description="This object should cast shadows", default=True)
    lightmapped: bpy.props.BoolProperty(name="Lightmapped", description="This object is lightmapped")
    beaming: bpy.props.BoolProperty(name="Beaming", description="This object should cast beams")
    tangentspace: bpy.props.BoolProperty(name="Tangent Space", description="This object is normal mapped")
    rotatetexture: bpy.props.BoolProperty(name="Rotate Texture", description="Texture should be automatically rotated to prevent seams")
    background_geometry: bpy.props.BoolProperty(name="Background Geometry", description="This object is part of background geometry")
    dirt_enabled: bpy.props.BoolProperty(name="Dirt", description="Enable dirt (TSL only)")
    dirt_texture: bpy.props.IntProperty(name="Dirt Texture", default=1)
    dirt_worldspace: bpy.props.IntProperty(name="Dirt World Space", default=1)
    hologram_donotdraw: bpy.props.BoolProperty(name="Hide in Hologram", description="This object should be hidden in hologram mode (e.g., tongue)")
    animateuv: bpy.props.BoolProperty(name="Animate UV", description="Animate texture coordinates")
    uvdirectionx: bpy.props.FloatProperty(name="X Direction", default=1.0)
    uvdirectiony: bpy.props.FloatProperty(name="Y Direction")
    uvjitter: bpy.props.FloatProperty(name="Jitter Amount")
    uvjitterspeed: bpy.props.FloatProperty(name="Jitter Speed")
    transparencyhint: bpy.props.IntProperty(name="Transparency Hint", min=0, max=32)
    selfillumcolor: bpy.props.FloatVectorProperty(name="Self-illum. Color",
                                                  description="This object should glow, but not emit light",
                                                  subtype='COLOR_GAMMA',
                                                  min=0.0, max=1.0)
    diffuse: bpy.props.FloatVectorProperty(name="Diffuse Color",
                                           subtype='COLOR_GAMMA',
                                           default=(0.8, 0.8, 0.8),
                                           min=0.0, max=1.0)
    ambient: bpy.props.FloatVectorProperty(name="Ambient Color",
                                           subtype='COLOR_GAMMA',
                                           default=(0.2, 0.2, 0.2),
                                           min=0.0, max=1.0)

    bwmposition: bpy.props.FloatVectorProperty(name="BWM Position",
                                               description="Walkmesh position in BWM file",
                                               subtype='XYZ')
    lytposition: bpy.props.FloatVectorProperty(name="LYT Position",
                                               description="Room position in LYT file",
                                               subtype='XYZ')

    # Danglymesh
    period: bpy.props.FloatProperty(name="Period", default=1.0, min=0.0, max=32.0)
    tightness: bpy.props.FloatProperty(name="Tightness", default=1.0, min=0.0, max=32.0)
    displacement: bpy.props.FloatProperty(name="Displacement", default=0.5, min=0.0, max=32.0)
    constraints: bpy.props.StringProperty(name="Constraints", description="Name of the vertex group to store constraints in")

    # Light
    ambientonly: bpy.props.BoolProperty(name="Ambient Only")
    lightpriority: bpy.props.IntProperty(name="Light Priority", default=3, soft_min=1, soft_max=5)
    fadinglight: bpy.props.BoolProperty(name="Fading Light")
    dynamictype: bpy.props.IntProperty(name="Dynamic Type", description="This light should affect: 0 - ???\n1 - Area geometry AND dynamic objects\n2 - Dynamic objects ONLY", min=0, max=2)
    affectdynamic: bpy.props.BoolProperty(name="Affect Dynamic", description="This light should affect dynamic objects")
    lensflares: bpy.props.BoolProperty(name="Lens Flares")
    flareradius: bpy.props.FloatProperty(name="Flare Radius", min=0.0, max=1e6)
    flare_list: bpy.props.CollectionProperty(type=LensFlarePropertyGroup)
    flare_list_idx: bpy.props.IntProperty()
    radius: bpy.props.FloatProperty(name="Radius", min=0.0, max=1e6, update=on_update_light_power)
    multiplier: bpy.props.FloatProperty(name="Multiplier", default=1.0, min=0.0, max=10.0, update=on_update_light_power)

    # Emitter
    alphaend: bpy.props.FloatProperty(name="Alpha End", default=1.0, min=0.0, max=1.0)
    alphastart: bpy.props.FloatProperty(name="Alpha Start", default=1.0, min=0.0, max=1.0)
    birthrate: bpy.props.FloatProperty(name="Birthrate", default=10.0, min=0.0)
    bounce_co: bpy.props.FloatProperty(name="Bounce Coefficient", min=0.0)
    combinetime: bpy.props.FloatProperty(name="Combine Time")
    drag: bpy.props.FloatProperty(name="Drag", description="Drag (m/s²)")
    fps: bpy.props.FloatProperty(name="FPS", description="Frames Per Second", default=24.0, min=0.0)
    frameend: bpy.props.FloatProperty(name="End Frame")
    framestart: bpy.props.FloatProperty(name="Start Frame")
    grav: bpy.props.FloatProperty(name="Gravity", description="Gravity (m/s²)", min=0.0)
    lifeexp: bpy.props.FloatProperty(name="Life Expectancy", default=1.0, min=-1.0)
    mass: bpy.props.FloatProperty(name="Mass", default=1.0, min=0.0)
    p2p_bezier2: bpy.props.FloatProperty(name="Bezier 2")
    p2p_bezier3: bpy.props.FloatProperty(name="Bezier 3")
    particlerot: bpy.props.FloatProperty(name="Particle Rotation", min=-360.0, max=360.0)
    randvel:  bpy.props.FloatProperty(name="Random Velocity")
    sizestart: bpy.props.FloatProperty(name="Size Start", default=1.0, min=0.0)
    sizeend: bpy.props.FloatProperty(name="Size End", default=1.0, min=0.0)
    sizestart_y: bpy.props.FloatProperty(name="Y Size Start", min=0.0)
    sizeend_y: bpy.props.FloatProperty(name="Y Size End", min=0.0)
    spread: bpy.props.FloatProperty(name="Spread", min=0.0)
    threshold: bpy.props.FloatProperty(name="Threshold")
    velocity:  bpy.props.FloatProperty(name="Velocity")
    xsize: bpy.props.FloatProperty(name="Size X")
    ysize: bpy.props.FloatProperty(name="Size Y")
    blurlength: bpy.props.FloatProperty(name="Blur Length", default=10.0)
    lightningdelay: bpy.props.FloatProperty(name="Lightning Delay", description="Lighting delay (seconds)", min=0.0, max=1000.0)
    lightningradius: bpy.props.FloatProperty(name="Lightning Radius", description="Lighting radius (meters)", min=0.0, max=1000.0)
    lightningsubdiv: bpy.props.FloatProperty(name="Lightning Subdivisions", min=0.0, max=12.0)
    lightningscale: bpy.props.FloatProperty(name="Lightning Scale", default=1.0, min=0.0, max=1.0)
    lightningzigzag: bpy.props.FloatProperty(name="Lightning Zig-Zag", min=0.0, max=30)
    alphamid: bpy.props.FloatProperty(name="Alpha Mid", default=1.0, min=-1.0, max=1.0)
    percentstart: bpy.props.FloatProperty(name="Percent Start", default=1.0, min=0.0, max=1.0)
    percentmid: bpy.props.FloatProperty(name="Percent Mid", default=1.0, min=0.0, max=1.0)
    percentend: bpy.props.FloatProperty(name="Percent End", default=1.0, min=0.0, max=1.0)
    sizemid: bpy.props.FloatProperty(name="sizeMid", default=1.0, min=0.0)
    sizemid_y: bpy.props.FloatProperty(name="sizeMid_y", min=0.0)
    randombirthrate: bpy.props.FloatProperty(name="Random Birthrate", default=10.0, min=0.0)
    targetsize: bpy.props.FloatProperty(name="Target Size", default=1.0, min=0.0)
    numcontrolpts: bpy.props.FloatProperty(name="Number of Control Points", min=0.0)
    controlptradius: bpy.props.FloatProperty(name="Control Point Radius", min=0.0)
    controlptdelay: bpy.props.FloatProperty(name="Control Point Delay", min=0.0)
    tangentspread: bpy.props.FloatProperty(name="Tangent Spread", description="Tangent spread (degrees)", min=0.0)
    tangentlength: bpy.props.FloatProperty(name="Tangent Length", min=0.0)
    colormid: bpy.props.FloatVectorProperty(name="Color Mid",
                                            subtype='COLOR_GAMMA',
                                            default=(1.0, 1.0, 1.0),
                                            min=0.0, max=1.0,
                                            soft_min=0.0, soft_max=1.0)
    colorend: bpy.props.FloatVectorProperty(name="Color End",
                                            subtype='COLOR_GAMMA',
                                            default=(1.0, 1.0, 1.0),
                                            min=0.0, max=1.0,
                                            soft_min=0.0, soft_max=1.0)
    colorstart: bpy.props.FloatVectorProperty(name="Color Start",
                                              subtype='COLOR_GAMMA',
                                              default=(1.0, 1.0, 1.0),
                                              min=0.0, max=1.0,
                                              soft_min=0.0, soft_max=1.0)
    deadspace: bpy.props.FloatProperty(name="Dead Space", min=0.0)
    blastradius: bpy.props.FloatProperty(name="Blast Radius", description="Blast radius (meters)", min=0.0)
    blastlength: bpy.props.FloatProperty(name="Blast Length", description="Blast length (seconds)", min=0.0)
    num_branches: bpy.props.IntProperty(name="Number of Branches")
    controlptsmoothing: bpy.props.FloatProperty(name="Control Point Smoothing")
    xgrid: bpy.props.IntProperty(name="X Grid")
    ygrid: bpy.props.IntProperty(name="Y Grid")
    spawntype: bpy.props.EnumProperty(name="Spawn", description="Spawn type",
                                      items=[("Normal", "Normal", "", 0),
                                             ("Trail", "Trail", "", 1)],
                                      default="Normal")
    update: bpy.props.EnumProperty(name="Update", description="Update type",
                                   items=[("NONE", "", "", 0),
                                          ("Fountain", "Fountain", "", 1),
                                          ("Single", "Single", "", 2),
                                          ("Explosion", "Explosion", "", 3),
                                          ("Lightning", "Lightning", "", 4)],
                                   default="NONE")
    emitter_render: bpy.props.EnumProperty(name="Render",
                                           items=[("NONE", "", "", 0),
                                                  ("Normal", "Normal", "", 1),
                                                  ("Linked", "Linked", "", 2),
                                                  ("Billboard_to_Local_Z", "Billboard to local Z", "", 3),
                                                  ("Billboard_to_World_Z", "Billboard to world Z", "", 4),
                                                  ("Aligned_to_World_Z", "Aligned to world Z", "", 5),
                                                  ("Aligned_to_Particle_Dir", "Aligned to particle dir.", "", 6),
                                                  ("Motion_Blur", "Motion Blur", "", 7)],
                                           default="NONE")
    blend: bpy.props.EnumProperty(name="Blend",
                                  items=[("NONE", "", "", 0),
                                         ("Normal", "Normal", "", 1),
                                         ("Punch-Through", "Punch-Through", "", 2),
                                         ("Lighten", "Lighten", "", 3)],
                                  default="NONE")
    texture: bpy.props.StringProperty(name="Texture", maxlen=32)
    chunk_name: bpy.props.StringProperty(name="Chunk Name", maxlen=16)
    twosidedtex: bpy.props.BoolProperty(name="Two-Sided Texture")
    loop: bpy.props.BoolProperty(name="Loop")
    renderorder: bpy.props.IntProperty(name="Render Order", min=0)
    frame_blending: bpy.props.BoolProperty(name="Frame Blending")
    depth_texture_name: bpy.props.StringProperty(name="Depth Texture Name", default=defines.NULL, maxlen=32)
    p2p: bpy.props.BoolProperty(name="P2P")
    p2p_type: bpy.props.EnumProperty(name="Type",
                                     items=[("Bezier", "Bezier", "Bezier", 0),
                                            ("Gravity", "Gravity", "Gravity", 1)],
                                     default="Bezier")
    affected_by_wind: bpy.props.BoolProperty(name="Affected By Wind")
    tinted: bpy.props.BoolProperty(name="Tinted", description="Texture should be tinted with start, mid, and end color")
    bounce: bpy.props.BoolProperty(name="Bounce")
    random: bpy.props.BoolProperty(name="Random")
    inherit: bpy.props.BoolProperty(name="Inherit")
    inheritvel: bpy.props.BoolProperty(name="Inherit Velocity")
    inherit_local: bpy.props.BoolProperty(name="Inherit Local")
    splat: bpy.props.BoolProperty(name="Splat")
    inherit_part: bpy.props.BoolProperty(name="Inherit Particle")
    depth_texture: bpy.props.BoolProperty(name="Depth Texture")

    # Path Points
    path_connection_list: bpy.props.CollectionProperty(type=PathConnectionPropertyGroup)
    path_connection_idx: bpy.props.IntProperty()
