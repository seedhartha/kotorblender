import math

import bpy

from ... import (kb_def, kb_utils)

class KB_OT_anim_moveback(bpy.types.Operator):
    """Move an animation and its keyframes to the end of the animation list"""

    bl_idname = "kb.anim_moveback"
    bl_label = "Move an animation to the end"

    @classmethod
    def poll(self, context):
        """Prevent execution if animation list is empty."""
        mdl_base = kb_utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            return (len(mdl_base.nvb.animList) > 1)
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
        mdl_base = kb_utils.get_mdl_root_from_object(context.object)
        if not kb_utils.check_anim_bounds(mdl_base):
            self.report({'INFO'}, "Failure: Convoluted animations.")
            return {'CANCELLED'}
        anim_list = mdl_base.nvb.animList
        currentAnimIdx = mdl_base.nvb.animListIdx
        anim = anim_list[currentAnimIdx]
        # Grab some data for speed
        old_start = anim.frameStart
        old_end = anim.frameEnd
        # Grab a new starting frame
        last_frame = kb_utils.get_last_keyframe(mdl_base)
        start = int(math.ceil((last_frame + kb_def.anim_offset) / 10.0)) * 10
        # Move keyframes
        obj_list = [mdl_base]
        kb_utils.get_children_recursive(mdl_base, obj_list)
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
        mdl_base.nvb.animListIdx = newAnimIdx
        # Re-adjust the timeline to the new bounds
        kb_utils.toggle_anim_focus(context.scene, mdl_base)
        return {'FINISHED'}