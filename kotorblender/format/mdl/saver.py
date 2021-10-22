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