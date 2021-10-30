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

from math import sqrt

from mathutils import Matrix, Quaternion, Vector

from ...defines import Classification, Nodetype
from ...exception.malformedmdl import MalformedMdl
from ...exception.mdxnotfound import MdxNotFound
from ...scene.animation import Animation
from ...scene.animnode import AnimationNode
from ...scene.model import Model
from ...scene.modelnode.aabb import AabbNode
from ...scene.modelnode.danglymesh import DanglymeshNode
from ...scene.modelnode.dummy import DummyNode
from ...scene.modelnode.emitter import EmitterNode
from ...scene.modelnode.light import FlareList, LightNode
from ...scene.modelnode.lightsaber import LightsaberNode
from ...scene.modelnode.reference import ReferenceNode
from ...scene.modelnode.skinmesh import SkinmeshNode
from ...scene.modelnode.trimesh import FaceList, TrimeshNode

from ... import defines

from ..binreader import BinaryReader

MDL_OFFSET = 12

FN_PTR_1_K1_PC = 4273776
FN_PTR_1_K2_PC = 4285200

CLASS_OTHER = 0x00
CLASS_EFFECT = 0x01
CLASS_TILE = 0x02
CLASS_CHARACTER = 0x04
CLASS_DOOR = 0x08
CLASS_LIGHTSABER = 0x10
CLASS_PLACEABLE = 0x20
CLASS_FLYER = 0x40

NODE_BASE = 0x0001
NODE_LIGHT = 0x0002
NODE_EMITTER = 0x0004
NODE_REFERENCE = 0x0010
NODE_MESH = 0x0020
NODE_SKIN = 0x0040
NODE_DANGLY = 0x0100
NODE_AABB = 0x0200
NODE_SABER = 0x0800

CTRL_BASE_POSITION = 8
CTRL_BASE_ORIENTATION = 20
CTRL_BASE_SCALE = 36
CTRL_MESH_SELFILLUMCOLOR = 100
CTRL_MESH_ALPHA = 132
CTRL_LIGHT_COLOR = 76
CTRL_LIGHT_RADIUS = 88
CTRL_LIGHT_SHADOWRADIUS = 96
CTRL_LIGHT_VERTICALDISPLACEMENT = 100
CTRL_LIGHT_MULTIPLIER = 140
CTRL_EMITTER_ALPHAEND = 80
CTRL_EMITTER_ALPHASTART = 84
CTRL_EMITTER_BIRTHRATE = 88
CTRL_EMITTER_BOUNCE_CO = 92
CTRL_EMITTER_COMBINETIME = 96
CTRL_EMITTER_DRAG = 100
CTRL_EMITTER_FPS = 104
CTRL_EMITTER_FRAMEEND = 108
CTRL_EMITTER_FRAMESTART = 112
CTRL_EMITTER_GRAV = 116
CTRL_EMITTER_LIFEEXP = 120
CTRL_EMITTER_MASS = 124
CTRL_EMITTER_P2P_BEZIER2 = 128
CTRL_EMITTER_P2P_BEZIER3 = 132
CTRL_EMITTER_PARTICLEROT = 136
CTRL_EMITTER_RANDVEL = 140
CTRL_EMITTER_SIZESTART = 144
CTRL_EMITTER_SIZEEND = 148
CTRL_EMITTER_SIZESTART_Y = 152
CTRL_EMITTER_SIZEEND_Y = 156
CTRL_EMITTER_SPREAD = 160
CTRL_EMITTER_THRESHOLD = 164
CTRL_EMITTER_VELOCITY = 168
CTRL_EMITTER_XSIZE = 172
CTRL_EMITTER_YSIZE = 176
CTRL_EMITTER_BLURLENGTH = 180
CTRL_EMITTER_LIGHTNINGDELAY = 184
CTRL_EMITTER_LIGHTNINGRADIUS = 188
CTRL_EMITTER_LIGHTNINGSCALE = 192
CTRL_EMITTER_LIGHTNINGSUBDIV = 196
CTRL_EMITTER_LIGHTNINGZIGZAG = 200
CTRL_EMITTER_ALPHAMID = 216
CTRL_EMITTER_PERCENTSTART = 220
CTRL_EMITTER_PERCENTMID = 224
CTRL_EMITTER_PERCENTEND = 228
CTRL_EMITTER_SIZEMID = 232
CTRL_EMITTER_SIZEMID_Y = 236
CTRL_EMITTER_RANDOMBIRTHRATE = 240
CTRL_EMITTER_TARGETSIZE = 252
CTRL_EMITTER_NUMCONTROLPTS = 256
CTRL_EMITTER_CONTROLPTRADIUS = 260
CTRL_EMITTER_CONTROLPTDELAY = 264
CTRL_EMITTER_TANGENTSPREAD = 268
CTRL_EMITTER_TANGENTLENGTH = 272
CTRL_EMITTER_COLORMID = 284
CTRL_EMITTER_COLOREND = 380
CTRL_EMITTER_COLORSTART = 392
CTRL_EMITTER_DETONATE = 502

MDX_FLAG_VERTEX = 0x0001
MDX_FLAG_UV1 = 0x0002
MDX_FLAG_UV2 = 0x0004
MDX_FLAG_UV3 = 0x0008
MDX_FLAG_UV4 = 0x0010
MDX_FLAG_NORMAL = 0x0020
MDX_FLAG_COLOR = 0x0040
MDX_FLAG_TANGENT1 = 0x0080
MDX_FLAG_TANGENT2 = 0x0100
MDX_FLAG_TANGENT3 = 0x0200
MDX_FLAG_TANGENT4 = 0x0400

EMITTER_FLAG_P2P = 0x0001
EMITTER_FLAG_P2P_SEL = 0x0002
EMITTER_FLAG_AFFECTED_WIND = 0x0004
EMITTER_FLAG_TINTED = 0x0008
EMITTER_FLAG_BOUNCE = 0x0010
EMITTER_FLAG_RANDOM = 0x0020
EMITTER_FLAG_INHERIT = 0x0040
EMITTER_FLAG_INHERIT_VEL = 0x0080
EMITTER_FLAG_INHERIT_LOCAL = 0x0100
EMITTER_FLAG_SPLAT = 0x0200
EMITTER_FLAG_INHERIT_PART = 0x0400
EMITTER_FLAG_DEPTH_TEXTURE = 0x0800
EMITTER_FLAG_13 = 0x1000

