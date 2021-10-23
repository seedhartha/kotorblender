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

from bpy_extras.io_utils import unpack_list
from mathutils import Quaternion

from ..defines import Nodetype


class ModelNode:

    def __init__(self, name, type, parent, position, orientation):
        self.name = name
        self.type = type
        self.parent = parent
        self.position = position
        self.orientation = orientation

        self.children = []

    def add_to_collection(self, parent_obj):
        obj = bpy.data.objects.new(self.name, self.new_object_data())
        obj.parent = parent_obj
        obj.location = self.position
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = Quaternion(self.orientation)

        bpy.context.collection.objects.link(obj)

        for child in self.children:
            child.add_to_collection(obj)

    def new_object_data(self):
        if self.type is Nodetype.TRIMESH:
            return self.new_mesh()
        return None

    def new_mesh(self):
        mesh = bpy.data.meshes.new(self.name)
        mesh.vertices.add(len(self.verts))
        mesh.vertices.foreach_set("co", unpack_list(self.verts))
        num_faces = len(self.facelist.faces)
        mesh.loops.add(3 * num_faces)
        mesh.loops.foreach_set("vertex_index", unpack_list(self.facelist.faces))
        mesh.polygons.add(num_faces)
        mesh.polygons.foreach_set("loop_start", range(0, 3 * num_faces, 3))
        mesh.polygons.foreach_set("loop_total", (3,) * num_faces)
        mesh.update()
        return mesh