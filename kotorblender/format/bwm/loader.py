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

from ...exception.malformedfile import MalformedFile
from ...scene.areawalkmesh import AreaWalkmesh
from ...scene.modelnode.dummy import DummyNode
from ...scene.modelnode.trimesh import TrimeshNode
from ...scene.walkmesh import Walkmesh

from ..binreader import BinaryReader

WALKMESH_TYPE_SITUATED = 0
WALKMESH_TYPE_AREA = 1


class AABB:
    def __init__(self, bounding_box, face_idx, most_significant_plane, child_idx1, child_idx2):
        self.bounding_box = bounding_box
        self.face_idx = face_idx
        self.most_significant_plane = most_significant_plane
        self.child_idx1 = child_idx1
        self.child_idx2 = child_idx2


class BwmLoader:
    def __init__(self, path, model_name):
        self.path = path
        self.model_name = model_name
        self.bwm = BinaryReader(path, 'little')

    def load(self):
        print("Loading BWM '{}'".format(self.path))

        self.load_header()
        self.load_vertices()
        self.load_faces()
        self.load_aabbs()
        self.load_adjacent_edges()
        self.load_outer_edges()
        self.load_perimeters()

        return self.walkmesh

    def load_header(self):
        file_type = self.bwm.get_string(4)
        if file_type != "BWM ":
            raise MalformedFile("BWM file type is invalid: expected='BWM ', actual='{}'".format(file_type))

        version = self.bwm.get_string(4)
        type = self.bwm.get_uint32()
        rel_use_vec1 = [self.bwm.get_float() for _ in range(3)]
        rel_use_vec2 = [self.bwm.get_float() for _ in range(3)]
        abs_use_vec1 = [self.bwm.get_float() for _ in range(3)]
        abs_use_vec2 = [self.bwm.get_float() for _ in range(3)]
        position = [self.bwm.get_float() for _ in range(3)]
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

        if type == WALKMESH_TYPE_AREA:
            self.walkmesh = AreaWalkmesh()

            root_node = DummyNode("{}_wok".format(self.model_name))
            self.walkmesh.add_node(root_node)

            self.geom_node = TrimeshNode("{}_wok_geom".format(self.model_name))
            self.geom_node.roottype = "wok"
            self.geom_node.parent_name = root_node.name
            self.geom_node.position = position
            self.walkmesh.add_node(self.geom_node)
        else:
            walkmesh_type = "dwk" if self.path.endswith("dwk") else "pwk"
            self.walkmesh = Walkmesh(walkmesh_type)

            if walkmesh_type == "dwk":
                if self.path.endswith("0.dwk"):
                    dwk_state = "open1"
                elif self.path.endswith("1.dwk"):
                    dwk_state = "open2"
                else:
                    dwk_state = "closed"
                root_node_name = "{}_{}_{}".format(self.model_name, walkmesh_type, dwk_state)
                geom_node_name = "{}_{}_{}_geom".format(self.model_name, walkmesh_type, dwk_state)
            else:
                root_node_name = "{}_{}".format(self.model_name, walkmesh_type)
                geom_node_name = "{}_{}_geom".format(self.model_name, walkmesh_type)

            root_node = DummyNode(root_node_name)
            self.walkmesh.add_node(root_node)

            self.geom_node = TrimeshNode(geom_node_name)
            self.geom_node.roottype = walkmesh_type
            self.geom_node.parent_name = root_node.name
            self.geom_node.position = position
            self.walkmesh.add_node(self.geom_node)

            use1_node = DummyNode("{}_01".format(geom_node_name))
            use1_node.parent_name = geom_node_name
            use1_node.position = rel_use_vec1
            self.walkmesh.add_node(use1_node)

            use2_node = DummyNode("{}_02".format(geom_node_name))
            use2_node.parent_name = geom_node_name
            use2_node.position = rel_use_vec2
            self.walkmesh.add_node(use2_node)

    def load_vertices(self):
        self.bwm.seek(self.off_verts)
        for _ in range(self.num_verts):
            vert = [self.bwm.get_float() for _ in range(3)]
            self.geom_node.verts.append(vert)

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
            self.geom_node.facelist.faces.append(vert_indices[i])
            self.geom_node.facelist.uvIdx.append([0] * 3)
            self.geom_node.facelist.matId.append(material_ids[i])

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
        for i in range(self.num_adj_edges):
            adj_edges.append([self.bwm.get_int32() for _ in range(3)])

    def load_outer_edges(self):
        self.bwm.seek(self.off_outer_edges)
        for _ in range(self.num_outer_edges):
            index = self.bwm.get_uint32()
            transition = self.bwm.get_uint32()
            self.walkmesh.outer_edges.append((index, transition))

    def load_perimeters(self):
        self.bwm.seek(self.off_perimeters)
        self.perimeters = [self.bwm.get_uint32() for _ in range(self.num_perimeters)]
