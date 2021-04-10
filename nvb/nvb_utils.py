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
    return obj and (obj.type == 'EMPTY') and (obj.nvb.dummytype == dummytype)


def get_node_type(obj):
    """
    Get the node type (dummy, trimesh, skin, ...) of the blender object
    """
    objType  = obj.type
    if objType == 'EMPTY':
        if   obj.nvb.dummytype == nvb_def.Dummytype.PATCH:
            return "patch"
        elif obj.nvb.dummytype == nvb_def.Dummytype.REFERENCE:
            return "reference"
    elif objType == 'MESH':
        if   obj.nvb.meshtype == nvb_def.Meshtype.TRIMESH:
            return "trimesh"
        elif obj.nvb.meshtype == nvb_def.Meshtype.DANGLYMESH:
            return "danglymesh"
        elif obj.nvb.meshtype == nvb_def.Meshtype.SKIN:
            return "skin"
        elif obj.nvb.meshtype == nvb_def.Meshtype.EMITTER:
            return "emitter"
        elif obj.nvb.meshtype == nvb_def.Meshtype.AABB:
            return "aabb"
    elif objType == 'LIGHT':
        return "light"

    return "dummy"


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
        return ""
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


def set_object_rotation_aurora(obj, nwangle):
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = Quaternion((nwangle[0], nwangle[1], nwangle[2]), nwangle[3])


def get_aurora_rot_from_object(obj):
    q = obj.rotation_quaternion
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
