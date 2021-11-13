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

from .. import utils

from .model import Model
from .modelnode.dummy import DummyNode


class Walkmesh(Model):

    def __init__(self, walkmesh_type):
        Model.__init__(self)
        self.walkmesh_type = walkmesh_type

    def import_to_collection(self, parent_obj, collection):
        if type(self.root_node) != DummyNode or self.root_node.parent:
            raise RuntimeError("Root node has to be a dummy without a parent")

        self.import_nodes_to_collection(self.root_node, parent_obj, collection)

    @classmethod
    def from_aabb_node(cls, aabb):
        root_node = DummyNode("wok")
        root_node.children.append(aabb)

        walkmesh = Walkmesh("wok")
        walkmesh.root_node = root_node

        return walkmesh

    @classmethod
    def from_root_object(cls, obj):
        if utils.is_pwk_root(obj):
            walkmesh_type = "pwk"
        elif utils.is_dwk_root(obj):
            walkmesh_type = "dwk"
        else:
            raise ValueError("Cannot create walkmesh from root object '{}'".format(obj.name))

        walkmesh = Walkmesh(walkmesh_type)
        walkmesh.root_node = cls.model_node_from_object(obj, exclude_xwk=False)

        return walkmesh
