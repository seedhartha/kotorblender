import math

import bpy

from ... import kb_utils


class KB_OT_anim_scale(bpy.types.Operator):
    """Open a dialog to scale the length of a single animation"""

    bl_idname = "kb.anim_scale"
    bl_label = "Scale animation"

    scaleFactor : bpy.props.FloatProperty(name="scale",
                                          description="Scale the animation",
                                          min=0.1,
                                          default=1.0)

    @classmethod
    def poll(cls, context):
        """Prevent execution if no rootdummy was found."""
        mdl_base = kb_utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            return (len(mdl_base.nvb.animList) > 0)
        return False

    def scale_frames_up(self, target, animStart, animEnd, scaleFactor):
        if target.animation_data and target.animation_data.action:
            size_old = animEnd - animStart
            padding = (scaleFactor * size_old) - size_old
            for fcurve in target.animation_data.action.fcurves:
                # Move keyframes back to create enough space
                for p in reversed(fcurve.keyframe_points):
                    if (p.co[0] > animEnd):
                        p.co[0] += padding
                        p.handle_left.x += padding
                        p.handle_right.x += padding
                # Now scale the animation
                for p in fcurve.keyframe_points:
                    if (animStart < p.co[0] <= animEnd):
                        oldFrame = p.co[0]
                        newFrame = (oldFrame - animStart) * \
                            scaleFactor + animStart
                        p.co[0] = newFrame
                        p.handle_left.x = newFrame - \
                            (oldFrame - p.handle_left.x)
                        p.handle_right.x = newFrame + \
                            (p.handle_right.x - oldFrame)
                fcurve.update()

    def scale_frames_down(self, target, animStart, animEnd, scaleFactor):
        if target.animation_data and target.animation_data.action:
            for fcurve in target.animation_data.action.fcurves:
                    # Scale the animation down first
                    for p in fcurve.keyframe_points:
                        if (animStart < p.co[0] <= animEnd):
                            oldFrame = p.co[0]
                            newFrame = (oldFrame - animStart) * \
                                scaleFactor + animStart
                            p.co[0] = newFrame
                            p.handle_left.x = newFrame - \
                                (oldFrame - p.handle_left.x)
                            p.handle_right.x = newFrame + \
                                (p.handle_right.x - oldFrame)
                    fcurve.update()

    def scale_frames(self, target, animStart, animEnd, scaleFactor):
        if target.animation_data and target.animation_data.action:
            if scaleFactor > 1.0:
                self.scale_frames_up(target, animStart, animEnd, scaleFactor)
            elif scaleFactor < 1.0:
                self.scale_frames_down(target, animStart, animEnd, scaleFactor)

    def execute(self, context):
        mdl_base = kb_utils.get_mdl_root_from_object(context.object)
        if not kb_utils.check_anim_bounds(mdl_base):
            self.report({'INFO'}, "Error: Nested animations.")
            return {'CANCELLED'}
        anim = mdl_base.nvb.animList[mdl_base.nvb.animListIdx]
        # Check resulting length (has to be >= 1)
        oldSize = anim.frameEnd - anim.frameStart
        newSize = self.scaleFactor * oldSize
        if (newSize < 1):
            self.report({'INFO'}, "Error: Resulting size < 1.")
            return {'CANCELLED'}
        if (math.fabs(oldSize - newSize) < 1):
            self.report({'INFO'}, "Error: Same size.")
            return {'CANCELLED'}
        # Adjust keyframes
        obj_list = [mdl_base]
        kb_utils.get_children_recursive(mdl_base, obj_list)
        for obj in obj_list:
            # Adjust the objects animation
            self.scale_frames(obj, anim.frameStart,
                              anim.frameEnd, self.scaleFactor)
            # Adjust the object's material animation
            mat = obj.active_material
            if mat:
                self.scale_frames(mat, anim.frameStart,
                                  anim.frameEnd, self.scaleFactor)
            # Emitter keyframes
            part_sys = obj.particle_systems.active
            if part_sys:
                self.scale_frames(part_sys.settings, anim.frameStart,
                                  anim.frameEnd, self.scaleFactor)
        # Adjust the bounds of animations coming after the
        # target (scaled) animation
        padding = newSize - oldSize
        if padding > 0:
            for a in reversed(mdl_base.nvb.animList):
                if a.frameStart > anim.frameEnd:
                    a.frameStart += padding
                    a.frameEnd += padding
                    for e in a.eventList:
                        e.frame += padding
        # Adjust the target (scaled) animation itself
        anim.frameEnd += padding
        for e in anim.eventList:
            e.frame = (e.frame - anim.frameStart) * \
                self.scaleFactor + anim.frameStart
        # Re-adjust the timeline to the new bounds
        kb_utils.toggle_anim_focus(context.scene, mdl_base)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label("Scaling: ")
        row = layout.row()
        row.prop(self, "scaleFactor", text="Factor")

        layout.separator()

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)