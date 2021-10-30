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

from ..exception.malformedmdl import MalformedMdl

from .. import defines, glob, utils

from .modelnode.dummy import DummyNode

from . import armature


class Model:

    def __init__(self):
        self.nodeDict      = collections.OrderedDict()
        self.animDict      = dict() # No need to retain order

        self.name           = "UNNAMED"
        self.supermodel     = defines.null
        self.animscale      = 1.0
        self.classification = defines.Classification.UNKNOWN
        self.unknownC1      = 0
        self.ignorefog      = False
        self.compress_quats = False
        self.headlink       = False
        self.lytposition    = None

        self.animations = []

    def add_node(self, newNode):
        if not newNode:
            return
        key = newNode.parentName + newNode.name
        if key in self.nodeDict:
            print("KotorBlender: WARNING - node name conflict " + key + ".")
        else:
            self.nodeDict[key] = newNode

    def add_animation(self, anim):
        if not anim:
            return
        if anim.name in self.animDict:
            print("KotorBlender: WARNING - animation name conflict.")
        else:
            self.animDict[anim.name] = anim

    def import_to_collection(self, collection, wkm, position = (0.0, 0.0, 0.0)):
        mdl_root = None
        objIdx = 0
        if (glob.importGeometry) and self.nodeDict:
            it = iter(self.nodeDict.items())

            # The first node should be the rootdummy.
            # If the first node has a parent or isn't a dummy we don't
            # even try to import the mdl
            (_, node) = next(it)
            if (type(node) == DummyNode) and (utils.is_null(node.parentName)):
                obj                   = node.add_to_collection(collection)
                obj.location          = position
                obj.kb.dummytype      = defines.Dummytype.MDLROOT
                obj.kb.supermodel     = self.supermodel
                obj.kb.classification = self.classification
                obj.kb.unknownC1      = self.unknownC1
                obj.kb.ignorefog      = (self.ignorefog >= 1)
                obj.kb.compress_quats = (self.compress_quats >= 1)
                obj.kb.headlink       = (self.headlink >= 1)
                obj.kb.animscale      = self.animscale
                mdl_root = obj

                obj.kb.imporder = objIdx
                objIdx += 1
            else:
                raise MalformedMdl("First node has to be a dummy without a parent.")

            for (_, node) in it:
                obj = node.add_to_collection(collection)
                obj.kb.imporder = objIdx
                objIdx += 1

                # If LYT position is specified, set it for the AABB node
                if self.lytposition and node.nodetype == "aabb":
                    node.lytposition = self.lytposition
                    obj.kb.lytposition = self.lytposition

                if (utils.is_null(node.parentName)):
                    # Node without parent and not the mdl root.
                    raise MalformedMdl(node.name + " has no parent.")
                else:
                    # Check if such an object exists
                    if obj.parent is not None:
                        print("WARNING: Node already parented: {}".format(obj.name))
                        pass
                    elif mdl_root and node.parentName in bpy.data.objects and \
                         utils.ancestor_node(
                             bpy.data.objects[node.parentName],
                             utils.is_root_dummy
                         ).name == mdl_root.name:
                        # parent named node exists and is in our model
                        obj.parent = bpy.data.objects[node.parentName]
                        if node.parentName != self.name:
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
                        for altname in [node.parentName + ".{:03d}".format(i) for i in range(1,30)]:
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
                            raise MalformedMdl(node.name + " has no parent " + node.parentName)

        # Import the walkmesh, it will use any placeholder dummies just imported,
        # and the walkmesh nodes will be copied during animation import
        if (glob.importWalkmesh) and not wkm is None and wkm.walkmeshType != "wok":
            wkm.import_to_collection(collection)

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
        if glob.createArmature:
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