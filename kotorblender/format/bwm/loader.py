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
from ...scene.roomwalkmesh import RoomWalkmesh
from ...scene.walkmesh import Walkmesh

from ..binreader import BinaryReader

WALKMESH_TYPE_PLACEABLE = 0
WALKMESH_TYPE_ROOM = 1


class Face:
    def __init__(self, vert_indices, material_id, normal, distance):
        self.vert_indices = vert_indices
        self.material_id = material_id
        self.normal = normal
        self.distance = distance

        self.adj_edges = []


class AABB:
    def __init__(self, bounding_box, face_idx, most_significant_plane, child_idx1, child_idx2):
        self.bounding_box = bounding_box
        self.face_idx = face_idx
        self.most_significant_plane = most_significant_plane
        self.child_idx1 = child_idx1
        self.child_idx2 = child_idx2


class BwmLoader:

    def __init__(self, path):
        self.path = path
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
        self.bwm.skip(4) # unknown
        self.num_adj_edges = self.bwm.get_uint32()
        self.off_adj_edges = self.bwm.get_uint32()
        self.num_outer_edges = self.bwm.get_uint32()
        self.off_outer_edges = self.bwm.get_uint32()
        self.num_perimeters = self.bwm.get_uint32()
        self.off_perimeters = self.bwm.get_uint32()

        if type == WALKMESH_TYPE_PLACEABLE:
            self.walkmesh = Walkmesh()
        else:
            self.walkmesh = RoomWalkmesh()

    def load_vertices(self):
        self.bwm.seek(self.off_verts)
        for _ in range(self.num_verts):
            vert = [self.bwm.get_float() for _ in range(3)]
            self.walkmesh.verts.append(vert)

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

        self.walkmesh.faces = [Face(vert_indices[i], material_ids[i], normals[i], distances[i]) for i in range(self.num_faces)]

    def load_aabbs(self):
        self.aabbs = []
        self.bwm.seek(self.off_aabbs)
        for _ in range(self.num_aabbs):
            bounding_box = [self.bwm.get_float() for _ in range(6)]
            face_idx = self.bwm.get_int32()
            self.bwm.skip(4) # unknown
            most_significant_plane = self.bwm.get_uint32()
            child_idx1 = self.bwm.get_uint32()
            child_idx2 = self.bwm.get_uint32()
            self.aabbs.append(AABB(bounding_box, face_idx, most_significant_plane, child_idx1, child_idx2))

    def load_adjacent_edges(self):
        self.bwm.seek(self.off_adj_edges)
        for i in range(self.num_adj_edges):
            self.walkmesh.faces[i].adj_edges = [self.bwm.get_int32() for _ in range(3)]

    def load_outer_edges(self):
        self.bwm.seek(self.off_outer_edges)
        for _ in range(self.num_outer_edges):
            index = self.bwm.get_uint32()
            transition = self.bwm.get_uint32()
            self.walkmesh.outerEdges.append((index, transition))

    def load_perimeters(self):
        self.bwm.seek(self.off_perimeters)
        self.perimeters = [self.bwm.get_uint32() for _ in range(self.num_perimeters)]
