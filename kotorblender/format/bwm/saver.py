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

from ...scene.modelnode.trimesh import FaceList, TrimeshNode

from ... import utils

from ..binwriter import BinaryWriter

from .types import *


class BwmSaver:
    def __init__(self, path, walkmesh):
        self.bwm = BinaryWriter(path, 'little')
        self.walkmesh = walkmesh

        self.bwm_pos = 0
        self.bwm_size = 0

        self.off_verts = 0
        self.off_vert_indices = 0
        self.off_material_ids = 0
        self.off_normals = 0
        self.off_distances = 0
        self.off_aabbs = 0
        self.off_adjacent_edges = 0
        self.off_outer_edges = 0
        self.off_perimeters = 0

        self.root_node = None
        self.geom_node = None
        self.use_node1 = None
        self.use_node2 = None

    def save(self):
        self.peek_walkmesh()

        self.save_header()
        self.save_vertices()
        self.save_faces()
        self.save_aabbs()

    def peek_walkmesh(self):
        self.bwm_pos += 136  # header

        # In area walkmeshes, geometry node is root node. In placeable
        # walkmeshes, geometry node is the only child of the root node.
        geom_node = self.walkmesh.root_node
        if utils.is_dwk_root(geom_node) or utils.is_pwk_root(geom_node):
            geom_node = geom_node.children[0]
        if not isinstance(geom_node, TrimeshNode):
            raise ValueError("Unable to find geometry node while saving BWM")

        # Vertices
        self.off_verts = self.bwm_pos
        self.bwm_pos += 4 * 3 * len(geom_node.verts)

        num_faces = len(geom_node.facelist.faces)

        # Vertex Indices
        self.off_vert_indices = self.bwm_pos
        self.bwm_pos += 4 * 3 * num_faces

        # Material Ids
        self.off_material_ids = self.bwm_pos
        self.bwm_pos += 4 * num_faces

        # Normals
        self.off_normals = self.bwm_pos
        self.bwm_pos += 4 * 3 * num_faces

        # Distances
        self.off_distances = self.bwm_pos
        self.bwm_pos += 4 * num_faces

        self.bwm_size = self.bwm_pos

    def save_header(self):
        walkmesh_type = WALKMESH_TYPE_AREA if self.walkmesh.walkmesh_type == "wok" else WALKMESH_TYPE_PLACEABLE
        rel_use_vec1 = self.use_node1.position if self.use_node1 else [0.0] * 3
        rel_use_vec2 = self.use_node2.position if self.use_node2 else [0.0] * 3
        position = self.

        if self.walkmesh.walkmesh_type == "dwk":
            abs_use_vec1 = [position[i] + rel_use_vec1[i] for i in range(3)]
            abs_use_vec2 = [position[i] + rel_use_vec2[i] for i in range(3)]
        else:
            abs_use_vec1 = [0.0] * 3
            abs_use_vec2 = [0.0] * 3

        num_verts = len(self.geom_node.verts)
        num_faces = len(self.geom_node.facelist.faces)
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
        pass

    def save_faces(self):
        pass

    def save_aabbs(self):
        pass
