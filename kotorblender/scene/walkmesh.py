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

from .. import utils

from .model import Model


class Walkmesh(Model):

    def __init__(self, walkmesh_type):
        Model.__init__(self)
        self.walkmesh_type = walkmesh_type

        self.outer_edges = []

    def import_to_collection(self, parent_name, collection):
        if not self.node_dict:
            return
        for node in self.node_dict.values():
            if utils.is_null(node.parent_name):
                node.parent_name = parent_name
            obj = node.add_to_collection(collection)
            if node.parent_name in bpy.data.objects:
                obj.parent = bpy.data.objects[node.parent_name]
                obj.matrix_parent_inverse = obj.parent.matrix_world.inverted()
