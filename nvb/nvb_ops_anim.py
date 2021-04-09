"""Contains Blender Operators for manipulating animation properties."""

import math

import bpy

from . import nvb_def, nvb_utils


class KB_OT_anim_clone(bpy.types.Operator):
    """Clone animation and add it to the animation list"""

    bl_idname = 'kb.anim_clone'
    bl_label = 'Clone animation'

    @classmethod
    def poll(cls, context):
        """Prevent execution if no rootdummy was found."""
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            return (len(mdl_base.nvb.animList) > 0)
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
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        source_anim = mdl_base.nvb.animList[mdl_base.nvb.animListIdx]
        animStart = source_anim.frameStart
        animEnd = source_anim.frameEnd
        # Adds a new animation to the end of the list
        cloned_anim = nvb_utils.create_anim_list_item(mdl_base, True)
        # Copy data
        cloned_anim.frameEnd = cloned_anim.frameStart + (animEnd - animStart)
        cloned_anim.transtime = source_anim.transtime
        cloned_anim.root_obj = source_anim.root_obj
        cloned_anim.name = source_anim.name + '_copy'
        # Copy events
        self.clone_events(source_anim, cloned_anim)
        # Copy keyframes
        obj_list = [mdl_base]
        nvb_utils.get_children_recursive(mdl_base, obj_list)
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


class KB_OT_anim_scale(bpy.types.Operator):
    """Open a dialog to scale the length of a single animation"""

    bl_idname = 'kb.anim_scale'
    bl_label = 'Scale animation'

    scaleFactor : bpy.props.FloatProperty(name='scale',
                                          description='Scale the animation',
                                          min=0.1,
                                          default=1.0)

    @classmethod
    def poll(cls, context):
        """Prevent execution if no rootdummy was found."""
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
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
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        if not nvb_utils.check_anim_bounds(mdl_base):
            self.report({'INFO'}, 'Error: Nested animations.')
            return {'CANCELLED'}
        anim = mdl_base.nvb.animList[mdl_base.nvb.animListIdx]
        # Check resulting length (has to be >= 1)
        oldSize = anim.frameEnd - anim.frameStart
        newSize = self.scaleFactor * oldSize
        if (newSize < 1):
            self.report({'INFO'}, 'Error: Resulting size < 1.')
            return {'CANCELLED'}
        if (math.fabs(oldSize - newSize) < 1):
            self.report({'INFO'}, 'Error: Same size.')
            return {'CANCELLED'}
        # Adjust keyframes
        obj_list = [mdl_base]
        nvb_utils.get_children_recursive(mdl_base, obj_list)
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
        nvb_utils.toggle_anim_focus(context.scene, mdl_base)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label('Scaling: ')
        row = layout.row()
        row.prop(self, 'scaleFactor', text='Factor')

        layout.separator()

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class KB_OT_anim_crop(bpy.types.Operator):
    """Open a dialog to crop a single animation"""

    bl_idname = 'kb.anim_crop'
    bl_label = 'Crop animation'

    cropFront : bpy.props.IntProperty(
                    name='cropFront',
                    min=0,
                    description='Insert Frames before the first keyframe')
    cropBack : bpy.props.IntProperty(
                    name='cropBack',
                    min=0,
                    description='Insert Frames after the last keyframe')

    @classmethod
    def poll(cls, context):
        rootDummy = nvb_utils.get_mdl_root_from_object(context.object)
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
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        if not nvb_utils.check_anim_bounds(mdl_base):
            self.report({'INFO'}, 'Failure: Convoluted animations.')
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
            self.report({'INFO'}, 'Failure: Resulting length < 1.')
            return {'CANCELLED'}
        # Pad keyframes
        obj_list = [mdl_base]
        nvb_utils.get_children_recursive(mdl_base, obj_list)
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
        nvb_utils.toggle_anim_focus(context.scene, mdl_base)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label('Crop: ')
        row = layout.row()
        split = row.split()
        col = split.column(align=True)
        col.prop(self, 'cropFront', text='Front')
        col.prop(self, 'cropBack', text='Back')

        layout.separator()

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class KB_OT_anim_pad(bpy.types.Operator):
    """Open a dialog to pad a single animation"""

    bl_idname = 'kb.anim_pad'
    bl_label = 'Pad animation'

    pad_front : bpy.props.IntProperty(
                    name='Pad Front',
                    min=0,
                    description='Insert Frames before the first keyframe')
    pad_back : bpy.props.IntProperty(
                    name='Pad Back',
                    min=0,
                    description='Insert Frames after the last keyframe')

    @classmethod
    def poll(cls, context):
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
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
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        if not nvb_utils.check_anim_bounds(mdl_base):
            self.report({'INFO'}, 'Failure: Convoluted animations.')
            return {'CANCELLED'}
        anim = mdl_base.nvb.animList[mdl_base.nvb.animListIdx]
        frame_start = anim.frameStart
        frame_end = anim.frameEnd
        # Cancel if padding is 0
        if (self.pad_front + self.pad_back) <= 0:
            self.report({'INFO'}, 'Failure: No changes.')
            return {'CANCELLED'}
        # Pad keyframes
        obj_list = [mdl_base]
        nvb_utils.get_children_recursive(mdl_base, obj_list)
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
        nvb_utils.toggle_anim_focus(context.scene, mdl_base)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label('Padding: ')
        row = layout.row()
        split = row.split()
        col = split.column(align=True)
        col.prop(self, 'pad_front', text='Front')
        col.prop(self, 'pad_back', text='Back')
        layout.separator()

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class KB_OT_anim_focus(bpy.types.Operator):
    """Set the Start and end frames of the timeline"""

    bl_idname = 'kb.anim_focus'
    bl_label = 'Set start and end frame of the timeline to the animation'

    @classmethod
    def poll(self, context):
        """Prevent execution if animation list is empty."""
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            return (len(mdl_base.nvb.animList) > 0)
        return False

    def execute(self, context):
        """Set the timeline to this animation."""
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        nvb_utils.toggle_anim_focus(context.scene, mdl_base)
        return {'FINISHED'}


