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

BWM_TYPE_PWK_DWK = 0
BWM_TYPE_WOK = 1


class AABB:
    def __init__(self, bounding_box, face_idx, most_significant_plane, child_idx1, child_idx2):
        self.bounding_box = bounding_box
        self.face_idx = face_idx
        self.most_significant_plane = most_significant_plane
        self.child_idx1 = child_idx1
        self.child_idx2 = child_idx2
