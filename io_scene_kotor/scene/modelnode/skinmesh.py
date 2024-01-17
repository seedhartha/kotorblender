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

from ...constants import MeshType, NodeType
from .trimesh import TrimeshNode


class SkinmeshNode(TrimeshNode):
    def __init__(self, name="UNNAMED"):
        TrimeshNode.__init__(self, name)
        self.nodetype = NodeType.SKIN
        self.meshtype = MeshType.SKIN

    def apply_edge_loop_mesh(self, mesh, obj):
        TrimeshNode.apply_edge_loop_mesh(self, mesh, obj)
        self.apply_bone_weights(mesh, obj)

    def apply_bone_weights(self, mesh, obj):
        groups = dict()
        for vert_idx, vert_weights in enumerate(mesh.weights):
            for bone_name, weight in vert_weights:
                if bone_name in groups:
                    groups[bone_name].add([vert_idx], weight, "REPLACE")
                else:
                    group = obj.vertex_groups.new(name=bone_name)
                    group.add([vert_idx], weight, "REPLACE")
                    groups[bone_name] = group

    def unapply_edge_loop_mesh(self, obj):
        mesh = TrimeshNode.unapply_edge_loop_mesh(self, obj)
        self.unapply_bone_weights(obj, mesh)
        return mesh

    def unapply_bone_weights(self, obj, mesh):
        mesh.weights = [[]] * len(mesh.verts)
        for vert_idx in range(len(mesh.verts)):
            vert = obj.data.vertices[vert_idx]
            vert_weights = []
            for group_weight in vert.groups:
                if group_weight == 0.0:
                    continue
                group = obj.vertex_groups[group_weight.group]
                vert_weights.append((group.name, group_weight.weight))
            vert_weights.sort(key=lambda x: x[1], reverse=True)
            if len(vert_weights) > 4:
                vert_weights = vert_weights[0:3]
            mesh.weights[vert_idx] = vert_weights
