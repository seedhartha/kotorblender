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

from mathutils import Matrix, Vector

from ..defines import Meshtype

from .. import utils


def recreate_armature(mdl_root):
    if not utils.is_mdl_root(mdl_root):
        return None

    skinmeshes = utils.get_children_recursive(mdl_root, utils.is_skin_mesh)
    if not skinmeshes:
        return None

    # Create an armature and make it active
    armature_name = "Armature_" + mdl_root.name
    if armature_name in bpy.data.armatures:
        armature = bpy.data.armatures[armature_name]
        if armature.animation_data:
            bpy.data.actions.remove(armature.animation_data.action)
        bpy.data.armatures.remove(armature)
    armature = bpy.data.armatures.new(armature_name)
    armature.display_type = 'STICK'
    armature_object = bpy.data.objects.new(armature_name, armature)
    armature_object.show_in_front = True
    bpy.context.collection.objects.link(armature_object)
    bpy.context.view_layer.objects.active = armature_object

    # Enter Edit Mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Recursively create armature bones from bone nodes
    create_bones_recursive(armature, mdl_root)

    # Enter Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add Armature modifier to all skinmeshes
    for mesh in skinmeshes:
        modifier = mesh.modifiers.new(name="Armature", type="ARMATURE")
        modifier.object = armature_object

    return armature_object


def create_bones_recursive(armature, obj, parent_bone=None):
    mat_trans = Matrix.Translation(obj.location)
    mat_rot = obj.rotation_quaternion.to_matrix().to_4x4()
    mat_bone = mat_trans @ mat_rot
    if parent_bone:
        mat_bone = parent_bone.matrix @ mat_bone

    bone = armature.edit_bones.new(obj.name)
    bone.parent = parent_bone
    bone.head = [0.0] * 3
    bone.tail = Vector((0.0, 1e-3, 0.0))
    bone.matrix = mat_bone

    for child in obj.children:
        if child.type == 'MESH' and child.kb.meshtype == Meshtype.SKIN:
            continue
        create_bones_recursive(armature, child, bone)
