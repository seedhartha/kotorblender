class BinaryWriter:

    def __init__(self, path):
        self.file = open(path, "wb")

    def __del__(self):
        self.file.close()

    def put_int8(self, val):
        pass

    def put_int16(self, val):
        pass

    def put_int32(self, val):
        pass

    def put_uint8(self, val):
        pass

    def put_uint16(self, val):
        pass

    def put_uint32(self, val):
        pass

    def put_float(self, val):
        pass

    def put_string(self, val):
        pass

    def put_c_string(self, val):
        pass