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

from ..constants import NodeType, ANIM_REST_POSE_OFFSET
from ..utils import time_to_frame, frame_to_time


class Property:
    def __init__(
        self, label, data_path, bl_dim, mdl_to_bl_cvt=None, bl_to_mdl_cvt=None
    ):
        self.label = label
        self.data_path = data_path
        self.bl_dim = bl_dim
        self.mdl_to_bl_cvt = mdl_to_bl_cvt
        self.bl_to_mdl_cvt = bl_to_mdl_cvt


PROPERTIES = [
    Property(
        "position",
        "location",
        3,
        mdl_to_bl_cvt=lambda val, restloc, animscale: [
            restloc[i] + animscale * val[i] for i in range(3)
        ],
        bl_to_mdl_cvt=lambda val, restloc: [val[i] - restloc[i] for i in range(3)],
    ),
    Property("orientation", "rotation_quaternion", 4),
    Property(
        "scale",
        "scale",
        3,
        mdl_to_bl_cvt=lambda val, restloc: [val[0], val[0], val[0]],
        bl_to_mdl_cvt=lambda val, restloc: [val[0]],
    ),
    # Meshes
    Property("alpha", "kb.alpha", 1),
    Property("selfillumcolor", "kb.selfillumcolor", 3),
    # Lights
    Property("color", "color", 3),
    Property("radius", "kb.radius", 1),
    Property("multiplier", "kb.multiplier", 1),
    # Emitters
    Property("alphastart", "kb.alphastart", 1),
    Property("alphamid", "kb.alphamid", 1),
    Property("alphaend", "kb.alphaend", 1),
    Property("birthrate", "kb.birthrate", 1),
    Property("randombirthrate", "kb.randombirthrate", 1),
    Property("bounce_co", "kb.bounce_co", 1),
    Property("combinetime", "kb.combinetime", 1),
    Property("drag", "kb.drag", 1),
    Property("fps", "kb.fps", 1),
    Property("frameend", "kb.frameend", 1),
    Property("framestart", "kb.framestart", 1),
    Property("grav", "kb.grav", 1),
    Property("lifeexp", "kb.lifeexp", 1),
    Property("mass", "kb.mass", 1),
    Property("p2p_bezier2", "kb.p2p_bezier2", 1),
    Property("p2p_bezier3", "kb.p2p_bezier3", 1),
    Property("particlerot", "kb.particlerot", 1),
    Property("randvel", "kb.randvel", 1),
    Property("sizestart", "kb.sizestart", 1),
    Property("sizemid", "kb.sizemid", 1),
    Property("sizeend", "kb.sizeend", 1),
    Property("sizestart_y", "kb.sizestart_y", 1),
    Property("sizemid_y", "kb.sizemid_y", 1),
    Property("sizeend_y", "kb.sizeend_y", 1),
    Property("spread", "kb.spread", 1),
    Property("threshold", "kb.threshold", 1),
    Property("velocity", "kb.velocity", 1),
    Property("xsize", "kb.xsize", 1),
    Property("ysize", "kb.ysize", 1),
    Property("blurlength", "kb.blurlength", 1),
    Property("lightningdelay", "kb.lightningdelay", 1),
    Property("lightningradius", "kb.lightningradius", 1),
    Property("lightningsubdiv", "kb.lightningsubdiv", 1),
    Property("lightningscale", "kb.lightningscale", 1),
    Property("lightningzigzag", "kb.lightningzigzag", 1),
    Property("percentstart", "kb.percentstart", 1),
    Property("percentmid", "kb.percentmid", 1),
    Property("percentend", "kb.percentend", 1),
    Property("targetsize", "kb.targetsize", 1),
    Property("numcontrolpts", "kb.numcontrolpts", 1),
    Property("controlptradius", "kb.controlptradius", 1),
    Property("controlptdelay", "kb.controlptdelay", 1),
    Property("tangentspread", "kb.tangentspread", 1),
    Property("tangentlength", "kb.tangentlength", 1),
    Property("colorstart", "kb.colorstart", 3),
    Property("colormid", "kb.colormid", 3),
    Property("colorend", "kb.colorend", 3),
]

LABEL_TO_PROPERTY = {prop.label: prop for prop in PROPERTIES}
DATA_PATH_TO_PROPERTY = {prop.data_path: prop for prop in PROPERTIES}


