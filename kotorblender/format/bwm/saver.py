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

from mathutils import Vector

from ...defines import WkmMaterial
from ...scene.modelnode.aabb import AabbNode
from ...scene.modelnode.trimesh import FaceList

from ..binwriter import BinaryWriter

from .types import *


class BwmSaver:
    def __init__(self, path, walkmesh):
        self.bwm = BinaryWriter(path, 'little')
        self.walkmesh = walkmesh

        self.bwm_pos = 0
        self.bwm_size = 0

        self.num_verts = 0
        self.off_verts = 0
        self.num_faces = 0
        self.off_vert_indices = 0
        self.off_material_ids = 0
        self.off_normals = 0
        self.off_distances = 0
        self.off_aabbs = 0
        self.off_adjacent_edges = 0
        self.off_outer_edges = 0
        self.off_perimeters = 0

        self.geom_node = None
        self.use_node1 = None
        self.use_node2 = None

        self.facelist = FaceList()

    def save(self):
        self.peek_walkmesh()

        self.save_header()
        self.save_vertices()
        self.save_faces()
        self.save_aabbs()

    def peek_walkmesh(self):
        # Header
        self.bwm_pos += 136

        self.geom_node = self.walkmesh.root_node.find_child(lambda node: isinstance(node, AabbNode))
        self.peek_faces()

        self.num_verts = len(self.geom_node.verts)
        self.num_faces = len(self.facelist.faces)

        # Vertices
        self.off_verts = self.bwm_pos
        self.bwm_pos += 4 * 3 * self.num_verts

        # Vertex Indices
        self.off_vert_indices = self.bwm_pos
        self.bwm_pos += 4 * 3 * self.num_faces

        # Material Ids
        self.off_material_ids = self.bwm_pos
        self.bwm_pos += 4 * self.num_faces

        # Normals
        self.off_normals = self.bwm_pos
        self.bwm_pos += 4 * 3 * self.num_faces

        # Distances
        self.off_distances = self.bwm_pos
        self.bwm_pos += 4 * self.num_faces

        self.bwm_size = self.bwm_pos

    def peek_faces(self):
        walkable_face_indices = []
        non_walkable_face_indices = []
        for face_idx, _ in enumerate(self.geom_node.facelist.faces):
            mat_id = self.geom_node.facelist.matId[face_idx]
            if mat_id in WkmMaterial.NONWALKABLE:
                non_walkable_face_indices.append(face_idx)
            else:
                walkable_face_indices.append(face_idx)
        face_indices = walkable_face_indices + non_walkable_face_indices
        for face_idx in face_indices:
            self.facelist.faces.append(self.geom_node.facelist.faces[face_idx])
            self.facelist.matId.append(self.geom_node.facelist.matId[face_idx])
            self.facelist.normals.append(self.geom_node.facelist.normals[face_idx])

    def save_header(self):
        walkmesh_type = WALKMESH_TYPE_AREA if self.walkmesh.walkmesh_type == "wok" else WALKMESH_TYPE_PLACEABLE
        rel_use_vec1 = self.use_node1.position if self.use_node1 else [0.0] * 3
        rel_use_vec2 = self.use_node2.position if self.use_node2 else [0.0] * 3
        position = self.walkmesh.root_node.position

        if self.walkmesh.walkmesh_type == "dwk":
            abs_use_vec1 = [position[i] + rel_use_vec1[i] for i in range(3)]
            abs_use_vec2 = [position[i] + rel_use_vec2[i] for i in range(3)]
        else:
            abs_use_vec1 = [0.0] * 3
            abs_use_vec2 = [0.0] * 3

        num_verts = len(self.geom_node.verts)
        num_faces = len(self.facelist.faces)
        num_aabbs = 0
        off_aabbs = 0
        num_adj_edges = 0
        off_adj_edges = 0
        num_outer_edges = 0
        off_outer_edges = 0
        num_perimeters = 0
        off_perimeters = 0

        self.bwm.put_string("BWM V1.0")
        self.bwm.put_uint32(walkmesh_type)
        for val in rel_use_vec1:
            self.bwm.put_float(val)
        for val in rel_use_vec2:
            self.bwm.put_float(val)
        for val in abs_use_vec1:
            self.bwm.put_float(val)
        for val in abs_use_vec2:
            self.bwm.put_float(val)
        for val in position:
            self.bwm.put_float(val)
        self.bwm.put_uint32(num_verts)
        self.bwm.put_uint32(self.off_verts)
        self.bwm.put_uint32(num_faces)
        self.bwm.put_uint32(self.off_vert_indices)
        self.bwm.put_uint32(self.off_material_ids)
        self.bwm.put_uint32(self.off_normals)
        self.bwm.put_uint32(self.off_distances)
        self.bwm.put_uint32(num_aabbs)
        self.bwm.put_uint32(off_aabbs)
        self.bwm.put_uint32(0)  # unknown
        self.bwm.put_uint32(num_adj_edges)
        self.bwm.put_uint32(off_adj_edges)
        self.bwm.put_uint32(num_outer_edges)
        self.bwm.put_uint32(off_outer_edges)
        self.bwm.put_uint32(num_perimeters)
        self.bwm.put_uint32(off_perimeters)

    def save_vertices(self):
        for vert in self.geom_node.verts:
            for val in vert:
                self.bwm.put_float(val)

    def save_faces(self):
        # Vertex Indices
        for face in self.facelist.faces:
            for val in face:
                self.bwm.put_uint32(val)

        # Material Ids
        for mat_id in self.facelist.matId:
            self.bwm.put_uint32(mat_id)

        # Normals
        for normal in self.facelist.normals:
            for val in normal:
                self.bwm.put_float(val)

        # Distances
        for face_idx, face in enumerate(self.facelist.faces):
            vert1 = Vector(self.geom_node.verts[face[0]])
            normal = Vector(self.facelist.normals[face_idx])
            distance = -1.0 * (normal @ vert1)
            self.bwm.put_float(distance)

    def save_aabbs(self):
        pass