CLASS_BY_VALUE = {
    CLASS_OTHER: Classification.UNKNOWN,
    CLASS_EFFECT: Classification.EFFECT,
    CLASS_TILE: Classification.TILE,
    CLASS_CHARACTER: Classification.CHARACTER,
    CLASS_DOOR: Classification.DOOR,
    CLASS_LIGHTSABER: Classification.SABER,
    CLASS_PLACEABLE: Classification.DOOR,
    CLASS_FLYER: Classification.FLYER
}

EMITTER_CONTROLLER_KEYS = [
    (CTRL_EMITTER_ALPHASTART, "alphaStart", 1),
    (CTRL_EMITTER_ALPHAMID, "alphaMid", 1),
    (CTRL_EMITTER_ALPHAEND, "alphaEnd", 1),
    (CTRL_EMITTER_BIRTHRATE, "birthrate", 1),
    (CTRL_EMITTER_RANDOMBIRTHRATE, "m_fRandomBirthRate", 1),
    (CTRL_EMITTER_BOUNCE_CO, "bounce_co", 1),
    (CTRL_EMITTER_COMBINETIME, "combinetime", 1),
    (CTRL_EMITTER_DRAG, "drag", 1),
    (CTRL_EMITTER_FPS, "fps", 1),
    (CTRL_EMITTER_FRAMEEND, "frameEnd", 1),
    (CTRL_EMITTER_FRAMESTART, "frameStart", 1),
    (CTRL_EMITTER_GRAV, "grav", 1),
    (CTRL_EMITTER_LIFEEXP, "lifeExp", 1),
    (CTRL_EMITTER_MASS, "mass", 1),
    (CTRL_EMITTER_P2P_BEZIER2, "p2p_bezier2", 1),
    (CTRL_EMITTER_P2P_BEZIER3, "p2p_bezier3", 1),
    (CTRL_EMITTER_PARTICLEROT, "particleRot", 1),
    (CTRL_EMITTER_RANDVEL, "randvel", 1),
    (CTRL_EMITTER_SIZESTART, "sizeStart", 1),
    (CTRL_EMITTER_SIZEMID, "sizeMid", 1),
    (CTRL_EMITTER_SIZEEND, "sizeEnd", 1),
    (CTRL_EMITTER_SIZESTART_Y, "sizeStart_y", 1),
    (CTRL_EMITTER_SIZEMID_Y, "sizeMid_y", 1),
    (CTRL_EMITTER_SIZEEND_Y, "sizeEnd_y", 1),
    (CTRL_EMITTER_SPREAD, "spread", 1),
    (CTRL_EMITTER_THRESHOLD, "threshold", 1),
    (CTRL_EMITTER_VELOCITY, "velocity", 1),
    (CTRL_EMITTER_XSIZE, "xsize", 1),
    (CTRL_EMITTER_YSIZE, "ysize", 1),
    (CTRL_EMITTER_BLURLENGTH, "blurlength", 1),
    (CTRL_EMITTER_LIGHTNINGDELAY, "lightningDelay", 1),
    (CTRL_EMITTER_LIGHTNINGRADIUS, "lightningRadius", 1),
    (CTRL_EMITTER_LIGHTNINGSUBDIV, "lightningSubDiv", 1),
    (CTRL_EMITTER_LIGHTNINGSCALE, "lightningScale", 1),
    (CTRL_EMITTER_LIGHTNINGZIGZAG, "lightningzigzag", 1),
    (CTRL_EMITTER_PERCENTSTART, "percentStart", 1),
    (CTRL_EMITTER_PERCENTMID, "percentMid", 1),
    (CTRL_EMITTER_PERCENTEND, "percentEnd", 1),
    (CTRL_EMITTER_TARGETSIZE, "targetsize", 1),
    (CTRL_EMITTER_NUMCONTROLPTS, "numcontrolpts", 1),
    (CTRL_EMITTER_CONTROLPTRADIUS, "controlptradius", 1),
    (CTRL_EMITTER_CONTROLPTDELAY, "controlptdelay", 1),
    (CTRL_EMITTER_TANGENTSPREAD, "tangentspread", 1),
    (CTRL_EMITTER_TANGENTLENGTH, "tangentlength", 1),
    (CTRL_EMITTER_COLORSTART, "colorStart", 3),
    (CTRL_EMITTER_COLORMID, "colorMid", 3),
    (CTRL_EMITTER_COLOREND, "colorEnd", 3)
]


class ControllerKey:
    def __init__(self, ctrl_type, num_rows, timekeys_start, values_start, num_columns):
        self.ctrl_type = ctrl_type
        self.num_rows = num_rows
        self.timekeys_start = timekeys_start
        self.values_start = values_start
        self.num_columns = num_columns


class ControllerRow:
    def __init__(self, timekey, values):
        self.timekey = timekey
        self.values = values

    def __repr__(self):
        return "{{timekey={}, values={}}}".format(self.timekey, self.values)


class ArrayDefinition:
    def __init__(self, offset, count):
        self.offset = offset
        self.count = count


