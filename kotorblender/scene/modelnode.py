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

from ..defines import Dummytype, Meshtype, Nodetype

from . import light, material


class ModelNode:

    def __init__(self, name, node_type, parent, position, orientation):
        self.name = name
        self.node_type = node_type
        self.parent = parent
        self.position = position
        self.orientation = orientation

        self.children = []

    def add_to_collection(self, parent_obj=None):
        obj = bpy.data.objects.new(self.name, self.new_object_data())

        if parent_obj is None:
            obj.kb.dummytype = Dummytype.MDLROOT
        obj.kb.restloc = self.position
        obj.kb.restrot = self.orientation

        obj.parent = parent_obj
        obj.location = self.position
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = Quaternion(self.orientation)

        if self.is_mesh_type():
            obj.kb.meshtype = self.get_mesh_type()
            obj.kb.diffuse = self.diffuse
            obj.kb.ambient = self.ambient
            obj.kb.bitmap = self.bitmap
            obj.kb.bitmap2 = self.bitmap2
            obj.kb.alpha = self.alpha
            obj.kb.selfillumcolor = self.selfillumcolor
            material.rebuild_material(obj)

            if self.node_type is Nodetype.SKIN:
                for vert_idx, vert_weights in enumerate(self.weights):
                    for weight in vert_weights:
                        if weight[0] in obj.vertex_groups:
                            vert_group = obj.vertex_groups[weight[0]]
                        else:
                            vert_group = obj.vertex_groups.new(name=weight[0])
                        vert_group.add([vert_idx], weight[1], 'REPLACE')

        elif self.node_type is Nodetype.LIGHT:
            obj.kb.radius = self.radius
            obj.kb.multiplier = self.multiplier
            light.calc_light_power(obj)

        bpy.context.collection.objects.link(obj)

        for child in self.children:
            child.add_to_collection(obj)

        return obj

    def new_object_data(self):
        if self.is_mesh_type():
            return self.new_mesh()
        if self.node_type is Nodetype.LIGHT:
            return self.new_light()
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

        # Diffuse UV map
        if len(self.tverts) > 0:
            uv = unpack_list([self.tverts[i] for indices in self.facelist.uvIdx for i in indices])
            uv_layer = mesh.uv_layers.new(name="UVMap", do_init=False)
            uv_layer.data.foreach_set("uv", uv)

        # Lightmap UV map
        if len(self.tverts1) > 0:
            uv = unpack_list([self.tverts1[i] for indices in self.facelist.uvIdx for i in indices])
            uv_layer = mesh.uv_layers.new(name="UVMap_lm", do_init=False)
            uv_layer.data.foreach_set("uv", uv)

        mesh.update()
        return mesh

    def new_light(self):
        light = bpy.data.lights.new(self.name, 'POINT')
        light.color = self.color
        return light

    def is_mesh_type(self):
        return self.node_type in [
            Nodetype.TRIMESH,
            Nodetype.DANGLYMESH,
            Nodetype.SKIN,
            Nodetype.AABB,
            Nodetype.LIGHTSABER]

    def get_mesh_type(self):
        switch = {
            Nodetype.TRIMESH: Meshtype.TRIMESH,
            Nodetype.DANGLYMESH: Meshtype.DANGLYMESH,
            Nodetype.SKIN: Meshtype.SKIN,
            Nodetype.AABB: Meshtype.AABB,
            Nodetype.LIGHTSABER: Meshtype.LIGHTSABER
        }
        return switch[self.node_type]