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

import re

from ..defines import Dummytype, Meshtype, Nodetype
from ..exception.malformedfile import MalformedFile

from .. import defines, glob

from .animation import Animation
from .modelnode.aabb import AabbNode
from .modelnode.danglymesh import DanglymeshNode
from .modelnode.dummy import DummyNode
from .modelnode.emitter import EmitterNode
from .modelnode.light import LightNode
from .modelnode.lightsaber import LightsaberNode
from .modelnode.reference import ReferenceNode
from .modelnode.skinmesh import SkinmeshNode
from .modelnode.trimesh import TrimeshNode

from . import armature


class Model:

    def __init__(self):
        self.name = "UNNAMED"
        self.supermodel = defines.NULL
        self.animscale = 1.0
        self.classification = defines.Classification.UNKNOWN
        self.subclassification = 0
        self.ignorefog = False

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
        for anim in self.animations:
            anim.add_to_objects(mdl_root)

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
        model.ignorefog = root_obj.kb.ignorefog
        model.animscale = root_obj.kb.animscale

        model.root_node = Model.model_node_from_object(root_obj)
        model.animations = [Animation.from_list_anim(anim, root_obj) for anim in root_obj.kb.anim_list]

        return model

    @classmethod
    def model_node_from_object(cls, obj, parent=None):
        if obj.type == 'EMPTY':
            if obj.kb.dummytype == Dummytype.REFERENCE:
                node_type = Nodetype.REFERENCE
            else:
                node_type = Nodetype.DUMMY
        elif obj.type == 'MESH':
            if obj.kb.meshtype == Meshtype.EMITTER:
                node_type = Nodetype.EMITTER
            elif obj.kb.meshtype == Meshtype.AABB:
                node_type = Nodetype.AABB
            elif obj.kb.meshtype == Meshtype.SKIN:
                node_type = Nodetype.SKIN
            elif obj.kb.meshtype == Meshtype.LIGHTSABER:
                node_type = Nodetype.LIGHT
            elif obj.kb.meshtype == Meshtype.DANGLYMESH:
                node_type = Nodetype.DANGLYMESH
            else:
                node_type = Nodetype.TRIMESH
        elif obj.type == 'LIGHT':
            node_type = Nodetype.LIGHT

        switch = {
            Nodetype.DUMMY: DummyNode,
            Nodetype.REFERENCE: ReferenceNode,
            Nodetype.TRIMESH: TrimeshNode,
            Nodetype.DANGLYMESH: DanglymeshNode,
            Nodetype.SKIN: SkinmeshNode,
            Nodetype.EMITTER: EmitterNode,
            Nodetype.LIGHT: LightNode,
            Nodetype.AABB: AabbNode,
            Nodetype.LIGHTSABER: LightsaberNode
        }

        name = obj.name
        if re.match(r".+\.\d{3}$", name):
            name = name[:-4]

        node = switch[node_type](name)
        if parent:
            node.parent = parent
            node.from_root = parent.from_root
        node.load_object_data(obj)
        node.from_root = node.from_root @ obj.matrix_local

        for child_obj in sorted(obj.children, key=lambda o: o.kb.export_order):
            if child_obj.type == 'EMPTY' and child_obj.kb.dummytype in [Dummytype.PWKROOT, Dummytype.DWKROOT]:
                continue
            child = Model.model_node_from_object(child_obj, node)
            node.children.append(child)

        return node
