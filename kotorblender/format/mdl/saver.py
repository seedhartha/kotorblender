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

from mathutils import Vector

from ...defines import Nodetype

from ... import aabb, utils

from ..binwriter import BinaryWriter

from .types import *


class MdlSaver:
    def __init__(self, path, model, tsl):
        self.path = path
        self.mdl = BinaryWriter(path, 'little')

        basepath, _ = os.path.splitext(path)
        mdx_path = basepath + ".mdx"
        self.mdx = BinaryWriter(mdx_path, 'little')

        self.model = model
        self.tsl = tsl

        # Model
        self.mdl_pos = 0
        self.mdx_pos = 0
        self.mdl_size = 0
        self.mdx_size = 0
        self.off_name_offsets = 0
        self.off_anim_offsets = 0

        # Nodes
        self.nodes = []
        self.node_names = []
        self.name_offsets = []
        self.node_offsets = []
        self.children_offsets = []
        self.parent_indices = []
        self.child_indices = []
        self.node_idx_by_name = dict()
        self.node_idx_by_number = dict()

        # Lights
        self.flare_sizes_offsets = dict()
        self.flare_positions_offsets = dict()
        self.flare_colorshifts_offsets = dict()
        self.flare_texture_offset_offsets = dict()
        self.flare_textures_offsets = dict()

        # Meshes
        self.mesh_bounding_boxes = dict()
        self.mesh_averages = dict()
        self.mesh_radii = dict()
        self.mesh_total_areas = dict()
        self.verts_offsets = dict()
        self.faces_offsets = dict()
        self.index_count_offsets = dict()
        self.index_offset_offsets = dict()
        self.inv_count_offsets = dict()
        self.indices_offsets = dict()
        self.mdx_offsets = dict()

        # Skinmeshes
        self.bonemap_offsets = dict()
        self.qbone_offsets = dict()
        self.tbone_offsets = dict()
        self.skin_garbage_offsets = dict()

        # Danglymeshes
        self.constraints_offsets = dict()
        self.dangly_verts_offsets = dict()

        # AABB
        self.aabbs = dict()
        self.aabb_offsets = dict()

        # Sabers
        self.saber_verts_offsets = dict()
        self.saber_uv_offsets = dict()
        self.saber_normals_offsets = dict()

        # Controllers
        self.controller_keys = []
        self.controller_data = []
        self.controller_offsets = []
        self.controller_counts = []
        self.controller_data_offsets = []
        self.controller_data_counts = []

        # Animations
        self.anim_offsets = []
        self.anim_events_offsets = []
        self.anim_nodes = []
        self.anim_node_offsets = []
        self.anim_children_offsets = []
        self.anim_parent_indices = []
        self.anim_child_indices = []
        self.anim_controller_keys = []
        self.anim_controller_data = []
        self.anim_controller_offsets = []
        self.anim_controller_counts = []
        self.anim_controller_data_offsets = []
        self.anim_controller_data_counts = []

    def save(self):
        self.peek_model()

        self.save_file_header()
        self.save_geometry_header()
        self.save_model_header()
        self.save_names()
        self.save_animations()
        self.save_nodes()

    def peek_model(self):
        self.mdl_pos = 80 + 116  # geometry header + model header
        self.off_name_offsets = self.mdl_pos

        self.peek_nodes(self.model.root_node)

        # Nodes
        for node_idx, node in enumerate(self.nodes):
            self.node_names.append(node.name)
            self.node_idx_by_name[node.name] = node_idx
            self.node_idx_by_number[node.node_number] = node_idx

        # Animation Nodes
        for anim_idx, anim in enumerate(self.model.animations):
            self.anim_nodes.append([])
            self.anim_parent_indices.append([])
            self.anim_child_indices.append([])
            self.peek_anim_nodes(anim_idx, anim.root_node)

        self.mdl_pos += 4 * len(self.nodes)  # name offsets

        self.peek_node_names()
        self.peek_animations()
        self.peek_node_data()

        self.mdl_size = self.mdl_pos
        self.mdx_size = self.mdx_pos

    def peek_nodes(self, node, parent_idx=None):
        node_idx = len(self.nodes)
        self.nodes.append(node)
        self.parent_indices.append(parent_idx)
        self.child_indices.append([])

        for child in node.children:
            child_idx = len(self.nodes)
            self.child_indices[node_idx].append(child_idx)
            self.peek_nodes(child, node_idx)

    def peek_anim_nodes(self, anim_idx, node, parent_idx=None):
        node_idx = len(self.anim_nodes[anim_idx])
        self.anim_nodes[anim_idx].append(node)
        self.anim_parent_indices[anim_idx].append(parent_idx)
        self.anim_child_indices[anim_idx].append([])

        for child in node.children:
            if not child.animated:
                continue
            child_idx = len(self.anim_nodes[anim_idx])
            self.anim_child_indices[anim_idx][node_idx].append(child_idx)
            self.peek_anim_nodes(anim_idx, child, node_idx)

    def peek_node_names(self):
        for node in self.nodes:
            self.name_offsets.append(self.mdl_pos)
            self.mdl_pos += len(node.name) + 1

    def peek_animations(self):
        self.off_anim_offsets = self.mdl_pos
        self.mdl_pos += 4 * len(self.model.animations)

        for anim_idx, anim in enumerate(self.model.animations):
            # Animation Header
            self.anim_offsets.append(self.mdl_pos)
            self.mdl_pos += 136

            # Events
            self.anim_events_offsets.append(self.mdl_pos)
            self.mdl_pos += 36 * len(anim.events)

            self.anim_node_offsets.append([])
            self.anim_children_offsets.append([])
            self.anim_controller_keys.append([])
            self.anim_controller_data.append([])
            self.anim_controller_counts.append([])
            self.anim_controller_data_counts.append([])
            self.anim_controller_offsets.append([])
            self.anim_controller_data_offsets.append([])

            # Animation Nodes
            for node_idx, node in enumerate(self.anim_nodes[anim_idx]):
                model_node = self.nodes[self.node_idx_by_number[node.node_number]]
                type_flags = self.get_node_flags(model_node)

                # Geometry Header
                self.anim_node_offsets[anim_idx].append(self.mdl_pos)
                self.mdl_pos += 80

                # Children
                self.anim_children_offsets[anim_idx].append(self.mdl_pos)
                self.mdl_pos += 4 * len(self.anim_child_indices[anim_idx][node_idx])

                # Controllers
                ctrl_keys = []
                ctrl_data = []
                self.peek_anim_controllers(node, type_flags, ctrl_keys, ctrl_data)
                ctrl_count = len(ctrl_keys)
                ctrl_data_count = len(ctrl_data)
                self.anim_controller_keys[anim_idx].append(ctrl_keys)
                self.anim_controller_data[anim_idx].append(ctrl_data)
                self.anim_controller_counts[anim_idx].append(ctrl_count)
                self.anim_controller_data_counts[anim_idx].append(ctrl_data_count)
                self.anim_controller_offsets[anim_idx].append(self.mdl_pos)
                self.mdl_pos += 16 * ctrl_count

                # Controller Data
                self.anim_controller_data_offsets[anim_idx].append(self.mdl_pos)
                self.mdl_pos += 4 * ctrl_data_count

    def peek_node_data(self):
        for node_idx, node in enumerate(self.nodes):
            # Geometry Header
            self.node_offsets.append(self.mdl_pos)
            self.mdl_pos += 80

            type_flags = self.get_node_flags(node)

            # Light Header
            if type_flags & NODE_LIGHT:
                self.mdl_pos += 92

                # Lens Flares
                if node.lensflares:
                    self.flare_sizes_offsets[node_idx] = self.mdl_pos
                    self.mdl_pos += 4 * len(node.flare_list.sizes)

                    self.flare_positions_offsets[node_idx] = self.mdl_pos
                    self.mdl_pos += 4 * len(node.flare_list.positions)

                    self.flare_colorshifts_offsets[node_idx] = self.mdl_pos
                    self.mdl_pos += 4 * 3 * len(node.flare_list.colorshifts)

                    self.flare_texture_offset_offsets[node_idx] = self.mdl_pos
                    self.mdl_pos += 4 * len(node.flare_list.textures)

                    self.flare_textures_offsets[node_idx] = []
                    for tex in node.flare_list.textures:
                        self.flare_textures_offsets[node_idx].append(self.mdl_pos)
                        self.mdl_pos += len(tex) + 1

            # Emitter Header
            if type_flags & NODE_EMITTER:
                self.mdl_pos += 224

            # Reference Header
            if type_flags & NODE_REFERENCE:
                self.mdl_pos += 36

            # Mesh Header
            if type_flags & NODE_MESH:
                self.mdl_pos += 332
                if self.tsl:
                    self.mdl_pos += 8

            # Skin Header
            if type_flags & NODE_SKIN:
                self.mdl_pos += 100

            # Dangly Header
            if type_flags & NODE_DANGLY:
                self.mdl_pos += 28

            # AABB Header
            if type_flags & NODE_AABB:
                self.mdl_pos += 4

            # Saber Header
            if type_flags & NODE_SABER:
                self.mdl_pos += 20

            # Mesh Data
            if type_flags & NODE_MESH:
                num_faces = len(node.facelist.vertices)

                # Faces
                self.faces_offsets[node_idx] = self.mdl_pos
                self.mdl_pos += 32 * num_faces

                # Vertex Indices Offset
                self.index_offset_offsets[node_idx] = self.mdl_pos
                if not type_flags & NODE_SABER:
                    self.mdl_pos += 4

                # Vertices
                num_verts = NUM_SABER_VERTS if type_flags & NODE_SABER else len(node.verts)
                self.verts_offsets[node_idx] = self.mdl_pos
                self.mdl_pos += 4 * 3 * num_verts

                # Vertex Indices Count
                self.index_count_offsets[node_idx] = self.mdl_pos
                if not type_flags & NODE_SABER:
                    self.mdl_pos += 4

                # Inverted Counter
                self.inv_count_offsets[node_idx] = self.mdl_pos
                if not type_flags & NODE_SABER:
                    self.mdl_pos += 4

                # Vertex Indices
                self.indices_offsets[node_idx] = self.mdl_pos
                if not type_flags & NODE_SABER:
                    self.mdl_pos += 2 * 3 * num_faces

                # MDX data
                if type_flags & NODE_SABER:
                    self.mdx_offsets[node_idx] = 0
                else:
                    self.mdx_offsets[node_idx] = self.mdx_pos
                    self.mdx_pos += 4 * 3 * (num_verts + 1)
                    self.mdx_pos += 4 * 3 * (num_verts + 1)
                    if node.uv1:
                        self.mdx_pos += 4 * 2 * (num_verts + 1)
                    if node.uv2:
                        self.mdx_pos += 4 * 2 * (num_verts + 1)
                    if node.tangentspace:
                        self.mdx_pos += 4 * 9 * (num_verts + 1)
                    if type_flags & NODE_SKIN:
                        self.mdx_pos += 4 * 8 * (num_verts + 1)

                # Bounding Box, Average, Total Area
                bb_min = Vector()
                bb_max = Vector()
                average = Vector()
                total_area = 0.0
                for face in node.facelist.vertices:
                    verts = [Vector(node.verts[i]) for i in face]
                    for vert in verts:
                        bb_min.x = min(bb_min.x, vert.x)
                        bb_min.y = min(bb_min.y, vert.y)
                        bb_min.z = min(bb_min.z, vert.z)
                        bb_max.x = max(bb_max.x, vert.x)
                        bb_max.y = max(bb_max.y, vert.y)
                        bb_max.z = max(bb_max.z, vert.z)
                        average += vert
                    edge1 = verts[1] - verts[0]
                    edge2 = verts[2] - verts[0]
                    edge3 = verts[2] - verts[1]
                    area = self.calculate_face_area(edge1, edge2, edge3)
                    if area != 1.0:
                        total_area += area
                average /= 3 * len(node.facelist.vertices)
                self.mesh_bounding_boxes[node_idx] = [*bb_min, *bb_max]
                self.mesh_averages[node_idx] = [*average]
                self.mesh_total_areas[node_idx] = total_area

                # Radius
                radius = 0.0
                for face in node.facelist.vertices:
                    verts = [Vector(node.verts[i]) for i in face]
                    for vert in verts:
                        radius = max(radius, (vert - average).length)
                self.mesh_radii[node_idx] = radius

            # Skin Data
            if type_flags & NODE_SKIN:
                num_bones = len(self.nodes)

                # Bonemap
                self.bonemap_offsets[node_idx] = self.mdl_pos
                self.mdl_pos += 4 * num_bones

                # QBones
                self.qbone_offsets[node_idx] = self.mdl_pos
                self.mdl_pos += 4 * 4 * num_bones

                # TBones
                self.tbone_offsets[node_idx] = self.mdl_pos
                self.mdl_pos += 4 * 3 * num_bones

                # Garbage
                self.skin_garbage_offsets[node_idx] = self.mdl_pos
                self.mdl_pos += 4 * num_bones

            # Dangly Data
            if type_flags & NODE_DANGLY:
                # Constraints
                self.constraints_offsets[node_idx] = self.mdl_pos
                self.mdl_pos += 4 * len(node.constraints)

                # Vertices
                self.dangly_verts_offsets[node_idx] = self.mdl_pos
                self.mdl_pos += 4 * 3 * len(node.verts)

            # AABB Data
            if type_flags & NODE_AABB:
                self.aabb_offsets[node_idx] = []
                aabbs = self.generate_aabb_tree(node)
                for _ in range(len(aabbs)):
                    self.aabb_offsets[node_idx].append(self.mdl_pos)
                    self.mdl_pos += 40
                self.aabbs[node_idx] = aabbs

            # Saber Data
            if type_flags & NODE_SABER:
                self.saber_verts_offsets[node_idx] = self.mdl_pos
                self.mdl_pos += 4 * 3 * NUM_SABER_VERTS

                self.saber_uv_offsets[node_idx] = self.mdl_pos
                self.mdl_pos += 4 * 2 * NUM_SABER_VERTS

                self.saber_normals_offsets[node_idx] = self.mdl_pos
                self.mdl_pos += 4 * 3 * NUM_SABER_VERTS

            # Children
            self.children_offsets.append(self.mdl_pos)
            self.mdl_pos += 4 * len(node.children)

            # Controllers
            ctrl_keys = []
            ctrl_data = []
            self.peek_controllers(node, type_flags, ctrl_keys, ctrl_data)
            ctrl_count = len(ctrl_keys)
            ctrl_data_count = len(ctrl_data)
            self.controller_keys.append(ctrl_keys)
            self.controller_data.append(ctrl_data)
            self.controller_counts.append(ctrl_count)
            self.controller_data_counts.append(ctrl_data_count)
            self.controller_offsets.append(self.mdl_pos)
            self.mdl_pos += 16 * ctrl_count

            # Controller Data
            self.controller_data_offsets.append(self.mdl_pos)
            self.mdl_pos += 4 * ctrl_data_count

    def peek_controllers(self, node, type_flags, out_keys, out_data):
        if not node.parent:
            return

        data_count = 0

        # Base Controllers

        out_keys.append(ControllerKey(CTRL_BASE_POSITION, 1, data_count, data_count + 1, 3))
        out_data.append(0.0)  # timekey
        for val in node.position:
            out_data.append(val)
        data_count += 4

        out_keys.append(ControllerKey(CTRL_BASE_ORIENTATION, 1, data_count, data_count + 1, 4))
        out_data.append(0.0)  # timekey
        for val in node.orientation[1:4]:
            out_data.append(val)
        out_data.append(node.orientation[0])
        data_count += 5

        out_keys.append(ControllerKey(CTRL_BASE_SCALE, 1, data_count, data_count + 1, 1))
        out_data.append(0.0)  # timekey
        out_data.append(node.scale)
        data_count += 2

        # Mesh Controllers

        if type_flags & NODE_MESH:
            out_keys.append(ControllerKey(CTRL_MESH_SELFILLUMCOLOR, 1, data_count, data_count + 1, 3))
            out_data.append(0.0)  # timekey
            for val in node.selfillumcolor:
                out_data.append(val)
            data_count += 4

            out_keys.append(ControllerKey(CTRL_MESH_ALPHA, 1, data_count, data_count + 1, 1))
            out_data.append(0.0)  # timekey
            out_data.append(node.alpha)
            data_count += 2

        # Light Controllers

        if type_flags & NODE_LIGHT:
            out_keys.append(ControllerKey(CTRL_LIGHT_COLOR, 1, data_count, data_count + 1, 3))
            out_data.append(0.0)  # timekey
            for val in node.color:
                out_data.append(val)
            data_count += 4

            out_keys.append(ControllerKey(CTRL_LIGHT_RADIUS, 1, data_count, data_count + 1, 1))
            out_data.append(0.0)  # timekey
            out_data.append(node.radius)
            data_count += 2

            out_keys.append(ControllerKey(CTRL_LIGHT_MULTIPLIER, 1, data_count, data_count + 1, 1))
            out_data.append(0.0)  # timekey
            out_data.append(node.multiplier)
            data_count += 2

        # Emitter Controllers

        if type_flags & NODE_EMITTER:
            for ctrl_val, key, dim in EMITTER_CONTROLLER_KEYS:
                value = getattr(node, key, None)
                if value is None:
                    continue
                out_keys.append(ControllerKey(ctrl_val, 1, data_count, data_count + 1, dim))
                out_data.append(0.0)  # timekey
                if dim == 1:
                    out_data.append(value)
                else:
                    for val in value:
                        out_data.append(val)
                data_count += 1 + dim

    def peek_anim_controllers(self, node, type_flags, out_keys, out_data):

        def append_keyframes(key, ctrl_type, num_columns, data_count, converter=None):
            if key not in node.keyframes:
                return data_count
            keyframes = node.keyframes[key]
            num_rows = len(keyframes)
            out_keys.append(ControllerKey(ctrl_type, num_rows, data_count, data_count + num_rows, num_columns))
            for i in range(num_rows):
                out_data.append(keyframes[i][0])  # timekey
            for i in range(num_rows):
                values = keyframes[i][1:1+num_columns]
                if converter:
                    values = converter(values)
                for val in values:
                    out_data.append(val)
            return data_count + (1 + num_columns) * num_rows

        if not node.parent:
            return

        data_count = 0

        # Base Controllers

        data_count = append_keyframes("position", CTRL_BASE_POSITION, 3, data_count)
        data_count = append_keyframes("orientation", CTRL_BASE_ORIENTATION, 4, data_count, lambda values: [*values[1:4], values[0]])
        data_count = append_keyframes("scale", CTRL_BASE_SCALE, 1, data_count)

        # Mesh Controllers

        if type_flags & NODE_MESH:
            data_count = append_keyframes("selfillumcolor", CTRL_MESH_SELFILLUMCOLOR, 3, data_count)
            data_count = append_keyframes("alpha", CTRL_MESH_ALPHA, 1, data_count)

        # Light Controllers

        if type_flags & NODE_LIGHT:
            data_count = append_keyframes("color", CTRL_LIGHT_COLOR, 3, data_count)
            data_count = append_keyframes("radius", CTRL_LIGHT_RADIUS, 1, data_count)
            data_count = append_keyframes("multiplier", CTRL_LIGHT_MULTIPLIER, 1, data_count)

        # Emitter Controllers

        if type_flags & NODE_EMITTER:
            for ctrl_type, key, dim in EMITTER_CONTROLLER_KEYS:
                data_count = append_keyframes(key, ctrl_type, dim, data_count)

    def save_file_header(self):
        self.mdl.put_uint32(0)  # pseudo signature
        self.mdl.put_uint32(self.mdl_size)
        self.mdl.put_uint32(self.mdx_size)

    def save_geometry_header(self):
        if self.tsl:
            fn_ptr1 = MODEL_FN_PTR_1_K2_PC
            fn_ptr2 = MODEL_FN_PTR_2_K2_PC
        else:
            fn_ptr1 = MODEL_FN_PTR_1_K1_PC
            fn_ptr2 = MODEL_FN_PTR_2_K1_PC
        model_name = self.model.name.ljust(32, '\0')
        off_root_node = self.node_offsets[0]
        total_num_nodes = len(self.nodes)
        ref_count = 0
        model_type = MODEL_MODEL

        self.mdl.put_uint32(fn_ptr1)
        self.mdl.put_uint32(fn_ptr2)
        self.mdl.put_string(model_name)
        self.mdl.put_uint32(off_root_node)
        self.mdl.put_uint32(total_num_nodes)
        self.put_array_def(0, 0)  # runtime array
        self.put_array_def(0, 0)  # runtime array
        self.mdl.put_uint32(ref_count)
        self.mdl.put_uint8(model_type)
        for _ in range(3):
            self.mdl.put_uint8(0)  # padding

    def save_model_header(self):
        classification = next(iter(key for key, value in CLASS_BY_VALUE.items() if value == self.model.classification))
        subclassification = self.model.subclassification
        affected_by_fog = 1 if self.model.affected_by_fog else 0
        num_child_models = 0
        supermodel_ref = 0
        bounding_box = [-5.0, -5.0, -1.0, 5.0, 5.0, 10.0]
        radius = 7.0  # TODO
        scale = self.model.animscale
        supermodel_name = self.model.supermodel.ljust(32, '\0')

        if not utils.is_null(self.model.animroot) and self.node_names.count(self.model.animroot) > 0:
            off_anim_root = self.node_offsets[self.node_names.index(self.model.animroot)]
        else:
            off_anim_root = self.node_offsets[0]

        mdx_size = self.mdx_size
        mdx_offset = 0

        self.mdl.put_uint8(classification)
        self.mdl.put_uint8(subclassification)
        self.mdl.put_uint8(0)  # unknown
        self.mdl.put_uint8(affected_by_fog)
        self.mdl.put_uint32(num_child_models)
        self.put_array_def(self.off_anim_offsets, len(self.model.animations))  # animation offsets
        self.mdl.put_uint32(supermodel_ref)
        for val in bounding_box:
            self.mdl.put_float(val)
        self.mdl.put_float(radius)
        self.mdl.put_float(scale)
        self.mdl.put_string(supermodel_name)
        self.mdl.put_uint32(off_anim_root)
        self.mdl.put_uint32(0)  # unknown
        self.mdl.put_uint32(mdx_size)
        self.mdl.put_uint32(mdx_offset)
        self.put_array_def(self.off_name_offsets, len(self.nodes))  # name offsets

    def save_names(self):
        for offset in self.name_offsets:
            self.mdl.put_uint32(offset)
        for node in self.nodes:
            self.mdl.put_c_string(node.name)

    def save_animations(self):
        for offset in self.anim_offsets:
            self.mdl.put_uint32(offset)

        for anim_idx, anim in enumerate(self.model.animations):
            if self.tsl:
                fn_ptr1 = ANIM_FN_PTR_1_K2_PC
                fn_ptr2 = ANIM_FN_PTR_2_K2_PC
            else:
                fn_ptr1 = ANIM_FN_PTR_1_K1_PC
                fn_ptr2 = ANIM_FN_PTR_2_K1_PC
            name = anim.name.ljust(32, '\0')
            off_root_node = self.anim_node_offsets[anim_idx][0]
            total_num_nodes = len(self.anim_nodes[anim_idx])
            ref_count = 0
            model_type = MODEL_ANIM
            anim_root = anim.animroot.ljust(32, '\0')

            self.mdl.put_uint32(fn_ptr1)
            self.mdl.put_uint32(fn_ptr2)
            self.mdl.put_string(name)
            self.mdl.put_uint32(off_root_node)
            self.mdl.put_uint32(total_num_nodes)
            self.put_array_def(0, 0)  # runtime array
            self.put_array_def(0, 0)  # runtime array
            self.mdl.put_uint32(ref_count)
            self.mdl.put_uint8(model_type)
            for _ in range(3):
                self.mdl.put_uint8(0)  # padding
            self.mdl.put_float(anim.length)
            self.mdl.put_float(anim.transtime)
            self.mdl.put_string(anim_root)
            self.put_array_def(self.anim_events_offsets[anim_idx], len(anim.events))
            self.mdl.put_uint32(0)  # padding

            for time, event in anim.events:
                self.mdl.put_float(time)
                self.mdl.put_string(event.ljust(32, '\0'))

            self.save_anim_nodes(anim_idx)

    def save_anim_nodes(self, anim_idx):
        for node_idx, node in enumerate(self.anim_nodes[anim_idx]):
            # Geometry Header

            type_flags = NODE_BASE
            name_index = self.node_names.index(node.name)
            off_root = self.anim_offsets[anim_idx]
            parent_idx = self.anim_parent_indices[anim_idx][node_idx]
            off_parent = self.anim_node_offsets[anim_idx][parent_idx] if parent_idx is not None else 0
            position = [0.0] * 3
            orientation = [1.0, 0.0, 0.0, 0.0]
            child_indices = self.anim_child_indices[anim_idx][node_idx]

            self.mdl.put_uint16(type_flags)
            self.mdl.put_uint16(node.node_number)
            self.mdl.put_uint16(name_index)
            self.mdl.put_uint16(0)  # padding
            self.mdl.put_uint32(off_root)
            self.mdl.put_uint32(off_parent)
            for val in position:
                self.mdl.put_float(val)
            for val in orientation:
                self.mdl.put_float(val)
            self.put_array_def(self.anim_children_offsets[anim_idx][node_idx], len(child_indices))
            self.put_array_def(self.anim_controller_offsets[anim_idx][node_idx], self.anim_controller_counts[anim_idx][node_idx])
            self.put_array_def(self.anim_controller_data_offsets[anim_idx][node_idx], self.anim_controller_data_counts[anim_idx][node_idx])

            # Children

            for child_idx in child_indices:
                self.mdl.put_uint32(self.anim_node_offsets[anim_idx][child_idx])

            # Controllers

            for key in self.anim_controller_keys[anim_idx][node_idx]:
                if key.ctrl_type in [CTRL_BASE_POSITION, CTRL_BASE_ORIENTATION]:
                    unk1 = key.ctrl_type + 8
                else:
                    unk1 = 0xffff

                self.mdl.put_uint32(key.ctrl_type)
                self.mdl.put_uint16(unk1)
                self.mdl.put_uint16(key.num_rows)
                self.mdl.put_uint16(key.timekeys_start)
                self.mdl.put_uint16(key.values_start)
                self.mdl.put_uint8(key.num_columns)

                for _ in range(3):
                    self.mdl.put_uint8(0)  # padding

            # Controller Data

            for val in self.anim_controller_data[anim_idx][node_idx]:
                self.mdl.put_float(val)

    def save_nodes(self):
        num_meshes = 0

        for node_idx, node in enumerate(self.nodes):
            # Geometry Header

            type_flags = self.get_node_flags(node)
            node_number = node.node_number
            name_index = node_idx
            off_root = 0
            parent_idx = self.parent_indices[node_idx]
            off_parent = self.node_offsets[parent_idx] if parent_idx is not None else 0
            position = node.position
            orientation = node.orientation
            child_indices = self.child_indices[node_idx]

            self.mdl.put_uint16(type_flags)
            self.mdl.put_uint16(node_number)
            self.mdl.put_uint16(name_index)
            self.mdl.put_uint16(0)  # padding
            self.mdl.put_uint32(off_root)
            self.mdl.put_uint32(off_parent)
            for val in position:
                self.mdl.put_float(val)
            for val in orientation:
                self.mdl.put_float(val)
            self.put_array_def(self.children_offsets[node_idx], len(child_indices))
            self.put_array_def(self.controller_offsets[node_idx], self.controller_counts[node_idx])
            self.put_array_def(self.controller_data_offsets[node_idx], self.controller_data_counts[node_idx])

            # Light Header

            if type_flags & NODE_LIGHT:
                shadow = node.shadow
                light_priority = node.lightpriority
                ambient_only = node.ambientonly
                dynamic_type = node.ndynamictype
                affect_dynamic = node.affectdynamic
                fading_light = node.fadinglight
                flare = node.lensflares
                flare_radius = node.flareradius

                self.mdl.put_float(flare_radius)
                self.put_array_def(0, 0)  # unknown
                self.put_array_def(self.flare_sizes_offsets[node_idx] if node.lensflares else 0, len(node.flare_list.sizes))
                self.put_array_def(self.flare_positions_offsets[node_idx] if node.lensflares else 0, len(node.flare_list.positions))
                self.put_array_def(self.flare_colorshifts_offsets[node_idx] if node.lensflares else 0, len(node.flare_list.colorshifts))
                self.put_array_def(self.flare_texture_offset_offsets[node_idx] if node.lensflares else 0, len(node.flare_list.textures))
                self.mdl.put_uint32(light_priority)
                self.mdl.put_uint32(ambient_only)
                self.mdl.put_uint32(dynamic_type)
                self.mdl.put_uint32(affect_dynamic)
                self.mdl.put_uint32(shadow)
                self.mdl.put_uint32(flare)
                self.mdl.put_uint32(fading_light)

                # Lens Flares
                if node.lensflares:
                    for size in node.flare_list.sizes:
                        self.mdl.put_float(size)
                    for position in node.flare_list.positions:
                        self.mdl.put_float(position)
                    for colorshift in node.flare_list.colorshifts:
                        for val in colorshift:
                            self.mdl.put_float(val)
                    for i in range(len(node.flare_list.textures)):
                        off_tex = self.flare_textures_offsets[node_idx][i]
                        self.mdl.put_uint32(off_tex)
                    for tex in node.flare_list.textures:
                        self.mdl.put_c_string(tex)

            # Emitter Header

            if type_flags & NODE_EMITTER:
                update = node.update.ljust(32, '\0')
                render = node.render_emitter.ljust(32, '\0')
                blend = node.blend.ljust(32, '\0')
                texture = node.texture.ljust(32, '\0')
                chunk_name = node.chunk_name.ljust(16, '\0')
                twosided_tex = 1 if node.twosidedtex else 0
                loop = 1 if node.loop else 0
                frame_blending = 1 if node.frame_blending else 0
                depth_texture_name = node.depth_texture_name.ljust(32, '\0')

                flags = 0
                if node.p2p:
                    flags |= EMITTER_FLAG_P2P
                if node.p2p_sel:
                    flags |= EMITTER_FLAG_P2P_SEL
                if node.affected_by_wind:
                    flags |= EMITTER_FLAG_AFFECTED_WIND
                if node.tinted:
                    flags |= EMITTER_FLAG_TINTED
                if node.bounce:
                    flags |= EMITTER_FLAG_BOUNCE
                if node.random:
                    flags |= EMITTER_FLAG_RANDOM
                if node.inherit:
                    flags |= EMITTER_FLAG_INHERIT
                if node.inheritvel:
                    flags |= EMITTER_FLAG_INHERIT_VEL
                if node.inherit_local:
                    flags |= EMITTER_FLAG_INHERIT_LOCAL
                if node.splat:
                    flags |= EMITTER_FLAG_SPLAT
                if node.inherit_part:
                    flags |= EMITTER_FLAG_INHERIT_PART
                if node.depth_texture:
                    flags |= EMITTER_FLAG_DEPTH_TEXTURE

                self.mdl.put_float(node.deadspace)
                self.mdl.put_float(node.blastradius)
                self.mdl.put_float(node.blastlength)
                self.mdl.put_uint32(node.num_branches)
                self.mdl.put_float(node.controlptsmoothing)
                self.mdl.put_uint32(node.xgrid)
                self.mdl.put_uint32(node.ygrid)
                self.mdl.put_uint32(node.spawntype)
                self.mdl.put_string(update)
                self.mdl.put_string(render)
                self.mdl.put_string(blend)
                self.mdl.put_string(texture)
                self.mdl.put_string(chunk_name)
                self.mdl.put_uint32(twosided_tex)
                self.mdl.put_uint32(loop)
                self.mdl.put_uint16(node.renderorder)
                self.mdl.put_uint8(frame_blending)
                self.mdl.put_string(depth_texture_name)
                self.mdl.put_uint8(0)  # padding
                self.mdl.put_uint32(flags)

            # Reference Header

            if type_flags & NODE_REFERENCE:
                ref_model = node.refmodel.ljust(32, '\0')
                reattachable = node.reattachable

                self.mdl.put_string(ref_model)
                self.mdl.put_uint32(reattachable)

            # Mesh Header

            if type_flags & NODE_MESH:
                fn_ptr1, fn_ptr2 = self.get_mesh_fn_ptr(type_flags)

                bounding_box = self.mesh_bounding_boxes[node_idx]
                radius = self.mesh_radii[node_idx]
                average = self.mesh_averages[node_idx]
                diffuse = node.diffuse
                ambient = node.ambient
                transparency_hint = node.transparencyhint
                bitmap = node.bitmap.ljust(32, '\0')
                bitmap2 = node.bitmap2.ljust(32, '\0')
                bitmap3 = "".ljust(12, '\0')
                bitmap4 = "".ljust(12, '\0')
                animate_uv = node.animateuv
                uv_dir_x = node.uvdirectionx
                uv_dir_y = node.uvdirectiony
                uv_jitter = node.uvjitter
                uv_jitter_speed = node.uvjitterspeed

                mdx_data_size = 0
                mdx_data_bitmap = 0
                off_mdx_verts = 0xffffffff
                off_mdx_normals = 0xffffffff
                off_mdx_colors = 0xffffffff
                off_mdx_uv1 = 0xffffffff
                off_mdx_uv2 = 0xffffffff
                off_mdx_uv3 = 0xffffffff
                off_mdx_uv4 = 0xffffffff
                off_mdx_tan_space1 = 0xffffffff
                off_mdx_tan_space2 = 0xffffffff
                off_mdx_tan_space3 = 0xffffffff
                off_mdx_tan_space4 = 0xffffffff
                if not type_flags & NODE_SABER:
                    mdx_data_size += 4 * (3 + 3)
                    mdx_data_bitmap = MDX_FLAG_VERTEX | MDX_FLAG_NORMAL
                    off_mdx_verts = 0
                    off_mdx_normals = 4 * 3
                    if node.uv1:
                        mdx_data_bitmap |= MDX_FLAG_UV1
                        off_mdx_uv1 = mdx_data_size
                        mdx_data_size += 4 * 2
                    if node.uv2:
                        mdx_data_bitmap |= MDX_FLAG_UV2
                        off_mdx_uv2 = mdx_data_size
                        mdx_data_size += 4 * 2
                    if node.tangentspace:
                        mdx_data_bitmap |= MDX_FLAG_TANGENT1
                        off_mdx_tan_space1 = mdx_data_size
                        mdx_data_size += 4 * 9
                    if type_flags & NODE_SKIN:
                        mdx_data_size += 4 * 8  # bone weights + bone indices

                if type_flags & NODE_SABER:
                    saber_vert_indices = []
                    for i in range(8):
                        saber_vert_indices.append(i)
                    for i in range(20):
                        for j in range(4):
                            saber_vert_indices.append(j)
                    for i in range(8, 16):
                        saber_vert_indices.append(i)
                    for i in range(20):
                        for j in range(8, 12):
                            saber_vert_indices.append(j)
                    num_verts = NUM_SABER_VERTS
                else:
                    num_verts = len(node.verts)

                num_faces = len(node.facelist.vertices)

                num_textures = 0
                if node.uv1:
                    num_textures += 1
                if node.uv2:
                    num_textures += 1

                has_lightmap = node.lightmapped
                rotate_texture = node.rotatetexture
                background_geometry = node.background_geometry
                shadow = node.shadow
                beaming = node.beaming
                render = node.render
                dirt_enabled = node.dirt_enabled
                dirt_texture = node.dirt_texture
                dirt_coord_space = node.dirt_worldspace
                hide_in_holograms = node.hologram_donotdraw
                total_area = self.mesh_total_areas[node_idx]
                mdx_offset = self.mdx_offsets[node_idx]
                off_vert_array = self.verts_offsets[node_idx]

                self.mdl.put_uint32(fn_ptr1)
                self.mdl.put_uint32(fn_ptr2)
                self.put_array_def(self.faces_offsets[node_idx], num_faces)  # faces
                for val in bounding_box:
                    self.mdl.put_float(val)
                self.mdl.put_float(radius)
                for val in average:
                    self.mdl.put_float(val)
                for val in diffuse:
                    self.mdl.put_float(val)
                for val in ambient:
                    self.mdl.put_float(val)
                self.mdl.put_uint32(transparency_hint)
                self.mdl.put_string(bitmap)
                self.mdl.put_string(bitmap2)
                self.mdl.put_string(bitmap3)
                self.mdl.put_string(bitmap4)

                if type_flags & NODE_SABER:
                    self.put_array_def(self.index_count_offsets[node_idx], 0)  # indices count
                    self.put_array_def(self.index_offset_offsets[node_idx], 0)  # indices offset
                    self.put_array_def(self.inv_count_offsets[node_idx], 0)  # inverted counter
                else:
                    self.put_array_def(self.index_count_offsets[node_idx], 1)  # indices count
                    self.put_array_def(self.index_offset_offsets[node_idx], 1)  # indices offset
                    self.put_array_def(self.inv_count_offsets[node_idx], 1)  # inverted counter

                self.mdl.put_uint32(0xffffffff)  # unknown
                self.mdl.put_uint32(0xffffffff)  # unknown
                self.mdl.put_uint32(0)  # unknown
                self.mdl.put_uint8(3)  # saber unknown
                for _ in range(7):
                    self.mdl.put_uint8(0)  # saber unknown
                self.mdl.put_uint32(animate_uv)
                self.mdl.put_float(uv_dir_x)
                self.mdl.put_float(uv_dir_y)
                self.mdl.put_float(uv_jitter)
                self.mdl.put_float(uv_jitter_speed)
                self.mdl.put_uint32(mdx_data_size)
                self.mdl.put_uint32(mdx_data_bitmap)
                self.mdl.put_uint32(off_mdx_verts)
                self.mdl.put_uint32(off_mdx_normals)
                self.mdl.put_uint32(off_mdx_colors)
                self.mdl.put_uint32(off_mdx_uv1)
                self.mdl.put_uint32(off_mdx_uv2)
                self.mdl.put_uint32(off_mdx_uv3)
                self.mdl.put_uint32(off_mdx_uv4)
                self.mdl.put_uint32(off_mdx_tan_space1)
                self.mdl.put_uint32(off_mdx_tan_space2)
                self.mdl.put_uint32(off_mdx_tan_space3)
                self.mdl.put_uint32(off_mdx_tan_space4)
                self.mdl.put_uint16(num_verts)
                self.mdl.put_uint16(num_textures)
                self.mdl.put_uint8(has_lightmap)
                self.mdl.put_uint8(rotate_texture)
                self.mdl.put_uint8(background_geometry)
                self.mdl.put_uint8(shadow)
                self.mdl.put_uint8(beaming)
                self.mdl.put_uint8(render)

                if self.tsl:
                    self.mdl.put_uint8(dirt_enabled)
                    self.mdl.put_uint8(0)  # padding
                    self.mdl.put_uint16(dirt_texture)
                    self.mdl.put_uint16(dirt_coord_space)
                    self.mdl.put_uint8(hide_in_holograms)
                    self.mdl.put_uint8(0)  # padding

                self.mdl.put_uint16(0)  # padding
                self.mdl.put_float(total_area)
                self.mdl.put_uint32(0)  # padding
                self.mdl.put_uint32(mdx_offset)
                self.mdl.put_uint32(off_vert_array)

            # Skin Header

            if type_flags & NODE_SKIN:
                bone_names = set()
                for vert_weights in node.weights:
                    for bone_name, _ in vert_weights:
                        bone_names.add(bone_name)
                bone_indices = []
                for bone_name in bone_names:
                    bone_indices.append(self.node_idx_by_name[bone_name])
                bonemap = [-1] * len(self.nodes)
                for bone_idx, bone_node_idx in enumerate(bone_indices):
                    bonemap[bone_node_idx] = bone_idx

                off_mdx_bone_weights = mdx_data_size - 4 * 8
                off_mdx_bone_indices = mdx_data_size - 4 * 4
                off_bonemap = self.bonemap_offsets[node_idx]
                num_bones = len(self.nodes)

                self.put_array_def(0, 0)  # unknown
                self.mdl.put_uint32(off_mdx_bone_weights)
                self.mdl.put_uint32(off_mdx_bone_indices)
                self.mdl.put_uint32(off_bonemap)
                self.mdl.put_uint32(num_bones)
                self.put_array_def(self.qbone_offsets[node_idx], num_bones)  # QBones
                self.put_array_def(self.tbone_offsets[node_idx], num_bones)  # TBones
                self.put_array_def(self.skin_garbage_offsets[node_idx], num_bones)  # garbage
                for i in range(16):
                    if i < len(bone_indices):
                        self.mdl.put_uint16(bone_indices[i])
                    else:
                        self.mdl.put_uint16(0xffff)
                self.mdl.put_uint32(0)  # padding

            # Dangly Header

            if type_flags & NODE_DANGLY:
                displacement = node.displacement
                tightness = node.tightness
                period = node.period
                off_vert_data = self.dangly_verts_offsets[node_idx]

                self.put_array_def(self.constraints_offsets[node_idx], len(node.constraints))
                self.mdl.put_float(displacement)
                self.mdl.put_float(tightness)
                self.mdl.put_float(period)
                self.mdl.put_uint32(off_vert_data)

            # AABB Header

            if type_flags & NODE_AABB:
                self.mdl.put_uint32(self.aabb_offsets[node_idx][0])

            # Saber Header

            if type_flags & NODE_SABER:
                saber_inv_count1 = self.get_inverted_counter(num_meshes + 1)
                saber_inv_count2 = self.get_inverted_counter(num_meshes + 2)
                num_meshes += 2

                self.mdl.put_uint32(self.saber_verts_offsets[node_idx])
                self.mdl.put_uint32(self.saber_uv_offsets[node_idx])
                self.mdl.put_uint32(self.saber_normals_offsets[node_idx])
                self.mdl.put_uint32(saber_inv_count1)
                self.mdl.put_uint32(saber_inv_count2)

            # Mesh Data

            if type_flags & NODE_MESH:
                # Face Adjacencies
                face_adjacencies = []
                for face_idx in range(num_faces):
                    face_adjacencies.append([-1, -1, -1])
                for face_idx, face in enumerate(node.facelist.vertices):
                    edges = [tuple(sorted(edge)) for edge in [(face[0], face[1]),
                                                              (face[1], face[2]),
                                                              (face[2], face[0])]]
                    for other_face_idx in range(face_idx + 1, num_faces):
                        other_face = node.facelist.vertices[other_face_idx]
                        other_edges = [tuple(sorted(edge)) for edge in [(other_face[0], other_face[1]),
                                                                        (other_face[1], other_face[2]),
                                                                        (other_face[2], other_face[0])]]
                        num_adj_faces = 0
                        for i in range(3):
                            if face_adjacencies[face_idx][i] != -1:
                                num_adj_faces += 1
                                continue
                            for j in range(3):
                                if edges[i] == other_edges[j]:
                                    face_adjacencies[face_idx][i] = other_face_idx
                                    face_adjacencies[other_face_idx][j] = face_idx
                                    num_adj_faces += 1
                                    break
                        if num_adj_faces == 3:
                            break

                # Faces
                for face_idx, face in enumerate(node.facelist.vertices):
                    vert1 = Vector(node.verts[face[0]])
                    normal = Vector(node.facelist.normals[face_idx])
                    distance = -1.0 * (normal @ vert1)
                    material_id = node.facelist.materials[face_idx]

                    for val in normal:
                        self.mdl.put_float(val)
                    self.mdl.put_float(distance)
                    self.mdl.put_uint32(material_id)
                    for val in face_adjacencies[face_idx]:
                        self.mdl.put_int16(val)
                    for val in face:
                        self.mdl.put_uint16(val)

                # Vertex Indices Offset
                if not type_flags & NODE_SABER:
                    self.mdl.put_uint32(self.indices_offsets[node_idx])

                # Vertices
                if type_flags & NODE_SABER:
                    for vert_idx in saber_vert_indices:
                        for val in node.verts[vert_idx]:
                            self.mdl.put_float(val)
                else:
                    for vert in node.verts:
                        for val in vert:
                            self.mdl.put_float(val)

                # Vertex Indices Count, Inverted Mesh Counter, Vertex Indices
                if not type_flags & NODE_SABER:
                    num_meshes += 1
                    mesh_inv_count = self.get_inverted_counter(num_meshes)

                    self.mdl.put_uint32(3 * len(node.facelist.vertices))  # vertex index count
                    self.mdl.put_uint32(mesh_inv_count)  # inverted mesh counter

                    # Vertex Indices
                    for face in node.facelist.vertices:
                        for val in face:
                            self.mdl.put_uint16(val)

                # MDX data
                if not type_flags & NODE_SABER:
                    for vert_idx, vert in enumerate(node.verts):
                        for val in vert:
                            self.mdx.put_float(val)
                        for val in node.normals[vert_idx]:
                            self.mdx.put_float(val)
                        if node.uv1:
                            for val in node.uv1[vert_idx]:
                                self.mdx.put_float(val)
                        if node.uv2:
                            for val in node.uv2[vert_idx]:
                                self.mdx.put_float(val)
                        if node.tangentspace:
                            for i in range(3):
                                self.mdx.put_float(node.tangents[vert_idx][i])
                                self.mdx.put_float(node.bitangents[vert_idx][i])
                                self.mdx.put_float(node.tangentspacenormals[vert_idx][i])
                        if type_flags & NODE_SKIN:
                            vert_weights = node.weights[vert_idx]
                            bone_weights = []
                            for bone_name, weight in vert_weights:
                                bone_node_idx = self.node_idx_by_name[bone_name]
                                bone_idx = bonemap[bone_node_idx]
                                bone_weights.append((bone_idx, weight))
                            for i in range(4):
                                if i < len(bone_weights):
                                    self.mdx.put_float(bone_weights[i][1])
                                else:
                                    self.mdx.put_float(0.0)
                            for i in range(4):
                                if i < len(bone_weights):
                                    self.mdx.put_float(float(bone_weights[i][0]))
                                else:
                                    self.mdx.put_float(-1.0)
                    # Extra MDX data
                    for _ in range(3):
                        self.mdx.put_float(1000000.0)
                    for _ in range(3):
                        self.mdx.put_float(0.0)
                    if node.uv1:
                        for _ in range(2):
                            self.mdx.put_float(0.0)
                    if node.uv2:
                        for _ in range(2):
                            self.mdx.put_float(0.0)
                    if node.tangentspace:
                        for _ in range(9):
                            self.mdx.put_float(0.0)
                    if type_flags & NODE_SKIN:
                        self.mdx.put_float(1.0)
                        for _ in range(7):
                            self.mdx.put_float(0.0)

            # Skin Data

            if type_flags & NODE_SKIN:
                # Bonemap
                for bone_idx in bonemap:
                    self.mdl.put_float(float(bone_idx))

                num_bones = len(bonemap)

                # QBones, TBones
                qbones = [None] * num_bones
                tbones = [None] * num_bones
                for i in range(num_bones):
                    bone_trans = self.nodes[i].from_root.inverted() @ node.from_root
                    tbones[i], qbones[i], _ = bone_trans.decompose()
                for i in range(num_bones):
                    qbone = qbones[i]
                    self.mdl.put_float(qbone.w)
                    self.mdl.put_float(qbone.x)
                    self.mdl.put_float(qbone.y)
                    self.mdl.put_float(qbone.z)
                for i in range(num_bones):
                    tbone = tbones[i]
                    self.mdl.put_float(tbone.x)
                    self.mdl.put_float(tbone.y)
                    self.mdl.put_float(tbone.z)

                # Garbage
                for _ in range(num_bones):
                    self.mdl.put_uint32(0)

            # Dangly Data

            if type_flags & NODE_DANGLY:
                for val in node.constraints:
                    self.mdl.put_float(val)
                for vert in node.verts:
                    for val in vert:
                        self.mdl.put_float(val)

            # AABB Data

            if type_flags & NODE_AABB:
                for aabb in self.aabbs[node_idx]:
                    child_idx1 = aabb[6]
                    child_idx2 = aabb[7]
                    face_idx = aabb[8]
                    split_axis = aabb[9]

                    if face_idx == -1:
                        off_child1 = self.aabb_offsets[node_idx][child_idx1]
                        off_child2 = self.aabb_offsets[node_idx][child_idx2]
                    else:
                        off_child1 = 0
                        off_child2 = 0

                    switch = {
                        -3: AABB_NEGATIVE_Z,
                        -2: AABB_NEGATIVE_Y,
                        -1: AABB_NEGATIVE_X,
                        0: AABB_NO_CHILDREN,
                        1: AABB_POSITIVE_X,
                        2: AABB_POSITIVE_Y,
                        3: AABB_POSITIVE_Z
                    }
                    most_significant_plane = switch[split_axis]

                    # Bounding Box
                    for val in aabb[: 6]:
                        self.mdl.put_float(val)

                    self.mdl.put_uint32(off_child1)
                    self.mdl.put_uint32(off_child2)
                    self.mdl.put_int32(face_idx)
                    self.mdl.put_uint32(most_significant_plane)

            # Saber Data

            if type_flags & NODE_SABER:
                for vert_idx in saber_vert_indices:
                    for val in node.verts[vert_idx]:
                        self.mdl.put_float(val)
                for vert_idx in saber_vert_indices:
                    for val in node.uv1[vert_idx]:
                        self.mdl.put_float(val)
                for vert_idx in saber_vert_indices:
                    for val in node.normals[vert_idx]:
                        self.mdl.put_float(val)

            # Children

            for child_idx in child_indices:
                self.mdl.put_uint32(self.node_offsets[child_idx])

            # Controllers

            for key in self.controller_keys[node_idx]:
                unk1 = 0xffff

                self.mdl.put_uint32(key.ctrl_type)
                self.mdl.put_uint16(unk1)
                self.mdl.put_uint16(key.num_rows)
                self.mdl.put_uint16(key.timekeys_start)
                self.mdl.put_uint16(key.values_start)
                self.mdl.put_uint8(key.num_columns)

                for _ in range(3):
                    self.mdl.put_uint8(0)  # padding

            # Controller Data

            for val in self.controller_data[node_idx]:
                self.mdl.put_float(val)

    def get_node_flags(self, node):
        switch = {
            Nodetype.DUMMY: NODE_BASE,
            Nodetype.REFERENCE: NODE_BASE | NODE_REFERENCE,
            Nodetype.TRIMESH: NODE_BASE | NODE_MESH,
            Nodetype.DANGLYMESH: NODE_BASE | NODE_MESH | NODE_DANGLY,
            Nodetype.SKIN: NODE_BASE | NODE_MESH | NODE_SKIN,
            Nodetype.EMITTER: NODE_BASE | NODE_EMITTER,
            Nodetype.LIGHT: NODE_BASE | NODE_LIGHT,
            Nodetype.AABB: NODE_BASE | NODE_MESH | NODE_AABB,
            Nodetype.LIGHTSABER: NODE_BASE | NODE_MESH | NODE_SABER
        }
        return switch[node.nodetype]

    def get_mesh_fn_ptr(self, type_flags):
        if type_flags & NODE_SKIN:
            if self.tsl:
                fn_ptr1 = SKIN_FN_PTR_1_K2_PC
                fn_ptr2 = SKIN_FN_PTR_2_K2_PC
            else:
                fn_ptr1 = SKIN_FN_PTR_1_K1_PC
                fn_ptr2 = SKIN_FN_PTR_2_K1_PC
        elif type_flags & NODE_DANGLY:
            if self.tsl:
                fn_ptr1 = DANGLY_FN_PTR_1_K2_PC
                fn_ptr2 = DANGLY_FN_PTR_2_K2_PC
            else:
                fn_ptr1 = DANGLY_FN_PTR_1_K1_PC
                fn_ptr2 = DANGLY_FN_PTR_2_K1_PC
        else:
            if self.tsl:
                fn_ptr1 = MESH_FN_PTR_1_K2_PC
                fn_ptr2 = MESH_FN_PTR_2_K2_PC
            else:
                fn_ptr1 = MESH_FN_PTR_1_K1_PC
                fn_ptr2 = MESH_FN_PTR_2_K1_PC

        return (fn_ptr1, fn_ptr2)

    def calculate_face_area(self, edge1, edge2, edge3):
        a = edge1.length
        b = edge2.length
        c = edge3.length
        s = (a + b + c) / 2.0
        if a <= 0.0 or b <= 0.0 or c <= 0.0:
            return -1.0
        if a > b + c or b > a + c or c > a + b:
            return -1.0
        area2 = s * (s - a) * (s - b) * (s - c)
        return sqrt(area2)

    def generate_aabb_tree(self, node):
        face_list = []
        face_idx = 0

        for face in node.facelist.vertices:
            v0 = Vector(node.verts[face[0]])
            v1 = Vector(node.verts[face[1]])
            v2 = Vector(node.verts[face[2]])
            centroid = (v0 + v1 + v2) / 3
            face_list.append((face_idx, [v0, v1, v2], centroid))
            face_idx += 1

        aabbs = []
        aabb.generate_tree(aabbs, face_list)

        return aabbs

    def get_inverted_counter(self, count):
        quo = count // 100
        mod = count % 100
        return int(pow(2, quo) * 100 - count + (100 * quo if mod else 0) + (0 if quo else -1))

    def put_array_def(self, offset, count):
        self.mdl.put_uint32(offset)
        self.mdl.put_uint32(count)
        self.mdl.put_uint32(count)