class KB_OT_anim_new(bpy.types.Operator):
    """Add a new animation to the animation list"""

    bl_idname = 'kb.anim_new'
    bl_label = 'Create new animation'

    @classmethod
    def poll(self, context):
        """Prevent execution if no object is selected."""
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        return (mdl_base is not None)

    def execute(self, context):
        """Create the animation"""
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        anim = nvb_utils.create_anim_list_item(mdl_base, True)
        anim.root_obj = mdl_base.name
        # Create an unique name
        name_list = [an.name for an in mdl_base.nvb.animList]
        name_idx = 0
        new_name = "anim.{:0>3d}".format(name_idx)
        while new_name in name_list:
            name_idx += 1
            new_name = "anim.{:0>3d}".format(name_idx)
        anim.name = new_name
        return {'FINISHED'}


class KB_OT_anim_delete(bpy.types.Operator):
    """Delete the selected animation and its keyframes"""

    bl_idname = 'kb.anim_delete'
    bl_label = 'Delete an animation'

    @classmethod
    def poll(self, context):
        """Prevent execution if animation list is empty."""
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            return (len(mdl_base.nvb.animList) > 0)
        return False

    def delete_frames(self, obj, frame_start, frame_end):
        """Delete the animation's keyframes."""
        if obj.animation_data and obj.animation_data.action:
            for fcu in obj.animation_data.action.fcurves:
                dp = fcu.data_path
                frames = [p.co[0] for p in fcu.keyframe_points
                          if frame_start <= p.co[0] <= frame_end]
                for f in frames:
                    obj.keyframe_delete(dp, frame=f)
                fcu.update()

    def execute(self, context):
        """Delete the animation."""
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        anim_list = mdl_base.nvb.animList
        anim_list_idx = mdl_base.nvb.animListIdx
        anim = anim_list[anim_list_idx]
        # Grab some data for speed
        frame_start = anim.frameStart
        frame_end = anim.frameEnd
        # Remove keyframes
        obj_list = [mdl_base]
        nvb_utils.get_children_recursive(mdl_base, obj_list)
        for obj in obj_list:
            # Objects animation
            self.delete_frames(obj, frame_start, frame_end)
            # Material animation
            if obj.active_material:
                self.delete_frames(obj.active_material, frame_start, frame_end)
            # Emitter animation
            part_sys = obj.particle_systems.active
            if part_sys:
                self.delete_frames(part_sys.settings, frame_start, frame_end)
        # Remove animation from List
        anim_list.remove(anim_list_idx)
        if anim_list_idx > 0:
            mdl_base.nvb.animListIdx = anim_list_idx - 1
        return {'FINISHED'}


