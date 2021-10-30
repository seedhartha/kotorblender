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

from ... import defines

from .geometry import GeometryNode


class ReferenceNode(GeometryNode):

    def __init__(self, name = "UNNAMED"):
        GeometryNode.__init__(self, name)
        self.nodetype = "reference"

        self.dummytype    = defines.Dummytype.REFERENCE
        self.refmodel     = defines.null
        self.reattachable = 0

    def set_object_data(self, obj):
        GeometryNode.set_object_data(self, obj)

        obj.kb.dummytype    = self.dummytype
        obj.kb.refmodel     = self.refmodel
        obj.kb.reattachable = (self.reattachable == 1)
