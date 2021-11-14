# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy

from .animevent import AnimEventPropertyGroup


class AnimPropertyGroup(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    transtime: bpy.props.FloatProperty(name="Transition Time",
                                       description="Blending time between animations in seconds",
                                       default=0.25, min=0.0, max=2.0)
    root: bpy.props.StringProperty(name="Root", description="This animation should only affect children of selected object")
    frame_start: bpy.props.IntProperty(name="Start Frame", min=0)
    frame_end: bpy.props.IntProperty(name="End Frame", min=0)
    event_list: bpy.props.CollectionProperty(type=AnimEventPropertyGroup)
    event_list_idx: bpy.props.IntProperty()
