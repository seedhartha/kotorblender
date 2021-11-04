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
import re

from ..defines import Dummytype

from .. import defines, utils

from .animnode import AnimationNode


class Animation:

    def __init__(self, name="UNNAMED"):
        self.name = name
        self.length = 1.0
        self.transtime = 1.0
        self.animroot = defines.NULL
        self.root_node = None

        self.events = []

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

    @classmethod
    def append_to_object(cls, mdl_root, name, length=0.0, transtime=0.25, animroot=defines.NULL):
        anim = mdl_root.kb.anim_list.add()
        anim.name = name
        anim.root_obj = animroot
        anim.transtime = Animation.time_to_frame(transtime)
        anim.frame_start = Animation.get_next_frame(mdl_root)
        anim.frame_end = anim.frame_start + Animation.time_to_frame(length)
        return anim

    @classmethod
    def append_event_to_object_anim(cls, list_anim, name, time):
        event = list_anim.event_list.add()
        event.name = name
        event.frame = list_anim.frame_start + Animation.time_to_frame(time)

    @classmethod
    def time_to_frame(cls, time):
        return round(defines.FPS * time)

    @classmethod
    def get_next_frame(cls, mdl_root):
        last_frame = max([defines.ANIM_GLOBSTART] + [a.frame_end for a in mdl_root.kb.anim_list])
        return int(math.ceil((last_frame + defines.ANIM_OFFSET) / 10.0)) * 10

    @classmethod
    def from_list_anim(cls, list_anim, mdl_root):
        anim = Animation(list_anim.name)
        anim.length = Animation.frame_to_time(list_anim.frame_end - list_anim.frame_start)
        anim.transtime = Animation.frame_to_time(list_anim.transtime)
        anim.animroot = list_anim.root_obj
        anim.root_node = Animation.animation_node_from_object(list_anim, mdl_root)

        for event in list_anim.event_list:
            time = Animation.frame_to_time(event.frame - list_anim.frame_start)
            name = event.name
            anim.events.append((time, name))

        return anim

    @classmethod
    def animation_node_from_object(cls, anim, obj, parent=None):
        name = obj.name
        if re.match(r".+\.\d{3}$", name):
            name = name[:-4]

        node = AnimationNode(name)
        node.supernode_number = obj.kb.node_number
        node.parent = parent

        node.load_keyframes_from_object(anim, obj)
        if obj.type == 'LIGHT':
            node.load_keyframes_from_object(anim, obj.data)
        node.animated = bool(node.keyframes)

        for child_obj in sorted(obj.children, key=lambda o: o.kb.export_order):
            if child_obj.type == 'EMPTY' and child_obj.kb.dummytype in [Dummytype.PWKROOT, Dummytype.DWKROOT]:
                continue
            child = Animation.animation_node_from_object(anim, child_obj, node)
            if not node.animated and child.animated:
                node.animated = True
            node.children.append(child)

        return node

    @classmethod
    def frame_to_time(cls, frame):
        return frame / defines.FPS
