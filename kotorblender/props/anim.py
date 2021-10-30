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
    """Properties for a single animation in the animation list."""

    name: bpy.props.StringProperty(name="Name",
                                   description="Name of this animation",
                                   default="unnamed", options=set())
    ttime: bpy.props.FloatProperty(
        name="Transitiontime", subtype='TIME', options=set(),
        description="Blending time between animations in seconds",
        default=0.25, min=0.0, soft_max=60.0)
    transtime: bpy.props.FloatProperty(
        name="Transitiontime", subtype='TIME', options=set(),
        description="Blending time between animations in frames",
        default=7.5, min=0.0, soft_max=60.0)
    root: bpy.props.StringProperty(name="Root", default="", options=set(),
                                   description="Entry point of the animation")
    root_obj: bpy.props.StringProperty(
        name="Root", description="Entry point of the animation",
        default="unnamed", options=set())
    mute: bpy.props.BoolProperty(name="Export", default=False, options=set(),
                                 description="Export animation to MDL")
    frame_start: bpy.props.IntProperty(name="Start", default=0, options=set(),
                                       description="Animation Start", min=0)
    frame_end: bpy.props.IntProperty(name="End", default=0, options=set(),
                                     description="Animation End", min=0)

    event_list: bpy.props.CollectionProperty(type=AnimEventPropertyGroup)
    event_list_idx: bpy.props.IntProperty(name="Index for event List",
                                          default=0, options=set())
