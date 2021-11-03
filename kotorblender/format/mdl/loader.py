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

from ...defines import Nodetype
from ...exception.malformedfile import MalformedFile
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

from .types import *

MDL_OFFSET = 12

SABER_FACES = [
    [5, 4, 0],
    [0, 1, 5],
    [13, 8, 12],
    [8, 13, 9],
    [6, 5, 1],
    [1, 2, 6],
    [10, 9, 13],
    [13, 14, 10],
    [3, 6, 2],
    [6, 3, 7],
    [15, 11, 14],
    [10, 14, 11]
]


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

        self.node_names = []
        self.node_by_number = dict()

    def load(self):
        print("Loading MDL '{}'".format(self.path))

        self.model = Model()

        self.load_file_header()
        self.load_geometry_header()
        self.load_model_header()
        self.load_names()
        self.peek_nodes(self.off_root_node)

        self.model.root_node = self.load_nodes(self.off_root_node, 0)

        self.load_animations()

        return self.model

    def load_file_header(self):
        if self.mdl.get_uint32() != 0:
            raise MalformedFile("Invalid MDL signature")
        self.mdl_size = self.mdl.get_uint32()
        self.mdx_size = self.mdl.get_uint32()

    def load_geometry_header(self):
        fn_ptr1 = self.mdl.get_uint32()
        self.tsl = fn_ptr1 == MODEL_FN_PTR_1_K2_PC

        fn_ptr2 = self.mdl.get_uint32()
        model_name = self.mdl.get_c_string_up_to(32)
        self.off_root_node = self.mdl.get_uint32()
        total_num_nodes = self.mdl.get_uint32()
        runtime_arr1 = self.get_array_def()
        runtime_arr2 = self.get_array_def()
        ref_count = self.mdl.get_uint32()

        self.model_type = self.mdl.get_uint8()
        if self.model_type != 2:
            raise MalformedFile("Invalid model type: expected=2, actual={}".format(self.model_type))

        self.mdl.skip(3)  # padding

        self.model.name = model_name

    def load_model_header(self):
        classification = self.mdl.get_uint8()
        subclassification = self.mdl.get_uint8()
        self.mdl.skip(1)  # unknown
        affected_by_fog = self.mdl.get_uint8()
        num_child_models = self.mdl.get_uint32()
        self.animation_arr = self.get_array_def()
        supermodel_ref = self.mdl.get_uint32()
        bounding_box = [self.mdl.get_float() for _ in range(6)]
        radius = self.mdl.get_float()
        scale = self.mdl.get_float()
        supermodel_name = self.mdl.get_c_string_up_to(32)
        off_head_root_node = self.mdl.get_uint32()
        self.mdl.skip(4)  # padding

        mdx_size = self.mdl.get_uint32()
        if mdx_size != self.mdx_size:
            raise MalformedFile("MDX size mismatch: expected={}, actual={}".format(self.mdx_size, mdx_size))

        mdx_offset = self.mdl.get_uint32()
        self.name_arr = self.get_array_def()

        try:
            self.model.classification = CLASS_BY_VALUE[classification]
        except KeyError:
            raise MalformedFile("Invalid classification: " + str(classification))
        self.model.subclassification = subclassification
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

    def peek_nodes(self, offset):
        self.mdl.seek(MDL_OFFSET + offset)
        self.mdl.skip(4)
        name_index = self.mdl.get_uint16()
        self.mdl.skip(38)
        children_arr = self.get_array_def()

        name = self.names[name_index]
        self.node_names.append(name)

        self.mdl.seek(MDL_OFFSET + children_arr.offset)
        child_offsets = [self.mdl.get_uint32() for _ in range(children_arr.count)]
        for off_child in child_offsets:
            self.peek_nodes(off_child)

    def load_nodes(self, offset, export_order, parent=None):
        self.mdl.seek(MDL_OFFSET + offset)
        print("Loading model node at {}".format(offset))

        type_flags = self.mdl.get_uint16()
        supernode_number = self.mdl.get_uint16()
        name_index = self.mdl.get_uint16()
        self.mdl.skip(2)  # padding
        off_root = self.mdl.get_uint32()
        off_parent = self.mdl.get_uint32()
        position = [self.mdl.get_float() for _ in range(3)]
        orientation = [self.mdl.get_float() for _ in range(4)]
        children_arr = self.get_array_def()
        controller_arr = self.get_array_def()
        controller_data_arr = self.get_array_def()

        name = self.names[name_index]
        node_type = self.get_node_type(type_flags)
        node = self.new_node(name, node_type)

        self.node_by_number[supernode_number] = node

        if parent:
            node.parent = parent
            node.from_root = parent.from_root

        node.supernode_number = supernode_number
        node.export_order = export_order
        node.position = position
        node.orientation = orientation
        node.from_root = node.from_root @ Matrix.Translation(Vector(position)) @ Quaternion(orientation).to_matrix().to_4x4()

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

            node.shadow = shadow
            node.lightpriority = light_priority
            node.ambientonly = ambient_only
            node.ndynamictype = dynamic_type
            node.affectdynamic = affect_dynamic
            node.fadinglight = fading_light
            node.lensflares = flare
            node.flareradius = flare_radius
            node.flare_list = FlareList()

        if type_flags & NODE_EMITTER:
            dead_space = self.mdl.get_float()
            blast_radius = self.mdl.get_float()
            blast_length = self.mdl.get_float()
            num_branches = self.mdl.get_uint32()
            ctrl_point_smoothing = self.mdl.get_float()
            x_grid = self.mdl.get_uint32()
            y_grid = self.mdl.get_uint32()
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
            self.mdl.skip(1)  # padding
            flags = self.mdl.get_uint32()

            # object data
            node.deadspace = dead_space
            node.blastradius = blast_radius
            node.blastlength = blast_length
            node.num_branches = num_branches
            node.controlptsmoothing = ctrl_point_smoothing
            node.xgrid = x_grid
            node.ygrid = y_grid
            node.spawntype = spawn_type
            node.update = update
            node.render_emitter = render
            node.blend = blend
            node.texture = texture
            node.chunk_name = chunk_name
            node.twosidedtex = twosided_tex != 0
            node.loop = loop != 0
            node.renderorder = render_order
            node.frame_blending = frame_blending != 0
            node.depth_texture_name = depth_texture_name if len(depth_texture_name) > 0 and depth_texture_name.lower() != "null" else defines.NULL
            # flags
            node.p2p = flags & EMITTER_FLAG_P2P != 0
            node.p2p_sel = flags & EMITTER_FLAG_P2P_SEL != 0
            node.affected_by_wind = flags & EMITTER_FLAG_AFFECTED_WIND != 0
            node.tinted = flags & EMITTER_FLAG_TINTED != 0
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
            self.mdl.skip(3 * 4)  # unknown
            self.mdl.skip(8)  # saber unknown
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
                self.mdl.skip(1)  # padding
                dirt_texture = self.mdl.get_uint16()
                dirt_coord_space = self.mdl.get_uint16()
                hide_in_holograms = self.mdl.get_uint8()
                self.mdl.skip(1)  # padding

            self.mdl.skip(2)  # padding
            total_area = self.mdl.get_float()
            self.mdl.skip(4)  # padding
            mdx_offset = self.mdl.get_uint32()
            off_vert_arr = self.mdl.get_uint32()

            node.render = render
            node.shadow = shadow
            node.lightmapped = has_lightmap
            node.beaming = beaming
            node.tangentspace = 1 if mdx_data_bitmap & MDX_FLAG_TANGENT1 else 0
            node.rotatetexture = rotate_texture
            node.background_geometry = background_geometry
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
            bone_indices = [self.mdl.get_uint16() for _ in range(16)]
            self.mdl.skip(4)  # padding

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
            off_saber_verts = self.mdl.get_uint32()
            off_saber_uv = self.mdl.get_uint32()
            off_saber_normals = self.mdl.get_uint32()
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
                for val, key, dim in EMITTER_CONTROLLER_KEYS:
                    if val not in controllers:
                        continue
                    if dim == 1:
                        setattr(node, key, controllers[val][0].values[0])
                    else:
                        setattr(node, key, controllers[val][0].values[:dim])

        if type_flags & NODE_LIGHT:
            self.mdl.seek(MDL_OFFSET + flare_size_arr.offset)
            node.flare_list.sizes = [self.mdl.get_float() for _ in range(flare_size_arr.count)]

            self.mdl.seek(MDL_OFFSET + flare_position_arr.offset)
            node.flare_list.positions = [self.mdl.get_float() for _ in range(flare_position_arr.count)]

            self.mdl.seek(MDL_OFFSET + flare_color_shift_arr.offset)
            for _ in range(flare_color_shift_arr.count):
                color_shift = [self.mdl.get_float() for _ in range(3)]
                node.flare_list.colorshifts.append(color_shift)

            self.mdl.seek(MDL_OFFSET + flare_tex_name_arr.offset)
            tex_name_offsets = [self.mdl.get_uint32() for _ in range(flare_tex_name_arr.count)]
            for tex_name_offset in tex_name_offsets:
                self.mdl.seek(MDL_OFFSET + tex_name_offset)
                node.flare_list.textures.append(self.mdl.get_c_string())

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
            if type_flags & NODE_SABER:
                for face in SABER_FACES:
                    node.facelist.faces.append(face)
                    node.facelist.uvIdx.append(face)
                    node.facelist.matId.append(0)
            elif face_arr.count > 0:
                self.mdl.seek(MDL_OFFSET + face_arr.offset)
                for _ in range(face_arr.count):
                    normal = [self.mdl.get_float() for _ in range(3)]
                    plane_distance = self.mdl.get_float()
                    material_id = self.mdl.get_uint32()
                    adjacent_faces = [self.mdl.get_uint16() for _ in range(3)]
                    vert_indices = [self.mdl.get_uint16() for _ in range(3)]
                    node.facelist.faces.append(tuple(vert_indices))
                    node.facelist.uvIdx.append(tuple(vert_indices))
                    node.facelist.matId.append(material_id)
                if index_count_arr.count > 0:
                    self.mdl.seek(MDL_OFFSET + index_count_arr.offset)
                    num_indices = self.mdl.get_uint32()
                if index_offset_arr.count > 0:
                    self.mdl.seek(MDL_OFFSET + index_offset_arr.offset)
                    off_indices = self.mdl.get_uint32()

            node.verts = []
            node.tverts = []
            node.tverts1 = []
            node.weights = []

            if type_flags & NODE_SABER:
                saber_verts = []
                self.mdl.seek(MDL_OFFSET + off_saber_verts)
                for i in range(176):
                    saber_verts.append([self.mdl.get_float() for _ in range(3)])
                saber_tverts = []
                self.mdl.seek(MDL_OFFSET + off_saber_uv)
                for i in range(176):
                    saber_tverts.append([self.mdl.get_float() for _ in range(2)])
                for i in range(4):
                    node.verts.append(saber_verts[i])
                    node.tverts.append(saber_tverts[i])
                for i in range(4):
                    node.verts.append(saber_verts[i])
                    node.tverts.append(saber_tverts[4+i])
                for i in range(88, 92):
                    node.verts.append(saber_verts[i])
                    node.tverts.append(saber_tverts[i])
                for i in range(88, 92):
                    node.verts.append(saber_verts[i])
                    node.tverts.append(saber_tverts[4+i])
            elif mdx_data_size > 0:
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
                            node_name = self.node_names[node_idx]
                            vert_weights.append([node_name, bone_weights[i]])
                        node.weights.append(vert_weights)

        if type_flags & NODE_DANGLY:
            self.mdl.seek(MDL_OFFSET + constraint_arr.offset)
            node.constraints = [self.mdl.get_float() for _ in range(constraint_arr.count)]

        self.mdl.seek(MDL_OFFSET + children_arr.offset)
        child_offsets = [self.mdl.get_uint32() for _ in range(children_arr.count)]
        for child_idx, off_child in enumerate(child_offsets):
            child = self.load_nodes(off_child, child_idx, node)
            node.children.append(child)

        return node

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
        print("Loading animation at {}".format(offset))

        fn_ptr1 = self.mdl.get_uint32()
        fn_ptr2 = self.mdl.get_uint32()
        name = self.mdl.get_c_string_up_to(32)
        off_root_node = self.mdl.get_uint32()
        total_num_nodes = self.mdl.get_uint32()
        runtime_arr1 = self.get_array_def()
        runtime_arr2 = self.get_array_def()
        ref_count = self.mdl.get_uint32()
        model_type = self.mdl.get_uint8()
        self.mdl.skip(3)  # padding
        length = self.mdl.get_float()
        transition = self.mdl.get_float()
        anim_root = self.mdl.get_c_string_up_to(32)
        event_arr = self.get_array_def()
        self.mdl.skip(4)  # padding

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

        anim.root_node = self.load_anim_nodes(off_root_node, anim)
        self.model.animations.append(anim)

    def load_anim_nodes(self, offset, anim, parent=None):
        self.mdl.seek(MDL_OFFSET + offset)
        print("Loading animation node at {}".format(offset))

        type_flags = self.mdl.get_uint16()
        supernode_number = self.mdl.get_uint16()
        name_index = self.mdl.get_uint16()
        self.mdl.skip(2)  # padding
        off_root = self.mdl.get_uint32()
        off_parent = self.mdl.get_uint32()
        position = [self.mdl.get_float() for _ in range(3)]
        orientation = [self.mdl.get_float() for _ in range(4)]
        children_arr = self.get_array_def()
        controller_arr = self.get_array_def()
        controller_data_arr = self.get_array_def()

        name = self.names[name_index]
        node = AnimationNode(name)
        node.supernode_number = supernode_number
        node.nodetype = self.get_node_type(type_flags)
        node.parent = parent

        if controller_arr.count > 0:
            if not supernode_number in self.node_by_number:
                raise MalformedFile("Model node not found for animation node: " + str(name))
            supernode = self.node_by_number[supernode_number]
            controllers = self.load_controllers(controller_arr, controller_data_arr)
            if CTRL_BASE_POSITION in controllers:
                node.keyframes["position"] = [[row.timekey] + self.position_controller_to_vector(row.values, supernode.position) for row in controllers[CTRL_BASE_POSITION]]
            if CTRL_BASE_ORIENTATION in controllers:
                node.keyframes["orientation"] = [[row.timekey] + self.orientation_controller_to_quaternion(row.values) for row in controllers[CTRL_BASE_ORIENTATION]]
            if CTRL_BASE_SCALE in controllers:
                node.keyframes["scale"] = [[row.timekey] + [row.values[0]] * 3 for row in controllers[CTRL_BASE_SCALE]]
            if isinstance(supernode, TrimeshNode):
                if CTRL_MESH_ALPHA in controllers:
                    node.keyframes["alpha"] = [[row.timekey] + [row.values[0]] for row in controllers[CTRL_MESH_ALPHA]]
                if CTRL_MESH_SELFILLUMCOLOR in controllers:
                    node.keyframes["selfillumcolor"] = [[row.timekey] + row.values[:3] for row in controllers[CTRL_MESH_SELFILLUMCOLOR]]
            if isinstance(supernode, LightNode):
                if CTRL_LIGHT_COLOR in controllers:
                    node.keyframes["color"] = [[row.timekey] + row.values[:3] for row in controllers[CTRL_LIGHT_COLOR]]
                if CTRL_LIGHT_RADIUS in controllers:
                    node.keyframes["radius"] = [[row.timekey] + [row.values[0]] for row in controllers[CTRL_LIGHT_RADIUS]]
                if CTRL_LIGHT_MULTIPLIER in controllers:
                    node.keyframes["multiplier"] = [[row.timekey] + [row.values[0]] for row in controllers[CTRL_LIGHT_MULTIPLIER]]
            if isinstance(supernode, EmitterNode):
                for key in EMITTER_CONTROLLER_KEYS:
                    if not key[0] in controllers:
                        continue
                    num_columns = key[2]
                    node.keyframes[key[1]] = [[row.timekey] + row.values[:num_columns] for row in controllers[key[0]]]

        self.mdl.seek(MDL_OFFSET + children_arr.offset)
        child_offsets = [self.mdl.get_uint32() for _ in range(children_arr.count)]
        for off_child in child_offsets:
            child = self.load_anim_nodes(off_child, anim, node)
            node.children.append(child)

        return node

    def load_controllers(self, controller_arr, controller_data_arr):
        self.mdl.seek(MDL_OFFSET + controller_arr.offset)
        keys = []
        for _ in range(controller_arr.count):
            ctrl_type = self.mdl.get_uint32()
            self.mdl.skip(2)  # unknown
            num_rows = self.mdl.get_uint16()
            timekeys_start = self.mdl.get_uint16()
            values_start = self.mdl.get_uint16()
            num_columns = self.mdl.get_uint8()
            self.mdl.skip(3)  # padding
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
            raise MalformedFile("Invalid node type")

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
            raise MalformedFile("Unsupported number of orientation columns: " + str(num_columns))

    def get_array_def(self):
        offset = self.mdl.get_uint32()
        count1 = self.mdl.get_uint32()
        count2 = self.mdl.get_uint32()
        if count1 != count2:
            raise MalformedFile("Array count mismatch: count1={}, count2={}".format(count1, count2))

        return ArrayDefinition(offset, count1)