class MdlLoader:

    def __init__(self, path):
        self.path = path
        self.mdl = BinaryReader(path, 'little')

        base, _ = os.path.splitext(path)
        mdx_path = base + ".mdx"
        if not os.path.exists(mdx_path):
            raise MdxNotFound("MDX file '{}' not found".format(mdx_path))

        self.mdx = BinaryReader(mdx_path, 'little')
        self.node_names_df = [] # depth first array of node names

    def load(self):
        print("Loading MDL '{}'".format(self.path))

        self.model = Model()

        self.load_file_header()
        self.load_geometry_header()
        self.load_model_header()
        self.load_names()
        self.load_nodes(self.off_root_node)
        self.load_animations()

        return self.model

    def load_file_header(self):
        if self.mdl.get_uint32() != 0:
            raise MalformedMdl("Invalid MDL signature")
        self.mdl_size = self.mdl.get_uint32()
        self.mdx_size = self.mdl.get_uint32()

    def load_geometry_header(self):
        fn_ptr1 = self.mdl.get_uint32()
        self.tsl = fn_ptr1 == FN_PTR_1_K2_PC
        fn_ptr2 = self.mdl.get_uint32()
        model_name = self.mdl.get_c_string_up_to(32)
        self.off_root_node = self.mdl.get_uint32()
        total_num_nodes = self.mdl.get_uint32()
        runtime_arr1 = self.get_array_def()
        runtime_arr2 = self.get_array_def()
        ref_count = self.mdl.get_uint32()

        self.model_type = self.mdl.get_uint8()
        if self.model_type != 2:
            raise MalformedMdl("Invalid model type: expected=2, actual={}".format(self.model_type))

        self.mdl.skip(3) # padding

        self.model.name = model_name

    def load_model_header(self):
        classification = self.mdl.get_uint8()
        subclassification = self.mdl.get_uint8()
        self.mdl.skip(1) # unknown
        affected_by_fog = self.mdl.get_uint8()
        num_child_models = self.mdl.get_uint32()
        self.animation_arr = self.get_array_def()
        supermodel_ref = self.mdl.get_uint32()
        bounding_box = [self.mdl.get_float() for _ in range(6)]
        radius = self.mdl.get_float()
        scale = self.mdl.get_float()
        supermodel_name = self.mdl.get_c_string_up_to(32)
        off_head_root_node = self.mdl.get_uint32()
        self.mdl.skip(4) # padding

        mdx_size = self.mdl.get_uint32()
        if mdx_size != self.mdx_size:
            raise MalformedMdl("MDX size mismatch: expected={}, actual={}".format(self.mdx_size, mdx_size))

        mdx_offset = self.mdl.get_uint32()
        self.name_arr = self.get_array_def()

        try:
            self.model.classification = CLASS_BY_VALUE[classification]
        except KeyError:
            raise MalformedMdl("Invalid classification: " + str(classification))
        self.model.unknownC1 = subclassification
        self.model.supermodel = supermodel_name
        self.model.animscale = scale
        self.model.ignorefog = affected_by_fog == 0

    def load_names(self):
        self.names = []
        self.mdl.seek(MDL_OFFSET + self.name_arr.offset)
        offsets = [self.mdl.get_uint32() for _ in range(self.name_arr.count)]
        for off in offsets:
            self.mdl.seek(MDL_OFFSET + off)
            self.names.append(self.mdl.get_c_string())

    def load_nodes(self, offset, parent=None):
        self.mdl.seek(MDL_OFFSET + offset)

        type_flags = self.mdl.get_uint16()
        supernode_number = self.mdl.get_uint16()
        name_index = self.mdl.get_uint16()
        self.mdl.skip(2) # padding
        off_root = self.mdl.get_uint32()
        off_parent = self.mdl.get_uint32()
        position = [self.mdl.get_float() for _ in range(3)]
        orientation = [self.mdl.get_float() for _ in range(4)]
        children_arr = self.get_array_def()
        controller_arr = self.get_array_def()
        controller_data_arr = self.get_array_def()

        name = self.names[name_index]
        self.node_names_df.append(name)

        node_type = self.get_node_type(type_flags)
        node = self.new_node(name, node_type)
        self.model.add_node(node)

        if parent:
            node.parentName = parent.name
            node.fromRoot = parent.fromRoot

        node.supernodeNumber = supernode_number
        node.position = position
        node.orientation = orientation
        node.fromRoot = node.fromRoot @ Matrix.Translation(Vector(position)) @ Quaternion(orientation).to_matrix().to_4x4()

        if type_flags & NODE_LIGHT:
            flare_radius = self.mdl.get_float()
            unknown_arr = self.get_array_def()
            flare_size_arr = self.get_array_def()
            flare_position_arr = self.get_array_def()
            flare_color_shift_arr = self.get_array_def()
            flare_tex_name_arr = self.get_array_def()
            light_priority = self.mdl.get_uint32()
            ambient_only = self.mdl.get_uint32()
            dynamic_type = self.mdl.get_uint32()
            affect_dynamic = self.mdl.get_uint32()
            shadow = self.mdl.get_uint32()
            flare = self.mdl.get_uint32()
            fading_light = self.mdl.get_uint32()

            node.shadow        = shadow
            node.lightpriority = light_priority
            node.ambientonly   = ambient_only
            node.ndynamictype  = dynamic_type
            node.affectdynamic = affect_dynamic
            node.fadinglight   = fading_light
            node.lensflares    = flare
            node.flareradius   = flare_radius
            node.flareList     = FlareList()

        if type_flags & NODE_EMITTER:
            dead_space = self.mdl.get_float()
            blast_radius = self.mdl.get_float()
            blast_length = self.mdl.get_float()
            num_branches = self.mdl.get_uint32()
            ctrl_point_smoothing = self.mdl.get_float()
            x_grid = self.mdl.get_float()
            y_grid = self.mdl.get_float()
            spawn_type = self.mdl.get_uint32()
            update = self.mdl.get_c_string_up_to(32)
            render = self.mdl.get_c_string_up_to(32)
            blend = self.mdl.get_c_string_up_to(32)
            texture = self.mdl.get_c_string_up_to(32)
            chunk_name = self.mdl.get_c_string_up_to(16)
            twosided_tex = self.mdl.get_uint32()
            loop = self.mdl.get_uint32()
            render_order = self.mdl.get_uint16()
            frame_blending = self.mdl.get_uint8()
            depth_texture_name = self.mdl.get_c_string_up_to(32)
            self.mdl.skip(1) # padding
            flags = self.mdl.get_uint32()

            # object data
            node.deadspace = dead_space
            node.blastradius = blast_radius
            node.blastlength = blast_length
            node.numBranches = num_branches
            node.controlptsmoothing = ctrl_point_smoothing
            node.xgrid = x_grid
            node.ygrid = y_grid
            node.spawntype = spawn_type
            node.update = update
            node.render = render
            node.blend = blend
            node.texture = texture
            node.chunkName = chunk_name
            node.twosidedtex = twosided_tex != 0
            node.loop = loop != 0
            node.renderorder = render_order
            node.m_bFrameBlending = frame_blending != 0
            node.m_sDepthTextureName = depth_texture_name if len(depth_texture_name) > 0 and depth_texture_name.lower() != "null" else defines.null
            # flags
            node.p2p = flags & EMITTER_FLAG_P2P != 0
            node.p2p_sel = flags & EMITTER_FLAG_P2P_SEL != 0
            node.affectedByWind = flags & EMITTER_FLAG_AFFECTED_WIND != 0
            node.m_isTinted = flags & EMITTER_FLAG_TINTED != 0
            node.bounce = flags & EMITTER_FLAG_BOUNCE != 0
            node.random = flags & EMITTER_FLAG_RANDOM != 0
            node.inherit = flags & EMITTER_FLAG_INHERIT != 0
            node.inheritvel = flags & EMITTER_FLAG_INHERIT_VEL != 0
            node.inherit_local = flags & EMITTER_FLAG_INHERIT_LOCAL != 0
            node.splat = flags & EMITTER_FLAG_SPLAT != 0
            node.inherit_part = flags & EMITTER_FLAG_INHERIT_PART != 0
            node.depth_texture = flags & EMITTER_FLAG_DEPTH_TEXTURE != 0

        if type_flags & NODE_REFERENCE:
            ref_model = self.mdl.get_c_string_up_to(32)
            reattachable = self.mdl.get_uint32()

            node.refmodel = ref_model
            node.reattachable = reattachable

        if type_flags & NODE_MESH:
            fn_ptr1 = self.mdl.get_uint32()
            fn_ptr2 = self.mdl.get_uint32()
            face_arr = self.get_array_def()
            bouding_box = [self.mdl.get_float() for _ in range(6)]
            radius = self.mdl.get_float()
            average = [self.mdl.get_float() for _ in range(3)]
            diffuse = [self.mdl.get_float() for _ in range(3)]
            ambient = [self.mdl.get_float() for _ in range(3)]
            transparency_hint = self.mdl.get_uint32()
            bitmap = self.mdl.get_c_string_up_to(32)
            bitmap2 = self.mdl.get_c_string_up_to(32)
            bitmap3 = self.mdl.get_c_string_up_to(12)
            bitmap4 = self.mdl.get_c_string_up_to(12)
            index_count_arr = self.get_array_def()
            index_offset_arr = self.get_array_def()
            inv_counter_arr = self.get_array_def()
            self.mdl.skip(3 * 4) # unknown
            self.mdl.skip(8) # saber unknown
            animate_uv = self.mdl.get_uint32()
            uv_dir_x = self.mdl.get_float()
            uv_dir_y = self.mdl.get_float()
            uv_jitter = self.mdl.get_float()
            uv_jitter_speed = self.mdl.get_float()
            mdx_data_size = self.mdl.get_uint32()
            mdx_data_bitmap = self.mdl.get_uint32()
            off_mdx_verts = self.mdl.get_uint32()
            off_mdx_normals = self.mdl.get_uint32()
            off_mdx_colors = self.mdl.get_uint32()
            off_mdx_uv1 = self.mdl.get_uint32()
            off_mdx_uv2 = self.mdl.get_uint32()
            off_mdx_uv3 = self.mdl.get_uint32()
            off_mdx_uv4 = self.mdl.get_uint32()
            off_mdx_tan_space1 = self.mdl.get_uint32()
            off_mdx_tan_space2 = self.mdl.get_uint32()
            off_mdx_tan_space3 = self.mdl.get_uint32()
            off_mdx_tan_space4 = self.mdl.get_uint32()
            num_verts = self.mdl.get_uint16()
            num_textures = self.mdl.get_uint16()
            has_lightmap = self.mdl.get_uint8()
            rotate_texture = self.mdl.get_uint8()
            background_geometry = self.mdl.get_uint8()
            shadow = self.mdl.get_uint8()
            beaming = self.mdl.get_uint8()
            render = self.mdl.get_uint8()

            if self.tsl:
                dirt_enabled = self.mdl.get_uint8()
                self.mdl.skip(1) # padding
                dirt_texture = self.mdl.get_uint16()
                dirt_coord_space = self.mdl.get_uint16()
                hide_in_holograms = self.mdl.get_uint8()
                self.mdl.skip(1) # padding

            self.mdl.skip(2) # padding
            total_area = self.mdl.get_float()
            self.mdl.skip(4) # padding
            mdx_offset = self.mdl.get_uint32()
            off_vert_arr = self.mdl.get_uint32()

            node.render = render
            node.shadow = shadow
            node.lightmapped = has_lightmap
            node.beaming = beaming
            node.tangentspace = 1 if mdx_data_bitmap & MDX_FLAG_TANGENT1 else 0
            node.rotatetexture = rotate_texture
            node.m_bIsBackgroundGeometry = background_geometry
            node.animateuv = animate_uv
            node.uvdirectionx = uv_dir_x
            node.uvdirectiony = uv_dir_y
            node.uvjitter = uv_jitter
            node.uvjitterspeed = uv_jitter_speed
            node.transparencyhint = transparency_hint
            node.ambient = ambient
            node.diffuse = diffuse
            node.center = average

            if len(bitmap) > 0 and bitmap.lower() != "null":
                node.bitmap = bitmap
            if len(bitmap2) > 0 and bitmap2.lower() != "null":
                node.bitmap2 = bitmap2

            if self.tsl:
                node.dirt_enabled = dirt_enabled
                node.dirt_texture = dirt_texture
                node.dirt_worldspace = dirt_coord_space
                node.hologram_donotdraw = hide_in_holograms

        if type_flags & NODE_SKIN:
            unknown_arr = self.get_array_def()
            off_mdx_bone_weights = self.mdl.get_uint32()
            off_mdx_bone_indices = self.mdl.get_uint32()
            off_bonemap = self.mdl.get_uint32()
            num_bonemap = self.mdl.get_uint32()
            qbone_arr = self.get_array_def()
            tbone_arr = self.get_array_def()
            garbage_arr = self.get_array_def()
            for _ in range(16):
                bone_indices = self.mdl.get_uint16()
            self.mdl.skip(4) # padding

        if type_flags & NODE_DANGLY:
            constraint_arr = self.get_array_def()
            displacement = self.mdl.get_float()
            tightness = self.mdl.get_float()
            period = self.mdl.get_float()
            off_vert_data = self.mdl.get_uint32()

            node.displacement = displacement
            node.period = period
            node.tightness = tightness

        if type_flags & NODE_AABB:
            off_root_aabb = self.mdl.get_uint32()
            self.load_aabb(off_root_aabb)

        if type_flags & NODE_SABER:
            off_verts = self.mdl.get_uint32()
            off_uv = self.mdl.get_uint32()
            off_normals = self.mdl.get_uint32()
            inv_count1 = self.mdl.get_uint32()
            inv_count2 = self.mdl.get_uint32()

        if controller_arr.count > 0:
            controllers = self.load_controllers(controller_arr, controller_data_arr)
            if type_flags & NODE_MESH:
                node.alpha = controllers[CTRL_MESH_ALPHA][0].values[0] if CTRL_MESH_ALPHA in controllers else 1.0
                node.selfillumcolor = controllers[CTRL_MESH_SELFILLUMCOLOR][0].values if CTRL_MESH_SELFILLUMCOLOR in controllers else [0.0] * 3
            elif type_flags & NODE_LIGHT:
                node.color = controllers[CTRL_LIGHT_COLOR][0].values if CTRL_LIGHT_COLOR in controllers else [1.0] * 3
                node.radius = controllers[CTRL_LIGHT_RADIUS][0].values[0] if CTRL_LIGHT_RADIUS in controllers else 1.0
                node.multiplier = controllers[CTRL_LIGHT_MULTIPLIER][0].values[0] if CTRL_LIGHT_MULTIPLIER in controllers else 1.0
            elif type_flags & NODE_EMITTER:
                node.alphastart = controllers[CTRL_EMITTER_ALPHASTART][0].values[0] if CTRL_EMITTER_ALPHASTART in controllers else 0.0
                node.alphamid = controllers[CTRL_EMITTER_ALPHAMID][0].values[0] if CTRL_EMITTER_ALPHAMID in controllers else 0.0
                node.alphaend = controllers[CTRL_EMITTER_ALPHAEND][0].values[0] if CTRL_EMITTER_ALPHAEND in controllers else 0.0
                node.birthrate = controllers[CTRL_EMITTER_BIRTHRATE][0].values[0] if CTRL_EMITTER_BIRTHRATE in controllers else 0.0
                node.m_frandombirthrate = controllers[CTRL_EMITTER_RANDOMBIRTHRATE][0].values[0] if CTRL_EMITTER_RANDOMBIRTHRATE in controllers else 0.0
                node.bounce_co = controllers[CTRL_EMITTER_BOUNCE_CO][0].values[0] if CTRL_EMITTER_BOUNCE_CO in controllers else 0.0
                node.combinetime = controllers[CTRL_EMITTER_COMBINETIME][0].values[0] if CTRL_EMITTER_COMBINETIME in controllers else 0.0
                node.drag = controllers[CTRL_EMITTER_DRAG][0].values[0] if CTRL_EMITTER_DRAG in controllers else 0.0
                node.fps = int(controllers[CTRL_EMITTER_FPS][0].values[0] if CTRL_EMITTER_FPS in controllers else 0.0)
                node.frameend = int(controllers[CTRL_EMITTER_FRAMEEND][0].values[0] if CTRL_EMITTER_FRAMEEND in controllers else 0.0)
                node.framestart = int(controllers[CTRL_EMITTER_FRAMESTART][0].values[0] if CTRL_EMITTER_FRAMESTART in controllers else 0.0)
                node.grav = controllers[CTRL_EMITTER_GRAV][0].values[0] if CTRL_EMITTER_GRAV in controllers else 0.0
                node.lifeexp = controllers[CTRL_EMITTER_LIFEEXP][0].values[0] if CTRL_EMITTER_LIFEEXP in controllers else 0.0
                node.mass = controllers[CTRL_EMITTER_MASS][0].values[0] if CTRL_EMITTER_MASS in controllers else 0.0
                node.p2p_bezier2 = controllers[CTRL_EMITTER_P2P_BEZIER2][0].values[0] if CTRL_EMITTER_P2P_BEZIER2 in controllers else 0.0
                node.p2p_bezier3 = controllers[CTRL_EMITTER_P2P_BEZIER3][0].values[0] if CTRL_EMITTER_P2P_BEZIER3 in controllers else 0.0
                node.particlerot = controllers[CTRL_EMITTER_PARTICLEROT][0].values[0] if CTRL_EMITTER_PARTICLEROT in controllers else 0.0
                node.randvel = controllers[CTRL_EMITTER_RANDVEL][0].values[0] if CTRL_EMITTER_RANDVEL in controllers else 0.0
                node.sizestart = controllers[CTRL_EMITTER_SIZESTART][0].values[0] if CTRL_EMITTER_SIZESTART in controllers else 0.0
                node.sizemid = controllers[CTRL_EMITTER_SIZEMID][0].values[0] if CTRL_EMITTER_SIZEMID in controllers else 0.0
                node.sizeend = controllers[CTRL_EMITTER_SIZEEND][0].values[0] if CTRL_EMITTER_SIZEEND in controllers else 0.0
                node.sizestart_y = controllers[CTRL_EMITTER_SIZESTART_Y][0].values[0] if CTRL_EMITTER_SIZESTART_Y in controllers else 0.0
                node.sizemid_y = controllers[CTRL_EMITTER_SIZEMID_Y][0].values[0] if CTRL_EMITTER_SIZEMID_Y in controllers else 0.0
                node.sizeend_y = controllers[CTRL_EMITTER_SIZEEND_Y][0].values[0] if CTRL_EMITTER_SIZEEND_Y in controllers else 0.0
                node.spread = controllers[CTRL_EMITTER_SPREAD][0].values[0] if CTRL_EMITTER_SPREAD in controllers else 0.0
                node.threshold = controllers[CTRL_EMITTER_THRESHOLD][0].values[0] if CTRL_EMITTER_THRESHOLD in controllers else 0.0
                node.velocity = controllers[CTRL_EMITTER_VELOCITY][0].values[0] if CTRL_EMITTER_VELOCITY in controllers else 0.0
                node.xsize = int(controllers[CTRL_EMITTER_XSIZE][0].values[0] if CTRL_EMITTER_XSIZE in controllers else 2.0)
                node.ysize = int(controllers[CTRL_EMITTER_YSIZE][0].values[0] if CTRL_EMITTER_YSIZE in controllers else 2.0)
                node.blurlength = controllers[CTRL_EMITTER_BLURLENGTH][0].values[0] if CTRL_EMITTER_BLURLENGTH in controllers else 0.0
                node.lightningdelay = controllers[CTRL_EMITTER_LIGHTNINGDELAY][0].values[0] if CTRL_EMITTER_LIGHTNINGDELAY in controllers else 0.0
                node.lightningradius = controllers[CTRL_EMITTER_LIGHTNINGRADIUS][0].values[0] if CTRL_EMITTER_LIGHTNINGRADIUS in controllers else 0.0
                node.lightningsubdiv = int(controllers[CTRL_EMITTER_LIGHTNINGSUBDIV][0].values[0] if CTRL_EMITTER_LIGHTNINGSUBDIV in controllers else 0.0)
                node.lightningscale = controllers[CTRL_EMITTER_LIGHTNINGSCALE][0].values[0] if CTRL_EMITTER_LIGHTNINGSCALE in controllers else 0.0
                node.lightningzigzag = int(controllers[CTRL_EMITTER_LIGHTNINGZIGZAG][0].values[0] if CTRL_EMITTER_LIGHTNINGZIGZAG in controllers else 0.0)
                node.percentstart = controllers[CTRL_EMITTER_PERCENTSTART][0].values[0] if CTRL_EMITTER_PERCENTSTART in controllers else 0.0
                node.percentmid = controllers[CTRL_EMITTER_PERCENTMID][0].values[0] if CTRL_EMITTER_PERCENTMID in controllers else 0.0
                node.percentend = controllers[CTRL_EMITTER_PERCENTEND][0].values[0] if CTRL_EMITTER_PERCENTEND in controllers else 0.0
                node.targetsize = int(controllers[CTRL_EMITTER_TARGETSIZE][0].values[0] if CTRL_EMITTER_TARGETSIZE in controllers else 0.0)
                node.numcontrolpts = int(controllers[CTRL_EMITTER_NUMCONTROLPTS][0].values[0] if CTRL_EMITTER_NUMCONTROLPTS in controllers else 0.0)
                node.controlptradius = controllers[CTRL_EMITTER_CONTROLPTRADIUS][0].values[0] if CTRL_EMITTER_CONTROLPTRADIUS in controllers else 0.0
                node.controlptdelay = int(controllers[CTRL_EMITTER_CONTROLPTDELAY][0].values[0] if CTRL_EMITTER_CONTROLPTDELAY in controllers else 0.0)
                node.tangentspread = int(controllers[CTRL_EMITTER_TANGENTSPREAD][0].values[0] if CTRL_EMITTER_TANGENTSPREAD in controllers else 0.0)
                node.tangentlength = controllers[CTRL_EMITTER_TANGENTLENGTH][0].values[0] if CTRL_EMITTER_TANGENTLENGTH in controllers else 0.0
                node.colorstart = controllers[CTRL_EMITTER_COLORSTART][0].values[0:3] if CTRL_EMITTER_COLORSTART in controllers else [1.0] * 3
                node.colormid = controllers[CTRL_EMITTER_COLORMID][0].values[0:3] if CTRL_EMITTER_COLORMID in controllers else [1.0] * 3
                node.colorend = controllers[CTRL_EMITTER_COLOREND][0].values[0:3] if CTRL_EMITTER_COLOREND in controllers else [1.0] * 3

        if type_flags & NODE_LIGHT:
            self.mdl.seek(MDL_OFFSET + flare_size_arr.offset)
            node.flareList.sizes = [self.mdl.get_float() for _ in range(flare_size_arr.count)]

            self.mdl.seek(MDL_OFFSET + flare_position_arr.offset)
            node.flareList.positions = [self.mdl.get_float() for _ in range(flare_position_arr.count)]

            self.mdl.seek(MDL_OFFSET + flare_color_shift_arr.offset)
            for _ in range(flare_color_shift_arr.count):
                color_shift = [self.mdl.get_float() for _ in range(3)]
                node.flareList.colorshifts.append(color_shift)

            self.mdl.seek(MDL_OFFSET + flare_tex_name_arr.offset)
            tex_name_offsets = [self.mdl.get_uint32() for _ in range(flare_tex_name_arr.count)]
            for tex_name_offset in tex_name_offsets:
                self.mdl.seek(MDL_OFFSET + tex_name_offset)
                node.flareList.textures.append(self.mdl.get_c_string())

        if type_flags & NODE_SKIN:
            if num_bonemap > 0:
                self.mdl.seek(MDL_OFFSET + off_bonemap)
                bonemap = [int(self.mdl.get_float()) for _ in range(num_bonemap)]
            else:
                bonemap = []
            node_by_bone = dict()
            for node_idx, bone_idx in enumerate(bonemap):
                if bone_idx == -1:
                    continue
                node_by_bone[bone_idx] = node_idx

        if type_flags & NODE_MESH:
            node.facelist = FaceList()
            if face_arr.count > 0:
                self.mdl.seek(MDL_OFFSET + face_arr.offset)
                for _ in range(face_arr.count):
                    normal = [self.mdl.get_float() for _ in range(3)]
                    plane_distance = self.mdl.get_float()
                    material_id = self.mdl.get_uint32()
                    adjacent_faces = [self.mdl.get_uint16() for _ in range(3)]
                    vert_indices = [self.mdl.get_uint16() for _ in range(3)]
                    node.facelist.faces.append(tuple(vert_indices))
                    node.facelist.shdgr.append(1) # TODO
                    node.facelist.uvIdx.append(tuple(vert_indices))
                    node.facelist.matId.append(material_id)
                if index_count_arr.count > 0:
                    self.mdl.seek(MDL_OFFSET + index_count_arr.offset)
                    num_indices = self.mdl.get_uint32()
                if index_offset_arr.count > 0:
                    self.mdl.seek(MDL_OFFSET + index_offset_arr.offset)
                    off_indices = self.mdl.get_uint32()

            if type_flags & NODE_DANGLY:
                self.mdl.seek(MDL_OFFSET + constraint_arr.offset)
                node.constraints = [self.mdl.get_float() for _ in range(constraint_arr.count)]

            node.verts = []
            node.tverts = []
            node.tverts1 = []
            node.weights = []
            for i in range(num_verts):
                self.mdx.seek(mdx_offset + i * mdx_data_size + off_mdx_verts)
                node.verts.append(tuple([self.mdx.get_float() for _ in range(3)]))
                if mdx_data_bitmap & MDX_FLAG_UV1:
                    self.mdx.seek(mdx_offset + i * mdx_data_size + off_mdx_uv1)
                    node.tverts.append(tuple([self.mdx.get_float() for _ in range(2)]))
                if mdx_data_bitmap & MDX_FLAG_UV2:
                    self.mdx.seek(mdx_offset + i * mdx_data_size + off_mdx_uv2)
                    node.tverts1.append(tuple([self.mdx.get_float() for _ in range(2)]))
                if type_flags & NODE_SKIN:
                    self.mdx.seek(mdx_offset + i * mdx_data_size + off_mdx_bone_weights)
                    bone_weights = [self.mdx.get_float() for _ in range(4)]
                    self.mdx.seek(mdx_offset + i * mdx_data_size + off_mdx_bone_indices)
                    bone_indices = [self.mdx.get_float() for _ in range(4)]
                    vert_weights = []
                    for i in range(4):
                        bone_idx = int(bone_indices[i])
                        if bone_idx == -1:
                            continue
                        node_idx = node_by_bone[bone_idx]
                        node_name = self.node_names_df[node_idx]
                        vert_weights.append([node_name, bone_weights[i]])
                    node.weights.append(vert_weights)

        self.mdl.seek(MDL_OFFSET + children_arr.offset)
        child_offsets = [self.mdl.get_uint32() for _ in range(children_arr.count)]
        for off_child in child_offsets:
            self.load_nodes(off_child, node)

    def load_aabb(self, offset):
        self.mdl.seek(MDL_OFFSET + offset)
        bounding_box = [self.mdl.get_float() for _ in range(6)]
        off_child1 = self.mdl.get_uint32()
        off_child2 = self.mdl.get_uint32()
        face_idx = self.mdl.get_int32()
        most_significant_plane = self.mdl.get_uint32()

        if off_child1 > 0:
            self.load_aabb(off_child1)
        if off_child2 > 0:
            self.load_aabb(off_child2)

    def load_animations(self):
        if self.animation_arr.count == 0:
            return
        self.mdl.seek(MDL_OFFSET + self.animation_arr.offset)
        offsets = [self.mdl.get_uint32() for _ in range(self.animation_arr.count)]
        for offset in offsets:
            self.load_animation(offset)

    def load_animation(self, offset):
        self.mdl.seek(MDL_OFFSET + offset)
        fn_ptr1 = self.mdl.get_uint32()
        fn_ptr2 = self.mdl.get_uint32()
        name = self.mdl.get_c_string_up_to(32)
        off_root_node = self.mdl.get_uint32()
        total_num_nodes = self.mdl.get_uint32()
        runtime_arr1 = self.get_array_def()
        runtime_arr2 = self.get_array_def()
        ref_count = self.mdl.get_uint32()
        model_type = self.mdl.get_uint8()
        self.mdl.skip(3) # padding
        length = self.mdl.get_float()
        transition = self.mdl.get_float()
        anim_root = self.mdl.get_c_string_up_to(32)
        event_arr = self.get_array_def()
        self.mdl.skip(4) # padding

        anim = Animation(name)
        anim.length = length
        anim.transtime = transition
        anim.animroot = anim_root

        if event_arr.count > 0:
            self.mdl.seek(MDL_OFFSET + event_arr.offset)
            for _ in range(event_arr.count):
                time = self.mdl.get_float()
                event_name = self.mdl.get_c_string_up_to(32)
                anim.events.append((time, event_name))

        self.model.animations.append(anim)
        self.load_anim_nodes(off_root_node, anim)

    def load_anim_nodes(self, offset, anim, parent=None):
        self.mdl.seek(MDL_OFFSET + offset)

        type_flags = self.mdl.get_uint16()
        supernode_number = self.mdl.get_uint16()
        name_index = self.mdl.get_uint16()
        self.mdl.skip(2) # padding
        off_root = self.mdl.get_uint32()
        off_parent = self.mdl.get_uint32()
        position = [self.mdl.get_float() for _ in range(3)]
        orientation = [self.mdl.get_float() for _ in range(4)]
        children_arr = self.get_array_def()
        controller_arr = self.get_array_def()
        controller_data_arr = self.get_array_def()

        name = self.names[name_index]
        node = AnimationNode(name)
        node.nodetype = self.get_node_type(type_flags)
        node.parent = parent.name if parent else defines.null
        anim.nodes.append(node)

        if controller_arr.count > 0:
            supernode = next((node for node in self.model.nodeDict.values() if node.supernodeNumber == supernode_number), None)
            if not supernode:
                raise MalformedMdl("Model node not found for animation node: " + str(name))
            base_position = supernode.position
            controllers = self.load_controllers(controller_arr, controller_data_arr)
            if CTRL_BASE_POSITION in controllers:
                node.object_data["position"] = (
                    [[row.timekey] + self.position_controller_to_vector(row.values, base_position) for row in controllers[CTRL_BASE_POSITION]],
                    "location",
                    3
                    )
            if CTRL_BASE_ORIENTATION in controllers:
                node.object_data["orientation"] = (
                    [[row.timekey] + self.orientation_controller_to_quaternion(row.values) for row in controllers[CTRL_BASE_ORIENTATION]],
                    "rotation_quaternion",
                    4
                    )
            if CTRL_BASE_SCALE in controllers:
                node.object_data["scale"] = (
                    [[row.timekey] + [row.values[0]] * 3 for row in controllers[CTRL_BASE_SCALE]],
                    "scale",
                    3
                    )
            if isinstance(supernode, TrimeshNode):
                if CTRL_MESH_ALPHA in controllers:
                    node.object_data["alpha"] = (
                        [[row.timekey] + [row.values[0]] for row in controllers[CTRL_MESH_ALPHA]],
                        "kb.alpha",
                        1
                        )
                if CTRL_MESH_SELFILLUMCOLOR in controllers:
                    node.object_data["selfillumcolor"] = (
                        [[row.timekey] + row.values[:3] for row in controllers[CTRL_MESH_SELFILLUMCOLOR]],
                        "kb.selfillumcolor",
                        3
                        )
            if isinstance(supernode, LightNode):
                if CTRL_LIGHT_COLOR in controllers:
                    node.object_data["color"] = (
                        [[row.timekey] + row.values[:3] for row in controllers[CTRL_LIGHT_COLOR]],
                        "color",
                        3
                        )
                if CTRL_LIGHT_RADIUS in controllers:
                    node.object_data["radius"] = (
                        [[row.timekey] + [row.values[0]] for row in controllers[CTRL_LIGHT_RADIUS]],
                        "distance",
                        1
                        )
            if isinstance(supernode, EmitterNode):
                for key in EMITTER_CONTROLLER_KEYS:
                    if not key[0] in controllers:
                        continue
                    num_columns = key[2]
                    node.emitter_data[key[1]] = (
                        [[row.timekey] + row.values[:num_columns] for row in controllers[key[0]]],
                        "",
                        num_columns
                    )

        self.mdl.seek(MDL_OFFSET + children_arr.offset)
        child_offsets = [self.mdl.get_uint32() for _ in range(children_arr.count)]
        for off_child in child_offsets:
            self.load_anim_nodes(off_child, anim, node)

    def load_controllers(self, controller_arr, controller_data_arr):
        self.mdl.seek(MDL_OFFSET + controller_arr.offset)
        keys = []
        for _ in range(controller_arr.count):
            ctrl_type = self.mdl.get_uint32()
            self.mdl.skip(2) # unknown
            num_rows = self.mdl.get_uint16()
            timekeys_start = self.mdl.get_uint16()
            values_start = self.mdl.get_uint16()
            num_columns = self.mdl.get_uint8()
            self.mdl.skip(3) # padding
            keys.append(ControllerKey(ctrl_type, num_rows, timekeys_start, values_start, num_columns))
        controllers = dict()
        for key in keys:
            self.mdl.seek(MDL_OFFSET + controller_data_arr.offset + 4 * key.timekeys_start)
            timekeys = [self.mdl.get_float() for _ in range(key.num_rows)]
            self.mdl.seek(MDL_OFFSET + controller_data_arr.offset + 4 * key.values_start)
            if key.ctrl_type == CTRL_BASE_ORIENTATION and key.num_columns == 2:
                integral = True
                num_columns = 1
            else:
                integral = False
                num_columns = key.num_columns & 0xf
                bezier = key.num_columns & 0x10
                if bezier:
                    num_columns *= 3
            values = [self.mdl.get_uint32() if integral else self.mdl.get_float() for _ in range(num_columns * key.num_rows)]
            controllers[key.ctrl_type] = [ControllerRow(timekeys[i], values[i*num_columns:i*num_columns+num_columns]) for i in range(key.num_rows)]
        return controllers

    def get_node_type(self, flags):
        if flags & NODE_SABER:
            return Nodetype.LIGHTSABER
        if flags & NODE_AABB:
            return Nodetype.AABB
        if flags & NODE_DANGLY:
            return Nodetype.DANGLYMESH
        if flags & NODE_SKIN:
            return Nodetype.SKIN
        if flags & NODE_MESH:
            return Nodetype.TRIMESH
        if flags & NODE_REFERENCE:
            return Nodetype.REFERENCE
        if flags & NODE_EMITTER:
            return Nodetype.EMITTER
        if flags & NODE_LIGHT:
            return Nodetype.LIGHT
        return Nodetype.DUMMY

    def new_node(self, name, node_type):
        switch = {
            Nodetype.DUMMY: DummyNode,
            Nodetype.REFERENCE: ReferenceNode,
            Nodetype.TRIMESH: TrimeshNode,
            Nodetype.DANGLYMESH: DanglymeshNode,
            Nodetype.LIGHTSABER: LightsaberNode,
            Nodetype.SKIN: SkinmeshNode,
            Nodetype.EMITTER: EmitterNode,
            Nodetype.LIGHT: LightNode,
            Nodetype.AABB: AabbNode
            }
        try:
            return switch[node_type](name)
        except KeyError:
            raise MalformedMdl("Invalid node type")

    def position_controller_to_vector(self, values, base_position):
        return [
            values[0] + base_position[0],
            values[1] + base_position[1],
            values[2] + base_position[2]
            ]

    def orientation_controller_to_quaternion(self, values):
        num_columns = len(values)
        if num_columns == 4:
            return [values[3], *values[0:3]]
        elif num_columns == 1:
            comp = values[0]
            x = ((comp & 0x7ff) / 1023.0) - 1.0
            y = (((comp >> 11) & 0x7ff) / 1023.0) - 1.0
            z = ((comp >> 22) / 511.0) - 1.0
            mag2 = x * x + y * y + z * z
            if mag2 < 1.0:
                w = sqrt(1.0 - mag2)
            else:
                w = 0.0
            return [w, x, y, z]
        else:
            raise MalformedMdl("Unsupported number of orientation columns: " + str(num_columns))

    def get_array_def(self):
        offset = self.mdl.get_uint32()
        count1 = self.mdl.get_uint32()
        count2 = self.mdl.get_uint32()
        if count1 != count2:
            raise MalformedMdl("Array count mismatch: count1={}, count2={}".format(count1, count2))

        return ArrayDefinition(offset, count1)