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

CONSTRAINTS = "constraints"


class DanglymeshNode(TrimeshNode):
    def __init__(self, name="UNNAMED"):
        TrimeshNode.__init__(self, name)
        self.nodetype = NodeType.DANGLYMESH
        self.meshtype = MeshType.DANGLYMESH
        self.period = 1.0
        self.tightness = 1.0
        self.displacement = 1.0

    def apply_edge_loop_mesh(self, mesh, obj):
        TrimeshNode.apply_edge_loop_mesh(self, mesh, obj)
        self.apply_vertex_constraints(mesh, obj)

    def apply_vertex_constraints(self, mesh, obj):
        group = obj.vertex_groups.new(name=CONSTRAINTS)
        for vert_idx, constraint in enumerate(mesh.constraints):
            weight = constraint / 255
            group.add([vert_idx], weight, "REPLACE")
        obj.kb.constraints = group.name

    def set_object_data(self, obj, options):
        TrimeshNode.set_object_data(self, obj, options)
        obj.kb.period = self.period
        obj.kb.tightness = self.tightness
        obj.kb.displacement = self.displacement

    def load_object_data(self, obj, eval_obj, options):
        TrimeshNode.load_object_data(self, obj, eval_obj, options)
        self.period = obj.kb.period
        self.tightness = obj.kb.tightness
        self.displacement = obj.kb.displacement

    def unapply_edge_loop_mesh(self, obj):
        mesh = TrimeshNode.unapply_edge_loop_mesh(self, obj)
        self.unapply_vertex_constraints(obj, mesh)
        return mesh

    def unapply_vertex_constraints(self, obj, mesh):
        if CONSTRAINTS not in obj.vertex_groups:
            mesh.constraints = [0] * range(len(mesh.verts))
            return
        group = obj.vertex_groups[CONSTRAINTS]
        mesh.constraints = [255.0 * group.weight(i) for i in range(len(mesh.verts))]
