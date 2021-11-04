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
from mathutils import Vector

from ... import defines, utils

from .trimesh import TrimeshNode, UV_MAP_DIFFUSE, UV_MAP_LIGHTMAP


class AabbNode(TrimeshNode):

    def __init__(self, name="UNNAMED"):
        TrimeshNode.__init__(self, name)
        self.nodetype = "aabb"
        self.meshtype = defines.Meshtype.AABB
        self.roomlinks = []
        self.lytposition = (0.0, 0.0, 0.0)

    def compute_lyt_position(self, wok_geom):
        wok_vert = Vector(wok_geom.verts[wok_geom.facelist.faces[0][0]])
        wok_mat_id = wok_geom.facelist.matId[0]
        for i in range(len(self.facelist.faces)):
            mdl_mat_id = self.facelist.matId[i]
            if mdl_mat_id == wok_mat_id:
                mdl_vert = self.verts[self.facelist.faces[i][0]]
                mdl_vert_from_root = self.from_root @ Vector(mdl_vert)
                self.lytposition = wok_vert - mdl_vert_from_root
                break

    def compute_room_links(self, wok_geom, outer_edges):
        for edge in outer_edges:
            if edge[1] == 0xffffffff:
                continue
            wok_face = wok_geom.facelist.faces[edge[0] // 3]
            wok_verts = [wok_geom.verts[idx] for idx in wok_face]
            for face_idx, mdl_vert_indices in enumerate(self.facelist.faces):
                mdl_verts = [self.verts[idx] for idx in mdl_vert_indices]
                mdl_verts_from_root = [self.from_root @ Vector(vert) for vert in mdl_verts]
                mdl_verts_lyt_space = [vert + self.lytposition for vert in mdl_verts_from_root]
                if all([utils.is_close_3(wok_verts[i], mdl_verts_lyt_space[i]) for i in range(3)]):
                    self.roomlinks.append((3 * face_idx + (edge[0] % 3), edge[1]))
                    break

    def add_to_collection(self, collection):
        mesh = self.create_mesh(self.name)
        obj = bpy.data.objects.new(self.name, mesh)
        self.set_object_data(obj)
        self.set_room_links(mesh)
        collection.objects.link(obj)

        # Merge Vertices By Distance
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.mode_set(mode='OBJECT')

        return obj

    def create_mesh(self, name):
        # Create the mesh itself
        mesh = bpy.data.meshes.new(name)
        mesh.vertices.add(len(self.verts))
        mesh.vertices.foreach_set("co", unpack_list(self.verts))
        num_faces = len(self.facelist.faces)
        mesh.loops.add(3 * num_faces)
        mesh.loops.foreach_set("vertex_index", unpack_list(self.facelist.faces))
        mesh.polygons.add(num_faces)
        mesh.polygons.foreach_set("loop_start", range(0, 3 * num_faces, 3))
        mesh.polygons.foreach_set("loop_total", (3,) * num_faces)

        # Create materials
        for wok_mat in defines.WOK_MATERIALS:
            mat_name = wok_mat[0]
            # Walkmesh materials will be shared across multiple walkmesh
            # objects
            if mat_name in bpy.data.materials:
                material = bpy.data.materials[mat_name]
            else:
                material = bpy.data.materials.new(mat_name)
                material.diffuse_color = [*wok_mat[1], 1.0]
                material.specular_color = (0.0, 0.0, 0.0)
                material.specular_intensity = wok_mat[2]
            mesh.materials.append(material)

        # Apply the walkmesh materials to each face
        for idx, polygon in enumerate(mesh.polygons):
            polygon.material_index = self.facelist.matId[idx]

        # Create UV map
        if len(self.tverts) > 0:
            uv = unpack_list([self.tverts[i] for indices in self.facelist.uvIdx for i in indices])
            uv_layer = mesh.uv_layers.new(name=UV_MAP_DIFFUSE, do_init=False)
            uv_layer.data.foreach_set("uv", uv)

        # Create lightmap UV map
        if len(self.tverts1) > 0:
            uv = unpack_list([self.tverts1[i] for indices in self.facelist.uvIdx for i in indices])
            uv_layer = mesh.uv_layers.new(name=UV_MAP_LIGHTMAP, do_init=False)
            uv_layer.data.foreach_set("uv", uv)

        mesh.update()
        return mesh

    def set_object_data(self, obj):
        TrimeshNode.set_object_data(self, obj)

        obj.kb.lytposition = self.lytposition

    def load_object_data(self, obj):
        TrimeshNode.load_object_data(self, obj)

        self.lytposition = obj.kb.lytposition

    def set_room_links(self, mesh):
        if not "RoomLinks" in mesh.vertex_colors:
            room_vert_colors = mesh.vertex_colors.new(name="RoomLinks")
        else:
            room_vert_colors = mesh.vertex_colors["RoomLinks"]
        for link in self.roomlinks:
            face_idx = int(link[0] / 3)
            edge_idx = link[0] % 3
            room_color = [0.0 / 255, (200 + link[1]) / 255.0, 0.0 / 255]
            real_idx = 0
            for polyglon_idx, polygon in enumerate(mesh.polygons):
                if polygon.material_index not in defines.WkmMaterial.NONWALKABLE:
                    if real_idx == face_idx:
                        face_idx = polyglon_idx
                        break
                    else:
                        real_idx += 1
            face = mesh.polygons[face_idx]
            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                if vert_idx in face.edge_keys[edge_idx]:
                    room_vert_colors.data[loop_idx].color = [*room_color, 1.0]
