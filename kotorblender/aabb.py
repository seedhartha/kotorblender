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

from mathutils import Vector


def generate_tree(aabb_tree, face_list, rlevel=0):
    if rlevel > 128:
        raise ValueError("rlevel must not exceed 128, but is equal to {}".format(rlevel))

    if not face_list:
        raise ValueError("face_list must not be empty")

    # Calculate bounding box min/max and centroid
    bb_min = Vector((100000.0, 100000.0, 100000.0))
    bb_max = Vector((-100000.0, -100000.0, -100000.0))
    bb_centroid = Vector()
    for face in face_list:
        face_verts = face[1]
        for vert in face_verts:
            for axis in range(3):
                if bb_min[axis] > vert[axis]:
                    bb_min[axis] = vert[axis]
                if bb_max[axis] < vert[axis]:
                    bb_max[axis] = vert[axis]
        face_centroid = face[2]
        bb_centroid = bb_centroid + face_centroid
    bb_centroid = bb_centroid / len(face_list)

    # Only one face left - this node is a leaf
    if len(face_list) == 1:
        face_idx = face_list[0][0]
        aabb_tree.append([*bb_min[:3], *bb_max[:3], -1, -1, face_idx, 0])
        return

    # Find longest axis
    split_axis = 0
    bb_size = bb_max - bb_min
    if bb_size.y > bb_size.x:
        split_axis = 1
    if bb_size.z > bb_size.y:
        split_axis = 2

    # Change axis in case points are coplanar with the split plane
    change_axis = True
    for face in face_list:
        face_centroid = face[2]
        change_axis = change_axis and face_centroid[split_axis] == bb_centroid[split_axis]
    if change_axis:
        split_axis += 1
        if split_axis == 3:
            split_axis = 0

    # Put faces on the left and right side of the split plane into separate
    # lists. Try all axises to prevent tree degeneration.
    face_list_left = []
    face_list_right = []
    tested_axes = 1
    while True:
        # Sort faces by side
        face_list_left = []
        face_list_right = []
        for face in face_list:
            face_centroid = face[2]
            if face_centroid[split_axis] < bb_centroid[split_axis]:
                face_list_left.append(face)
            else:
                face_list_right.append(face)

        # Neither list is empty, this split will do just fine
        if face_list_left and face_list_right:
            break

        # At least one of the lists is empty - try another axis
        split_axis += 1
        if split_axis == 3:
            split_axis = 0
        tested_axes += 1
        if tested_axes == 3:
            raise RuntimeError("Generated tree is degenerate")

    node = [*bb_min[:3], *bb_max[:3], 0, 0, -1, 1 + split_axis]
    aabb_tree.append(node)
    node[6] = len(aabb_tree)
    generate_tree(aabb_tree, face_list_left, rlevel+1)
    node[7] = len(aabb_tree)
    generate_tree(aabb_tree, face_list_right, rlevel+1)
