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

from .. import defines

DATA_PATH_BY_LABEL = {
    "position": "location",
    "orientation": "rotation_quaternion",
    "scale": "scale",

    # Meshes
    "alpha": "kb.alpha",
    "selfillumcolor": "kb.selfillumcolor",

    # Lights
    "color": "color",
    "radius": "kb.radius",
    "multiplier": "kb.multiplier",

    # Emitters
    "alphastart": "kb.alphastart",
    "alphamid": "kb.alphamid",
    "alphaend": "kb.alphaend",
    "birthrate": "kb.birthrate",
    "randombirthrate": "kb.randombirthrate",
    "bounce_co": "kb.bounce_co",
    "combinetime": "kb.combinetime",
    "drag": "kb.drag",
    "fps": "kb.fps",
    "frameend": "kb.frameend",
    "framestart": "kb.framestart",
    "grav": "kb.grav",
    "lifeexp": "kb.lifeexp",
    "mass": "kb.mass",
    "p2p_bezier2": "kb.p2p_bezier2",
    "p2p_bezier3": "kb.p2p_bezier3",
    "particlerot": "kb.particlerot",
    "randvel": "kb.randvel",
    "sizestart": "kb.sizestart",
    "sizemid": "kb.sizemid",
    "sizeend": "kb.sizeend",
    "sizestart_y": "kb.sizestart_y",
    "sizemid_y": "kb.sizemid_y",
    "sizeend_y": "kb.sizeend_y",
    "spread": "kb.spread",
    "threshold": "kb.threshold",
    "velocity": "kb.velocity",
    "xsize": "kb.xsize",
    "ysize": "kb.ysize",
    "blurlength": "kb.blurlength",
    "lightningdelay": "kb.lightningdelay",
    "lightningradius": "kb.lightningradius",
    "lightningsubdiv": "kb.lightningsubdiv",
    "lightningscale": "kb.lightningscale",
    "lightningzigzag": "kb.lightningzigzag",
    "percentstart": "kb.percentstart",
    "percentmid": "kb.percentmid",
    "percentend": "kb.percentend",
    "targetsize": "kb.targetsize",
    "numcontrolpts": "kb.numcontrolpts",
    "controlptradius": "kb.controlptradius",
    "controlptdelay": "kb.controlptdelay",
    "tangentspread": "kb.tangentspread",
    "tangentlength": "kb.tangentlength",
    "colorstart": "kb.colorstart",
    "colormid": "kb.colormid",
    "colorend": "kb.colorend"
}

LABEL_BY_DATA_PATH = {value: key for key, value in DATA_PATH_BY_LABEL.items()}

CONVERTER_BY_LABEL = {
    "position": lambda val, animscale: [val[i] * animscale for i in range(3)],
    "scale": lambda val, _: [val[0], val[0], val[0]]
}

CONVERTER_BY_DATA_PATH = {
    "scale": lambda val: [val[0]]
}


