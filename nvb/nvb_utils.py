import math
import os
import sys

import bpy
from mathutils import Quaternion, Vector

from . import nvb_def


def is_null(s):
    return (not s or s.lower() == nvb_def.null.lower())


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def isclose_3f(a, b, rel_tol=0.1):
    return (isclose(a[0], b[0], rel_tol) and
            isclose(a[1], b[1], rel_tol) and
            isclose(a[2], b[2], rel_tol))


def is_number(s):
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True


def get_name(s):
    """
    To be able to switch to case sensitive and back
    Still not certain mdl node names are case sensitive
    """
    return s


def get_real_name(s):
    """
    Do a case insensitive search through existing objects,
    returning name or None if not found
    """
    try:
        return [name for name in bpy.data.objects.keys() if name.lower() == s.lower()][0]
    except:
        return None


def get_valid_exports(rootDummy, validExports):
    validExports.append(rootDummy.name)
    for child in rootDummy.children:
        get_valid_exports(child, validExports)


def ancestor_node(obj, test):
    try:
        if test(obj):
            return obj
    except:
        pass
    if obj is not None and obj.parent:
        return ancestor_node(obj.parent, test)
    return None


def search_node(obj, test):
    try:
        if obj and test(obj):
            return obj
        match = None
        for child in obj.children:
            match = search_node(child, test)
            if match is not None:
                return match
    except:
        pass
    return None


def search_node_all(obj, test):
    nodes = []
    for child in obj.children:
        nodes.extend(search_node_all(child, test))
    try:
        if obj and test(obj):
            nodes.append(obj)
    except:
        pass
    return nodes


def search_node_in_model(obj, test):
    """
    Helper to search through entire model from any starting point in hierarchy;
    walks up to model root and performs find-one search.
    """
    return search_node(ancestor_node(obj, is_root_dummy), test)


def is_root_dummy(obj, dummytype = nvb_def.Dummytype.MDLROOT):
    if not obj:
        return False
    return (obj.type == 'EMPTY') and (obj.nvb.dummytype == dummytype)


def get_node_type(obj):
    """
    Get the node type (dummy, trimesh, skin, ...) of the blender object
    """
    objType  = obj.type
    if objType == 'EMPTY':
        if   obj.nvb.dummytype == nvb_def.Dummytype.PATCH:
            return 'patch'
        elif obj.nvb.dummytype == nvb_def.Dummytype.REFERENCE:
            return 'reference'
    elif objType == 'MESH':
        if   obj.nvb.meshtype == nvb_def.Meshtype.TRIMESH:
            return 'trimesh'
        elif obj.nvb.meshtype == nvb_def.Meshtype.DANGLYMESH:
            return 'danglymesh'
        elif obj.nvb.meshtype == nvb_def.Meshtype.SKIN:
            return 'skin'
        elif obj.nvb.meshtype == nvb_def.Meshtype.EMITTER:
            return 'emitter'
        elif obj.nvb.meshtype == nvb_def.Meshtype.AABB:
            return 'aabb'
    elif objType == 'LIGHT':
        return 'light'

    return 'dummy'


def get_children_recursive(obj, obj_list):
    """
    Helper following neverblender naming, compatibility layer
    Get all descendent nodes under obj in a flat list
    """
    obj_list.extend(search_node_all(obj, lambda o: o is not None))


def get_mdl_root_from_object(obj):
    return ancestor_node(obj, is_root_dummy)


def get_mdl_root_from_context():
    """
    Method to find the best MDL root dummy based on user intent
    """
    # 1. Search first selected object, if any
    if bpy.context.selected_objects:
        obj = bpy.context.selected_objects[0]
        match = get_mdl_root_from_object(obj)
        if match:
            return match

    # 2. Search Empty objects in the current collection
    matches = [o for o in bpy.context.collection.objects if is_root_dummy(o)]
    if matches:
        return matches[0]

    # 3. Search all Empty objects
    matches = [m for m in bpy.data.objects if is_root_dummy(m)]
    if matches:
        return matches[0]

    return None


def get_fcurve(action, data_path, index=0, group_name=None):
    """Get the fcurve with specified properties or create one."""
    fcu = action.fcurves.find(data_path, index=index)
    if not fcu:  # Create new Curve
        fcu = action.fcurves.new(data_path=data_path, index=index)
        if group_name:  # Add curve to group
            if group_name in action.groups:
                group = action.groups[group_name]
            else:
                group = action.groups.new(group_name)
            fcu.group = group
    return fcu