class KB_OT_anim_moveback(bpy.types.Operator):
    """Move an animation and its keyframes to the end of the animation list"""

    bl_idname = 'kb.anim_moveback'
    bl_label = 'Move an animation to the end'

    @classmethod
    def poll(self, context):
        """Prevent execution if animation list is empty."""
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
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
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        if not nvb_utils.check_anim_bounds(mdl_base):
            self.report({'INFO'}, 'Failure: Convoluted animations.')
            return {'CANCELLED'}
        anim_list = mdl_base.nvb.animList
        currentAnimIdx = mdl_base.nvb.animListIdx
        anim = anim_list[currentAnimIdx]
        # Grab some data for speed
        old_start = anim.frameStart
        old_end = anim.frameEnd
        # Grab a new starting frame
        last_frame = nvb_utils.get_last_keyframe(mdl_base)
        start = int(math.ceil((last_frame + nvb_def.anim_offset) / 10.0)) * 10
        # Move keyframes
        obj_list = [mdl_base]
        nvb_utils.get_children_recursive(mdl_base, obj_list)
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
        nvb_utils.toggle_anim_focus(context.scene, mdl_base)
        return {'FINISHED'}


class KB_OT_anim_move(bpy.types.Operator):
    """Move an item in the animation list, without affecting keyframes"""

    bl_idname = 'kb.anim_move'
    bl_label = 'Move an animation in the list, without affecting keyframes'
    bl_options = {'UNDO'}

    direction : bpy.props.EnumProperty(items=(('UP', 'Up', ''),
                                              ('DOWN', 'Down', '')))

    @classmethod
    def poll(self, context):
        """Prevent execution if animation list has less than 2 elements."""
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            return (len(mdl_base.nvb.animList) > 1)
        return False

    def execute(self, context):
        """Move an item in the animation list."""
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        anim_list = mdl_base.nvb.animList

        currentIdx = mdl_base.nvb.animListIdx
        new_idx = 0
        max_idx = len(anim_list) - 1
        if self.direction == 'DOWN':
            new_idx = currentIdx + 1
        elif self.direction == 'UP':
            new_idx = currentIdx - 1
        else:
            return {'CANCELLED'}

        new_idx = max(0, min(new_idx, max_idx))
        if new_idx == currentIdx:
            return {'CANCELLED'}
        anim_list.move(currentIdx, new_idx)
        mdl_base.nvb.animListIdx = new_idx
        return {'FINISHED'}


class KB_OT_anim_event_new(bpy.types.Operator):
    """Add a new item to the event list"""

    bl_idname = 'kb.anim_event_new'
    bl_label = 'Add a new event to an animation'
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        """Enable only if there is an animation."""
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            anim_list = mdl_base.nvb.animList
            anim_list_idx = mdl_base.nvb.animListIdx
            return (anim_list_idx >= 0) and len(anim_list) > anim_list_idx
        return False

    def execute(self, context):
        """Add the new item."""
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        anim = mdl_base.nvb.animList[mdl_base.nvb.animListIdx]

        eventList = anim.eventList
        newEvent = eventList.add()
        if anim.frameStart <= bpy.context.scene.frame_current <= anim.frameEnd:
            newEvent.frame = bpy.context.scene.frame_current
        else:
            newEvent.frame = anim.frameStart

        return {'FINISHED'}


class KB_OT_anim_event_delete(bpy.types.Operator):
    """Delete the selected item from the event list"""

    bl_idname = 'kb.anim_event_delete'
    bl_label = 'Deletes an event from an animation'
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        """Enable only if the list isn't empty."""
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            anim_list = mdl_base.nvb.animList
            anim_list_idx = mdl_base.nvb.animListIdx
            if (anim_list_idx >= 0) and len(anim_list) > anim_list_idx:
                anim = anim_list[anim_list_idx]
                ev_list = anim.eventList
                ev_list_idx = anim.eventListIdx
                return ev_list_idx >= 0 and len(ev_list) > ev_list_idx
        return False

    def execute(self, context):
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        anim = mdl_base.nvb.animList[mdl_base.nvb.animListIdx]
        eventList = anim.eventList
        eventIdx = anim.eventListIdx

        eventList.remove(eventIdx)
        if eventIdx > 0:
            eventIdx = eventIdx - 1

        return {'FINISHED'}