class AnimationNode:

    def __init__(self, name="UNNAMED"):
        self.nodetype = defines.Nodetype.DUMMY
        self.name = name
        self.supernode_number = 0
        self.parent = None
        self.children = []
        self.keyframes = dict()

        self.animated = False  # this node or its children contain keyframes

    def add_keyframes_to_object(self, anim, obj, root_name, animscale):
        for label, data in self.keyframes.items():
            if label not in DATA_PATH_BY_LABEL or not data:
                continue

            # Action, Animation Data

            if obj.type == 'LIGHT' and label == "color":
                target = obj.data
                action_name = "{}.{}.data".format(root_name, obj.name)
            else:
                target = obj
                action_name = "{}.{}".format(root_name, obj.name)

            action = self.get_or_create_action(action_name)
            self.get_or_create_animation_data(target, action)

            # Convert keyframes to frames/values

            frames = [anim.frame_start + defines.FPS * d[0] for d in data]

            if label in CONVERTER_BY_LABEL:
                converter = CONVERTER_BY_LABEL[label]
                values = [converter(d[1:], animscale) for d in data]
            else:
                values = [d[1:] for d in data]

            dim = len(values[0])

            # Keyframe Points

            data_path = DATA_PATH_BY_LABEL[label]
            fcurves = [self.get_or_create_fcurve(action, data_path, i) for i in range(dim)]
            keyframe_points = [fcurve.keyframe_points for fcurve in fcurves]

            # Rest Pose Keyframes

            if data_path.startswith("kb."):
                rest_values = getattr(target.kb, data_path[3:])
            else:
                rest_values = getattr(target, data_path)
            rest_frame = anim.frame_start - defines.ANIM_REST_POSE_OFFSET
            if dim == 1:
                keyframe_points[0].insert(rest_frame, rest_values, options={'FAST'})
            else:
                for i in range(dim):
                    keyframe_points[i].insert(rest_frame, rest_values[i], options={'FAST'})

            # Animation Keyframes

            for frame, val in zip(frames, values):
                for i in range(dim):
                    keyframe_points[i].insert(frame, val[i], options={'FAST'})
            for kfp in keyframe_points:
                kfp.update()

    def get_or_create_action(self, name):
        if name in bpy.data.actions:
            return bpy.data.actions[name]
        else:
            return bpy.data.actions.new(name=name)

    def get_or_create_animation_data(self, target, action):
        anim_data = target.animation_data
        if not anim_data:
            anim_data = target.animation_data_create()
            anim_data.action = action
        return anim_data

    def get_or_create_fcurve(self, action, data_path, index):
        fcurve = action.fcurves.find(data_path, index=index)
        if not fcurve:
            fcurve = action.fcurves.new(data_path=data_path, index=index)
        return fcurve

    def load_keyframes_from_object(self, anim, target):
        anim_data = target.animation_data
        if not anim_data:
            return

        action = anim_data.action
        if not action:
            return

        keyframes = self.get_keyframes_in_range(action, anim.frame_start, anim.frame_end)
        flat_keyframes = self.flatten_keyframes(keyframes)

        for data_path, dp_keyframes in flat_keyframes.items():
            if data_path not in LABEL_BY_DATA_PATH:
                continue

            label = LABEL_BY_DATA_PATH[data_path]
            self.keyframes[label] = []

            for point in dp_keyframes:
                timekey = (point[0] - anim.frame_start) / defines.FPS
                if data_path in CONVERTER_BY_DATA_PATH:
                    converter = CONVERTER_BY_DATA_PATH[data_path]
                    values = converter(point[1:])
                else:
                    values = point[1:]
                self.keyframes[label].append([timekey] + values)

    @classmethod
    def get_keyframes_in_range(cls, action, start, end):
        keyframes = dict()
        for fcurve in action.fcurves:
            data_path = fcurve.data_path
            array_index = fcurve.array_index
            keyframe_points = fcurve.keyframe_points
            for kp in keyframe_points:
                frame = round(kp.co[0])
                if frame < start or frame > end:
                    continue
                if data_path not in keyframes:
                    keyframes[data_path] = []
                dim = len(keyframes[data_path])
                while dim <= array_index:
                    keyframes[data_path].append([])
                    dim += 1
                keyframes[data_path][array_index].append((frame, kp.co[1]))

        return keyframes

    @classmethod
    def flatten_keyframes(cls, keyframes):
        flat_keyframes = dict()
        for data_path, dp_keyframes in keyframes.items():
            dim = len(dp_keyframes)
            assert dim > 0
            num_points = len(dp_keyframes[0])
            assert all([len(x) == num_points for x in dp_keyframes[1:]])
            flat_keyframes[data_path] = []
            for i in range(num_points):
                flat_keyframes[data_path].append([dp_keyframes[0][i][0]] + [dp_keyframes[j][i][1] for j in range(dim)])

        return flat_keyframes
