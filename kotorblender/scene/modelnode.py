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


class ModelNode:

    def __init__(self, name, type, parent, position, orientation):
        self.name = name
        self.type = type
        self.parent = parent
        self.position = position
        self.orientation = orientation

        self.children = []

    def add_to_collection(self, parent_obj):
        obj = bpy.data.objects.new(self.name, None)
        obj.parent = parent_obj

        bpy.context.collection.objects.link(obj)

        for child in self.children:
            child.add_to_collection(obj)