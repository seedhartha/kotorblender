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

import collections

import bpy

from ..exception.malformedfile import MalformedFile

from .. import defines, glob, utils

from .modelnode.dummy import DummyNode

from . import armature


class Model:

    def __init__(self):
        self.node_dict = collections.OrderedDict()
        self.anim_dict = dict()  # No need to retain order

        self.name = "UNNAMED"
        self.supermodel = defines.null
        self.animscale = 1.0
        self.classification = defines.Classification.UNKNOWN
        self.subclassification = 0
        self.ignorefog = False
        self.compress_quats = False
        self.headlink = False

        self.animations = []

    def add_node(self, new_node):
        if not new_node:
            return
        key = new_node.parent_name + new_node.name
        if key in self.node_dict:
            print("KotorBlender: WARNING - node name conflict " + key + ".")
        else:
            self.node_dict[key] = new_node

    def add_animation(self, anim):
        if not anim:
            return
        if anim.name in self.anim_dict:
            print("KotorBlender: WARNING - animation name conflict.")
        else:
            self.anim_dict[anim.name] = anim

    def import_to_collection(self, collection, position=(0.0, 0.0, 0.0)):
        mdl_root = None
        objIdx = 0
        if self.node_dict:
            it = iter(self.node_dict.items())

            # The first node should be the rootdummy.
            # If the first node has a parent or isn't a dummy we don't
            # even try to import the mdl
            (_, node) = next(it)
            if (type(node) == DummyNode) and (utils.is_null(node.parent_name)):
                obj = node.add_to_collection(collection)
                obj.location = position
                obj.kb.dummytype = defines.Dummytype.MDLROOT
                obj.kb.supermodel = self.supermodel
                obj.kb.classification = self.classification
                obj.kb.subclassification = self.subclassification
                obj.kb.ignorefog = (self.ignorefog >= 1)
                obj.kb.compress_quats = (self.compress_quats >= 1)
                obj.kb.headlink = (self.headlink >= 1)
                obj.kb.animscale = self.animscale
                mdl_root = obj

                obj.kb.imporder = objIdx
                objIdx += 1
            else:
                raise MalformedFile("First node has to be a dummy without a parent.")

            for (_, node) in it:
                obj = node.add_to_collection(collection)
                obj.kb.imporder = objIdx
                objIdx += 1

                if (utils.is_null(node.parent_name)):
                    # Node without parent and not the mdl root.
                    raise MalformedFile(node.name + " has no parent.")
                else:
                    # Check if such an object exists
                    if obj.parent is not None:
                        print("WARNING: Node already parented: {}".format(obj.name))
                        pass
                    elif mdl_root and node.parent_name in bpy.data.objects and \
                            utils.ancestor_node(
                                bpy.data.objects[node.parent_name],
                                utils.is_root_dummy
                            ).name == mdl_root.name:
                        # parent named node exists and is in our model
                        obj.parent = bpy.data.objects[node.parent_name]
                        if node.parent_name != self.name:
                            # child of non-root, preserve orientation
                            obj.matrix_parent_inverse = obj.parent.matrix_world.inverted()
                    else:
                        # parent node was not found in our model,
                        # this should mean that a node of the same name already
                        # existed in the scene,
                        # perform search for parent node in our model,
                        # taking into account blender .001 suffix naming scheme,
                        # note: only searching 001-030
                        found = False
                        for altname in [node.parent_name + ".{:03d}".format(i) for i in range(1, 30)]:
                            if altname in bpy.data.objects and \
                               utils.ancestor_node(
                                   bpy.data.objects[altname],
                                   utils.is_root_dummy
                               ).name == mdl_root.name:
                                # parent node in our model exists with suffix
                                obj.parent = bpy.data.objects[altname]
                                obj.matrix_parent_inverse = obj.parent.matrix_world.inverted()
                                found = True
                                break
                        # Node with invalid parent.
                        if not found:
                            raise MalformedFile(node.name + " has no parent " + node.parent_name)

        # Attempt to import animations
        # Search for the MDL root if not already present
        if not mdl_root:
            for obj in collection.objects:
                if utils.is_root_dummy(obj, defines.Dummytype.MDLROOT):
                    mdl_root = obj
                    break
            # Still none ? Don't try to import anims then
            if not mdl_root:
                return

        armature_object = None
        if glob.import_armatures:
            armature_object = armature.recreate_armature(mdl_root)
        else:
            # When armature creation is disabled, see if the MDL root already has an armature and use that
            skinmeshes = utils.search_node_all(mdl_root, lambda o: o.kb.meshtype == defines.Meshtype.SKIN)
            for skinmesh in skinmeshes:
                for modifier in skinmesh.modifiers:
                    if modifier.type == 'ARMATURE':
                        armature_object = modifier.object
                        break
                if armature_object:
                    break

        if glob.import_animations:
            self.create_animations(mdl_root, armature_object)

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
