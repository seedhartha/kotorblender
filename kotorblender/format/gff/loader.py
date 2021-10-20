from struct import pack, unpack

from ...exception.malformedgff import MalformedGffFile
from ...expando import Expando

from ..binreader import BinaryReader

FILE_VERSION = "V3.2"

FIELD_TYPE_DWORD = 4
FIELD_TYPE_FLOAT = 8
FIELD_TYPE_STRUCT = 14
FIELD_TYPE_LIST = 15

class GffLoader:

    def __init__(self, path, fileType):
        self.reader = BinaryReader(path, 'little')
        self.fileType = fileType.ljust(4)

    def load(self):
        fileType = self.reader.get_string(4)
        fileVersion = self.reader.get_string(4)

        if fileType != self.fileType:
            raise MalformedGffFile("GFF file type is invalid: expected={}, actual={}".format(self.fileType, fileType))
        if fileVersion != FILE_VERSION:
            raise MalformedGffFile("GFF file version is invalid: expected={}, actual={}".format(FILE_VERSION, fileVersion))

        self.offStructs = self.reader.get_uint32()
        self.numStructs = self.reader.get_uint32()
        self.offFields = self.reader.get_uint32()
        self.numFields = self.reader.get_uint32()
        self.offLabels = self.reader.get_uint32()
        self.numLabels = self.reader.get_uint32()
        self.offFieldData = self.reader.get_uint32()
        self.numFieldData = self.reader.get_uint32()
        self.offFieldIndices = self.reader.get_uint32()
        self.numFieldIndices = self.reader.get_uint32()
        self.offListIndices = self.reader.get_uint32()
        self.numListIndices = self.reader.get_uint32()

        self.load_structs()
        self.load_fields()
        self.load_labels()
        self.load_field_indices()
        self.load_list_indices()

        return self.new_tree_struct(0)

    def load_structs(self):
        self.structs = []
        self.reader.seek(self.offStructs)
        for _ in range(0, self.numStructs):
            struct = Expando()
            struct.type = self.reader.get_uint32()
            struct.dataOrDataOffset = self.reader.get_uint32()
            struct.numFields = self.reader.get_uint32()
            self.structs.append(struct)

    def load_fields(self):
        self.fields = []
        self.reader.seek(self.offFields)
        for _ in range(0, self.numFields):
            field = Expando()
            field.type = self.reader.get_uint32()
            field.labelIdx = self.reader.get_uint32()
            field.dataOrDataOffset = self.reader.get_uint32()
            self.fields.append(field)

    def load_labels(self):
        self.reader.seek(self.offLabels)
        self.labels = [self.reader.get_string(16).rstrip('\0') for _ in range(0, self.numLabels)]

    def load_field_data(self):
        self.reader.seek(self.offFieldData)
        self.fieldData = self.reader.get_bytes(self.numFieldData)

    def load_field_indices(self):
        self.reader.seek(self.offFieldIndices)
        self.fieldIndices = [self.reader.get_uint32() for _ in range(0, self.numFieldIndices // 4)]

    def load_list_indices(self):
        self.reader.seek(self.offListIndices)
        self.listIndices = [self.reader.get_uint32() for _ in range(0, self.numListIndices // 4)]

    def new_tree_struct(self, structIdx):
        tree = dict()
        struct = self.structs[structIdx]
        nodes = []
        if struct.numFields == 1:
            nodes.append(self.new_tree_field(struct.dataOrDataOffset))
        else:
            start = struct.dataOrDataOffset // 4
            stop = start + struct.numFields
            for index in self.fieldIndices[start:stop]:
                nodes.append(self.new_tree_field(index))
        for node in nodes:
            tree[node.key] = node.value
        return tree

    def new_tree_field(self, fieldIdx):
        field = self.fields[fieldIdx]
        label = self.labels[field.labelIdx]

        if field.type == FIELD_TYPE_DWORD:
            data = field.dataOrDataOffset
        elif field.type == FIELD_TYPE_FLOAT:
            data = self.repack_int_to_float(field.dataOrDataOffset)
        elif field.type == FIELD_TYPE_STRUCT:
            data = self.new_tree_struct(field.dataOrDataOffset)
        elif field.type == FIELD_TYPE_LIST:
            size = self.listIndices[field.dataOrDataOffset // 4]
            start = field.dataOrDataOffset // 4 + 1
            stop = start + size
            indices = self.listIndices[start:stop]
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