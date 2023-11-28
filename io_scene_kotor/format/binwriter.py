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
