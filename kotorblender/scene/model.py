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

import bpy

from ..exception.malformedfile import MalformedFile

from .. import defines, glob

from .modelnode.dummy import DummyNode

from . import armature


class Model:

    def __init__(self):
        self.name = "UNNAMED"
        self.supermodel = defines.null
        self.animscale = 1.0
        self.classification = defines.Classification.UNKNOWN
        self.subclassification = 0
        self.ignorefog = False
        self.compress_quats = False
        self.headlink = False

        self.root_node = None
        self.animations = []

    def import_to_collection(self, collection, position=(0.0, 0.0, 0.0)):
        if type(self.root_node) != DummyNode or self.root_node.parent:
            raise MalformedFile("Root node has to be a dummy without a parent")

        root_obj = self.root_node.add_to_collection(collection)
        root_obj.location = position
        root_obj.kb.dummytype = defines.Dummytype.MDLROOT
        root_obj.kb.supermodel = self.supermodel
        root_obj.kb.classification = self.classification
        root_obj.kb.subclassification = self.subclassification
        root_obj.kb.ignorefog = (self.ignorefog >= 1)
        root_obj.kb.compress_quats = (self.compress_quats >= 1)
        root_obj.kb.headlink = (self.headlink >= 1)
        root_obj.kb.animscale = self.animscale

        for child in self.root_node.children:
            self.import_nodes_to_collection(child, root_obj, collection)

        if glob.import_armatures:
            armature_object = armature.recreate_armature(root_obj)
        else:
            armature_object = None

        if glob.import_animations:
            self.create_animations(root_obj, armature_object)

        return root_obj

    def import_nodes_to_collection(self, node, parent_obj, collection):
        obj = node.add_to_collection(collection)
        obj.parent = parent_obj
        obj.matrix_parent_inverse = parent_obj.matrix_world.inverted()

        for child in node.children:
            self.import_nodes_to_collection(child, obj, collection)

    def create_animations(self, mdl_root, armature_object):
        # Load the 'default' animation first, so it is at the front
        anims = [a for a in self.animations if a.name == "default"]
        for a in anims:
            a.add_to_objects(mdl_root)
        # Load the rest of the anims
        anims = [a for a in self.animations if a.name != "default"]
        for a in anims:
            a.add_to_objects(mdl_root)
        if armature_object:
            armature.create_armature_animations(mdl_root, armature_object)

    def find_node(self, test):
        if test(self.root_node):
            return self.root_node
        return self.root_node.find_child(test)

    @classmethod
    def from_mdl_root(cls, root_obj):
        model = Model()
        model.name = root_obj.name
        model.supermodel = root_obj.kb.supermodel
        model.classification = root_obj.kb.classification
        model.subclassification = root_obj.kb.subclassification
        model.ignorefog = not root_obj.kb.ignorefog
        model.compress_quats = root_obj.kb.compress_quats
        model.headlink = root_obj.kb.headlink
        model.animscale = root_obj.kb.animscale

        return model
