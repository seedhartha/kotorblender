
import struct

from sys import byteorder

class BinaryReader:

    def __init__(self, path, byteorder):
        self.file = open(path, "rb")
        self.byteorder = byteorder

    def __del__(self):
        self.file.close()

    def get_int8(self):
        return int.from_bytes(self.file.read(1), self.byteorder, signed=True)

    def get_int16(self):
        return int.from_bytes(self.file.read(2), self.byteorder, signed=True)

    def get_int32(self):
        return int.from_bytes(self.file.read(4), self.byteorder, signed=True)

    def get_uint8(self):
        return int.from_bytes(self.file.read(1), self.byteorder, signed=False)

    def get_uint16(self):
        return int.from_bytes(self.file.read(2), self.byteorder, signed=False)

    def get_uint32(self):
        return int.from_bytes(self.file.read(4), self.byteorder, signed=False)

    def get_float(self):
        bo_literal = '>' if byteorder == 'big' else '<'
        [val] = struct.unpack(bo_literal + "f", self.file.read(4))
        return val

    def get_string(self, len):
        return self.file.read(len).decode("utf-8")

    def get_c_string(self):
        str = ""
        while True:
            ch = self.file.read(1).decode("utf-8")
            if ch == '\0':
                break
            str += ch
        return str