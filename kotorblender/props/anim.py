import bpy

from .animevent import AnimEventPropertyGroup


class AnimPropertyGroup(bpy.types.PropertyGroup):
    """Properties for a single animation in the animation list."""

    name : bpy.props.StringProperty(name="Name",
                                    description="Name of this animation",
                                    default="unnamed", options=set())
    ttime : bpy.props.FloatProperty(
        name="Transitiontime", subtype='TIME', options=set(),
        description="Blending time between animations in seconds",
        default=0.25, min=0.0, soft_max=60.0)
    transtime : bpy.props.FloatProperty(
        name="Transitiontime", subtype='TIME', options=set(),
        description="Blending time between animations in frames",
        default=7.5, min=0.0, soft_max=60.0)
    root : bpy.props.StringProperty(name="Root", default="", options=set(),
                                    description="Entry point of the animation")
    root_obj : bpy.props.StringProperty(
        name="Root", description="Entry point of the animation",
        default="unnamed", options=set())
    mute : bpy.props.BoolProperty(name="Export", default=False, options=set(),
                                  description="Export animation to MDL")
    frameStart : bpy.props.IntProperty(name="Start", default=0, options=set(),
                                       description="Animation Start", min=0)
    frameEnd : bpy.props.IntProperty(name="End", default=0, options=set(),
                                     description="Animation End", min=0)

    eventList : bpy.props.CollectionProperty(type=AnimEventPropertyGroup)
    eventListIdx : bpy.props.IntProperty(name="Index for event List",
                                         default=0, options=set())