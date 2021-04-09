import bmesh
import bpy

from . import nvb_def, nvb_utils


class KB_UL_anims(bpy.types.UIList):
    """UI List for displaying animations."""

    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname, index):
        """Draw a single animation."""

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, 'name', text='', emboss=False)
            icn = 'CHECKBOX_DEHLT' if item.mute else 'CHECKBOX_HLT'
            layout.prop(item, 'mute', text='', icon=icn, emboss=False)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label('', icon='POSE_DATA')


class KB_UL_anim_events(bpy.types.UIList):
    """UI List for displaying animation events."""

    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname, index):
        """Draw a single animation event."""

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.7, align=False)
            split.prop(item, 'name', text='', emboss=False)
            row = split.row(align=True)
            row.prop(item, 'frame', text='', emboss=False)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label('', icon='LIGHT')


class KB_MT_animlist_specials(bpy.types.Menu):
    """Animation List Specials."""

    bl_label = "Animation List Specials"

    def draw(self, context):
        """Draw the panel."""
        layout = self.layout
        layout.operator('kb.anim_moveback',
                        icon='LOOP_FORWARDS')
        layout.operator('kb.anim_pad',
                        icon='FULLSCREEN_ENTER')
        layout.operator('kb.anim_crop',
                        icon='FULLSCREEN_EXIT')
        layout.operator('kb.anim_scale',
                        icon='SORTSIZE')
        layout.operator('kb.anim_clone',
                        icon='NODETREE')


class NVB_PT_animlist(bpy.types.Panel):
    """Property panel for animationslist.

    Property panel for additional properties needed for the mdl file
    format. This is only available for EMPTY objects.
    It is located under the object data panel in the properties window
    """

    bl_label = 'Odyssey Animations'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    @classmethod
    def poll(cls, context):
        """Draw only if part of a valid mdl is selected."""
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        return mdl_base is not None

    def draw(self, context):
        """Draw the panel."""
        layout = self.layout
        mdl_base = nvb_utils.get_mdl_root_from_object(context.object)
        if mdl_base:
            # Display and add/remove animations
            row = layout.row()
            row.template_list('KB_UL_anims', 'TheAnimList',
                              mdl_base.nvb, 'animList',
                              mdl_base.nvb, 'animListIdx',
                              rows=7)
            col = row.column(align=True)
            col.operator('kb.anim_new', icon='ADD', text='')
            col.operator('kb.anim_delete', icon='REMOVE', text='')
            col.separator()
            col.operator('kb.anim_move',
                         icon='TRIA_UP', text='').direction = 'UP'
            col.operator('kb.anim_move',
                         icon='TRIA_DOWN', text='').direction = 'DOWN'
            col.separator()
            col.operator('kb.anim_focus',
                         icon='RENDER_ANIMATION', text='')
            col.menu('KB_MT_animlist_specials',
                     icon='DOWNARROW_HLT', text="")
            anim_list = mdl_base.nvb.animList
            anim_list_idx = mdl_base.nvb.animListIdx
            if anim_list_idx >= 0 and len(anim_list) > anim_list_idx:
                anim = anim_list[anim_list_idx]
                row = layout.row()
                row.prop(anim, 'name')
                row = layout.row()
                row.prop(anim, 'root_obj')
                row = layout.row()
                row.prop(anim, 'transtime')
                row = layout.row()
                split = row.split()
                col = split.column(align=True)
                col.prop(anim, 'frameStart')
                col.prop(anim, 'frameEnd')

                # Event Helper. Display and add/remove events.
                box = layout.box()
                box.label(text='Events')

                row = box.row()
                row.template_list('KB_UL_anim_events', 'TheEventList',
                                  anim, 'eventList',
                                  anim, 'eventListIdx')
                col = row.column(align=True)
                col.operator('kb.anim_event_new', text='', icon='ADD')
                col.operator('kb.anim_event_delete', text='', icon='REMOVE')
                col.separator()
                col.operator('kb.anim_event_move',
                             icon='TRIA_UP', text='').direction = 'UP'
                col.operator('kb.anim_event_move',
                             icon='TRIA_DOWN', text='').direction = 'DOWN'
            layout.separator()


