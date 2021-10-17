import bpy


class AnimEventPropertyGroup(bpy.types.PropertyGroup):
    """Properties for a single event in the even list."""

    name : bpy.props.StringProperty(name="Name", default="unnamed",
                                    description="Name for this event",
                                    options=set())
    frame : bpy.props.IntProperty(
        name="Frame", default=1,
        description="Frame at which the event should fire",
        options=set())