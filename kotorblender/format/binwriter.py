import struct

class BinaryWriter:

    def __init__(self, path, byteorder):
        self.file = open(path, "wb")
        self.byteorder = byteorder

    def __del__(self):
        self.file.close()

    def tell(self):
        return self.tell()

    def put_int8(self, val):
        self.file.write(val.to_bytes(1, byteorder=self.byteorder, signed=True))

    def put_int16(self, val):
        self.file.write(val.to_bytes(2, byteorder=self.byteorder, signed=True))

    def put_int32(self, val):
        self.file.write(val.to_bytes(4, byteorder=self.byteorder, signed=True))

    def put_uint8(self, val):
        self.file.write(val.to_bytes(1, byteorder=self.byteorder, signed=False))

    def put_uint16(self, val):
        self.file.write(val.to_bytes(2, byteorder=self.byteorder, signed=False))

    def put_uint32(self, val):
        self.file.write(val.to_bytes(4, byteorder=self.byteorder, signed=False))

    def put_float(self, val):
        bo_literal = '>' if self.byteorder == 'big' else '<'
        self.file.write(struct.pack(bo_literal + "f", val))

    def put_string(self, val):
        self.file.write(val.encode("utf-8"))

    def put_c_string(self, val):
        self.file.write((val + '\0').encode("utf-8"))

    def put_bytes(self, bytes):
        self.file.write(bytes)