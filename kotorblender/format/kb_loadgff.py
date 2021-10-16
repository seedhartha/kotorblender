from .kb_readbin import BinaryReader

class GffLoader:

    def __init__(self, path):
        self.reader = BinaryReader(path, 'little')

    def save():
        pass