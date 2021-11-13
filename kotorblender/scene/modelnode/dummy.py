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

from ...defines import DummyType, NodeType

from .geometry import GeometryNode


class DummyNode(GeometryNode):

    def __init__(self, name="UNNAMED"):
        GeometryNode.__init__(self, name)

        self.nodetype = NodeType.DUMMY
        self.dummytype = DummyType.NONE

    def set_object_data(self, obj, options):
        GeometryNode.set_object_data(self, obj, options)

        obj.kb.dummytype = self.dummytype

    def load_object_data(self, obj, options):
        GeometryNode.load_object_data(self, obj, options)

        self.dummytype = obj.kb.dummytype
