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

    # Emitters
    "alphastart": "kb.alphastart",
    "alphamid": "kb.alphamid",
    "alphaend": "kb.alphaend",
    "birthrate": "kb.birthrate",
    "random_birth_rate": "kb.random_birth_rate",
    "bounce_co": "kb.bounce_co",
    "combinetime": "kb.combinetime",
    "drag": "kb.drag",
    "fps": "kb.fps",
    "frame_end": "kb.frame_end",
    "frame_start": "kb.frame_start",
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
    "scale": lambda val: [val[0] * 3]
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

    def add_keyframes_to_object(self, anim, obj, root_name):
        for label, data in self.keyframes.items():
            if label not in DATA_PATH_BY_LABEL or not data:
                continue
            if label in CONVERTER_BY_LABEL:
                converter = CONVERTER_BY_LABEL[label]
                values = [converter(d[1:]) for d in data]
            else:
                values = [d[1:] for d in data]

            frames = [anim.frame_start + defines.FPS * d[0] for d in data]
            dim = len(values[0])

            # Action

            action_name = "{}.{}".format(root_name, obj.name)
            action = self.get_or_create_action(action_name)

            # Animation Data

            target = obj
            if obj.type == 'LIGHT' and label == "color":
                target = obj.data
            self.get_or_create_animation_data(target, action)

            # Keyframe Points

            data_path = DATA_PATH_BY_LABEL[label]
            fcurves = [self.get_or_create_fcurve(action, data_path, i) for i in range(dim)]
            keyframe_points = [fcurve.keyframe_points for fcurve in fcurves]

            # Rest Pose Keyframes

            rest_pose_empty = all([fcurve.is_empty for fcurve in fcurves])
            if rest_pose_empty:
                if data_path.startswith("kb."):
                    rest_values = getattr(target.kb, data_path[3:])
                else:
                    rest_values = getattr(target, data_path)
                for i in range(dim):
                    keyframe_points[i].insert(defines.ANIM_GLOBSTART, rest_values[i], options={'FAST'})

            # Animation Keyframes

            for frame, val in zip(frames, values):
                for i in range(dim):
                    keyframe_points[i].insert(frame, val[i], options={'FAST'})
            for kfp in keyframe_points:
                kfp.update()

    def load_keyframes_from_object(self, anim, obj):
        anim_data = obj.animation_data
        if not anim_data:
            return

        action = anim_data.action
        if not action:
            return

        # Extract keyframes

        fcurve_frames = dict()
        fcurve_values = dict()
        for fcurve in action.fcurves:
            data_path = fcurve.data_path
            if data_path not in LABEL_BY_DATA_PATH:
                continue

            frames = []
            values = []
            keyframe_points = fcurve.keyframe_points
            for kfp in keyframe_points:
                if kfp.co[0] < anim.frame_start or kfp.co[0] > 1 + anim.frame_end:
                    continue
                frames.append(kfp.co[0])
                values.append(kfp.co[1])

            if data_path not in fcurve_frames:
                fcurve_frames[data_path] = []
            fcurve_frames[data_path].append(frames)

            if data_path not in fcurve_values:
                fcurve_values[data_path] = []
            fcurve_values[data_path].append(values)

        if not fcurve_frames:
            return

        # Flatten Keyframes

        flat_fcurve_frames = dict()
        for label, frames in fcurve_frames.items():
            flat_fcurve_frames[label] = frames[0]

        flat_fcurve_values = dict()
        for label, values in fcurve_values.items():
            flat_fcurve_values[label] = list(zip(*values))

        # Convert to animation node keyframes

        for data_path in flat_fcurve_frames.keys():
            frames = flat_fcurve_frames[data_path]
            timekeys = [(frame-anim.frame_start)/defines.FPS for frame in frames]

            if data_path in CONVERTER_BY_DATA_PATH:
                converter = CONVERTER_BY_DATA_PATH[data_path]
                values = [converter(val) for val in flat_fcurve_values[data_path]]
            else:
                values = flat_fcurve_values[data_path]

            label = LABEL_BY_DATA_PATH[data_path]
            self.keyframes[label] = [[time] + list(values[i]) for i, time in enumerate(timekeys)]

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
