import bpy


class KB_UL_anims(bpy.types.UIList):
    """UI List for displaying animations."""

    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname, index):
        """Draw a single animation."""

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False)
            icn = 'CHECKBOX_DEHLT' if item.mute else 'CHECKBOX_HLT'
            layout.prop(item, "mute", text="", icon=icn, emboss=False)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon='POSE_DATA')