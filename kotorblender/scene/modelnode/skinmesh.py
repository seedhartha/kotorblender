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


class SkinmeshNode(TrimeshNode):

    def __init__(self, name="UNNAMED"):
        TrimeshNode.__init__(self, name)
        self.nodetype = "skin"

        self.meshtype = defines.Meshtype.SKIN
        self.weights = []

    def set_object_data(self, obj):
        TrimeshNode.set_object_data(self, obj)

        self.add_skin_groups_to_object(obj)

    def compact_vertices(self, unique_indices, split_normals):
        TrimeshNode.compact_vertices(self, unique_indices, split_normals)

        for new_idx, old_idx in enumerate(unique_indices):
            self.weights[new_idx] = self.weights[old_idx]

        num_unique = len(unique_indices)
        self.weights = self.weights[:num_unique]

    def add_skin_groups_to_object(self, obj):
        groups = dict()
        for vert_idx, vert_weights in enumerate(self.weights):
            for bone_name, weight in vert_weights:
                if bone_name in groups:
                    groups[bone_name].add([vert_idx], weight, 'REPLACE')
                else:
                    group = obj.vertex_groups.new(name=bone_name)
                    group.add([vert_idx], weight, 'REPLACE')
                    groups[bone_name] = group

    def load_object_data(self, obj):
        TrimeshNode.load_object_data(self, obj)

        for vert in obj.data.vertices:
            vert_weights = []
            for group_weight in vert.groups:
                group = obj.vertex_groups[group_weight.group]
                vert_weights.append((group.name, group_weight.weight))
            self.weights.append(vert_weights)
