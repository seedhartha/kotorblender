import bpy


class KB_MT_animlist_specials(bpy.types.Menu):
    """Animation List Specials."""

    bl_label = "Animation List Specials"

    def draw(self, context):
        """Draw the panel."""
        layout = self.layout
        layout.operator("kb.anim_moveback",
                        icon='LOOP_FORWARDS')
        layout.operator("kb.anim_pad",
                        icon='FULLSCREEN_ENTER')
        layout.operator("kb.anim_crop",
                        icon='FULLSCREEN_EXIT')
        layout.operator("kb.anim_scale",
                        icon='SORTSIZE')
        layout.operator("kb.anim_clone",
                        icon='NODETREE')