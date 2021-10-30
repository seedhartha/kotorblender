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

from struct import pack, unpack

from ..binwriter import BinaryWriter

from .types import *


class GffSaver:

    def __init__(self, tree, path, file_type):
        self.tree = tree
        self.writer = BinaryWriter(path, 'little')
        self.file_type = file_type.ljust(4)

    def save(self):
        self.structs = []
        self.fields = []
        self.labels = []
        self.field_data = []
        self.field_indices = []
        self.list_indices = []
        self.decompose_tree()

        off_structs = 56
        num_structs = len(self.structs)
        off_fields = off_structs + 12 * num_structs
        num_fields = len(self.fields)
        off_labels = off_fields + 12 * num_fields
        num_labels = len(self.labels)
        off_field_data = off_labels + 16 * num_labels
        num_field_data = len(self.field_data)
        off_field_indices = off_field_data + num_field_data
        num_field_indices = 4 * len(self.field_indices)
        off_list_indices = off_field_indices + num_field_indices
        num_list_indices = 4 * len(self.list_indices)

        self.writer.put_string(self.file_type)
        self.writer.put_string(FILE_VERSION)
        self.writer.put_uint32(off_structs)
        self.writer.put_uint32(num_structs)
        self.writer.put_uint32(off_fields)
        self.writer.put_uint32(num_fields)
        self.writer.put_uint32(off_labels)
        self.writer.put_uint32(num_labels)
        self.writer.put_uint32(off_field_data)
        self.writer.put_uint32(num_field_data)
        self.writer.put_uint32(off_field_indices)
        self.writer.put_uint32(num_field_indices)
        self.writer.put_uint32(off_list_indices)
        self.writer.put_uint32(num_list_indices)

        for struct in self.structs:
            self.writer.put_uint32(struct.type)
            self.writer.put_uint32(struct.data_or_data_offset)
            self.writer.put_uint32(struct.num_fields)
        for field in self.fields:
            self.writer.put_uint32(field.type)
            self.writer.put_uint32(field.label_idx)
            self.writer.put_uint32(field.data_or_data_offset)
        for label in self.labels:
            self.writer.put_string(label.ljust(16, '\0'))
        if len(self.field_data) > 0:
            self.writer.put_bytes(bytearray(self.field_data))
        for idx in self.field_indices:
            self.writer.put_uint32(idx)
        for idx in self.list_indices:
            self.writer.put_uint32(idx)

    def decompose_tree(self):
        num_structs = 0
        queue = [self.tree]

        while queue:
            tree = queue.pop(0)
            field_indices = []

            for label, field_type in tree["_fields"].items():
                field_indices.append(len(self.fields))

                try:
                    label_idx = self.labels.index(label)
                except ValueError:
                    label_idx = len(self.labels)
                    self.labels.append(label)

                value = tree[label]
                if field_type == FIELD_TYPE_DWORD:
                    data_or_data_offset = value
                elif field_type == FIELD_TYPE_FLOAT:
                    data_or_data_offset = self.repack_float_to_int(value)
                elif field_type == FIELD_TYPE_STRUCT:
                    num_structs += 1
                    data_or_data_offset = num_structs
                    queue.append(value)
                elif field_type == FIELD_TYPE_LIST:
                    data_or_data_offset = 4 * len(self.list_indices)
                    self.list_indices.append(len(value))
                    for item in value:
                        num_structs += 1
                        self.list_indices.append(num_structs)
                        queue.append(item)
                else:
                    raise NotImplementedError("Field type {} is not supported".format(field_type))

                field = GffField(
                    field_type,
                    label_idx,
                    data_or_data_offset
                    )
                self.fields.append(field)

            if len(field_indices) == 1:
                data_or_data_offset = field_indices[0]
            else:
                data_or_data_offset = 4 * len(self.field_indices)
                for idx in field_indices:
                    self.field_indices.append(idx)

            struct = GffStruct(
                tree["_type"],
                data_or_data_offset,
                len(field_indices)
                )
            self.structs.append(struct)

    def repack_float_to_int(self, val):
        packed = pack("f", val)
        return unpack("i", packed)[0]
