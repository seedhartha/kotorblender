import bpy

from ... import kb_utils


class KB_OT_anim_crop(bpy.types.Operator):
    """Open a dialog to crop a single animation"""

    bl_idname = "kb.anim_crop"
    bl_label = "Crop animation"

    cropFront : bpy.props.IntProperty(
                    name="cropFront",
                    min=0,
                    description="Insert Frames before the first keyframe")
    cropBack : bpy.props.IntProperty(
                    name="cropBack",
                    min=0,
                    description="Insert Frames after the last keyframe")

    @classmethod
    def poll(cls, context):
        rootDummy = kb_utils.get_mdl_root_from_object(context.object)
        if rootDummy is not None:
            return (len(rootDummy.nvb.animList) > 0)
        return False

    def crop_frames(self, target, animStart, animEnd):
        if target.animation_data and target.animation_data.action:
            # Grab some values for speed
            cf = self.cropFront
            cb = self.cropBack
            # Find out which frames to delete
            action = target.animation_data.action
            framesToDelete = []
            # Find out which ones to delete
            for fcurve in target.animation_data.action.fcurves:
                for p in fcurve.keyframe_points:
                    if (animStart <= p.co[0] < animStart + cf) or \
                       (animEnd - cb < p.co[0] <= animEnd):
                        framesToDelete.append((fcurve.data_path, p.co[0]))
            # Delete the frames by accessing them from the object.
            # (Can't do it directly)
            for dp, f in framesToDelete:
                target.keyframe_delete(dp, frame=f)
            # Move the keyframes to the front to remove gaps
            for fcurve in action.fcurves:
                for p in fcurve.keyframe_points:
                    if (p.co[0] >= animStart):
                        p.co[0] -= cf
                        p.handle_left.x -= cf
                        p.handle_right.x -= cf
                        if (p.co[0] >= animEnd):
                            p.co[0] -= cb
                            p.handle_left.x -= cb
                            p.handle_right.x -= cb
                # For compatibility with older blender versions
                try:
                    fcurve.update()
                except AttributeError:
                    pass

    def execute(self, context):
        mdl_base = kb_utils.get_mdl_root_from_object(context.object)
        if not kb_utils.check_anim_bounds(mdl_base):
            self.report({'INFO'}, "Failure: Convoluted animations.")
            return {'CANCELLED'}
        animList = mdl_base.nvb.animList
        currentAnimIdx = mdl_base.nvb.animListIdx
        anim = animList[currentAnimIdx]
        # Grab some values for speed
        cf = self.cropFront
        cb = self.cropBack
        animStart = anim.frameStart
        animEnd = anim.frameEnd
        totalCrop = cf + cb
        # Resulting length has to be at lest 1 frame
        if totalCrop > (animEnd - animStart + 1):
            self.report({'INFO'}, "Failure: Resulting length < 1.")
            return {'CANCELLED'}
        # Pad keyframes
        obj_list = [mdl_base]
        kb_utils.get_children_recursive(mdl_base, obj_list)
        for obj in obj_list:
            # Objects animation
            self.crop_frames(obj, animStart, animEnd)
            # Material animation
            if obj.active_material:
                self.crop_frames(obj.active_material, animStart, animEnd)
            # Emitter animation
            part_sys = obj.particle_systems.active
            if part_sys:
                self.crop_frames(part_sys.settings, animStart, animEnd)
        # Update the animations in the list
        for a in mdl_base.nvb.animList:
            if a.frameStart > animStart:
                a.frameStart -= totalCrop
                a.frameEnd -= totalCrop
                for e in a.eventList:
                    e.frame -= totalCrop
        # Adjust the target animation itself
        for idx, e in enumerate(anim.eventList):
            if (animStart <= e.frame < animStart + cf) or \
               (animEnd - cb < e.frame <= animEnd):
                anim.eventList.remove(idx)
                anim.eventListIdx = 0
            else:
                e.frame -= totalCrop
        anim.frameEnd -= totalCrop
        # Re-adjust the timeline to the new bounds
        kb_utils.toggle_anim_focus(context.scene, mdl_base)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label("Crop: ")
        row = layout.row()
        split = row.split()
        col = split.column(align=True)
        col.prop(self, "cropFront", text="Front")
        col.prop(self, "cropBack", text="Back")

        layout.separator()

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)