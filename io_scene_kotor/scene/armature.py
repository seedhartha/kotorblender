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

import sys

import bpy

from mathutils import Quaternion, Vector

from ..constants import Classification, DummyType, MeshType
from ..utils import find_objects, is_skin_mesh, is_char_bone, is_char_dummy

from .animnode import AnimationNode


def rebuild_armature(mdl_root):
    if mdl_root.kb.classification != Classification.CHARACTER:
        return None

    # MDL root must have at least one skinmesh
    skinmeshes = find_objects(mdl_root, is_skin_mesh)
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
    armature.display_type = "STICK"
    armature_obj = bpy.data.objects.new(name, armature)
    armature_obj.show_in_front = True
    bpy.context.collection.objects.link(armature_obj)

    # Create armature bones
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode="EDIT")
    create_armature_bones(armature, mdl_root)
    bpy.ops.object.mode_set(mode="OBJECT")

    # Add Armature modifier to all skinmeshes
    for mesh in skinmeshes:
        modifier = None
        for mod in mesh.modifiers:
            if mod.type == "ARMATURE":
                modifier = mod
                break
        if not modifier:
            modifier = mesh.modifiers.new(name="Armature", type="ARMATURE")
        modifier.object = armature_obj

    bpy.context.view_layer.objects.active = mdl_root

    return armature_obj


def create_armature_bones(armature, obj, parent_bone=None):
    if not is_char_dummy(obj) and not is_char_bone(obj):
        for child in obj.children:
            create_armature_bones(armature, child, parent_bone)
        return
    bone = armature.edit_bones.new(obj.name)
    bone.parent = parent_bone
    bone.length = 1e-3
    bone.matrix = obj.matrix_world
    for child in obj.children:
        create_armature_bones(armature, child, bone)


def apply_object_keyframes(mdl_root, armature_obj):
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode="POSE")
    apply_object_keyframes_to_armature(mdl_root, armature_obj)
    bpy.ops.object.mode_set(mode="OBJECT")


def unapply_object_keyframes(mdl_root, armature_obj):
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.objects.active = mdl_root
    bpy.ops.object.mode_set(mode="OBJECT")
    unapply_object_keyframes_from_armature(mdl_root, mdl_root.name, armature_obj)


def apply_object_keyframes_to_armature(obj, armature_obj):
    if (
        obj.name in armature_obj.pose.bones
        and obj.animation_data
        and obj.animation_data.action
    ):
        action = obj.animation_data.action

        assert bpy.context.scene.frame_current == 0
        rest_location = obj.location
        rest_rotation = obj.rotation_quaternion

        keyframes = AnimationNode.get_keyframes(action)
        nested_keyframes = AnimationNode.nest_keyframes(keyframes)
        locations = []
        rotations = []
        for data_path, dp_keyframes in nested_keyframes.items():
            if data_path == "location":
                locations = [(values[0], Vector(values[1])) for values in dp_keyframes]
            if data_path == "rotation_quaternion":
                rotations = [
                    (values[0], Quaternion(values[1])) for values in dp_keyframes
                ]

        armature_anim_data = AnimationNode.get_or_create_animation_data(armature_obj)
        armature_action = AnimationNode.get_or_create_action(armature_obj.name)
        if not armature_anim_data.action:
            armature_anim_data.action = armature_action

        if locations:
            fcurves = [
                AnimationNode.get_or_create_fcurve(
                    armature_action, 'pose.bones["{}"].location'.format(obj.name), i
                )
                for i in range(3)
            ]
            keyframe_points = [fcurve.keyframe_points for fcurve in fcurves]
            for frame, location in locations:
                location_delta = location - rest_location
                for i in range(3):
                    keyframe = keyframe_points[i].insert(
                        frame, location_delta[i], options={"FAST"}
                    )
                    keyframe.interpolation = "LINEAR"
            for kfp in keyframe_points:
                kfp.update()
        if rotations:
            fcurves = [
                AnimationNode.get_or_create_fcurve(
                    armature_action,
                    'pose.bones["{}"].rotation_quaternion'.format(obj.name),
                    i,
                )
                for i in range(4)
            ]
            keyframe_points = [fcurve.keyframe_points for fcurve in fcurves]
            for frame, rotation in rotations:
                rotation_delta = rest_rotation.inverted() @ rotation
                for i in range(4):
                    keyframe = keyframe_points[i].insert(
                        frame, rotation_delta[i], options={"FAST"}
                    )
                    keyframe.interpolation = "LINEAR"
            for kfp in keyframe_points:
                kfp.update()

    for child in obj.children:
        apply_object_keyframes_to_armature(child, armature_obj)


def unapply_object_keyframes_from_armature(obj, root_name, armature_obj):
    if not armature_obj.animation_data:
        return
    armature_action = armature_obj.animation_data.action
    if not armature_action:
        return

    if obj.name in armature_obj.pose.bones:
        anim_data = AnimationNode.get_or_create_animation_data(obj)
        action = AnimationNode.get_or_create_action("{}.{}".format(root_name, obj.name))
        if not anim_data.action:
            anim_data.action = action

        assert bpy.context.scene.frame_current == 0
        rest_location = obj.location.copy()
        rest_rotation = obj.rotation_quaternion.copy()

        keyframes = AnimationNode.get_keyframes(
            armature_action, 0, sys.maxsize, 'pose.bones["{}"].'.format(obj.name)
        )
        nested_keyframes = AnimationNode.nest_keyframes(keyframes)
        locations = []
        rotations = []
        for data_path, dp_keyframes in nested_keyframes.items():
            if data_path == "location":
                locations = [(values[0], Vector(values[1])) for values in dp_keyframes]
            if data_path == "rotation_quaternion":
                rotations = [
                    (values[0], Quaternion(values[1])) for values in dp_keyframes
                ]
        if locations:
            fcurves = [
                AnimationNode.get_or_create_fcurve(action, "location", i)
                for i in range(3)
            ]
            keyframe_points = [fcurve.keyframe_points for fcurve in fcurves]
            for frame, location in locations:
                abs_location = rest_location + location
                for i in range(3):
                    keyframe = keyframe_points[i].insert(
                        frame, abs_location[i], options={"FAST"}
                    )
                    keyframe.interpolation = "LINEAR"
            for kfp in keyframe_points:
                kfp.update()
        if rotations:
            fcurves = [
                AnimationNode.get_or_create_fcurve(action, "rotation_quaternion", i)
                for i in range(4)
            ]
            keyframe_points = [fcurve.keyframe_points for fcurve in fcurves]
            for frame, rotation in rotations:
                abs_rotation = rest_rotation @ rotation
                for i in range(4):
                    keyframe = keyframe_points[i].insert(
                        frame, abs_rotation[i], options={"FAST"}
                    )
                    keyframe.interpolation = "LINEAR"
            for kfp in keyframe_points:
                kfp.update()

    for child in obj.children:
        unapply_object_keyframes_from_armature(child, root_name, armature_obj)
