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

from .. import defines, utils

from .animnode import AnimationNode


class Animation:

    def __init__(self, name="UNNAMED"):
        self.name = name
        self.length = 1.0
        self.transtime = 1.0
        self.animroot = defines.null
        self.event_list = []

        self.nodes = []
        self.events = []

    def add_to_objects(self, mdl_root):
        list_anim = self.create_list_anim(mdl_root)
        self.add_events_to_list_anim(list_anim)
        obj_by_node = self.associate_node_to_object(mdl_root)

        # Add object keyframes
        for node in self.nodes:
            if node.name.lower() in obj_by_node:
                obj = obj_by_node[node.name.lower()]
                node.add_object_keyframes(obj, list_anim, {"mdlname": mdl_root.name})
                self.create_rest_pose(obj, list_anim.frame_start-5)

    def create_list_anim(self, mdl_root):
        result = utils.create_anim_list_item(mdl_root)
        result.name = self.name
        result.transtime = defines.fps * self.transtime
        result.root = result.root_obj = self.get_anim_target(mdl_root).name
        result.frame_end = utils.nwtime2frame(self.length) + result.frame_start
        return result

    def add_events_to_list_anim(self, list_anim):
        for time, name in self.events:
            event = list_anim.event_list.add()
            event.name = name
            event.frame = utils.nwtime2frame(time) + list_anim.frame_start

    def associate_node_to_object(self, mdl_root):
        result = dict()
        for node in self.nodes:
            obj = utils.search_node(mdl_root, lambda o, name=node.name: o.name.lower() == name.lower())
            if obj:
                result[node.name.lower()] = obj
        return result

    def create_rest_pose(self, obj, frame=1):
        AnimationNode.create_restpose(obj, frame)

    def get_anim_target(self, mdl_root):
        result = utils.search_node(mdl_root, lambda o, name=self.animroot: o.name.lower() == name.lower())
        if not result:
            result = mdl_root
            print("KotorBlender: animation retargeted from {} to {}".format(self.animroot, mdl_root.name))
        return result
