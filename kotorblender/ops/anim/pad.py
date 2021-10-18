import bpy

from ... import utils


class KB_OT_anim_pad(bpy.types.Operator):
    """Open a dialog to pad a single animation"""

    bl_idname = "kb.anim_pad"
    bl_label = "Pad animation"

    pad_front : bpy.props.IntProperty(
                    name="Pad Front",
                    min=0,
                    description="Insert Frames before the first keyframe")
    pad_back : bpy.props.IntProperty(
                    name="Pad Back",
                    min=0,
                    description="Insert Frames after the last keyframe")

    @classmethod
    def poll(cls, context):
        mdl_base = utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            return (len(mdl_base.nvb.animList) > 0)
        return False

    def pad_frames(self, target, frame_start, frame_end):
        if target.animation_data and target.animation_data.action:
            for fcurve in target.animation_data.action.fcurves:
                for p in reversed(fcurve.keyframe_points):
                    if p.co[0] > frame_end:
                        p.co[0] += self.pad_back
                        p.handle_left.x += self.pad_back
                        p.handle_right.x += self.pad_back
                    if p.co[0] >= frame_start:
                        p.co[0] += self.pad_front
                        p.handle_left.x += self.pad_front
                        p.handle_right.x += self.pad_front
                fcurve.update()

    def execute(self, context):
        mdl_base = utils.get_mdl_root_from_object(context.object)
        if not utils.check_anim_bounds(mdl_base):
            self.report({'INFO'}, "Failure: Convoluted animations.")
            return {'CANCELLED'}
        anim = mdl_base.nvb.animList[mdl_base.nvb.animListIdx]
        frame_start = anim.frameStart
        frame_end = anim.frameEnd
        # Cancel if padding is 0
        if (self.pad_front + self.pad_back) <= 0:
            self.report({'INFO'}, "Failure: No changes.")
            return {'CANCELLED'}
        # Pad keyframes
        obj_list = [mdl_base]
        utils.get_children_recursive(mdl_base, obj_list)
        for obj in obj_list:
            # Objects animation
            self.pad_frames(obj, frame_start, frame_end)
            # Material animation
            if obj.active_material:
                self.pad_frames(obj.active_material, frame_start, frame_end)
            # Emitter animation
            part_sys = obj.particle_systems.active
            if part_sys:
                self.pad_frames(part_sys.settings, frame_start, frame_end)
        # Update the animations in the list
        totalPadding = self.pad_back + self.pad_front
        for a in mdl_base.nvb.animList:
            if a.frameStart > frame_end:
                a.frameStart += totalPadding
                a.frameEnd += totalPadding
                for ev in a.eventList:
                    ev.frame += totalPadding
        # Update the target animation itself
        anim.frameEnd += totalPadding
        for ev in anim.eventList:
            ev.frame += self.pad_front
        # Re-adjust the timeline to the new bounds
        utils.toggle_anim_focus(context.scene, mdl_base)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label("Padding: ")
        row = layout.row()
        split = row.split()
        col = split.column(align=True)
        col.prop(self, "pad_front", text="Front")
        col.prop(self, "pad_back", text="Back")
        layout.separator()

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)