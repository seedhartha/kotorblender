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

from ... import (defines, utils)

class KB_OT_anim_moveback(bpy.types.Operator):
    """Move an animation and its keyframes to the end of the animation list"""

    bl_idname = "kb.anim_moveback"
    bl_label = "Move an animation to the end"

    @classmethod
    def poll(self, context):
        """Prevent execution if animation list is empty."""
        mdl_base = utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            return (len(mdl_base.kb.animList) > 1)
        return False

    def move_frames(self, obj, frame_start, frame_end, new_start):
        """Move the animation keyframes."""
        if obj.animation_data and obj.animation_data.action:
            offset = new_start - frame_start
            frames_to_delete = []  # delete later or it may screw up keyframes
            for fcu in obj.animation_data.action.fcurves:
                dp = fcu.data_path
                kfp = fcu.keyframe_points
                frames = [p.co[0] for p in kfp
                          if frame_start <= p.co[0] <= frame_end]
                frames_to_delete.append((dp, frames))
                vals = [(p.co[0] + offset, p.co[1]) for p in kfp
                        if frame_start <= p.co[0] <= frame_end]
                kfp_cnt = len(kfp)
                kfp.add(len(vals))
                for i in range(len(vals)):
                    kfp[kfp_cnt+i].co = vals[i]
                fcu.update()
            # Access keyframes from object to delete them
            for dp, frames in frames_to_delete:
                for f in frames:
                    obj.keyframe_delete(dp, frame=f)

    def execute(self, context):
        """Move the animation."""
        mdl_base = utils.get_mdl_root_from_object(context.object)
        if not utils.check_anim_bounds(mdl_base):
            self.report({'INFO'}, "Failure: Convoluted animations.")
            return {'CANCELLED'}
        anim_list = mdl_base.kb.animList
        currentAnimIdx = mdl_base.kb.animListIdx
        anim = anim_list[currentAnimIdx]
        # Grab some data for speed
        old_start = anim.frameStart
        old_end = anim.frameEnd
        # Grab a new starting frame
        last_frame = utils.get_last_keyframe(mdl_base)
        start = int(math.ceil((last_frame + defines.anim_offset) / 10.0)) * 10
        # Move keyframes
        obj_list = [mdl_base]
        utils.get_children_recursive(mdl_base, obj_list)
        for obj in obj_list:
            # Object animation
            self.move_frames(obj, old_start, old_end, start)
            # Material animation
            mat = obj.active_material
            if mat:
                self.move_frames(mat, old_start, old_end, start)
            # Emitter animation
            part_sys = obj.particle_systems.active
            if part_sys:
                self.move_frames(part_sys.settings, old_start, old_end, start)
        # Adjust animations in the list
        for e in anim.eventList:
            e.frame = start + (e.frame - old_start)
        anim.frameStart = start
        anim.frameEnd = start + (old_end - old_start)
        # Set index
        newAnimIdx = len(anim_list) - 1
        anim_list.move(currentAnimIdx, newAnimIdx)
        mdl_base.kb.animListIdx = newAnimIdx
        # Re-adjust the timeline to the new bounds
        utils.toggle_anim_focus(context.scene, mdl_base)
        return {'FINISHED'}