class NVB_PT_smoothgroups(bpy.types.Panel):
    bl_label = "Smoothgroups"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(self, context):
        ob = context.object
        try:
            return ob and ob.mode == 'EDIT' and ob.type == 'MESH'
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        custom_icon = 'NONE'

        layout = self.layout

        me = context.object.data
        bm = bmesh.from_edit_mesh(me)

        # smoothgroups are a face-level phenomenon, insist on being in face mode
        if bm.select_mode != {'FACE'}:
            layout.label("Face select only", icon = 'INFO')
            return

        # the smoothgroup data layer
        sg_layer = bm.faces.layers.int.get(nvb_def.sg_layer_name)
        # count of faces per smoothgroup in this mesh
        sg = { i: 0 for i in range(0, 32) }
        # smoothgroups in use on selected faces
        sg_selected = set()
        for face in bm.faces:
            if sg_layer is None:
                continue
            face_sg = face[sg_layer]
            for power in sg.keys():
                sg_val = pow(2, power)
                if face_sg & sg_val:
                    sg[power] += 1
                    if face.select:
                        sg_selected.add(power + 1)

        # display readout of smoothgroups in use on selected faces
        row = layout.row()
        row.label(text="Selection: {}".format(
            ", ".join(str(x) for x in sorted(sg_selected))
        ))

        # display readout of smoothgroups in use on this mesh
        for i in range(0, 32):
            if sg[i]:
                row = layout.row(align=True)
                row.label("{}: {} faces".format(i + 1, sg[i]))
                op = row.operator('nvb.smoothgroup_select', text="", icon='EDIT')
                op.sg_number = i
                op.action = 'SEL'
                op = row.operator('nvb.smoothgroup_select', text="", icon='X')
                op.sg_number = i
                op.action = 'DESEL'

        # individual smoothgroup toggle buttons, apply to all selected faces
        row = layout.row(align=True)
        row.label(text="Toggle")
        row = layout.row(align=True)
        op = row.operator('nvb.smoothgroup_toggle', text = '1', icon=custom_icon)
        op.sg_number = 0
        op.activity = int(sg[1])
        op = row.operator('nvb.smoothgroup_toggle', text = '2', icon=custom_icon)
        op.sg_number = 1
        op.activity = int(sg[2])
        op = row.operator('nvb.smoothgroup_toggle', text = '3', icon=custom_icon)
        op.sg_number = 2
        op.activity = int(sg[3])
        row = layout.row(align=True)
        op = row.operator('nvb.smoothgroup_toggle', text = '4', icon=custom_icon)
        op.sg_number = 3
        op.activity = int(sg[4])
        op = row.operator('nvb.smoothgroup_toggle', text = '5', icon=custom_icon)
        op.sg_number = 4
        op.activity = int(sg[5])
        op = row.operator('nvb.smoothgroup_toggle', text = '6', icon=custom_icon)
        op.sg_number = 5
        op.activity = int(sg[6])
        row = layout.row(align=True)
        op = row.operator('nvb.smoothgroup_toggle', text = '7', icon=custom_icon)
        op.sg_number = 6
        op.activity = int(sg[7])
        op = row.operator('nvb.smoothgroup_toggle', text = '8', icon=custom_icon)
        op.sg_number = 7
        op.activity = int(sg[8])
        op = row.operator('nvb.smoothgroup_toggle', text = '9', icon=custom_icon)
        op.sg_number = 8
        op.activity = int(sg[9])

        # smoothgroup generation tools, same process as 'auto' during export
        row = layout.row(align=True)
        row.label(text="Generate")
        row = layout.row(align=True)
        row.operator_enum('nvb.smoothgroup_generate', 'action')


