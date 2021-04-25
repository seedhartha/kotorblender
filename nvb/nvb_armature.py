import bpy
from mathutils import Vector

from . import nvb_def, nvb_utils


def create_armature(rootdummy):
    # (Re)create armature
    armature_name = "Armature_"+rootdummy.name
    if armature_name in bpy.data.armatures:
        armature = bpy.data.armatures[armature_name]
        bpy.data.armatures.remove(armature)
    armature = bpy.data.armatures.new(armature_name)
    armature_object = bpy.data.objects.new(armature_name, armature)
    armature_object.show_in_front = True
    bpy.context.collection.objects.link(armature_object)
    bpy.context.view_layer.objects.active = armature_object

    # Enter Edit Mode
    bpy.ops.object.mode_set(mode='EDIT')

    _create_bones_recursive(armature, rootdummy)

    # Enter Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add Armature modifier to all skinmeshes
    skinmeshes = nvb_utils.search_node_all(rootdummy, lambda o: o.nvb.meshtype == nvb_def.Meshtype.SKIN)
    for mesh in skinmeshes:
        modifier = mesh.modifiers.new(name="Armature", type="ARMATURE")
        modifier.object = armature_object

    return armature_object


def _create_bones_recursive(armature, obj, parent_bone=None):
    # Skip Trimeshes whose Render flag is set to True
    if (obj.type == 'MESH') and obj.nvb.render:
        return

    bone = armature.edit_bones.new(obj.name)
    bone.parent = parent_bone
    bone.head = obj.matrix_world.to_translation()

    if obj.children:
        # If object has children, set bone tail to the average child location
        bone.tail = Vector([0.0] * 3)
        for child in obj.children:
            bone.tail += child.matrix_world.to_translation()
        bone.tail /= float(len(obj.children))

        # Recursively create bones from child objects
        for child in obj.children:
            _create_bones_recursive(armature, child, bone)
    else:
        # If object has no children, place bone tail away from its parent
        parent_dir = (parent_bone.tail - parent_bone.head).normalized()
        bone.tail = bone.head + 0.1 * parent_dir
