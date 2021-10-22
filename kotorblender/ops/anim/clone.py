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

from ... import utils


class KB_OT_anim_clone(bpy.types.Operator):
    """Clone animation and add it to the animation list"""

    bl_idname = "kb.anim_clone"
    bl_label = "Clone animation"

    @classmethod
    def poll(cls, context):
        """Prevent execution if no rootdummy was found."""
        mdl_base = utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            return (len(mdl_base.kb.animList) > 0)
        return False

    def clone_events(self, source_anim, target_anim):
        """Clone the animation events."""
        animStart = source_anim.frameStart
        for e in source_anim.eventList:
            cloned_event = target_anim.eventList.add()
            cloned_event.frame = target_anim.frameStart + (e.frame - animStart)
            cloned_event.name = e.name

    def clone_frames(self, obj, frame_start, frame_end, new_start):
        """Clone the animations keyframes."""
        if obj.animation_data and obj.animation_data.action:
            offset = new_start - frame_start
            for fcu in obj.animation_data.action.fcurves:
                kfp = fcu.keyframe_points
                vals = [(p.co[0] + offset, p.co[1]) for p in kfp
                        if frame_start <= p.co[0] <= frame_end]
                kfp_cnt = len(kfp)
                kfp.add(len(vals))
                for i in range(len(vals)):
                    kfp[kfp_cnt+i].co = vals[i]
                fcu.update()

    def execute(self, context):
        """Clone the animation."""
        mdl_base = utils.get_mdl_root_from_object(context.object)
        source_anim = mdl_base.kb.animList[mdl_base.kb.animListIdx]
        animStart = source_anim.frameStart
        animEnd = source_anim.frameEnd
        # Adds a new animation to the end of the list
        cloned_anim = utils.create_anim_list_item(mdl_base, True)
        # Copy data
        cloned_anim.frameEnd = cloned_anim.frameStart + (animEnd - animStart)
        cloned_anim.transtime = source_anim.transtime
        cloned_anim.root_obj = source_anim.root_obj
        cloned_anim.name = source_anim.name + "_copy"
        # Copy events
        self.clone_events(source_anim, cloned_anim)
        # Copy keyframes
        obj_list = [mdl_base]
        utils.get_children_recursive(mdl_base, obj_list)
        for obj in obj_list:
            # Object keyframes
            self.clone_frames(obj, animStart, animEnd, cloned_anim.frameStart)
            # Material keyframes
            mat = obj.active_material
            if mat:
                self.clone_frames(mat, animStart, animEnd,
                                  cloned_anim.frameStart)
            # Emitter keyframes
            part_sys = obj.particle_systems.active
            if part_sys:
                self.clone_frames(part_sys.settings,
                                  animStart, animEnd, cloned_anim.frameStart)
        return {'FINISHED'}