class NVB_UL_lightflares(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        custom_icon = 'NONE'

        # Supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(item.texture, icon = custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label('', icon = custom_icon)


class NVB_UL_animevents(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        custom_icon = 'NONE'

        # Supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(item.name, icon = custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label('', icon = custom_icon)


class NVB_PT_empty(bpy.types.Panel):
    """
    Property panel for additional properties needed for the mdl file
    format. This is only available for EMPTY objects.
    It is located under the object data panel in the properties window
    """
    bl_label = 'Odyssey Dummy Properties'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'EMPTY')

    def draw(self, context):
        obj    = context.object
        layout = self.layout

        row = layout.row()
        row.prop(obj.nvb, 'dummytype', text='Type')
        sep = layout.separator()

        # Display properties depending on type of the empty
        if (obj.nvb.dummytype == nvb_def.Dummytype.MDLROOT):
            if not obj.nvb.isanimation:
                # Animation Helper. Creates a new scene, copies all objects to it
                # and renames them
                row = layout.row()
                box = row.box()
                row = box.row()
                row.prop(obj.nvb, 'isanimation', text = 'Animation')
                sub = row.row()
                sub.enabled = False
                sub.prop(obj.nvb, 'animname', text = '')
                row = box.row(align = True)
                row.prop(obj.nvb, 'newanimname', text = 'Create')
                row.operator('nvb.animscene_add', text = '', icon='ADD')

                sep = layout.separator()

                row = layout.row()
                box = row.box()
                split = box.split()
                col = split.column()
                col.label(text = 'Classification:')
                col.label(text = 'Supermodel:')
                col.label(text = 'Ignore Fog:')
                col.label(text = 'Animation Scale:')
                if obj.nvb.classification == nvb_def.Classification.CHARACTER:
                    col.label(text = 'Head Model:')
                col = split.column()
                col.prop(obj.nvb, 'classification', text = '')
                col.prop(obj.nvb, 'supermodel', text = '')
                col.prop(obj.nvb, 'ignorefog', text = '')
                col.prop(obj.nvb, 'animscale', text = '')
                if obj.nvb.classification == nvb_def.Classification.CHARACTER:
                    col.prop(obj.nvb, 'headlink', text = '')

                sep = layout.separator()

                # Minimap Helper.
                # TODO: uncomment when compatible with Blender 2.8
                '''
                row = layout.row()
                box = row.box()
                box.label(text = 'Minimap Helper')
                row = box.row()
                row.prop(obj.nvb, 'minimapzoffset', text = 'z Offset')
                row = box.row()
                row.prop(obj.nvb, 'minimapsize', text = 'Minimap size')
                row = box.row()
                row.operator('nvb.render_minimap', text = 'Render Minimap', icon='NONE')
                '''

                # All Children Settings Helper
                row = layout.row()
                box = row.box()
                box.label(text="Child Node Settings")
                row = box.row()
                row.label(text="Smoothgroups")
                row = box.row()
                op = row.operator('nvb.children_smoothgroup', text="Direct")
                op.action = 'DRCT'
                op = row.operator('nvb.children_smoothgroup', text="Auto")
                op.action = 'AUTO'
                op = row.operator('nvb.children_smoothgroup', text="Single")
                op.action = 'SING'
                op = row.operator('nvb.children_smoothgroup', text="Separate")
                op.action = 'SEPR'
            else:
                # MDL Rootdummy in an animation scene
                row = layout.row()
                box = row.box()
                row = box.row()
                row.prop(obj.nvb, 'isanimation', text = 'Animation')
                sub = row.row()
                sub.enabled = False
                sub.prop(obj.nvb, 'animname', text = '')
                row = box.row(align = True)
                row.prop(obj.nvb, 'newanimname', text = 'Rename/Copy')
                row.operator('nvb.animscene_rename', text = '', icon='FILE_REFRESH')
                row.operator('nvb.animscene_add', text = '', icon='ADD')
                row = box.row()
                row.prop_search(obj.nvb, 'animroot', bpy.data, 'objects', text = 'Root')
                row = box.row()
                row.prop(obj.nvb, 'transtime')

                sep = layout.separator()
                # Event Helper. Display and add/remove events.
                row = layout.row()
                box = row.box()
                row = box.row()
                row.label(text = 'Event List')

                row = box.row()
                row.template_list('NVB_UILIST_ANIMEVENTS', 'The_List', obj.nvb, 'eventList', obj.nvb, 'eventListIdx')
                col = row.column(align = True)
                col.operator('nvb.animevent_new', text = '', icon='ADD')
                col.operator('nvb.animevent_delete', text = '', icon='REMOVE')
                col.separator()
                col.operator('nvb.animevent_move', icon='TRIA_UP', text = '').direction = 'UP'
                col.operator('nvb.animevent_move', icon='TRIA_DOWN', text = '').direction = 'DOWN'
                if obj.nvb.eventListIdx >= 0 and len(obj.nvb.eventList) > 0:
                    item = obj.nvb.eventList[obj.nvb.eventListIdx]
                    row = box.row()
                    row.prop(item, 'name')
                    row.prop(item, 'frame')

        elif (obj.nvb.dummytype == nvb_def.Dummytype.PWKROOT):
            pass

        elif (obj.nvb.dummytype == nvb_def.Dummytype.DWKROOT):
            pass

        elif (obj.nvb.dummytype == nvb_def.Dummytype.REFERENCE):
            row = layout.row()
            box = row.box()

            row = box.row()
            row.prop(obj.nvb, 'refmodel')
            row = box.row()
            row.prop(obj.nvb, 'reattachable')

        else:
            row = layout.row()
            box = row.box()

            row = box.row()
            row.prop(obj.nvb, 'wirecolor')
            row = box.row()
            row.prop(obj.nvb, 'dummysubtype')


class NVB_PT_light(bpy.types.Panel):
    """
    Property panel for additional light properties. This
    holds all properties not supported by blender at the moment,
    but used by OpenGL and the aurora engine. This is only available
    for LIGHT objects.
    It is located under the object data panel in the properties window
    """
    bl_label = 'Odyssey Light Properties'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'LIGHT')

    def draw(self, context):
        obj    = context.object
        layout = self.layout

        row = layout.row()
        row.prop(obj.nvb, 'lighttype', text='Type')

        sep = layout.separator()

        row = layout.row()
        box = row.box()

        row = box.row()
        row.prop(obj.nvb, 'wirecolor', text='Wirecolor')
        row = box.row()
        row.prop(obj.nvb, 'lightpriority', text='Priority')
        row = box.row()
        row.prop(obj.nvb, 'radius', text='Radius')
        row = box.row()
        row.prop(obj.nvb, 'multiplier', text='Multiplier')

        split = box.split()
        col = split.column(align=True)
        col.prop(obj.nvb, 'ambientonly', text='Ambient Only')
        col.prop(obj.nvb, 'shadow', text='Shadows')
        col = split.column(align=True)
        col.prop(obj.nvb, 'fadinglight', text='Fading')
        col.prop(obj.nvb, 'isdynamic', text='Dynamic Type')
        col.prop(obj.nvb, 'affectdynamic', text='Affect dynamic')

        sep = layout.separator()

        # Lens flares
        row = layout.row()
        row.enabled = (obj.nvb.lighttype == 'NONE')
        box = row.box()
        row = box.row()
        row.prop(obj.nvb, 'lensflares')
        sub = row.row(align=True)
        sub.active = obj.nvb.lensflares
        sub.prop(obj.nvb, 'flareradius', text='Radius')
        row = box.row()
        row.active = obj.nvb.lensflares
        row.template_list('NVB_UL_lightflares', 'The_List', obj.nvb, 'flareList', obj.nvb, 'flareListIdx')
        col = row.column(align = True)
        col.operator('nvb.lightflare_new', icon='ADD', text = '')
        col.operator('nvb.lightflare_delete', icon='REMOVE', text = '')
        col.separator()
        col.operator('nvb.lightflare_move', icon='TRIA_UP', text = '').direction = 'UP'
        col.operator('nvb.lightflare_move', icon='TRIA_DOWN', text = '').direction = 'DOWN'
        if obj.nvb.flareListIdx >= 0 and len(obj.nvb.flareList) > 0:
            item = obj.nvb.flareList[obj.nvb.flareListIdx]
            row = box.row()
            row.active = obj.nvb.lensflares
            row.prop(item, 'texture')
            row = box.row()
            row.active = obj.nvb.lensflares
            row.prop(item, 'colorshift')
            row = box.row()
            row.active = obj.nvb.lensflares
            row.prop(item, 'size')
            row.prop(item, 'position')


