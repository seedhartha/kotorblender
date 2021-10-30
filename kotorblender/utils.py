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

import math

import bpy
from mathutils import Quaternion

from . import defines


def is_null(s):
    return (not s or s.lower() == defines.null.lower())


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def isclose_3f(a, b, rel_tol=0.1):
    return (isclose(a[0], b[0], rel_tol) and
            isclose(a[1], b[1], rel_tol) and
            isclose(a[2], b[2], rel_tol))


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


def is_root_dummy(obj, dummytype = defines.Dummytype.MDLROOT):
    return obj and (obj.type == 'EMPTY') and (obj.kb.dummytype == dummytype)


def get_children_recursive(obj, obj_list):
    """
    Helper following neverblender naming, compatibility layer
    Get all descendent nodes under obj in a flat list
    """
    obj_list.extend(search_node_all(obj, lambda o: o is not None))


def get_mdl_root_from_object(obj):
    return ancestor_node(obj, is_root_dummy)


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
        frame = defines.anim_globstart
        if target:
            if target.animation_data and target.animation_data.action:
                for fcu in target.animation_data.action.fcurves:
                    frame = max(max([p.co[0] for p in fcu.keyframe_points],
                                    default=0), frame)
            return frame
    obj_list = [root_obj]
    get_children_recursive(root_obj, obj_list)
    frame_list = [defines.anim_globstart]
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
    last_frame = max([defines.anim_globstart] +
                     [a.frameEnd for a in mdl_base.kb.animList])
    if check_keyframes:
        last_frame = max(last_frame, get_last_keyframe(mdl_base))
    anim = mdl_base.kb.animList.add()
    anim.name = mdl_base.name
    start = int(math.ceil((last_frame + defines.anim_offset) / 10.0)) * 10
    anim.frameStart = start
    anim.frameEnd = start
    return anim


def nwtime2frame(time, fps = defines.fps):
    """
    For animations: Convert key time to frame number
    """
    return round(fps*time)


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
    return obj and (obj.type == 'EMPTY') and (obj.kb.dummytype == defines.Dummytype.PATHPOINT)


def get_mdl_root(obj):
    """
    :returns: MDL root object for the specified object.
    """
    if (obj.type == 'EMPTY') and (obj.kb.dummytype == defines.Dummytype.MDLROOT):
        return obj

    if not obj.parent:
        return None

    return get_mdl_root(obj.parent)
