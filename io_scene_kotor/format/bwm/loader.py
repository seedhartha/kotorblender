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

from ...defines import DummyType, RootType, WalkmeshType
from ...scene.modelnode.aabb import AabbNode
from ...scene.modelnode.dummy import DummyNode
from ...scene.modelnode.trimesh import FaceList
from ...scene.walkmesh import Walkmesh

from ..binreader import BinaryReader

from .types import *


class BwmLoader:
    def __init__(self, path, model_name):
        self.path = path
        self.model_name = model_name
        self.bwm = BinaryReader(path, 'little')

        self.position = [0.0] * 3
        self.verts = []
        self.facelist = FaceList()
        self.outer_edges = []

    def load(self):
        self.load_header()
        self.load_vertices()
        self.load_faces()
        self.load_aabbs()
        self.load_adjacent_edges()
        self.load_outer_edges()
        self.load_perimeters()

        return self.new_walkmesh()

    def load_header(self):
        file_type = self.bwm.get_string(4)
        if file_type != "BWM ":
            raise RuntimeError("BWM file type is invalid: expected='BWM ', actual='{}'".format(file_type))

        version = self.bwm.get_string(4)
        self.bwm_type = self.bwm.get_uint32()
        self.rel_use_vec1 = [self.bwm.get_float() for _ in range(3)]
        self.rel_use_vec2 = [self.bwm.get_float() for _ in range(3)]
        abs_use_vec1 = [self.bwm.get_float() for _ in range(3)]
        abs_use_vec2 = [self.bwm.get_float() for _ in range(3)]
        self.position = [self.bwm.get_float() for _ in range(3)]
        self.num_verts = self.bwm.get_uint32()
        self.off_verts = self.bwm.get_uint32()
        self.num_faces = self.bwm.get_uint32()
        self.off_vert_indices = self.bwm.get_uint32()
        self.off_material_ids = self.bwm.get_uint32()
        self.off_normals = self.bwm.get_uint32()
        self.off_distances = self.bwm.get_uint32()
        self.num_aabbs = self.bwm.get_uint32()
        self.off_aabbs = self.bwm.get_uint32()
        self.bwm.skip(4)  # unknown
        self.num_adj_edges = self.bwm.get_uint32()
        self.off_adj_edges = self.bwm.get_uint32()
        self.num_outer_edges = self.bwm.get_uint32()
        self.off_outer_edges = self.bwm.get_uint32()
        self.num_perimeters = self.bwm.get_uint32()
        self.off_perimeters = self.bwm.get_uint32()

    def load_vertices(self):
        self.bwm.seek(self.off_verts)
        for _ in range(self.num_verts):
            vert = [self.bwm.get_float() - self.position[i] for i in range(3)]
            self.verts.append(vert)

    def load_faces(self):
        vert_indices = []
        self.bwm.seek(self.off_vert_indices)
        for _ in range(self.num_faces):
            vert_indices.append([self.bwm.get_uint32() for _ in range(3)])

        self.bwm.seek(self.off_material_ids)
        material_ids = [self.bwm.get_uint32() for _ in range(self.num_faces)]

        normals = []
        self.bwm.seek(self.off_normals)
        for _ in range(self.num_faces):
            normal = [self.bwm.get_float() for _ in range(3)]
            normals.append(normal)

        self.bwm.seek(self.off_distances)
        distances = [self.bwm.get_float() for _ in range(self.num_faces)]

        for i in range(self.num_faces):
            self.facelist.vertices.append(vert_indices[i])
            self.facelist.uv.append([0] * 3)
            self.facelist.materials.append(material_ids[i])

    def load_aabbs(self):
        aabbs = []
        self.bwm.seek(self.off_aabbs)
        for _ in range(self.num_aabbs):
            bounding_box = [self.bwm.get_float() for _ in range(6)]
            face_idx = self.bwm.get_int32()
            self.bwm.skip(4)  # unknown
            most_significant_plane = self.bwm.get_uint32()
            child_idx1 = self.bwm.get_uint32()
            child_idx2 = self.bwm.get_uint32()
            aabbs.append(AABB(bounding_box, face_idx, most_significant_plane, child_idx1, child_idx2))

    def load_adjacent_edges(self):
        adj_edges = []
        self.bwm.seek(self.off_adj_edges)
        for _ in range(self.num_adj_edges):
            adj_edges.append([self.bwm.get_int32() for _ in range(3)])

    def load_outer_edges(self):
        self.bwm.seek(self.off_outer_edges)
        for _ in range(self.num_outer_edges):
            index = self.bwm.get_uint32()
            transition = self.bwm.get_int32()
            self.outer_edges.append((index, transition))

    def load_perimeters(self):
        self.bwm.seek(self.off_perimeters)
        self.perimeters = [self.bwm.get_uint32() for _ in range(self.num_perimeters)]

    def new_walkmesh(self):
        if self.bwm_type == BWM_TYPE_WOK:
            return self.new_area_walkmesh()
        elif self.bwm_type == BWM_TYPE_PWK_DWK:
            return self.new_placeable_walkmesh()
        else:
            raise RuntimeError("Unsupported walkmesh type: " + str(self.bwm_type))

    def new_area_walkmesh(self):
        root_node = DummyNode("{}_wok".format(self.model_name))

        geom_node = AabbNode("{}_wok_wg".format(self.model_name))
        geom_node.roottype = RootType.WALKMESH
        geom_node.position = self.position
        geom_node.parent = root_node
        geom_node.verts = self.verts
        geom_node.facelist = self.facelist
        geom_node.roomlinks = {edge_idx: transition for edge_idx, transition in self.outer_edges if transition != -1}

        root_node.children.append(geom_node)

        walkmesh = Walkmesh(WalkmeshType.WOK)
        walkmesh.root_node = root_node

        return walkmesh

    def new_placeable_walkmesh(self):
        walkmesh_type = WalkmeshType.DWK if self.path.endswith("dwk") else WalkmeshType.PWK
        if walkmesh_type == WalkmeshType.DWK:
            if self.path.endswith("1.dwk"):
                dwk_state = "open1"
            elif self.path.endswith("2.dwk"):
                dwk_state = "open2"
            else:
                dwk_state = "closed"
            root_name = "{}_dwk_{}".format(self.model_name, dwk_state)
            geom_name = "{}_dwk_wg_{}".format(self.model_name, dwk_state)
            use_name1 = "{}_dwk_dp_{}_01".format(self.model_name, dwk_state)
            use_name2 = "{}_dwk_dp_{}_02".format(self.model_name, dwk_state)
        else:
            root_name = "{}_pwk".format(self.model_name)
            geom_name = "{}_pwk_wg".format(self.model_name)
            use_name1 = "{}_pwk_use01".format(geom_name)
            use_name2 = "{}_pwk_use02".format(geom_name)

        root_node = DummyNode(root_name)
        root_node.dummytype = DummyType.DWKROOT if walkmesh_type == WalkmeshType.DWK else DummyType.PWKROOT

        geom_node = AabbNode(geom_name)
        geom_node.roottype = RootType.WALKMESH
        geom_node.position = self.position
        geom_node.parent = root_node
        geom_node.verts = self.verts
        geom_node.facelist = self.facelist

        use_node1 = DummyNode(use_name1)
        use_node1.dummytype = DummyType.USE1
        use_node1.position = self.rel_use_vec1
        use_node1.parent = root_node

        use_node2 = DummyNode(use_name2)
        use_node2.dummytype = DummyType.USE2
        use_node2.position = self.rel_use_vec2
        use_node2.parent = root_node

        root_node.children.append(geom_node)
        root_node.children.append(use_node1)
        root_node.children.append(use_node2)

        walkmesh = Walkmesh(walkmesh_type)
        walkmesh.root_node = root_node

        return walkmesh
