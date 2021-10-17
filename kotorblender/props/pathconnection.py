import bpy


class PathConnectionPropertyGroup(bpy.types.PropertyGroup):
    point : bpy.props.StringProperty(name="Point")