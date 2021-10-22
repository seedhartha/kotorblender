import bpy
from mathutils import Matrix, Quaternion, Vector

from . import defines, utils


def recreate_armature(mdl_root):
    """
    Recreate an armature from bone nodes of the MDL root.
    :param mdl_root: MDL root object - must contain at least one skinmesh
    """
    if not utils.is_root_dummy(mdl_root):
        return None

    skinmeshes = utils.search_node_all(mdl_root, lambda o: o.kb.meshtype == defines.Meshtype.SKIN)
    if not skinmeshes:
        print("KotorBlender: WARNING - skinmeshes not found under the MDL root - armature creation aborted")
        return None

    # Create an armature and make it active
    armature_name = "Armature_"+mdl_root.name
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
    _create_bones_recursive(armature, mdl_root)

    # Enter Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add Armature modifier to all skinmeshes
    for mesh in skinmeshes:
        modifier = mesh.modifiers.new(name="Armature", type="ARMATURE")
        modifier.object = armature_object

    return armature_object


def _create_bones_recursive(armature, obj, parent_bone=None):
    """
    Recursively create armature bones from bone nodes.
    """
    mat_trans = Matrix.Translation(obj.kb.restloc)
    mat_rot = utils.nwangle2quat(obj.kb.restrot).to_matrix().to_4x4()
    mat_bone = mat_trans @ mat_rot
    if parent_bone:
        mat_bone = parent_bone.matrix @ mat_bone

    bone = armature.edit_bones.new(obj.name)
    bone.parent = parent_bone
    bone.head = [0.0]*3
    bone.tail = Vector((0.0, 1e-3, 0.0))
    bone.matrix = mat_bone

    for child in obj.children:
        _create_bones_recursive(armature, child, bone)


def create_armature_animations(mdl_root, armature_object):
    """
    Create armature animations from bone node keyframes.
    :param mdl_root: MDL root object from which to extract keyframes
    :param armature_object: armature object to create animations for
    """
    # Enter Pose Mode
    bpy.ops.object.mode_set(mode='POSE')

    # Copy keyframes from objects to armature bones
    mdl_objects = []
    utils.get_children_recursive(mdl_root, mdl_objects)
    for obj in mdl_objects:
        if not obj.animation_data:
            continue
        obj_action = obj.animation_data.action

        # Ensure that a pose bone exists by name
        if not obj.name in armature_object.pose.bones:
            print("Bone not found: " + obj.name)
            continue
        bone = armature_object.pose.bones[obj.name]

        # Compute rest pose matrix of a bone
        if bone.parent:
            restmat = bone.parent.bone.matrix_local.inverted() @ bone.bone.matrix_local
        else:
            restmat = bone.bone.matrix_local

        loc_curves = [obj_action.fcurves.find("location", index=i) for i in range(3)]
        if loc_curves.count(None) == 0:
            loc_keyframes = list(map(lambda curve: curve.keyframe_points, loc_curves))
            assert len(loc_keyframes[0]) == len(loc_keyframes[1]) and len(loc_keyframes[1]) == len(loc_keyframes[2])
            locations = [(kp_x.co[0], Vector([kp_x.co[1], kp_y.co[1], kp_z.co[1]])) for kp_x, kp_y, kp_z in zip(*loc_keyframes)]
        else:
            locations = []

        rot_curves = [obj_action.fcurves.find("rotation_quaternion", index=i) for i in range(4)]
        if rot_curves.count(None) == 0:
            rot_keyframes = list(map(lambda curve: curve.keyframe_points, rot_curves))
            assert len(rot_keyframes[0]) == len(rot_keyframes[1]) and len(rot_keyframes[1]) == len(rot_keyframes[2]) and len(rot_keyframes[2]) == len(rot_keyframes[3])
            rotations = [(kp_w.co[0], Quaternion([kp_w.co[1], kp_x.co[1], kp_y.co[1], kp_z.co[1]])) for kp_w, kp_x, kp_y, kp_z in zip(*rot_keyframes)]
        else:
            rotations = []

        for loc in locations:
            transmat = Matrix.Translation(loc[1])
            rotmat = restmat.to_quaternion().to_matrix().to_4x4()
            bonemat = restmat.inverted() @ transmat @ rotmat
            bone.matrix_basis = bonemat
            bone.keyframe_insert("location", frame=loc[0])

        for rot in rotations:
            transmat = Matrix.Translation(restmat.to_translation())
            rotmat = rot[1].to_matrix().to_4x4()
            bonemat = restmat.inverted() @ transmat @ rotmat
            bone.matrix_basis = bonemat
            bone.keyframe_insert("rotation_quaternion", frame=rot[0])

    # Enter Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')