class NVB_PT_texture(bpy.types.Panel):
    """Texture properties panel, mostly for managing TXI files"""
    bl_label = 'Odyssey Texture Properties'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'texture'

    @classmethod
    def poll(cls, context):
        try:
            # yes for image textures
            return context.texture.image
        except:
            return False

    def draw_summ_prop(self, texture, layout, propname):
        """UI Summary prop entries which include default-reset control"""
        row = layout.row(align=True)
        row.prop(texture.nvb, propname)
        prop_names = [o.name for o in texture.nvb.modified_properties]
        if propname in prop_names:
            row.label(icon='FILE_TICK')
            op = row.operator('nvb.texture_info_ops', text='', icon='X', emboss=False)
            op.action = 'RESET'
            op.propname = propname
        else:
            row.label(icon='RADIOBUT_OFF')

    def draw_box_header(self, texture, layout, boxname, text):
        """UI Title and visibility toggle for texture property sub-groups"""
        row = layout.row()
        row.alignment = 'LEFT'
        state = getattr(texture.nvb, 'box_visible_' + boxname)
        if not state:
            row.operator('nvb.texture_info_box_ops', text=text, icon="TRIA_RIGHT", emboss=False).boxname = boxname
            return False
        else:
            row.operator('nvb.texture_info_box_ops', text=text, icon="TRIA_DOWN", emboss=False).boxname = boxname
            return True

    def draw(self, context):
        layout = self.layout
        texture = context.texture

        # TXI file operations
        row = layout.row(align=True)
        row.operator('nvb.texture_info_io', text=" Import", icon='IMPORT').action = 'LOAD'
        row.operator('nvb.texture_info_io', text=" Export", icon='EXPORT').action = 'SAVE'

        # Texture type
        if len(texture.nvb.modified_properties):
            box = layout.row().box()
            if self.draw_box_header(texture, box, 'summary', 'TXI File Summary'):
                for propname in texture.nvb.modified_properties:
                    self.draw_summ_prop(texture, box, propname.name)

        box = layout.row().box()
        if self.draw_box_header(texture, box, 'textures', 'Shader Textures'):
            box.prop(texture.nvb, 'envmaptexture')
            box.prop(texture.nvb, 'bumpmaptexture')
            box.prop(texture.nvb, 'bumpyshinytexture')

        box = layout.row().box()
        if self.draw_box_header(texture, box, 'procedural', 'Procedural Properties'):
            box.prop(texture.nvb, 'proceduretype')
            if texture.nvb.proceduretype == 'water':
                box.label(text="Water Settings")
                box.prop(texture.nvb, 'wateralpha')
                box.prop(texture.nvb, 'waterwidth')
                box.prop(texture.nvb, 'waterheight')
            elif texture.nvb.proceduretype == 'arturo':
                box.label(text="Arturo Settings")
                box.prop(texture.nvb, 'arturowidth')
                box.prop(texture.nvb, 'arturoheight')
            elif texture.nvb.proceduretype == 'cycle':
                box.label(text="Cycle Settings")
                box.prop(texture.nvb, 'defaultwidth')
                box.prop(texture.nvb, 'defaultheight')
                box.prop(texture.nvb, 'numx')
                box.prop(texture.nvb, 'numy')
                box.prop(texture.nvb, 'fps')
                box.prop(texture.nvb, 'filerange')
            box.separator()
            box.prop(texture.nvb, 'forcecyclespeed')
            box.prop(texture.nvb, 'anglecyclespeed')
            box.prop(texture.nvb, 'channelscale0')
            box.prop(texture.nvb, 'channelscale1')
            box.prop(texture.nvb, 'channelscale2')
            box.prop(texture.nvb, 'channelscale3')
            box.prop(texture.nvb, 'channeltranslate0')
            box.prop(texture.nvb, 'channeltranslate1')
            box.prop(texture.nvb, 'channeltranslate2')
            box.prop(texture.nvb, 'channeltranslate3')
            box.prop(texture.nvb, 'distort')
            box.prop(texture.nvb, 'distortangle')
            box.prop(texture.nvb, 'distortionamplitude')
            box.prop(texture.nvb, 'speed')

        box = layout.row().box()
        if self.draw_box_header(texture, box, 'bumpmap', 'Bumpmap Properties'):
            box.prop(texture.nvb, 'isbumpmap')
            box.prop(texture.nvb, 'isdiffusebumpmap')
            box.prop(texture.nvb, 'isspecularbumpmap')
            box.prop(texture.nvb, 'bumpmapscaling')
            box.prop(texture.nvb, 'bumpintensity')
            box.prop(texture.nvb, 'diffusebumpintensity')
            box.prop(texture.nvb, 'specularbumpintensity')
            box.prop(texture.nvb, 'specularcolor')

        box = layout.row().box()
        if self.draw_box_header(texture, box, 'envmap', 'Environment Map Properties'):
            box.prop(texture.nvb, 'isenvironmentmapped')
            box.prop(texture.nvb, 'envmapalpha')

        box = layout.row().box()
        if self.draw_box_header(texture, box, 'general', 'General Properties'):
            box.prop(texture.nvb, 'blending')
            box.prop(texture.nvb, 'clamp')
            box.prop(texture.nvb, 'downsamplemin')
            box.prop(texture.nvb, 'downsamplemax')
            box.prop(texture.nvb, 'compresstexture')
            box.prop(texture.nvb, 'filter')
            box.prop(texture.nvb, 'mipmap')
            box.prop(texture.nvb, 'maptexelstopixels')
            box.prop(texture.nvb, 'gamma')
            box.prop(texture.nvb, 'alphamean')
            box.prop(texture.nvb, 'cube')
            box.prop(texture.nvb, 'islightmap')
            box.prop(texture.nvb, 'renderbmlmtype')
            box.prop(texture.nvb, 'temporary')
            box.prop(texture.nvb, 'useglobalalpha')
            box.prop(texture.nvb, 'decal')

        box = layout.row().box()
        if self.draw_box_header(texture, box, 'font', 'Font Properties'):
            box.prop(texture.nvb, 'numchars')
            box.prop(texture.nvb, 'fontheight')
            box.prop(texture.nvb, 'baselineheight')
            box.prop(texture.nvb, 'texturewidth')
            box.prop(texture.nvb, 'spacingR')
            box.prop(texture.nvb, 'spacingB')

