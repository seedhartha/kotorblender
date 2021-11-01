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

    def add_skin_groups_to_object(self, obj):
        skin_group_dict = {}
        for vert_idx, vert_memberships in enumerate(self.weights):
            for membership in vert_memberships:
                if membership[0] in skin_group_dict:
                    skin_group_dict[membership[0]].add([vert_idx], membership[1], 'REPLACE')
                else:
                    vgroup = obj.vertex_groups.new(name=membership[0])
                    skin_group_dict[membership[0]] = vgroup
                    vgroup.add([vert_idx], membership[1], 'REPLACE')

    def load_object_data(self, obj):
        TrimeshNode.load_object_data(self, obj)
