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

from ...exception.malformedgff import MalformedGff
from ...expando import Expando

from ..binreader import BinaryReader

FILE_VERSION = "V3.2"

FIELD_TYPE_DWORD = 4
FIELD_TYPE_FLOAT = 8
FIELD_TYPE_STRUCT = 14
FIELD_TYPE_LIST = 15

class GffLoader:

    def __init__(self, path, file_type):
        self.reader = BinaryReader(path, 'little')
        self.file_type = file_type.ljust(4)

    def load(self):
        file_type = self.reader.get_string(4)
        file_version = self.reader.get_string(4)

        if file_type != self.file_type:
            raise MalformedGff("GFF file type is invalid: expected={}, actual={}".format(self.file_type, file_type))
        if file_version != FILE_VERSION:
            raise MalformedGff("GFF file version is invalid: expected={}, actual={}".format(FILE_VERSION, file_version))

        self.off_structs = self.reader.get_uint32()
        self.num_structs = self.reader.get_uint32()
        self.off_fields = self.reader.get_uint32()
        self.num_fields = self.reader.get_uint32()
        self.off_labels = self.reader.get_uint32()
        self.num_labels = self.reader.get_uint32()
        self.off_field_data = self.reader.get_uint32()
        self.num_field_data = self.reader.get_uint32()
        self.off_field_indices = self.reader.get_uint32()
        self.num_field_indices = self.reader.get_uint32()
        self.off_list_indices = self.reader.get_uint32()
        self.num_list_indices = self.reader.get_uint32()

        self.load_structs()
        self.load_fields()
        self.load_labels()
        self.load_field_indices()
        self.load_list_indices()

        return self.new_tree_struct(0)

    def load_structs(self):
        self.structs = []
        self.reader.seek(self.off_structs)
        for _ in range(0, self.num_structs):
            struct = Expando()
            struct.type = self.reader.get_uint32()
            struct.data_or_data_offset = self.reader.get_uint32()
            struct.num_fields = self.reader.get_uint32()
            self.structs.append(struct)

    def load_fields(self):
        self.fields = []
        self.reader.seek(self.off_fields)
        for _ in range(0, self.num_fields):
            field = Expando()
            field.type = self.reader.get_uint32()
            field.label_idx = self.reader.get_uint32()
            field.data_or_data_offset = self.reader.get_uint32()
            self.fields.append(field)

    def load_labels(self):
        self.reader.seek(self.off_labels)
        self.labels = [self.reader.get_string(16).rstrip('\0') for _ in range(0, self.num_labels)]

    def load_field_data(self):
        self.reader.seek(self.off_field_data)
        self.field_data = self.reader.get_bytes(self.num_field_data)

    def load_field_indices(self):
        self.reader.seek(self.off_field_indices)
        self.field_indices = [self.reader.get_uint32() for _ in range(0, self.num_field_indices // 4)]

    def load_list_indices(self):
        self.reader.seek(self.off_list_indices)
        self.list_indices = [self.reader.get_uint32() for _ in range(0, self.num_list_indices // 4)]

    def new_tree_struct(self, structIdx):
        tree = dict()
        struct = self.structs[structIdx]
        nodes = []
        if struct.num_fields == 1:
            nodes.append(self.new_tree_field(struct.data_or_data_offset))
        else:
            start = struct.data_or_data_offset // 4
            stop = start + struct.num_fields
            for index in self.field_indices[start:stop]:
                nodes.append(self.new_tree_field(index))
        for node in nodes:
            tree[node.key] = node.value
        return tree

    def new_tree_field(self, field_idx):
        field = self.fields[field_idx]
        label = self.labels[field.label_idx]

        if field.type == FIELD_TYPE_DWORD:
            data = field.data_or_data_offset
        elif field.type == FIELD_TYPE_FLOAT:
            data = self.repack_int_to_float(field.data_or_data_offset)
        elif field.type == FIELD_TYPE_STRUCT:
            data = self.new_tree_struct(field.data_or_data_offset)
        elif field.type == FIELD_TYPE_LIST:
            size = self.list_indices[field.data_or_data_offset // 4]
            start = field.data_or_data_offset // 4 + 1
            stop = start + size
            indices = self.list_indices[start:stop]
            data = [self.new_tree_struct(idx) for idx in indices]
        else:
            raise NotImplementedError("Field type {} is not supported".format(field.type))

        node = Expando()
        node.key = label
        node.value = data

        return node

    def repack_int_to_float(self, val):
        packed = pack("i", val)
        return unpack("f", packed)[0]