class NVB_PT_emitter(bpy.types.Panel):
    """
    Property panel for additional properties needed for the mdl file
    format. This is only available for particle systems.
    It is located under the particle panel in the properties window
    """
    bl_label       = 'Odyssey Emitter Properties'
    bl_space_type  = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    @classmethod
    def poll(cls, context):
        try:
            return context.object and \
                   context.object.type == 'MESH' and \
                   context.object.nvb.meshtype == nvb_def.Meshtype.EMITTER
        except:
            return False

    def draw(self, context):

        def factor_but(layout, target, toggle, factor, name):
            row = layout.row(align=True)
            row.prop(target, toggle, text="")
            sub = row.row()
            sub.active = getattr(target, toggle)
            sub.prop(target, factor, text=name, slider=True)
            return sub

        obj = context.object

        layout = self.layout

        row = layout.row()
        row.prop(obj.nvb, 'meshtype', text='Type')

        layout.separator()

        box = layout.row().box()
        row = box.row()
        row.prop(obj.nvb, 'update')
        row = box.row()
        row.prop(obj.nvb, 'render_emitter')
        if obj.nvb.update == 'Lightning' or \
           not nvb_utils.is_null(obj.nvb.chunkName):
            row.enabled = False
        row = box.row()
        row.prop(obj.nvb, 'blend')
        if not nvb_utils.is_null(obj.nvb.chunkName):
            row.enabled = False
        row = box.row()
        row.prop(obj.nvb, 'spawntype')
        if obj.nvb.update != 'Fountain' or \
           not nvb_utils.is_null(obj.nvb.chunkName):
            row.enabled = False

        box.separator()

        row = box.row()
        row.label(text="Emitter Size (cm)")
        row = box.row(align=True)
        row.prop(obj.nvb, "xsize")
        row.prop(obj.nvb, "ysize")

        box.separator()

        # Inheritance
        row = box.row()
        row.label(text="Inheritance")
        row = box.row()
        row.prop(obj.nvb, 'inherit')
        row.prop(obj.nvb, 'inherit_local')
        row = box.row()
        row.prop(obj.nvb, 'inheritvel')
        if obj.nvb.update == 'Lightning':
            row.enabled = False
        row.prop(obj.nvb, 'inherit_part')

        box.separator()

        row = box.row()
        row.label(text="Miscellaneous")
        row = box.row()
        row.prop(obj.nvb, "numBranches")
        row = box.row()
        row.prop(obj.nvb, 'renderorder')
        row = box.row()
        row.prop(obj.nvb, "threshold")

        row = box.row()
        box.label(text="Blur")
        row = box.row()
        row.prop(obj.nvb, 'combinetime')
        row = box.row()
        row.prop(obj.nvb, 'deadspace')

        box = layout.row().box()
        row = box.row()
        row.label(text="Particles", icon='PARTICLE_DATA')
        row = box.row()
        row.label(text="")
        row.label(text="Start")
        row.label(text="Mid")
        row.label(text="End")
        row = box.row()
        row.label(text="Percent")
        row.prop(obj.nvb, "percentstart", text="")
        row.prop(obj.nvb, "percentmid", text="")
        row.prop(obj.nvb, "percentend", text="")
        row = box.row()
        row.label(text="Color")
        row.prop(obj.nvb, "colorstart", text="")
        row.prop(obj.nvb, "colormid", text="")
        row.prop(obj.nvb, "colorend", text="")
        row = box.row()
        row.label(text="Alpha")
        row.prop(obj.nvb, "alphastart", text="")
        row.prop(obj.nvb, "alphamid", text="")
        row.prop(obj.nvb, "alphaend", text="")
        row = box.row()
        row.label(text="Size X")
        row.prop(obj.nvb, "sizestart", text="")
        row.prop(obj.nvb, "sizemid", text="")
        row.prop(obj.nvb, "sizeend", text="")
        row = box.row()
        row.label(text="Size Y")
        row.prop(obj.nvb, "sizestart_y", text="")
        row.prop(obj.nvb, "sizemid_y", text="")
        row.prop(obj.nvb, "sizeend_y", text="")

        box.separator()

        row = box.row()
        row.label(text="Birthrate")
        row = box.row()
        col = row.column()
        col.prop(obj.nvb, 'birthrate', text="")
        if obj.nvb.update == 'Lightning':
            col.enabled = False
        col = row.column()
        col.prop(obj.nvb, 'm_frandombirthrate', text="Random")
        if obj.nvb.update == 'Lightning':
            col.enabled = False
        row = box.row()
        col = row.column()
        col.prop(obj.nvb, 'lifeexp')
        if obj.nvb.update == 'Lightning':
            col.enabled = False
        col = row.column()
        col.prop(obj.nvb, 'mass')
        if obj.nvb.update == 'Lightning':
            col.enabled = False
        row = box.row()
        col = row.column()
        col.prop(obj.nvb, 'spread')
        if obj.nvb.update == 'Lightning':
            col.enabled = False
        col = row.column()
        col.prop(obj.nvb, 'particlerot')
        if obj.nvb.update == 'Lightning':
            col.enabled = False
        row = box.row()
        col = row.column()
        col.prop(obj.nvb, 'velocity')
        if obj.nvb.update == 'Lightning':
            col.enabled = False
        col = row.column()
        col.prop(obj.nvb, 'randvel')
        if obj.nvb.update == 'Lightning':
            col.enabled = False
        row = box.row()
        row.prop(obj.nvb, 'blurlength')
        row = box.row()
        row.prop(obj.nvb, 'targetsize')
        row = box.row()
        row.label(text="Tangent")
        row = box.row()
        row.prop(obj.nvb, 'tangentspread', text="Spread")
        row.prop(obj.nvb, 'tangentlength', text="Length")
        # detonate
        row = box.row()
        col = row.column()
        col.prop(obj.nvb, 'bounce')
        if obj.nvb.update == 'Lightning':
            col.enabled = False
        col = row.column()
        col.prop(obj.nvb, 'bounce_co')
        if obj.nvb.update == 'Lightning':
            col.enabled = False
        row = box.row()
        col = row.column()
        col.prop(obj.nvb, 'loop')
        if obj.nvb.update != 'Single' and \
           obj.nvb.update != 'Explosion':
            col.enabled = False
        col = row.column()
        col.prop(obj.nvb, 'splat')
        row = box.row()
        row.prop(obj.nvb, 'affectedByWind')
        if obj.nvb.update == 'Lightning':
            row.enabled = False
        row = box.row()
        row.prop(obj.nvb, 'm_isTinted')

        box = layout.row().box()
        row = box.row()
        row.label(text="Texture / Chunk", icon='TEXTURE')
        row = box.row()
        row.prop(obj.nvb, 'texture')
        if not nvb_utils.is_null(obj.nvb.chunkName):
            row.enabled = False
        row = box.row()
        row.prop(obj.nvb, 'twosidedtex')
        if not nvb_utils.is_null(obj.nvb.chunkName):
            row.enabled = False

        box.separator()

        row = box.row()
        row.label(text="Texture Animation")
        row = box.row()
        row.label(text="Grid")
        row.prop(obj.nvb, 'xgrid', text="X")
        row.prop(obj.nvb, 'ygrid', text="Y")
        if not nvb_utils.is_null(obj.nvb.chunkName):
            row.enabled = False
        row = box.row()
        row.prop(obj.nvb, 'fps')
        row = box.row()
        row.prop(obj.nvb, 'framestart')
        row.prop(obj.nvb, 'frameend')
        row = box.row()
        row.prop(obj.nvb, 'm_bFrameBlending')
        row = box.row()
        row.prop(obj.nvb, 'random')

        box.separator()

        row = box.row()
        row.label(text='Depth Texture')
        row = box.row()
        row.prop(obj.nvb, 'depth_texture')
        row = box.row()
        row.prop(obj.nvb, 'm_sDepthTextureName', text="")

        box.separator()

        row = box.row()
        row.label(text='Chunk Model')
        row = box.row()
        row.prop(obj.nvb, 'chunkName', text="")

        box = layout.row().box()
        row = box.row()
        row.label(text="Advanced", icon='PREFERENCES')

        # Lightning
        parent_box = box
        box = box.row().box()
        if obj.nvb.update != 'Lightning':
            box.enabled = False
        row = box.row()
        row.label(text='Lightning')
        row = box.row()
        row.prop(obj.nvb, 'lightningdelay')
        row = box.row()
        row.prop(obj.nvb, 'lightningradius')
        row = box.row()
        row.prop(obj.nvb, 'lightningsubdiv')
        row = box.row()
        row.prop(obj.nvb, 'lightningscale')
        row = box.row()
        row.prop(obj.nvb, 'lightningzigzag')
        box = parent_box

        box.separator()

        # Blast props
        parent_box = box
        box = box.row().box()
        row =  box.row()
        row.label(text='Blast')
        row =  box.row()
        row.prop(obj.nvb, 'blastradius')
        row =  box.row()
        row.prop(obj.nvb, 'blastlength')
        box = parent_box

        box.separator()

        # p2p settings
        parent_box = box
        box = box.row().box()
        if obj.nvb.update != 'Fountain' and\
           obj.nvb.update != 'Single':
            box.enabled = False
        row = box.row()
        row.label(text='P2P Settings')
        row = box.row()
        row.prop(obj.nvb, 'p2p')
        row = box.row()
        row.prop(obj.nvb, 'p2p_type')
        if not obj.nvb.p2p:
            row.enabled = False
        if not obj.nvb.p2p:
            row.enabled = False
        row = box.row()
        row.prop(obj.nvb, 'p2p_bezier2')
        if not obj.nvb.p2p or \
           obj.nvb.p2p_type == 'Gravity':
            row.enabled = False
        row = box.row()
        row.prop(obj.nvb, 'p2p_bezier3')
        if not obj.nvb.p2p or \
           obj.nvb.p2p_type == 'Gravity':
            row.enabled = False
        row = box.row()
        row.prop(obj.nvb, 'grav')
        if not obj.nvb.p2p or \
           obj.nvb.p2p_type == 'Bezier':
            row.enabled = False
        row = box.row()
        row.prop(obj.nvb, 'drag')
        if not obj.nvb.p2p or \
           obj.nvb.p2p_type == 'Bezier':
            row.enabled = False
        box = parent_box

        box.separator()

        parent_box = box
        box = box.row().box()
        row = box.row()
        row.label(text='Control Points')
        row = box.row()
        row.prop(obj.nvb, 'numcontrolpts')
        row = box.row()
        row.prop(obj.nvb, 'controlptradius')
        row = box.row()
        row.prop(obj.nvb, 'controlptdelay')
        row = box.row()
        row.prop(obj.nvb, 'controlptsmoothing')
        box = parent_box


