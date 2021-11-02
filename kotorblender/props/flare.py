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

from .. import defines


class FlarePropertyGroup(bpy.types.PropertyGroup):
    """
    Properties for a single flare in the flare list
    """

    texture: bpy.props.StringProperty(name="Texture",
                                      description="Texture name",
                                      default=defines.NULL)
    size: bpy.props.FloatProperty(name="Size",
                                  description="Flare size",
                                  default=1)
    position: bpy.props.FloatProperty(name="Position",
                                      description="Flare position",
                                      default=1)
    colorshift: bpy.props.FloatVectorProperty(name="Colorshift",
                                              description="Colorshift",
                                              subtype='COLOR_GAMMA',
                                              default=(0.0, 0.0, 0.0),
                                              min=-1.0, max=1.0,
                                              soft_min=0.0, soft_max=1.0)
