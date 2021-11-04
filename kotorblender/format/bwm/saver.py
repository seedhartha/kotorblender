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

from ... import aabb

from ..binwriter import BinaryWriter
from ..mdl.types import *

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
        self.aabbs = []

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
        self.peek_aabbs()

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

        # AABB
        self.off_aabbs = self.bwm_pos
        self.bwm_pos += 44 * len(self.aabbs)

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

    def peek_aabbs(self):
        face_list = []
        face_idx = 0

        for face in self.facelist.faces:
            v0 = Vector(self.geom_node.verts[face[0]])
            v1 = Vector(self.geom_node.verts[face[1]])
            v2 = Vector(self.geom_node.verts[face[2]])
            centroid = (v0 + v1 + v2) / 3
            face_list.append((face_idx, [v0, v1, v2], centroid))
            face_idx += 1

        aabbs = []
        aabb.generate_tree(aabbs, face_list)

        for aabb_node in aabbs:
            child_idx1 = aabb_node[6]
            child_idx2 = aabb_node[7]
            face_idx = aabb_node[8]
            split_axis = aabb_node[9]

            switch = {
                -3: AABB_NEGATIVE_Z,
                -2: AABB_NEGATIVE_Y,
                -1: AABB_NEGATIVE_X,
                0: AABB_NO_CHILDREN,
                1: AABB_POSITIVE_X,
                2: AABB_POSITIVE_Y,
                3: AABB_POSITIVE_Z
            }
            most_significant_plane = switch[split_axis]

            self.aabbs.append(AABB(aabb_node[:6], face_idx, most_significant_plane, child_idx1, child_idx2))

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
        num_aabbs = len(self.aabbs)
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
        self.bwm.put_uint32(self.off_aabbs)
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
        for aabb in self.aabbs:
            for val in aabb.bounding_box:
                self.bwm.put_float(val)
            self.bwm.put_int32(aabb.face_idx)
            self.bwm.put_uint32(0)  # unknown
            self.bwm.put_uint32(aabb.most_significant_plane)
            self.bwm.put_uint32(aabb.child_idx1)
            self.bwm.put_uint32(aabb.child_idx2)