def get_action(target, action_name):
    """Get the active action or create one."""
    # Get animation data, create if needed
    anim_data = target.animation_data
    if not anim_data:
        anim_data = target.animation_data_create()
    # Get action, create if needed
    action = anim_data.action
    if not action:
        action = bpy.data.actions.new(name=action_name)
        # action.use_fake_user = True
        anim_data.action = action
    return action


def get_last_keyframe(root_obj):
    """Get the last keyed frame of this object and its children."""
    def get_max_frame(target):
        frame = nvb_def.anim_globstart
        if target:
            if target.animation_data and target.animation_data.action:
                for fcu in target.animation_data.action.fcurves:
                    frame = max(max([p.co[0] for p in fcu.keyframe_points],
                                    default=0), frame)
            return frame
    obj_list = [root_obj]
    get_children_recursive(root_obj, obj_list)
    frame_list = [nvb_def.anim_globstart]
    for obj in obj_list:
        frame_list.append(get_max_frame(obj))
        mat = obj.active_material
        if mat:
            frame_list.append(get_max_frame(mat))
        part_sys = obj.particle_systems.active
        if part_sys:
            frame_list.append(get_max_frame(part_sys.settings))
    return max(frame_list)


def get_frame_interval(obj):
    """Get the first and last keyed frame of this object and its children."""
    obj_list = [obj]
    get_children_recursive(obj, obj_list)
    max_frame = nvb_def.anim_globstart
    min_frame = nvb_def.anim_globstart + 1000
    for o in obj_list:
        if o.animation_data and o.animation_data.action:
            action = o.animation_data.action
            for fcu in action.fcurves:
                max_frame = max(max([p.co[0] for p in fcu.keyframe_points],
                                    default=0), max_frame)
                min_frame = min(min([p.co[0] for p in fcu.keyframe_points],
                                    default=0), min_frame)
    return (min_frame, max_frame)


def create_anim_list_item(mdl_base, check_keyframes=False):
    """Append a new animation at the and of the animation list."""
    last_frame = max([nvb_def.anim_globstart] +
                     [a.frameEnd for a in mdl_base.nvb.animList])
    if check_keyframes:
        last_frame = max(last_frame, get_last_keyframe(mdl_base))
    anim = mdl_base.nvb.animList.add()
    anim.name = mdl_base.name
    start = int(math.ceil((last_frame + nvb_def.anim_offset) / 10.0)) * 10
    anim.frameStart = start
    anim.frameEnd = start
    return anim


def str2identifier(s):
    """Convert to lower case. Convert 'null' to empty string."""
    if (not s or s.lower() == nvb_def.null):
        return ''
    return s.lower()


def toggle_anim_focus(scene, mdl_base):
    """Set the Start and end frames of the timeline."""
    animList = mdl_base.nvb.animList
    animIdx = mdl_base.nvb.animListIdx

    anim = animList[animIdx]
    if (scene.frame_start == anim.frameStart) and \
       (scene.frame_end == anim.frameEnd):
        # Set timeline to include all current
        scene.frame_start = 1
        lastFrame = 1
        for anim in animList:
            if lastFrame < anim.frameEnd:
                lastFrame = anim.frameEnd
        scene.frame_end = lastFrame
    else:
        # Set timeline to the current animation
        scene.frame_start = anim.frameStart
        scene.frame_end = anim.frameEnd
    scene.frame_current = scene.frame_start


def check_anim_bounds(mdl_base):
    """
    Check for animations of this mdl base.

    Returns true, if are non-overlapping and only use by one object.
    """
    if len(mdl_base.nvb.animList) < 2:
        return True
    # TODO: use an interval tree
    animBounds = [(a.frameStart, a.frameEnd, idx) for idx, a in
                  enumerate(mdl_base.nvb.animList)]
    for a1 in animBounds:
        for a2 in animBounds:
            if (a1[0] <= a2[1]) and (a2[0] <= a1[1]) and (a1[2] != a2[2]):
                return False
    return True


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def get_image_filename(image):
    """
    Returns the image name without the file extension.
    """
    # Try getting the image name from the image source path
    filename = os.path.splitext(os.path.basename(image.filepath))[0]
    if (filename == ''):
        # If that doesn't work, get it from the image name
        filename = os.path.splitext(os.path.basename(image.name))[0]

    return filename


def get_shagr_id(shagrName):
    return  int(shagrName[-4:])


def get_shagr_name(shagrId):
    return  nvb_def.shagrPrefix + "{0:0>4}".format(shagrId)


def is_shagr(vgroup):
    """
    Determines wether vertex_group ist a shading group or not
    """
    return (nvb_def.shagrPrefix in vgroup.name)


