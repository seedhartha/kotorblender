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

from ...defines import DummyType, WalkmeshMaterial, WalkmeshType
from ...scene.modelnode.aabb import AabbNode
from ...scene.modelnode.dummy import DummyNode
from ...scene.modelnode.trimesh import FaceList

from ... import aabb, utils

from ..binwriter import BinaryWriter
from ..mdl.types import *

from .types import *

MERGE_DISTANCE = 1e-4


class BwmSaver:
    def __init__(self, path, walkmesh):
        self.path = path
        self.bwm = BinaryWriter(path, 'little')
        self.walkmesh = walkmesh

        self.bwm_pos = 0
        self.bwm_size = 0

        self.num_verts = 0
        self.off_verts = 0
        self.num_faces = 0
        self.num_walkable_faces = 0
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

        self.verts = []
        self.new_vert_by_old_vert = dict()
        self.facelist = FaceList()
        self.aabbs = []
        self.adjacent_edges = []
        self.outer_edges = []
        self.perimeters = []

    def save(self):
        self.peek_walkmesh()

        self.save_header()
        self.save_vertices()
        self.save_faces()
        self.save_aabbs()
        self.save_adjacent_edges()
        self.save_outer_edges()
        self.save_perimeters()

    def peek_walkmesh(self):
        self.bwm_type = BWM_TYPE_WOK if self.walkmesh.walkmesh_type == WalkmeshType.WOK else BWM_TYPE_PWK_DWK
        self.geom_node = self.walkmesh.root_node.find_node(lambda node: isinstance(node, AabbNode))
        self.use_node1 = self.walkmesh.root_node.find_node(lambda node: isinstance(node, DummyNode) and node.dummytype == DummyType.USE1)
        self.use_node2 = self.walkmesh.root_node.find_node(lambda node: isinstance(node, DummyNode) and node.dummytype == DummyType.USE2)

        self.peek_vertices()
        self.peek_faces()
        self.peek_aabbs()
        self.peek_edges()

        self.num_verts = len(self.verts)
        self.num_faces = len(self.facelist.vertices)

        # Header
        self.bwm_pos += 136

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

        # Adjacent Edges
        self.off_adjacent_edges = self.bwm_pos
        self.bwm_pos += 4 * 3 * self.num_walkable_faces

        # Outer Edges
        self.off_outer_edges = self.bwm_pos
        self.bwm_pos += 4 * 2 * len(self.outer_edges)

        # Perimeters
        self.off_perimeters = self.bwm_pos
        self.bwm_pos += 4 * len(self.perimeters)

        self.bwm_size = self.bwm_pos

    def peek_vertices(self):
        # Merge duplicates (fixes collision detection)
        num_verts = len(self.geom_node.verts)
        num_unique = 0
        for vert_idx, vert in enumerate(self.geom_node.verts):
            if vert_idx in self.new_vert_by_old_vert:
                continue
            for other_vert_idx in range(vert_idx+1, num_verts):
                if other_vert_idx in self.new_vert_by_old_vert:
                    continue
                other_vert = self.geom_node.verts[other_vert_idx]
                if utils.is_close_3(vert, other_vert, MERGE_DISTANCE):
                    self.new_vert_by_old_vert[other_vert_idx] = num_unique
            self.verts.append(vert)
            self.new_vert_by_old_vert[vert_idx] = num_unique
            num_unique += 1

        # Offset by node and LYT position
        for vert_idx, vert in enumerate(self.verts):
            self.verts[vert_idx] = [vert[i] + self.geom_node.position[i] + self.geom_node.lytposition[i] for i in range(3)]

    def peek_faces(self):
        walkable_face_indices = []
        non_walkable_face_indices = []
        for face_idx, _ in enumerate(self.geom_node.facelist.vertices):
            mat_id = self.geom_node.facelist.materials[face_idx]
            if mat_id in WalkmeshMaterial.NONWALKABLE:
                non_walkable_face_indices.append(face_idx)
            else:
                walkable_face_indices.append(face_idx)
                self.num_walkable_faces += 1
        face_indices = walkable_face_indices + non_walkable_face_indices
        for face_idx in face_indices:
            self.facelist.vertices.append([self.new_vert_by_old_vert[vert_idx] for vert_idx in self.geom_node.facelist.vertices[face_idx]])
            self.facelist.materials.append(self.geom_node.facelist.materials[face_idx])
            self.facelist.normals.append(self.geom_node.facelist.normals[face_idx])

    def peek_aabbs(self):
        if self.bwm_type == BWM_TYPE_PWK_DWK:
            return

        face_list = []
        face_idx = 0

        for face in self.facelist.vertices:
            v0 = Vector(self.verts[face[0]])
            v1 = Vector(self.verts[face[1]])
            v2 = Vector(self.verts[face[2]])
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

    def peek_edges(self):
        # Adjacent Edges
        for _ in range(self.num_walkable_faces):
            self.adjacent_edges.append([-1, -1, -1])
        for face_idx in range(self.num_walkable_faces):
            face = self.facelist.vertices[face_idx]
            edges = [tuple(sorted(edge)) for edge in [(face[0], face[1]), (face[1], face[2]), (face[2], face[0])]]
            for other_face_idx in range(face_idx + 1, self.num_walkable_faces):
                other_face = self.facelist.vertices[other_face_idx]
                other_edges = [tuple(sorted(edge)) for edge in [(other_face[0], other_face[1]), (other_face[1], other_face[2]), (other_face[2], other_face[0])]]
                num_adj_edges = 0
                for i in range(3):
                    if self.adjacent_edges[face_idx][i] != -1:
                        num_adj_edges += 1
                        continue
                    for j in range(3):
                        if edges[i] == other_edges[j]:
                            self.adjacent_edges[face_idx][i] = 3 * other_face_idx + j
                            self.adjacent_edges[other_face_idx][j] = 3 * face_idx + i
                            num_adj_edges += 1
                            break
                if num_adj_edges == 3:
                    break

        # Outer Edges, Perimeters
        visited_edges = set()
        for i in range(self.num_walkable_faces):
            for j in range(3):
                # Outer edges must not have adjacent edges
                if self.adjacent_edges[i][j] != -1:
                    continue
                # One visit per edge
                edge_idx = 3 * i + j
                if edge_idx in visited_edges:
                    continue
                next_face = i
                next_edge = j
                while next_face != -1:
                    adj_edge_idx = self.adjacent_edges[next_face][next_edge]
                    if adj_edge_idx == -1:
                        edge_idx = 3 * next_face + next_edge
                        if not edge_idx in visited_edges:
                            transition = self.geom_node.roomlinks[edge_idx] if edge_idx in self.geom_node.roomlinks else -1
                            self.outer_edges.append((edge_idx, transition))
                            visited_edges.add(edge_idx)
                            next_edge = (next_edge + 1) % 3
                        else:
                            next_face = -1
                            self.perimeters.append(len(self.outer_edges))
                    else:
                        next_face = adj_edge_idx // 3
                        next_edge = ((adj_edge_idx % 3) + 1) % 3

    def save_header(self):
        rel_use_vec1 = self.use_node1.position if self.use_node1 else [0.0] * 3
        rel_use_vec2 = self.use_node2.position if self.use_node2 else [0.0] * 3
        position = self.geom_node.position

        if self.walkmesh.walkmesh_type == WalkmeshType.DWK:
            abs_use_vec1 = [position[i] + rel_use_vec1[i] for i in range(3)]
            abs_use_vec2 = [position[i] + rel_use_vec2[i] for i in range(3)]
        else:
            abs_use_vec1 = [0.0] * 3
            abs_use_vec2 = [0.0] * 3

        num_verts = len(self.verts)
        num_faces = len(self.facelist.vertices)

        if self.bwm_type == BWM_TYPE_WOK:
            num_aabbs = len(self.aabbs)
            off_aabbs = self.off_aabbs
            num_adj_edges = self.num_walkable_faces
            off_adj_edges = self.off_adjacent_edges
            num_outer_edges = len(self.outer_edges)
            off_outer_edges = self.off_outer_edges
            num_perimeters = len(self.perimeters)
            off_perimeters = self.off_perimeters
        else:
            num_aabbs = 0
            off_aabbs = 0
            num_adj_edges = 0
            off_adj_edges = 0
            num_outer_edges = 0
            off_outer_edges = 0
            num_perimeters = 0
            off_perimeters = 0

        self.bwm.put_string("BWM V1.0")
        self.bwm.put_uint32(self.bwm_type)
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
        for vert in self.verts:
            for val in vert:
                self.bwm.put_float(val)

    def save_faces(self):
        # Vertex Indices
        for face in self.facelist.vertices:
            for val in face:
                self.bwm.put_uint32(val)

        # Material Ids
        for mat_id in self.facelist.materials:
            self.bwm.put_uint32(mat_id)

        # Normals
        for normal in self.facelist.normals:
            for val in normal:
                self.bwm.put_float(val)

        # Distances
        for face_idx, face in enumerate(self.facelist.vertices):
            vert1 = Vector(self.verts[face[0]])
            normal = Vector(self.facelist.normals[face_idx])
            distance = -1.0 * (normal @ vert1)
            self.bwm.put_float(distance)

    def save_aabbs(self):
        for aabb in self.aabbs:
            for val in aabb.bounding_box:
                self.bwm.put_float(val)
            self.bwm.put_int32(aabb.face_idx)
            self.bwm.put_uint32(4)  # unknown
            self.bwm.put_uint32(aabb.most_significant_plane)
            self.bwm.put_int32(aabb.child_idx1)
            self.bwm.put_int32(aabb.child_idx2)

    def save_adjacent_edges(self):
        for edges in self.adjacent_edges:
            for val in edges:
                self.bwm.put_int32(val)

    def save_outer_edges(self):
        for edge_idx, transition in self.outer_edges:
            self.bwm.put_uint32(edge_idx)
            self.bwm.put_int32(transition)

    def save_perimeters(self):
        for perimeter in self.perimeters:
            self.bwm.put_uint32(perimeter)
