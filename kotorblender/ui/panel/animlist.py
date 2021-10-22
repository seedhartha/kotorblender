import bpy

from ... import utils


class KB_PT_animlist(bpy.types.Panel):
    """Property panel for animationslist.

    Property panel for additional properties needed for the mdl file
    format. This is only available for EMPTY objects.
    It is located under the object data panel in the properties window
    """

    bl_label = "Odyssey Animations"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        """Draw only if part of a valid mdl is selected."""
        return utils.is_root_dummy(context.object)

    def draw(self, context):
        """Draw the panel."""
        layout = self.layout
        mdl_base = utils.get_mdl_root_from_object(context.object)
        if mdl_base:
            # Display and add/remove animations
            row = layout.row()
            row.template_list("KB_UL_anims", "TheAnimList",
                              mdl_base.kb, "animList",
                              mdl_base.kb, "animListIdx",
                              rows=7)
            col = row.column(align=True)
            col.operator("kb.anim_new", icon='ADD', text="")
            col.operator("kb.anim_delete", icon='REMOVE', text="")
            col.separator()
            col.operator("kb.anim_move",
                         icon='TRIA_UP', text="").direction = "UP"
            col.operator("kb.anim_move",
                         icon='TRIA_DOWN', text="").direction = "DOWN"
            col.separator()
            col.operator("kb.anim_focus",
                         icon='RENDER_ANIMATION', text="")
            col.menu("KB_MT_animlist_specials",
                     icon='DOWNARROW_HLT', text="")
            anim_list = mdl_base.kb.animList
            anim_list_idx = mdl_base.kb.animListIdx
            if anim_list_idx >= 0 and len(anim_list) > anim_list_idx:
                anim = anim_list[anim_list_idx]
                row = layout.row()
                row.prop(anim, "name")
                row = layout.row()
                row.prop(anim, "root_obj")
                row = layout.row()
                row.prop(anim, "transtime")
                row = layout.row()
                split = row.split()
                col = split.column(align=True)
                col.prop(anim, "frameStart")
                col.prop(anim, "frameEnd")

                # Event Helper. Display and add/remove events.
                box = layout.box()
                box.label(text="Events")

                row = box.row()
                row.template_list("KB_UL_anim_events", "TheEventList",
                                  anim, "eventList",
                                  anim, "eventListIdx")
                col = row.column(align=True)
                col.operator("kb.anim_event_new", text="", icon='ADD')
                col.operator("kb.anim_event_delete", text="", icon='REMOVE')
                col.separator()
                col.operator("kb.anim_event_move",
                             icon='TRIA_UP', text="").direction = "UP"
                col.operator("kb.anim_event_move",
                             icon='TRIA_DOWN', text="").direction = "DOWN"
            layout.separator()