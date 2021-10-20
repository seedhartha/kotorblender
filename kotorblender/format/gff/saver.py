from struct import pack, unpack

from ...expando import Expando

from ..binwriter import BinaryWriter

FILE_VERSION = "V3.2"

FIELD_TYPE_DWORD = 4
FIELD_TYPE_FLOAT = 8
FIELD_TYPE_STRUCT = 14
FIELD_TYPE_LIST = 15

class GffSaver:

    def __init__(self, tree, path, fileType):
        self.tree = tree
        self.writer = BinaryWriter(path, 'little')
        self.fileType = fileType.ljust(4)

    def save(self):
        self.structs = []
        self.fields = []
        self.labels = []
        self.fieldData = []
        self.fieldIndices = []
        self.listIndices = []
        self.decompose_tree()

        offStructs = 56
        numStructs = len(self.structs)
        offFields = offStructs + 12 * numStructs
        numFields = len(self.fields)
        offLabels = offFields + 12 * numFields
        numLabels = len(self.labels)
        offFieldData = offLabels + 16 * numLabels
        numFieldData = len(self.fieldData)
        offFieldIndices = offFieldData + numFieldData
        numFieldIndices = 4 * len(self.fieldIndices)
        offListIndices = offFieldIndices + numFieldIndices
        numListIndices = 4 * len(self.listIndices)

        self.writer.put_string(self.fileType)
        self.writer.put_string(FILE_VERSION)
        self.writer.put_uint32(offStructs)
        self.writer.put_uint32(numStructs)
        self.writer.put_uint32(offFields)
        self.writer.put_uint32(numFields)
        self.writer.put_uint32(offLabels)
        self.writer.put_uint32(numLabels)
        self.writer.put_uint32(offFieldData)
        self.writer.put_uint32(numFieldData)
        self.writer.put_uint32(offFieldIndices)
        self.writer.put_uint32(numFieldIndices)
        self.writer.put_uint32(offListIndices)
        self.writer.put_uint32(numListIndices)

        for struct in self.structs:
            self.writer.put_uint32(struct.type)
            self.writer.put_uint32(struct.dataOrDataOffset)
            self.writer.put_uint32(struct.numFields)
        for field in self.fields:
            self.writer.put_uint32(field.type)
            self.writer.put_uint32(field.labelIdx)
            self.writer.put_uint32(field.dataOrDataOffset)
        for label in self.labels:
            self.writer.put_string(label.ljust(16, '\0'))
        if len(self.fieldData) > 0:
            self.writer.put_bytes(bytearray(self.fieldData))
        for idx in self.fieldIndices:
            self.writer.put_uint32(idx)
        for idx in self.listIndices:
            self.writer.put_uint32(idx)

    def decompose_tree(self):
        numStructs = 0
        queue = [self.tree]

        while queue:
            tree = queue.pop(0)
            fieldIndices = []

            for label, fieldType in tree["_fields"].items():
                fieldIndices.append(len(self.fields))

                labelIdx = len(self.labels)
                self.labels.append(label)

                value = tree[label]
                if fieldType == FIELD_TYPE_DWORD:
                    dataOrDataOffset = value
                elif fieldType == FIELD_TYPE_FLOAT:
                    dataOrDataOffset = self.repack_float_to_int(value)
                elif fieldType == FIELD_TYPE_STRUCT:
                    numStructs += 1
                    dataOrDataOffset = numStructs
                    queue.append(value)
                elif fieldType == FIELD_TYPE_LIST:
                    dataOrDataOffset = 4 * len(self.listIndices)
                    self.listIndices.append(len(value))
                    for item in value:
                        numStructs += 1
                        self.listIndices.append(numStructs)
                        queue.append(item)
                else:
                    raise NotImplementedError("Field type {} is not supported".format(fieldType))

                field = Expando()
                field.type = fieldType
                field.labelIdx = labelIdx
                field.dataOrDataOffset = dataOrDataOffset
                self.fields.append(field)

            if len(fieldIndices) == 1:
                dataOrDataOffset = fieldIndices[0]
            else:
                dataOrDataOffset = 4 * len(self.fieldIndices)
                for idx in fieldIndices:
                    self.fieldIndices.append(idx)

            struct = Expando()
            struct.type = tree["_type"]
            struct.dataOrDataOffset = dataOrDataOffset
            struct.numFields = len(fieldIndices)
            self.structs.append(struct)

    def repack_float_to_int(self, val):
        packed = pack("f", val)
        return unpack("i", packed)[0]