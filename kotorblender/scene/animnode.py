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

from mathutils import Quaternion

from .. import defines, utils


class AnimationNode:

    def __init__(self, name="UNNAMED"):
        self.nodetype = defines.Nodetype.DUMMY
        self.name = name
        self.parent = defines.null

        self.emitter_data = dict()
        self.object_data = dict()

    def add_object_keyframes(self, obj, anim, options={}):
        if self.object_data:
            self.create_data_object(obj, anim, options)
        if self.emitter_data:
            self.create_data_emitter(obj, anim, options)

    def create_data_object(self, obj, anim, options={}):
        """Creates animations in object actions."""
        fps = defines.fps
        frame_start = anim.frame_start

        # Insert keyframes of each type
        for label, (data, data_path, data_dim) in self.object_data.items():
            frames = [fps * d[0] + frame_start for d in data]

            if obj.type == 'LIGHT' and label in ["radius", "color"]:
                # For light radius and color, target the object data
                use_action = utils.get_action(obj.data, options["mdlname"] + "." + obj.name)
            else:
                # Otherwise, target the object
                use_action = utils.get_action(obj, options["mdlname"] + "." + obj.name)

            if label == "position":
                values = [d[1:4] for d in data]
                data_dim = 3  # TODO: add support for Bezier keys
            elif label == "orientation":
                values = [d[1:5] for d in data]
                data_dim = 4
            elif label == "scale":
                values = [[d[1]]*3 for d in data]
                data_dim = 3
            else:
                values = [d[1:data_dim+1] for d in data]

            AnimationNode.insert_kfp(frames, values, use_action, data_path, data_dim)

    def create_data_emitter(self, obj, anim, options={}):
        """Creates animations in emitter actions."""
        fps = defines.fps
        frame_start = anim.frame_start
        action = utils.get_action(obj, options["mdlname"] + "." + obj.name)
        for label, (data, _, data_dim) in self.emitter_data.items():
            frames = [fps * d[0] + frame_start for d in data]
            values = [d[1:data_dim+1] for d in data]
            dp = "kb.{}".format(label)
            dp_dim = data_dim
            AnimationNode.insert_kfp(frames, values, action, dp, dp_dim, "Odyssey Emitter")

    @staticmethod
    def create_restpose(obj, frame=1):
        def insert_kfp(fcurves, frame, val, dim):
            # dim = len(val)
            for j in range(dim):
                kf = fcurves[j].keyframe_points.insert(frame, val[j], options={'FAST'})
                kf.interpolation = 'LINEAR'
        # Get animation data
        animData = obj.animation_data
        if not animData:
            return  # No data = no animation = no need for rest pose
        # Get action
        action = animData.action
        if not action:
            return  # No action = no animation = no need for rest pose
        fcu = [action.fcurves.find("rotation_quaternion", index=i) for i in range(4)]
        if fcu.count(None) < 1:
            q = obj.rotation_quaternion
            insert_kfp(fcu, frame, [q.w, q.x, q.y, q.z], 4)
        fcu = [action.fcurves.find("location", index=i) for i in range(3)]
        if fcu.count(None) < 1:
            insert_kfp(fcu, frame, obj.location, 3)
        fcu = [action.fcurves.find("scale", index=i) for i in range(3)]
        if fcu.count(None) < 1:
            insert_kfp(fcu, frame, obj.scale, 3)

    @staticmethod
    def insert_kfp(frames, values, action, dp, dp_dim, action_group=None):
        if not frames or not values:
            return
        fcu = [utils.get_fcurve(action, dp, i, action_group)
               for i in range(dp_dim)]
        kfp_list = [fcu[i].keyframe_points for i in range(dp_dim)]
        kfp_cnt = list(map(lambda x: len(x), kfp_list))
        list(map(lambda x: x.add(len(values)), kfp_list))
        for i, (frm, val) in enumerate(zip(frames, values)):
            for d in range(dp_dim):
                p = kfp_list[d][kfp_cnt[d]+i]
                p.co = frm, val[d]
                p.interpolation = 'LINEAR'
                # could do len == dp_dim * 3...
                if len(val) > dp_dim:
                    p.interpolation = 'BEZIER'
                    p.handle_left_type = 'FREE'
                    p.handle_right_type = 'FREE'
                    # initialize left and right handle x positions
                    h_left_frame = frm - defines.fps
                    h_right_frame = frm + defines.fps
                    # adjust handle x positions based on previous/next keyframes
                    if i > 0:
                        p_left = frames[i - 1]
                        print(" left {} frm {}".format(p_left, frm))
                        # place 1/3 into the distance from current keyframe
                        # to previous keyframe
                        h_left_frame = frm - ((frm - p_left) / 3.0)
                    if i < len(values) - 1:
                        p_right = frames[i + 1]
                        print("right {} frm {}".format(p_right, frm))
                        # place 1/3 into the distance from current keyframe
                        # to next keyframe
                        h_right_frame = frm + ((p_right - frm) / 3.0)
                    # set bezier handle positions,
                    # y values are relative, so added to initial value
                    p.handle_left[:] = [
                        h_left_frame,
                        val[d + dp_dim] + val[d]
                    ]
                    p.handle_right[:] = [
                        h_right_frame,
                        val[d + (2 * dp_dim)] + val[d]
                    ]
        list(map(lambda c: c.update(), fcu))
