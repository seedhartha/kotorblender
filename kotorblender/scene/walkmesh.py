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

from ..exception.malformedmdl import MalformedMdl

from .. import defines, utils

from .model import Model
from .modelnode.dummy import DummyNode


class Walkmesh(Model):

    def __init__(self, wkmType = "pwk"):
        Model.__init__(self)

        self.walkmeshType = wkmType

    def import_to_collection(self, collection):
        if self.nodeDict:
            # Walkmeshes have no rootdummys. We need to create one ourselves
            # Unless the rootdummy is in the model already, because that happens

            # Also, kotormax puts the rootdummy into the PWK and probably DWK,
            # making this not work.
            # Even worse, it parents the use dummies to the mesh,
            # making this doubly not work.

            # Our format expectations are more like what mdlops exports,
            # which is in line with the format used in NWN.

            # Look for the node parents for the list of parents. They should
            # all have the same name
            nameList = []
            for (_, node) in self.nodeDict.items():
                if node.parentName not in nameList:
                    nameList.append(node.parentName)
            self.name = nameList[0]

            if self.name in collection.objects and bpy.data.objects[self.name].kb.dummytype != defines.Dummytype.MDLROOT:
                node = bpy.data.objects[self.name].kb
                if self.walkmeshType == "dwk":
                    node.dummytype = defines.Dummytype.DWKROOT
                else:
                    node.dummytype = defines.Dummytype.PWKROOT
                rootdummy = bpy.data.objects[self.name]
            else:
                mdl_name = self.name
                wkm_name = self.name
                if not wkm_name.lower().endswith("_" + self.walkmeshType):
                    wkm_name += "_" + self.walkmeshType
                if mdl_name.lower().endswith("_" + self.walkmeshType):
                    mdl_name = mdl_name[0:-4]
                node = DummyNode(wkm_name)
                if self.walkmeshType == "dwk":
                    node.dummytype = defines.Dummytype.DWKROOT
                else:
                    node.dummytype = defines.Dummytype.PWKROOT
                node.name = wkm_name
                rootdummy = node.add_to_collection(collection)
                if mdl_name in bpy.data.objects:
                    rootdummy.parent = bpy.data.objects[mdl_name]
                else:
                    pass
            mdlroot = utils.ancestor_node(rootdummy, lambda o: o.kb.dummytype == defines.Dummytype.MDLROOT)
            if mdlroot is None and rootdummy.parent:
                mdlroot = rootdummy.parent
            if self.walkmeshType == "dwk":
                dp_open1 = utils.search_node(mdlroot, lambda o: "dwk_dp" in o.name.lower() and o.name.lower().endswith("open1_01"))
                dp_open2 = utils.search_node(mdlroot, lambda o: "dwk_dp" in o.name.lower() and o.name.lower().endswith("open2_01"))
                dp_closed01 = utils.search_node(mdlroot, lambda o: "dwk_dp" in o.name.lower() and o.name.lower().endswith("closed_01"))
                dp_closed02 = utils.search_node(mdlroot, lambda o: "dwk_dp" in o.name.lower() and o.name.lower().endswith("closed_02"))
                wg_open1 = utils.search_node(mdlroot, lambda o: "dwk_wg" in o.name.lower() and o.name.lower().endswith("open1"))
                wg_open2 = utils.search_node(mdlroot, lambda o: "dwk_wg" in o.name.lower() and o.name.lower().endswith("open2"))
                wg_closed = utils.search_node(mdlroot, lambda o: "dwk_wg" in o.name.lower() and o.name.lower().endswith("closed"))
            if self.walkmeshType == "pwk":
                pwk_wg = utils.search_node(mdlroot, lambda o: o.name.lower().endswith("_wg"))
                pwk_use01 = utils.search_node(mdlroot, lambda o: o.name.lower().endswith("pwk_use01"))
                pwk_use02 = utils.search_node(mdlroot, lambda o: o.name.lower().endswith("pwk_use02"))

            for (_, node) in self.nodeDict.items():
                # the node names may only be recorded in the MDL,
                # this means that the named dummy nodes already exist in-scene,
                # use these names to translate the WKM's special node names
                if "dp_open1_01" in node.name.lower() and dp_open1:
                    node.name = dp_open1.name
                if "dp_open2_01" in node.name.lower() and dp_open2:
                    node.name = dp_open2.name
                if "dp_closed_01" in node.name.lower() and dp_closed01:
                    node.name = dp_closed01.name
                if "dp_closed_02" in node.name.lower() and dp_closed02:
                    node.name = dp_closed02.name
                if "dwk_wg_open1" in node.name.lower() and wg_open1:
                    node.name = wg_open1.name
                if "dwk_wg_open2" in node.name.lower() and wg_open2:
                    node.name = wg_open2.name
                if "dwk_wg_closed" in node.name.lower() and wg_closed:
                    node.name = wg_closed.name
                if node.name.lower().endswith("_wg") and pwk_wg:
                    node.name = pwk_wg.name
                if node.name.lower().endswith("pwk_use01") and pwk_use01:
                    node.name = pwk_use01.name
                if node.name.lower().endswith("pwk_use02") and pwk_use02:
                    node.name = pwk_use02.name
                # remove pre-existing nodes that were added as part of a model
                if node.name in collection.objects:
                    obj = collection.objects[node.name]
                    collection.objects.unlink(obj)
                    bpy.data.objects.remove(obj)
                obj = node.add_to_collection(collection)
                # Check if such an object exists
                if node.parentName.lower() in [k.lower() for k in bpy.data.objects.keys()]:
                    parent_name = utils.get_real_name(node.parentName)
                    obj.parent = bpy.data.objects[parent_name]
                    obj.matrix_parent_inverse = obj.parent.matrix_world.inverted()
                else:
                    # Node with invalid parent.
                    raise MalformedMdl(node.name + " has no parent " + node.parentName)