from ..binwriter import BinaryWriter

class BinaryMdlSaver:

    def __init__(self, path):
        self.writer = BinaryWriter(path, 'little')

    def save(self):
        self.save_file_header()
        self.save_geometry_header()
        self.save_model_header()

    def save_file_header(self):
        self.writer.put_uint32(0) # signature
        self.writer.put_uint32(0) # MDL size
        self.writer.put_uint32(0) # MDX size

    def save_geometry_header(self):
        pass

    def save_model_header(self):
        pass