class AnimationNode:
    def __init__(self, name="UNNAMED"):
        self.nodetype = NodeType.DUMMY
        self.name = name
        self.node_number = 0
        self.parent = None
        self.children = []
        self.keyframes = dict()

        self.animated = False  # this node or its children contain keyframes

    def add_keyframes_to_object(self, anim, obj, root_name, animscale):
        for label, data in self.keyframes.items():
            if not data or not label in LABEL_TO_PROPERTY:
                continue
            prop = LABEL_TO_PROPERTY[label]

            if obj.type == "LIGHT" and label == "color":
                anim_subject = obj.data
                action_name = "{}.{}.data".format(root_name, obj.name)
            else:
                anim_subject = obj
                action_name = "{}.{}".format(root_name, obj.name)

            anim_data = self.get_or_create_animation_data(anim_subject)
            action = self.get_or_create_action(action_name)
            if not anim_data.action:
                anim_data.action = action

            data_path = prop.data_path
            fcurves = [
                self.get_or_create_fcurve(action, data_path, i)
                for i in range(prop.bl_dim)
            ]
            keyframe_points = [fcurve.keyframe_points for fcurve in fcurves]

            # Add rest pose keyframes

            if data_path.startswith("kb."):
                rest_values = getattr(anim_subject.kb, data_path[3:])
            else:
                rest_values = getattr(anim_subject, data_path)
            if hasattr(rest_values, "__len__"):
                rest_dim = len(rest_values)
            else:
                rest_dim = 1
                rest_values = [rest_values]
            left_rest_frame = anim.frame_start - ANIM_REST_POSE_OFFSET
            right_rest_frame = anim.frame_end + ANIM_REST_POSE_OFFSET
            for frame in [left_rest_frame, right_rest_frame]:
                for i in range(rest_dim):
                    keyframe = keyframe_points[i].insert(
                        frame, rest_values[i], options={"FAST"}
                    )
                    keyframe.interpolation = "CONSTANT"

            # Add animation keyframes

            frames = [anim.frame_start + time_to_frame(d[0]) for d in data]
            if prop.mdl_to_bl_cvt:
                values = [
                    prop.mdl_to_bl_cvt(d[1:], obj.location, animscale) for d in data
                ]
            else:
                values = [d[1:] for d in data]
            last_keyframes = [None] * prop.bl_dim
            for frame, val in zip(frames, values):
                for i in range(prop.bl_dim):
                    keyframe = keyframe_points[i].insert(
                        frame, val[i], options={"FAST"}
                    )
                    keyframe.interpolation = "LINEAR"
                    last_keyframes[i] = keyframe
            for keyframe in last_keyframes:
                keyframe.interpolation = "CONSTANT"
            for kfp in keyframe_points:
                kfp.update()

    def get_or_create_action(self, name):
        if name in bpy.data.actions:
            return bpy.data.actions[name]
        else:
            return bpy.data.actions.new(name=name)

    def get_or_create_animation_data(self, subject):
        if subject.animation_data:
            return subject.animation_data
        else:
            return subject.animation_data_create()

    def get_or_create_fcurve(self, action, data_path, index):
        fcurve = action.fcurves.find(data_path, index=index)
        if not fcurve:
            fcurve = action.fcurves.new(data_path=data_path, index=index)
        return fcurve

    def load_keyframes_from_object(self, anim, anim_subject):
        anim_data = anim_subject.animation_data
        if not anim_data:
            return

        action = anim_data.action
        if not action:
            return

        keyframes = self.get_keyframes_in_range(
            action, anim.frame_start, anim.frame_end
        )
        nested_keyframes = self.nest_keyframes(keyframes)

        for data_path, dp_keyframes in nested_keyframes.items():
            if not data_path in DATA_PATH_TO_PROPERTY:
                continue
            prop = DATA_PATH_TO_PROPERTY[data_path]
            label = prop.label
            self.keyframes[label] = []

            for keyframe in dp_keyframes:
                time = frame_to_time(keyframe[0] - anim.frame_start)
                if prop.bl_to_mdl_cvt:
                    restloc = (
                        anim_subject.location
                        if hasattr(anim_subject, "location")
                        else [0.0] * 3
                    )
                    values = prop.bl_to_mdl_cvt(keyframe[1], restloc)
                else:
                    values = keyframe[1]
                self.keyframes[label].append([time] + values)

    @classmethod
    def get_keyframes_in_range(cls, action, start, end):
        keyframes = dict()
        for fcurve in action.fcurves:
            data_path = fcurve.data_path
            array_index = fcurve.array_index
            if not data_path in DATA_PATH_TO_PROPERTY:
                continue
            prop = DATA_PATH_TO_PROPERTY[data_path]
            assert array_index >= 0 and array_index < prop.bl_dim
            for kp in fcurve.keyframe_points:
                frame = round(kp.co[0])
                if frame < start or frame > end:
                    continue
                if not data_path in keyframes:
                    keyframes[data_path] = [[] for _ in range(prop.bl_dim)]
                keyframes[data_path][array_index].append((frame, kp.co[1]))
        return keyframes

    @classmethod
    def nest_keyframes(cls, keyframes):
        nested = dict()
        for data_path, dp_keyframes in keyframes.items():
            assert data_path in DATA_PATH_TO_PROPERTY
            prop = DATA_PATH_TO_PROPERTY[data_path]
            assert prop.bl_dim > 0 and len(dp_keyframes) == prop.bl_dim
            num_frames = len(dp_keyframes[0])
            assert all(len(dpk) == num_frames for dpk in dp_keyframes[1:])
            for i in range(num_frames):
                frame = dp_keyframes[0][i][0]
                values = [0.0] * prop.bl_dim
                values[0] = dp_keyframes[0][i][1]
                for j in range(1, prop.bl_dim):
                    assert dp_keyframes[j][i][0] == frame
                    values[j] = dp_keyframes[j][i][1]
                if not data_path in nested:
                    nested[data_path] = []
                nested[data_path].append((frame, values))
        return nested
