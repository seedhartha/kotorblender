from ...exception.malformedmdl import MalformedMdlFile

from ..binreader import BinaryReader

class BinaryMdlLoader:

    def __init__(self, path):
        self.reader = BinaryReader(path, 'little')

    def load(self):
        self.load_file_header()
        self.load_geometry_header()
        self.load_model_header()

    def load_file_header(self):
        if self.reader.get_uint32() != 0:
            raise MalformedMdlFile("Invalid MDL signature")
        self._mdl_size = self.reader.get_uint32()
        self._mdx_size = self.reader.get_uint32()

    def load_geometry_header(self):
        pass

    def load_model_header(self):
        pass