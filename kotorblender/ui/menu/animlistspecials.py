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