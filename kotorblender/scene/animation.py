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

from .. import defines, utils


class Animation:

    def __init__(self, name, length, transtime, animroot, root_node, events):
        self.name = name
        self.length = length
        self.transtime = transtime
        self.animroot = animroot
        self.root_node = root_node
        self.events = events

    def add_to_object(self, obj):
        list_item = self.add_to_anim_list(obj)
        self.add_events_to_list_item(list_item)

    def add_to_anim_list(self, obj):
        item = utils.create_anim_list_item(obj)
        item.name = self.name
        item.transtime = defines.fps * self.transtime
        item.root = item.root_obj = self.get_anim_target(obj).name
        item.frameEnd = utils.nwtime2frame(self.length) + item.frameStart
        return item

    def add_events_to_list_item(self, item):
        for time, name in self.events:
            event = item.eventList.add()
            event.name = name
            event.frame = utils.nwtime2frame(time) + item.frameStart

    def get_anim_target(self, obj):
        return utils.search_node(
            obj,
            lambda o, name=self.animroot: o.name.lower() == name.lower())