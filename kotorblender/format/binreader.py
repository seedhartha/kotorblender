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

import struct

class BinaryReader:

    def __init__(self, path, byteorder):
        self.file = open(path, "rb")
        self.byteorder = byteorder

    def __del__(self):
        self.file.close()

    def seek(self, offset):
        self.file.seek(offset)

    def skip(self, offset):
        self.file.seek(offset, 1)

    def tell(self):
        return self.tell()

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
        bo_literal = '>' if self.byteorder == 'big' else '<'
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

    def get_c_string_up_to(self, max_len):
        str = ""
        len = max_len
        while len > 0:
            ch = self.file.read(1).decode("utf-8")
            len -= 1
            if ch == '\0':
                break
            str += ch
        if len > 0:
            self.file.seek(len, 1)
        return str

    def get_bytes(self, count):
        return self.file.read(count)