class NVB_PT_mesh(bpy.types.Panel):
    """
    Property panel for additional mesh properties. This
    holds all properties not supported by blender at the moment,
    but used by OpenGL and the aurora engine. This is only available
    for MESH objects.
    It is located under the object data panel in the properties window
    """
    bl_label = 'Odyssey Mesh Properties'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    @classmethod
    def poll(cls, context):
        return (context.object and \
                context.object.type == 'MESH' and \
                context.object.nvb.meshtype != nvb_def.Meshtype.EMITTER)

    def draw(self, context):
        obj      = context.object
        obj_type = obj.type
        layout   = self.layout

        row = layout.row()
        row.prop(obj.nvb, 'meshtype', text='Type')

        sep = layout.separator()

        if (obj.nvb.meshtype == nvb_def.Meshtype.EMITTER):
            row = layout.row()
            box = row.box()

            row = box.row()
            row.prop(obj.nvb, 'wirecolor', text='Wirecolor')
            row = box.row()
            row.prop_search(obj.nvb, 'rawascii', bpy.data, 'texts', text='Data')

        else: # Trimesh, danglymesh, skin
            row = layout.row()
            box = row.box()
            row = box.row()
            row.prop_search(obj.nvb, 'bitmap', bpy.data, 'images')
            row = box.row()
            row.prop_search(obj.nvb, 'bitmap2', bpy.data, 'images')
            row = box.row()
            row.prop(obj.nvb, 'diffuse')
            row = box.row()
            row.prop(obj.nvb, 'ambient')
            row = box.row()
            row.prop(obj.nvb, 'selfillumcolor')
            row = box.row()
            row.prop(obj.nvb, 'wirecolor')
            row = box.row()
            row.prop(obj.nvb, 'alpha')
            row = box.row()
            row.operator('kb.rebuild_material_nodes')

            row = layout.row()
            box = row.box()
            split = box.split()
            col = split.column()
            col.prop(obj.nvb, 'render', text='Render')
            col.prop(obj.nvb, 'shadow', text='Shadow')
            col.prop(obj.nvb, 'lightmapped', text='Lightmapped')
            col.prop(obj.nvb, 'tangentspace', text='Tangentspace')
            col.prop(obj.nvb, 'm_bIsBackgroundGeometry', text='Background Geometry')
            col = split.column()
            col.prop(obj.nvb, 'beaming', text='Beaming')
            col.prop(obj.nvb, 'inheritcolor', text='Inherit Color')
            col.prop(obj.nvb, 'rotatetexture', text='Rotate Texture')
            col.prop(obj.nvb, 'hologram_donotdraw')
            row = box.row()
            row.prop(obj.nvb, 'transparencyhint', text='Transparency Hint')
            row = box.row()
            row.prop(obj.nvb, 'animateuv')
            if obj.nvb.animateuv:
                row = box.row()
                split = box.split()
                col = split.column()
                col.prop(obj.nvb, 'uvdirectionx')
                col.prop(obj.nvb, 'uvjitter')
                col = split.column()
                col.prop(obj.nvb, 'uvdirectiony')
                col.prop(obj.nvb, 'uvjitterspeed')
            row = box.row()
            row.prop(obj.nvb, 'dirt_enabled')
            if obj.nvb.dirt_enabled:
                row = box.row()
                row.prop(obj.nvb, 'dirt_texture')
                row = box.row()
                row.prop(obj.nvb, 'dirt_worldspace')
            row = box.row()
            row.label(text = 'Smoothgroups')
            row.prop(obj.nvb, 'smoothgroup', text='Smooth Group', expand = True)

            # Additional props for danglymeshes
            if (obj.nvb.meshtype == nvb_def.Meshtype.DANGLYMESH):
                sep = layout.separator()

                row = layout.row()
                box = row.box()
                row = box.row()
                row.label(text = 'Danglymesh Properties')
                row = box.row()
                row.prop_search(obj.nvb, 'constraints', obj, 'vertex_groups', text='Constraints')
                row = box.row()
                row.prop(obj.nvb, 'period', text='Period')
                row = box.row()
                row.prop(obj.nvb, 'tightness', text='Tightness')
                row = box.row()
                row.prop(obj.nvb, 'displacement', text='Displacement')

            # Additional props for skins
            elif (obj.nvb.meshtype == nvb_def.Meshtype.SKIN):
                sep = layout.separator()

                row = layout.row()
                box = row.box()
                row = box.row()
                row.label(text = 'Create vertex group: ')
                row = box.row(align = True)
                row.prop_search(obj.nvb, 'skingroup_obj', context.scene, 'objects')
                row.operator('nvb.skingroup_add', text = '', icon='ADD')

            # Additional props for aabb walkmeshes
            elif (obj.nvb.meshtype == nvb_def.Meshtype.AABB):
                sep = layout.separator()

                row = layout.row()
                box = row.box()
                row = box.row()
                row.prop(obj.nvb, 'lytposition', text='LYT Position')
                row = box.row()
                row.operator('nvb.load_wok_mats', text = 'Load walkmesh materials', icon='NONE')


class KB_UL_path_points(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop_search(item, 'point', bpy.data, 'objects')


class NVB_PT_path_point(bpy.types.Panel):
    bl_label = 'Odyssey Path Point'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    @classmethod
    def poll(cls, context):
        return nvb_utils.is_path_point(context.object)

    def draw(self, context):
        row = self.layout.row()
        box = row.box()
        box.label(text='Connections')
        row = box.row()
        row.template_list('KB_UL_path_points', '', context.object.nvb, 'path_connections', context.object.nvb, 'active_path_connection')
        col = row.column(align=True)
        col.operator('kb.add_path_connection', icon='ADD', text='')
        col.operator('kb.remove_path_connection', icon='REMOVE', text='')