def set_object_rotation_aurora(obj, nwangle):
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = Quaternion((nwangle[0], nwangle[1], nwangle[2]), nwangle[3])


def get_aurora_rot_from_object(obj):
    q = obj.rotation_quaternion
    return [q.axis[0], q.axis[1], q.axis[2], q.angle]


def get_aurora_rot_from_matrix(matrix):
    """
    Get the rotation from a 4x4 matrix as Axis Angle in the format used by NWN
    NWN uses     [X, Y, Z, Angle]
    Blender uses [Angle, X, Y, Z]
    """
    q = matrix.to_quaternion()
    return [q.axis[0], q.axis[1], q.axis[2], q.angle]


def get_aurora_scale(obj):
    """
    If the scale is uniform, i.e, x=y=z, we will return
    the value. Else we'll return 1.
    """
    scale = obj.scale
    if (scale[0] == scale[1] == scale[2]):
        return scale[0]

    return 1.0


def nwtime2frame(time, fps = nvb_def.fps):
    """
    For animations: Convert key time to frame number
    """
    return round(fps*time)


def frame2nwtime(frame, fps = nvb_def.fps):
    return round(frame / fps, 7)


def quat2nwangle(quatValues):
    quat = Quaternion(quatValues)
    return [quat.axis[0], quat.axis[1], quat.axis[2], quat.angle]


def copy_anim_scene_check(theOriginal, newSuffix, oldSuffix = ''):
    """
    Checks if it possible to copy the object and it's children with the suffix
    It would be impossible if:
        - An object with the same name already exists
        - Object data with the same name already exists
    """
    oldName = theOriginal.name
    newName = 'ERROR'
    if oldSuffix:
        if oldName.endswith(oldSuffix):
            newName = oldName[:len(oldName)-len(oldSuffix)]
            if newName.endswith('.'):
                newName = newName[:len(newName)-1]
        else:
            newName = oldName.partition('.')[0]
            if not newName:
                print("Kotorblender: Unable to generate new name")
                return False
        newName = newName + '.' + newSuffix
    else:
        newName = oldName + '.' + newSuffix

    if newName in bpy.data.objects:
        print("Kotorblender: Duplicate object")
        return False

    objType = theOriginal.type
    if (objType == 'LIGHT'):
        if newName in bpy.data.lights:
            print("Kotorblender: Duplicate light")
            return False
    elif (objType == 'MESH'):
        if theOriginal.animation_data:
            action = theOriginal.animation_data.action
            for fcurve in action.fcurves:
                dataPath = fcurve.data_path
                if dataPath.endswith('alpha_factor'):
                    if newName in bpy.data.materials:
                        print("Kotorblender: Duplicate Material")
                        return False

        if newName in bpy.data.actions:
            print("Kotorblender: Duplicate Action")
            return False

    valid = True
    for child in theOriginal.children:
        valid = valid and copy_anim_scene_check(child, newSuffix, oldSuffix)

    return valid


def copy_anim_scene(scene, theOriginal, newSuffix, oldSuffix = '', parent = None):
    """
    Copy object and all it's children to scene.
    For object with simple (position, rotation) or no animations we
    create a linked copy.
    For alpha animation we'll need to copy the data too.
    """
    oldName = theOriginal.name
    newName = 'ERROR'
    if oldSuffix:
        if oldName.endswith(oldSuffix):
            newName = oldName[:len(oldName)-len(oldSuffix)]
            if newName.endswith('.'):
                newName = newName[:len(newName)-1]
        else:
            newName = oldName.partition('.')[0]
            if not newName:
                return
        newName = newName + '.' + newSuffix
    else:
        newName = oldName + '.' + newSuffix

    theCopy        = theOriginal.copy()
    theCopy.name   = newName
    theCopy.parent = parent

    # Do not bring in the unhandled ASCII data for geometry nodes
    # when cloning for animation
    if 'rawascii' in theCopy.nvb:
        theCopy.nvb.rawascii = ''

    # We need to copy the data for:
    # - Lights
    # - Meshes & materials when there are alphakeys
    objType = theOriginal.type
    if (objType == 'LIGHT'):
        data         = theOriginal.data.copy()
        data.name    = newName
        theCopy.data = data
    elif (objType == 'MESH'):
        if theOriginal.animation_data:
            action = theOriginal.animation_data.action
            for fcurve in action.fcurves:
                dataPath = fcurve.data_path
                if dataPath.endswith('alpha_factor'):
                    data         = theOriginal.data.copy()
                    data.name    = newName
                    theCopy.data = data
                    # Create a copy of the material
                    if (theOriginal.active_material):
                        material      = theOriginal.active_material.copy()
                        material.name = newName
                        theCopy.active_material = material
                        break
            actionCopy = action.copy()
            actionCopy.name = newName
            theCopy.animation_data.action = actionCopy

    # Link copy to the anim scene
    bpy.context.collection.objects.link(theCopy)

    # Convert all child objects too
    for child in theOriginal.children:
        copy_anim_scene(scene, child, newSuffix, oldSuffix, theCopy)

    # Return the copied rootDummy
    return theCopy