class KB_OT_anim_event_move(bpy.types.Operator):
    """Move an item in the event list"""

    bl_idname = 'kb.anim_event_move'
    bl_label = 'Move an item in the event  list'
    bl_options = {'UNDO'}

    direction : bpy.props.EnumProperty(items=(('UP', 'Up', ''),
                                              ('DOWN', 'Down', '')))

    @classmethod
    def poll(self, context):
        """Enable only if the list isn't empty."""
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        if mdl_base is not None:
            anim_list = mdl_base.nvb.animList
            anim_list_idx = mdl_base.nvb.animListIdx
            if (anim_list_idx >= 0) and len(anim_list) > anim_list_idx:
                anim = anim_list[anim_list_idx]
                ev_list = anim.eventList
                ev_list_idx = anim.eventListIdx
                return ev_list_idx >= 0 and len(ev_list) > ev_list_idx
        return False

    def execute(self, context):
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        anim = mdl_base.nvb.animList[mdl_base.nvb.animListIdx]
        eventList = anim.eventList

        currentIdx = anim.eventListIdx
        newIdx = 0
        maxIdx = len(eventList) - 1
        if self.direction == 'DOWN':
            newIdx = currentIdx + 1
        elif self.direction == 'UP':
            newIdx = currentIdx - 1
        else:
            return {'CANCELLED'}

        newIdx = max(0, min(newIdx, maxIdx))
        eventList.move(currentIdx, newIdx)
        anim.eventListIdx = newIdx
        return {'FINISHED'}


class KB_OT_amt_event_new(bpy.types.Operator):
    """Add a new event to the event list"""

    bl_idname = 'kb.amt_event_new'
    bl_label = 'Create new animation event'

    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        """Prevent execution if no object is selected."""
        return context.object and context.object.type == 'ARMATURE'

    def execute(self, context):
        """Create the animation"""
        amt = context.object
        if not amt:
            return
        event_list = amt.nvb.amt_event_list
        # Initialize the first events to add known event types
        nvb_utils.amt_event_list_init(amt)
        # Create an unique name
        name_list = [ev.name for ev in event_list]
        name_idx = 0
        new_name = "event.{:0>3d}".format(name_idx)
        while new_name in name_list:
            name_idx += 1
            new_name = "event.{:0>3d}".format(name_idx)
        # Add new event
        nvb_utils.amt_event_list_item_create(amt, new_name)
        if amt.animation_data and amt.animation_data.action:
            nvb_utils.init_amt_event_action(amt, amt.animation_data.action)
        return {'FINISHED'}


class KB_OT_amt_event_delete(bpy.types.Operator):
    """Delete the selected event and its keyframes"""

    bl_idname = 'kb.amt_event_delete'
    bl_label = 'Delete an animation event'

    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        """Prevent execution if event list is empty or the index invalid."""
        amt = context.object
        undeletable_events = len(nvb_def.animation_event_names)
        if amt and amt.type == 'ARMATURE':
            event_list = amt.nvb.amt_event_list
            event_list_idx = amt.nvb.amt_event_list_idx
            return (event_list_idx >= undeletable_events and
                    len(event_list) > event_list_idx)
        return False

    def delete_event_fcurve(self, obj, event_id):
        """Delete the events fcurve."""
        if obj.animation_data and obj.animation_data.action:
            action = obj.animation_data.action
            # Remove the current data path for that idx
            data_path = 'nvb.amt_event_list[' + str(event_id) + '].fire'
            fcu = action.fcurves.find(data_path, index=0)
            if fcu:
                action.fcurves.remove(fcu)

    def adjust_event_fcurves(self, obj, event_id_list):
        """All data path ids -1."""
        if obj.animation_data and obj.animation_data.action:
            action = obj.animation_data.action
            # Remove the current data path for that idx
            dp_prefix = 'nvb.amt_event_list['
            dp_suffix = '].fire'
            for ev_id in event_id_list:
                data_path = dp_prefix + str(ev_id) + dp_suffix
                fcu = action.fcurves.find(data_path, index=0)
                if fcu:
                    fcu.data_path = dp_prefix + str(ev_id-1) + dp_suffix

    def execute(self, context):
        """Delete the currently selcted event."""
        amt = context.object
        if not amt:
            return
        event_list = amt.nvb.amt_event_list
        event_list_idx = amt.nvb.amt_event_list_idx
        # Delete fcurve assoiated with the current event
        self.delete_event_fcurve(amt, event_list_idx)
        # Adjust the data paths of the other fcurves to the new ids
        event_idx_list = [id for id, _ in enumerate(event_list)
                          if id >= event_list_idx]
        self.adjust_event_fcurves(amt, event_idx_list)
        # We potentially removed keyframes => update scene
        context.scene.update()
        # Remove current event from List
        event_list.remove(event_list_idx)
        if event_list_idx > 0:
            amt.nvb.amt_event_list_idx = len(amt.nvb.amt_event_list)-1
        return {'FINISHED'}
