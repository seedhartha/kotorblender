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

import math

from .. import defines, utils


class Animation:

    def __init__(self, name="UNNAMED"):
        self.name = name
        self.length = 1.0
        self.transtime = 1.0
        self.animroot = defines.NULL
        self.events = []
        self.root_node = None

    def add_to_objects(self, mdl_root):
        list_anim = Animation.append_to_object(mdl_root, self.name, self.length, self.transtime, self.animroot)
        for time, name in self.events:
            Animation.append_event_to_object_anim(list_anim, name, time)

        objects = utils.get_children_recursive(mdl_root)
        object_by_number = {obj.kb.node_number: obj for obj in objects}
        self.add_nodes_to_objects(self.root_node, object_by_number, list_anim, mdl_root.name)

    def add_nodes_to_objects(self, node, object_by_number, anim, root_name):
        if node.supernode_number in object_by_number:
            obj = object_by_number[node.supernode_number]
            node.add_keyframes_to_object(anim, obj, root_name)
        for child in node.children:
            self.add_nodes_to_objects(child, object_by_number, anim, root_name)

    @staticmethod
    def append_to_object(mdl_root, name, length=0.0, transtime=0.25, animroot=defines.NULL):
        anim = mdl_root.kb.anim_list.add()
        anim.name = name
        anim.root_obj = animroot
        anim.transtime = Animation.time_to_frame(transtime)
        anim.frame_start = Animation.get_next_frame(mdl_root)
        anim.frame_end = anim.frame_start + Animation.time_to_frame(length)
        return anim

    @staticmethod
    def append_event_to_object_anim(list_anim, name, time):
        event = list_anim.event_list.add()
        event.name = name
        event.frame = list_anim.frame_start + Animation.time_to_frame(time)

    @staticmethod
    def time_to_frame(time):
        return round(defines.FPS * time)

    @staticmethod
    def get_next_frame(mdl_root):
        last_frame = max([defines.ANIM_GLOBSTART] + [a.frame_end for a in mdl_root.kb.anim_list])
        return int(math.ceil((last_frame + defines.ANIM_OFFSET) / 10.0)) * 10