def rename_anim_scene(obj, newSuffix, oldSuffix = ''):
    """
    Copy object and all it's children to scene.
    For object with simple (position, rotation) or no animations we
    create a linked copy.
    For alpha animation we'll need to copy the data too.
    """
    oldName = obj.name
    newName = 'ERROR'
    if oldSuffix:
        if oldName.endswith(oldSuffix):
            newName = oldName[:len(oldName)-len(oldSuffix)]
            if newName.endswith('.'):
                newName = newName[:len(newName)-1]
        else:
            newName = oldName.partition('.')[0]
            if not newName:
                return
        newName = newName + '.' + newSuffix
    else:
        newName = oldName + '.' + newSuffix

    obj.name = newName
    if obj.data:
        obj.data.name = newName
    # We need to copy the data for:
    # - Lights
    # - Meshes & materials when there are alphakeys
    objType = obj.type
    if (objType == 'MESH'):
        if obj.animation_data:
            action = obj.animation_data.action
            action.name = newName
            for fcurve in action.fcurves:
                dataPath = fcurve.data_path
                if dataPath.endswith('alpha_factor'):
                    # Create a copy of the material
                    if (obj.active_material):
                        material      = obj.active_material
                        material.name = newName
                        break

    # Convert all child objects too
    for child in obj.children:
        rename_anim_scene(child, newSuffix, oldSuffix)

    # Return the renamed rootDummy
    return obj


def create_hook_modifiers(obj):
    skingrName = ''
    for vg in obj.vertex_groups:
        if vg.name in bpy.data.objects:
            mod = obj.modifiers.new(vg.name + '.skin', 'HOOK')
            mod.object = bpy.data.objects[vg.name]
            mod.vertex_group = vg


def euler_filter(currEul, prevEul):

    def distance(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])

    def flip(e):
        f = e.copy()
        f[0] += math.pi
        f[1] *= -1
        f[1] += math.pi
        f[2] += math.pi
        return f

    def flip_diff(a, b):
        while abs(a - b) > math.pi:
            if a < b:
                b -= 2 * math.pi
            else:
                b += 2 * math.pi
        return b

    if not prevEul:
        # Nothing to compare to, return original value
        return currEul

    eul = currEul.copy()
    eul[0] = flip_diff(prevEul[0], eul[0])
    eul[1] = flip_diff(prevEul[1], eul[1])
    eul[2] = flip_diff(prevEul[2], eul[2])

    # Flip current euler
    flipEul = flip(eul)
    flipEul[0] = flip_diff(prevEul[0], flipEul[0])
    flipEul[1] = flip_diff(prevEul[1], flipEul[1])
    flipEul[2] = flip_diff(prevEul[2], flipEul[2])

    currDist = distance(prevEul, eul)
    flipDist = distance(prevEul, flipEul)

    if flipDist < currDist:
        return flipEul
    else:
        return eul


def float_to_byte(val):
    return int(val * 255)


def int_to_hex(val):
    return "{:02X}".format(val)


def color_to_hex(color):
    return "{}{}{}".format(
        int_to_hex(float_to_byte(color[0])),
        int_to_hex(float_to_byte(color[1])),
        int_to_hex(float_to_byte(color[2])))


def is_path_point(obj):
    return obj and (obj.type == 'EMPTY') and (obj.nvb.dummytype == nvb_def.Dummytype.PATHPOINT)


def get_mdl_root(obj):
    """
    :returns: MDL root object for the specified object.
    """
    if (obj.type == 'EMPTY') and (obj.nvb.dummytype == nvb_def.Dummytype.MDLROOT):
        return obj

    if not obj.parent:
        return None

    return get_mdl_root(obj.parent)


def calculate_bounding_box_size(obj):
    bbmin = Vector([sys.float_info.max] * 3)
    bbmax = Vector([sys.float_info.min] * 3)
    for co in obj.bound_box:
        for i in range(3):
            if co[i] < bbmin[i]: bbmin[i] = co[i]
            if co[i] > bbmax[i]: bbmax[i] = co[i]
    return bbmax - bbmin
