import bpy


class ListItemPropertyGroup(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(name="Property Name")