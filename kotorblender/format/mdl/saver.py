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

from ..binwriter import BinaryWriter

from .types import *


class MdlSaver:
    def __init__(self, path, model, tsl):
        self.mdl = BinaryWriter(path, 'little')

        basepath, _ = os.path.splitext(path)
        mdx_path = basepath + ".mdx"
        self.mdx = BinaryWriter(mdx_path, 'little')

        self.model = model
        self.tsl = tsl

        self.mdl_pos = 0
        self.mdx_pos = 0
        self.mdl_size = 0
        self.mdx_size = 0
        self.off_name_offsets = 0

        self.nodes = []
        self.name_offsets = []
        self.node_offsets = []
        self.children_offsets = []

        self.parent_indices = []
        self.child_indices = []

        self.controller_keys = []
        self.controller_data = []
        self.controller_offsets = []
        self.controller_counts = []
        self.controller_data_offsets = []
        self.controller_data_counts = []

    def save(self):
        self.peek_model()

        self.save_file_header()
        self.save_geometry_header()
        self.save_model_header()
        self.save_names()
        self.save_nodes()

    def peek_model(self):
        self.mdl_pos = 80 + 116  # geometry header + model header
        self.off_name_offsets = self.mdl_pos

        self.peek_nodes(self.model.root_node)

        self.mdl_pos += 4 * len(self.nodes)  # name offsets

        self.peek_node_names()
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

    def peek_node_names(self):
        for node in self.nodes:
            self.name_offsets.append(self.mdl_pos)
            self.mdl_pos += len(node.name) + 1

    def peek_node_data(self):
        for node in self.nodes:
            self.node_offsets.append(self.mdl_pos)
            self.mdl_pos += 80  # geometry header

            ctrl_keys = []
            ctrl_data = []
            self.peek_controllers(node, ctrl_keys, ctrl_data)
            ctrl_count = len(ctrl_keys)
            ctrl_data_count = len(ctrl_data)
            self.controller_keys.append(ctrl_keys)
            self.controller_data.append(ctrl_data)
            self.controller_counts.append(ctrl_count)
            self.controller_data_counts.append(ctrl_data_count)

            self.controller_offsets.append(self.mdl_pos)
            self.mdl_pos += 16 * ctrl_count

            self.controller_data_offsets.append(self.mdl_pos)
            self.mdl_pos += 4 * ctrl_data_count

            self.children_offsets.append(self.mdl_pos)
            self.mdl_pos += 4 * len(node.children)

    def peek_controllers(self, node, out_keys, out_data):
        if node.parent:
            return
        out_keys.append(ControllerKey(CTRL_BASE_POSITION, 1, 0, 1, 3))
        out_data.append(0.0)  # timekey
        for val in node.position:
            out_data.append(val)
        out_keys.append(ControllerKey(CTRL_BASE_ORIENTATION, 1, 4, 5, 4))
        out_data.append(0.0)  # timekey
        for val in node.orientation:
            out_data.append(val)

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
        model_type = 2

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
        affected_by_fog = 0 if self.model.ignorefog else 1
        num_child_models = 0
        supermodel_ref = 0
        bounding_box = [-5.0, -5.0, -1.0, 5.0, 5.0, 10.0]
        radius = 7.0  # TODO
        scale = self.model.animscale
        supermodel_name = self.model.supermodel.ljust(32, '\0')
        off_head_root_node = self.node_offsets[0]
        mdx_size = self.mdx_size
        mdx_offset = 0

        self.mdl.put_uint8(classification)
        self.mdl.put_uint8(subclassification)
        self.mdl.put_uint8(0)  # unknown
        self.mdl.put_uint8(affected_by_fog)
        self.mdl.put_uint32(num_child_models)
        self.put_array_def(0, 0)  # animation array
        self.mdl.put_uint32(supermodel_ref)
        for val in bounding_box:
            self.mdl.put_float(val)
        self.mdl.put_float(radius)
        self.mdl.put_float(scale)
        self.mdl.put_string(supermodel_name)
        self.mdl.put_uint32(off_head_root_node)
        self.mdl.put_uint32(0)  # unknown
        self.mdl.put_uint32(mdx_size)
        self.mdl.put_uint32(mdx_offset)
        self.put_array_def(self.off_name_offsets, len(self.nodes))  # name offsets

    def save_names(self):
        for offset in self.name_offsets:
            self.mdl.put_uint32(offset)
        for node in self.nodes:
            self.mdl.put_c_string(node.name)

    def save_nodes(self):
        for node_idx, node in enumerate(self.nodes):
            print("Persisting {} {}".format(node_idx, vars(node)))

            type_flags = NODE_BASE  # TODO
            supernode_number = node_idx
            name_index = node_idx
            off_root = 0
            parent_idx = self.parent_indices[node_idx]
            off_parent = self.node_offsets[parent_idx] if parent_idx else 0
            position = node.position
            orientation = node.orientation
            child_indices = self.child_indices[node_idx]

            self.mdl.put_uint16(type_flags)
            self.mdl.put_uint16(supernode_number)
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

            # TODO: support all node types

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

            for val in self.controller_data[node_idx]:
                self.mdl.put_float(val)

            for child_idx in child_indices:
                self.mdl.put_uint32(self.node_offsets[child_idx])

    def put_array_def(self, offset, count):
        self.mdl.put_uint32(offset)
        self.mdl.put_uint32(count)
        self.mdl.put_uint32(count)
