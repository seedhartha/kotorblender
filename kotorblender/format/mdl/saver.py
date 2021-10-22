from ..binwriter import BinaryWriter

class MdlSaver:

    def __init__(self, path):
        self.mdl = BinaryWriter(path, 'little')

    def save(self):
        self.save_file_header()
        self.save_geometry_header()
        self.save_model_header()

    def save_file_header(self):
        self.mdl.put_uint32(0) # signature
        self.mdl.put_uint32(0) # MDL size
        self.mdl.put_uint32(0) # MDX size

    def save_geometry_header(self):
        pass

    def save_model_header(self):
        pass