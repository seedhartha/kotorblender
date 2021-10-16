import bpy


class KB_UL_anim_events(bpy.types.UIList):
    """UI List for displaying animation events."""

    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname, index):
        """Draw a single animation event."""

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.7, align=False)
            split.prop(item, "name", text="", emboss=False)
            row = split.row(align=True)
            row.prop(item, "frame", text="", emboss=False)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label("", icon='LIGHT')