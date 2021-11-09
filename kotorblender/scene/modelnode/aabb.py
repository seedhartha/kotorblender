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

ROOM_LINKS_COLORS = "RoomLinks"


class AabbNode(TrimeshNode):

    def __init__(self, name="UNNAMED"):
        TrimeshNode.__init__(self, name)
        self.nodetype = "aabb"
        self.meshtype = defines.Meshtype.AABB

        self.bwmposition = (0.0, 0.0, 0.0)
        self.lytposition = (0.0, 0.0, 0.0)
        self.roomlinks = dict()

    def compute_lyt_position(self, wok_geom):
        wok_vert = Vector(wok_geom.verts[wok_geom.facelist.vertices[0][0]])
        wok_mat_id = wok_geom.facelist.materials[0]
        for i in range(len(self.facelist.vertices)):
            mdl_mat_id = self.facelist.materials[i]
            if mdl_mat_id == wok_mat_id:
                mdl_vert = self.verts[self.facelist.vertices[i][0]]
                mdl_vert_from_root = self.from_root @ Vector(mdl_vert)
                self.lytposition = wok_vert - mdl_vert_from_root + Vector(self.bwmposition)
                break

    def add_to_collection(self, collection):
        mesh = self.create_mesh(self.name)
        obj = bpy.data.objects.new(self.name, mesh)
        self.set_object_data(obj)
        self.apply_room_links(mesh)
        collection.objects.link(obj)

        return obj

    def create_mesh(self, name):
        self.merge_similar_vertices()

        # Create the mesh itself
        mesh = bpy.data.meshes.new(name)
        mesh.vertices.add(len(self.verts))
        mesh.vertices.foreach_set("co", unpack_list(self.verts))
        num_faces = len(self.facelist.vertices)
        mesh.loops.add(3 * num_faces)
        mesh.loops.foreach_set("vertex_index", unpack_list(self.facelist.vertices))
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
            polygon.material_index = self.facelist.materials[idx]

        # Create UV map
        if len(self.uv1) > 0:
            uv = unpack_list([self.uv1[i] for indices in self.facelist.uv for i in indices])
            uv_layer = mesh.uv_layers.new(name=UV_MAP_DIFFUSE, do_init=False)
            uv_layer.data.foreach_set("uv", uv)

        # Create lightmap UV map
        if len(self.uv2) > 0:
            uv = unpack_list([self.uv2[i] for indices in self.facelist.uv for i in indices])
            uv_layer = mesh.uv_layers.new(name=UV_MAP_LIGHTMAP, do_init=False)
            uv_layer.data.foreach_set("uv", uv)

        mesh.update()
        return mesh

    def apply_room_links(self, mesh):
        if ROOM_LINKS_COLORS in mesh.vertex_colors:
            colors = mesh.vertex_colors[ROOM_LINKS_COLORS]
        else:
            colors = mesh.vertex_colors.new(name=ROOM_LINKS_COLORS)

        for wok_edge_idx, transition in self.roomlinks.items():
            wok_face_idx = wok_edge_idx // 3
            aabb_face = None
            for walkable_idx, polygon in enumerate([p for p in mesh.polygons if p.material_index not in defines.WkmMaterial.NONWALKABLE]):
                if walkable_idx == wok_face_idx:
                    aabb_face = polygon
                    break
            if not aabb_face:
                continue
            for vert_idx, loop_idx in zip(aabb_face.vertices, aabb_face.loop_indices):
                if vert_idx in aabb_face.edge_keys[wok_edge_idx % 3]:
                    color = [0.0, (200.0 + transition) / 255.0, 0.0]
                    colors.data[loop_idx].color = [*color, 1.0]

    def unapply_room_links(self, mesh):
        self.roomlinks = dict()
        if ROOM_LINKS_COLORS not in mesh.vertex_colors:
            return
        colors = mesh.vertex_colors[ROOM_LINKS_COLORS]
        for walkable_idx, tri in enumerate([p for p in mesh.loop_triangles if p.material_index not in defines.WkmMaterial.NONWALKABLE]):
            for edge, loop_idx in enumerate(tri.loops):
                color = colors.data[loop_idx].color
                if color[0] > 0.0 or color[2] > 0.0 and (255.0 * color[1]) < 200.0:
                    continue
                edge_idx = 3 * walkable_idx + edge
                transition = int((255.0 * color[1]) - 200.0)
                self.roomlinks[edge_idx] = transition

    def set_object_data(self, obj):
        TrimeshNode.set_object_data(self, obj)

        obj.kb.bwmposition = self.bwmposition
        obj.kb.lytposition = self.lytposition

    def load_object_data(self, obj):
        TrimeshNode.load_object_data(self, obj)

        self.bwmposition = obj.kb.bwmposition
        self.lytposition = obj.kb.lytposition

        self.unapply_room_links(obj.data)
