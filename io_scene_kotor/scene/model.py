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

from mathutils import Matrix

from ..constants import DummyType, MeshType, NodeType, Classification, NULL
from ..utils import is_mdl_root, is_pwk_root, is_dwk_root, logger
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
        self.supermodel = NULL
        self.classification = Classification.OTHER
        self.subclassification = 0
        self.affected_by_fog = True
        self.animroot = NULL
        self.animscale = 1.0

        self.root_node = None
        self.animations = []

    def add_to_collection(self, collection, options, position=(0.0, 0.0, 0.0)):
        if type(self.root_node) != DummyNode or self.root_node.parent:
            raise RuntimeError("Root node has to be a dummy without a parent")

        logger().info(f"Adding model [{self.name}] to collection")

        if options.import_geometry:
            root_obj = self.root_node.add_to_collection(collection, options)
            root_obj.location = position
            root_obj.kb.dummytype = DummyType.MDLROOT
            root_obj.kb.supermodel = self.supermodel
            root_obj.kb.classification = self.classification
            root_obj.kb.subclassification = self.subclassification
            root_obj.kb.affected_by_fog = self.affected_by_fog
            root_obj.kb.animroot = self.animroot
            root_obj.kb.animscale = self.animscale

            for child in self.root_node.children:
                self.import_nodes_to_collection(child, root_obj, collection, options)

            animscale = (
                1.0  # animation scale must only be applied to supermodel animations
            )
        else:
            root_obj = next(
                iter(obj for obj in bpy.context.selected_objects if is_mdl_root(obj)),
                None,
            )
            if not root_obj:
                root_obj = next(
                    iter(
                        obj
                        for obj in bpy.context.collection.objects
                        if is_mdl_root(obj)
                    ),
                    None,
                )
            if not root_obj:
                return

            animscale = root_obj.kb.animscale

        if options.import_animations:
            self.create_animations(root_obj, animscale)

        if options.build_armature:
            armature_obj = armature.rebuild_armature(root_obj)
            if armature_obj:
                armature.apply_object_keyframes(root_obj, armature_obj)

        return root_obj

    def import_nodes_to_collection(self, node, parent_obj, collection, options):
        logger().debug(f"Importing node [{node.name}] to collection")

        obj = node.add_to_collection(collection, options)
        obj.parent = parent_obj

        for child in node.children:
            self.import_nodes_to_collection(child, obj, collection, options)

    def create_animations(self, mdl_root, animscale):
        for anim in self.animations:
            anim.add_to_objects(mdl_root, animscale)

    def find_node(self, test):
        return self.root_node.find_node(test)

    @classmethod
    def from_mdl_root(cls, root_obj, options):
        cls.sanitize_model(root_obj)

        model = Model()
        model.name = root_obj.name
        model.supermodel = root_obj.kb.supermodel
        model.classification = root_obj.kb.classification
        model.subclassification = root_obj.kb.subclassification
        model.affected_by_fog = root_obj.kb.affected_by_fog
        model.animroot = root_obj.kb.animroot
        model.animscale = root_obj.kb.animscale
        model.root_node = cls.model_node_from_object(root_obj, options)

        if options.export_animations:
            model.animations = [
                Animation.from_list_anim(anim, root_obj)
                for anim in root_obj.kb.anim_list
            ]

        return model

    @classmethod
    def sanitize_model(cls, root_obj):
        # Make a set of unique node numbers
        node_numbers = set()
        obj_stack = []
        obj_stack.append(root_obj)
        while obj_stack:
            obj = obj_stack.pop()
            if obj.kb.node_number in node_numbers:
                logger().warning(
                    f"Duplicate node number [{obj.kb.node_number}] in object [{obj.name}]"
                )
            if obj.kb.node_number != -1:
                node_numbers.add(obj.kb.node_number)
            for child in obj.children:
                obj_stack.append(child)
        sorted_node_numbers = sorted(node_numbers)
        if sorted_node_numbers:
            next_node_number = sorted_node_numbers[-1] + 1
        else:
            next_node_number = 0

        # Generate node numbers when undefined
        obj_stack.append(root_obj)
        while obj_stack:
            obj = obj_stack.pop()
            if obj.kb.node_number == -1:
                obj.kb.node_number = next_node_number
                next_node_number += 1
            for child in obj.children:
                obj_stack.append(child)

    @classmethod
    def model_node_from_object(cls, obj, options, parent=None, exclude_xwk=True):
        if exclude_xwk and (is_pwk_root(obj) or is_dwk_root(obj)):
            return None

        if obj.type == "EMPTY":
            if obj.kb.dummytype == DummyType.REFERENCE:
                node_type = NodeType.REFERENCE
            else:
                node_type = NodeType.DUMMY
        elif obj.type == "MESH":
            if obj.kb.meshtype == MeshType.EMITTER:
                node_type = NodeType.EMITTER
            elif obj.kb.meshtype == MeshType.AABB:
                node_type = NodeType.AABB
            elif obj.kb.meshtype == MeshType.SKIN:
                node_type = NodeType.SKIN
            elif obj.kb.meshtype == MeshType.LIGHTSABER:
                node_type = NodeType.LIGHTSABER
            elif obj.kb.meshtype == MeshType.DANGLYMESH:
                node_type = NodeType.DANGLYMESH
            else:
                node_type = NodeType.TRIMESH
        elif obj.type == "LIGHT":
            node_type = NodeType.LIGHT

        switch = {
            NodeType.DUMMY: DummyNode,
            NodeType.REFERENCE: ReferenceNode,
            NodeType.TRIMESH: TrimeshNode,
            NodeType.DANGLYMESH: DanglymeshNode,
            NodeType.SKIN: SkinmeshNode,
            NodeType.EMITTER: EmitterNode,
            NodeType.LIGHT: LightNode,
            NodeType.AABB: AabbNode,
            NodeType.LIGHTSABER: LightsaberNode,
        }

        name = obj.name
        if re.match(r".+\.\d{3}$", name):
            name = name[:-4]

        node = switch[node_type](name)
        node.parent = parent

        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        node.load_object_data(obj, eval_obj, options)

        # Ignore transformations up to MDL root
        if not parent:
            node.position = (0.0, 0.0, 0.0)
            node.orientation = (1.0, 0.0, 0.0, 0.0)
            node.from_root = Matrix()

        for child_obj in sorted(obj.children, key=lambda o: o.kb.export_order):
            child = cls.model_node_from_object(child_obj, options, node, exclude_xwk)
            if child:
                node.children.append(child)

        return node
