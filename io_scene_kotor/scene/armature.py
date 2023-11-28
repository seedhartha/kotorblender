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

import bpy

from mathutils import Matrix, Quaternion, Vector

from ..defines import DummyType, MeshType

from .. import defines, utils

from .animnode import AnimationNode


def rebuild_armature(mdl_root):
    # Reset Pose
    bpy.context.scene.frame_set(0)

    # MDL root must have at least one skinmesh
    skinmeshes = utils.find_objects(mdl_root, utils.is_skin_mesh)
    if not skinmeshes:
        return None

    # Remove existing armature
    name = "Armature_" + mdl_root.name
    if name in bpy.context.collection.objects:
        armature_obj = bpy.context.collection.objects[name]
        armature_obj.animation_data_clear()
        armature = armature_obj.data
        bpy.context.collection.objects.unlink(armature_obj)
        bpy.data.armatures.remove(armature)

    # Create an armature and activate it
    armature = bpy.data.armatures.new(name)
    armature.display_type = 'STICK'
    armature_obj = bpy.data.objects.new(name, armature)
    armature_obj.show_in_front = True
    bpy.context.collection.objects.link(armature_obj)
    bpy.context.view_layer.objects.active = armature_obj

    # Create armature bones
    bpy.ops.object.mode_set(mode='EDIT')
    create_armature_bones(armature, mdl_root)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Copy object keyframes to armature
    bpy.ops.object.mode_set(mode='POSE')
    for anim in mdl_root.kb.anim_list:
        copy_object_keyframes_to_armature(anim, mdl_root, armature_obj)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add Armature modifier to all skinmeshes
    for mesh in skinmeshes:
        modifier = mesh.modifiers.new(name="Armature", type="ARMATURE")
        modifier.object = armature_obj

    bpy.context.view_layer.objects.active = mdl_root

    # Reset Pose
    bpy.context.scene.frame_set(0)

    return armature_obj


def create_armature_bones(armature, obj, parent_bone=None):
    bone = armature.edit_bones.new(obj.name)
    bone.parent = parent_bone
    bone.head = [0.0] * 3
    bone.tail = Vector((0.0, 1e-3, 0.0))
    bone.matrix = obj.matrix_world

    for child in obj.children:
        if child.type == 'EMPTY' and child.kb.dummytype != DummyType.NONE:
            continue
        if child.type == 'MESH' and child.kb.meshtype != MeshType.TRIMESH:
            continue
        create_armature_bones(armature, child, bone)


def copy_object_keyframes_to_armature(anim, obj, armature_obj):
    if obj.name in armature_obj.pose.bones and obj.animation_data and obj.animation_data.action:
        bone = armature_obj.pose.bones[obj.name]
        action = obj.animation_data.action

        # Calculate rest pose bone matrix, relative to parent
        rel_rest_mat = bone.bone.matrix_local
        if bone.parent:
            rel_rest_mat = bone.parent.bone.matrix_local.inverted() @ rel_rest_mat
        rel_rest_mat_inv = rel_rest_mat.inverted()
        rest_position, rest_orientation, _ = rel_rest_mat.decompose()

        # Extract position and orientation keyframes
        keyframes = AnimationNode.get_keyframes_in_range(action, anim.frame_start, anim.frame_end)
        flat_keyframes = AnimationNode.flatten_keyframes(keyframes)
        positions = []
        orientations = []
        for data_path, dp_keyframes in flat_keyframes.items():
            if data_path == "location":
                positions = [(values[0], Vector(values[1:])) for values in dp_keyframes]
            if data_path == "rotation_quaternion":
                orientations = [(values[0], Quaternion(values[1:])) for values in dp_keyframes]

        # Insert rest pose keyframes
        rest_frame = anim.frame_start - defines.ANIM_REST_POSE_OFFSET
        bone.matrix_basis = Matrix()
        bone.keyframe_insert("location", frame=rest_frame)
        bone.keyframe_insert("rotation_quaternion", frame=rest_frame)

        frames = set()
        for frame, _ in positions:
            frames.add(frame)
        for frame, _ in orientations:
            frames.add(frame)

        # Insert bone keyframes for each frame
        for frame in frames:
            position = sample_position(positions, frame, rest_position)
            orientation = sample_orientation(orientations, frame, rest_orientation)
            rel_pose_mat = Matrix.Translation(position) @ orientation.to_matrix().to_4x4()
            if bone.parent:
                bone.matrix_basis = rel_rest_mat_inv @ rel_pose_mat
            bone.keyframe_insert("location", frame=frame)
            bone.keyframe_insert("rotation_quaternion", frame=frame)

    for child in obj.children:
        copy_object_keyframes_to_armature(anim, child, armature_obj)


def sample_position(positions, frame_at, rest_position):
    left, right = None, None

    for frame, position in positions:
        if frame == frame_at:
            return position
        elif frame < frame_at:
            left = (frame, position)
        elif frame > frame_at:
            right = (frame, position)
            break

    if not left and not right:
        return rest_position
    if left and not right:
        return left[1]
    if right and not left:
        return right[1]

    return left[1].lerp(right[1], (frame_at - left[0]) / (right[0] - left[0]))


def sample_orientation(orientations, frame_at, rest_orientation):
    left, right = None, None

    for frame, orientation in orientations:
        if frame == frame_at:
            return orientation
        elif frame < frame_at:
            left = (frame, orientation)
        elif frame > frame_at:
            right = (frame, orientation)
            break

    if not left and not right:
        return rest_orientation
    if left and not right:
        return left[1]
    if right and not left:
        return right[1]

    return left[1].slerp(right[1], (frame_at - left[0]) / (right[0] - left[0]))
