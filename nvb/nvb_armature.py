import bpy
from mathutils import Matrix, Vector

from . import nvb_def, nvb_utils


def create_armature(rootdummy):
    # (Re)create armature
    armature_name = "Armature_"+rootdummy.name
    if armature_name in bpy.data.armatures:
        armature = bpy.data.armatures[armature_name]
        bpy.data.armatures.remove(armature)
    armature = bpy.data.armatures.new(armature_name)
    armature.display_type = 'STICK'
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
    mat_trans = Matrix.Translation(obj.nvb.restloc)
    mat_rot = nvb_utils.nwangle2quat(obj.nvb.restrot).to_matrix().to_4x4()
    mat_bone = mat_trans @ mat_rot
    if parent_bone:
        mat_bone = parent_bone.matrix @ mat_bone

    bone = armature.edit_bones.new(obj.name)
    bone.parent = parent_bone
    bone.head = [0.0]*3
    bone.tail = Vector((0.0, 1e-3, 0.0))
    bone.matrix = mat_bone

    # Recursively create bones from child objects
    for child in obj.children:
        _create_bones_recursive(armature, child, bone)
