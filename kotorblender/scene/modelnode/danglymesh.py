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

from ... import defines

from .trimesh import TrimeshNode

CONSTRAINTS = "constraints"


class DanglymeshNode(TrimeshNode):

    def __init__(self, name="UNNAMED"):
        TrimeshNode.__init__(self, name)
        self.nodetype = "danglymesh"

        self.meshtype = defines.Meshtype.DANGLYMESH
        self.period = 1.0
        self.tightness = 1.0
        self.displacement = 1.0
        self.constraints = []

    def set_object_data(self, obj, options):
        TrimeshNode.set_object_data(self, obj, options)

        obj.kb.period = self.period
        obj.kb.tightness = self.tightness
        obj.kb.displacement = self.displacement
        self.add_constraints_to_object(obj)

    def compact_vertices(self, unique_indices, split_normals):
        TrimeshNode.compact_vertices(self, unique_indices, split_normals)

        for new_idx, old_idx in enumerate(unique_indices):
            self.constraints[new_idx] = self.constraints[old_idx]

        num_unique = len(unique_indices)
        self.constraints = self.constraints[:num_unique]

    def add_constraints_to_object(self, obj):
        group = obj.vertex_groups.new(name=CONSTRAINTS)
        for vert_idx, constraint in enumerate(self.constraints):
            weight = constraint / 255
            group.add([vert_idx], weight, 'REPLACE')
        obj.kb.constraints = group.name

    def load_object_data(self, obj, options):
        TrimeshNode.load_object_data(self, obj, options)

        self.period = obj.kb.period
        self.tightness = obj.kb.tightness
        self.displacement = obj.kb.displacement

        if CONSTRAINTS not in self.eval_obj.vertex_groups:
            return
        group = self.eval_obj.vertex_groups[CONSTRAINTS]
        self.constraints = [255.0 * group.weight(i) for i in range(len(self.verts))]
