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

import bpy

from mathutils import Vector

from ..defines import Dummytype, Meshtype, Nodetype
from ..exception.malformedfile import MalformedFile

from .. import defines, glob, utils

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


class Model:

    def __init__(self):
        self.name = "UNNAMED"
        self.supermodel = defines.NULL
        self.classification = defines.Classification.UNKNOWN
        self.subclassification = 0
        self.ignorefog = False
        self.animroot = defines.NULL
        self.animscale = 1.0

        self.root_node = None
        self.animations = []

    def import_to_collection(self, collection, position=(0.0, 0.0, 0.0)):
        if type(self.root_node) != DummyNode or self.root_node.parent:
            raise MalformedFile("Root node has to be a dummy without a parent")

        print("Importing model '{}' to collection".format(self.name))

        root_obj = self.root_node.add_to_collection(collection)
        root_obj.location = position
        root_obj.kb.dummytype = defines.Dummytype.MDLROOT
        root_obj.kb.supermodel = self.supermodel
        root_obj.kb.classification = self.classification
        root_obj.kb.subclassification = self.subclassification
        root_obj.kb.ignorefog = self.ignorefog
        root_obj.kb.animroot = self.animroot
        root_obj.kb.animscale = self.animscale

        for child in self.root_node.children:
            self.import_nodes_to_collection(child, root_obj, collection)

        if glob.import_armatures:
            armature = self.create_armature(root_obj)

        if glob.import_animations:
            self.create_animations(root_obj, armature)

        return root_obj

    def import_nodes_to_collection(self, node, parent_obj, collection):
        obj = node.add_to_collection(collection)
        obj.parent = parent_obj
        obj.matrix_parent_inverse = parent_obj.matrix_world.inverted()

        for child in node.children:
            self.import_nodes_to_collection(child, obj, collection)

    def create_armature(self, mdl_root):
        # MDL root must have at least one skinmesh
        skinmeshes = utils.get_children_recursive(mdl_root, utils.is_skin_mesh)
        if not skinmeshes:
            return None

        # Create an armature and make it active
        name = "Armature_" + mdl_root.name
        armature = bpy.data.armatures.new(name)
        armature.display_type = 'STICK'
        armature_obj = bpy.data.objects.new(name, armature)
        armature_obj.show_in_front = True
        bpy.context.collection.objects.link(armature_obj)
        bpy.context.view_layer.objects.active = armature_obj

        # Enter Edit Mode
        bpy.ops.object.mode_set(mode='EDIT')

        # Recursively create armature bones from model bones
        self.create_bones_recursive(armature, mdl_root)

        # Enter Object Mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Add Armature modifier to all bone objects
        for bone in armature.bones:
            bone_obj = bpy.context.collection.objects[bone.name]
            if utils.is_mesh_type(bone_obj, Meshtype.TRIMESH):
                group = bone_obj.vertex_groups.new(name=bone.name)
                group.add(range(len(bone_obj.data.vertices)), 1.0, 'REPLACE')
                modifier = bone_obj.modifiers.new(name="Armature", type="ARMATURE")
                modifier.object = armature_obj

        # Add Armature modifier to all skinmeshes
        for mesh in skinmeshes:
            modifier = mesh.modifiers.new(name="Armature", type="ARMATURE")
            modifier.object = armature_obj

        return armature_obj

    def create_bones_recursive(self, armature, obj, parent=None):
        bone = armature.edit_bones.new(obj.name)
        bone.parent = parent
        bone.head = [0.0] * 3
        bone.tail = Vector((0.0, 1e-3, 0.0))
        bone.matrix = obj.matrix_world

        for child in obj.children:
            if utils.is_skin_mesh(child):
                continue
            self.create_bones_recursive(armature, child, bone)

    def create_animations(self, mdl_root, armature):
        for anim in self.animations:
            anim.add_to_objects(mdl_root, armature)

    def find_node(self, test):
        return self.root_node.find_node(test)

    @classmethod
    def from_mdl_root(cls, root_obj):
        print("Constructing model from object '{}'".format(root_obj.name))

        model = Model()
        model.name = root_obj.name
        model.supermodel = root_obj.kb.supermodel
        model.classification = root_obj.kb.classification
        model.subclassification = root_obj.kb.subclassification
        model.ignorefog = root_obj.kb.ignorefog
        model.animroot = root_obj.kb.animroot
        model.animscale = root_obj.kb.animscale

        model.root_node = cls.model_node_from_object(root_obj)

        if glob.export_animations:
            model.animations = [Animation.from_list_anim(anim, root_obj) for anim in root_obj.kb.anim_list]

        return model

    @classmethod
    def model_node_from_object(cls, obj, parent=None, exclude_xwk=True):
        if exclude_xwk and (utils.is_pwk_root(obj) or utils.is_dwk_root(obj)):
            return None

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
                node_type = Nodetype.LIGHTSABER
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
            child = cls.model_node_from_object(child_obj, node, exclude_xwk)
            if child:
                node.children.append(child)

        return node
