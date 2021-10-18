import bpy

from .. import defines


class FlarePropertyGroup(bpy.types.PropertyGroup):
    """
    Properties for a single flare in the flare list
    """

    texture : bpy.props.StringProperty(name = "Texture",
                                       description = "Texture name",
                                       default = defines.null)
    size : bpy.props.FloatProperty(name = "Size",
                                 description = "Flare size",
                                 default = 1)
    position : bpy.props.FloatProperty(name = "Position",
                                       description = "Flare position",
                                       default = 1)
    colorshift : bpy.props.FloatVectorProperty( name = "Colorshift",
                                                description = "Colorshift",
                                                subtype = 'COLOR_GAMMA',
                                                default = (0.0, 0.0, 0.0),
                                                min = -1.0, max = 1.0,
                                                soft_min = 0.0, soft_max = 1.0)