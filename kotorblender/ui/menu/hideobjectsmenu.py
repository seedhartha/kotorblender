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

class KB_MT_hide_menu(bpy.types.Menu):
    bl_label = "KBlender"

    def draw(self, context):
        layout = self.layout
        
        layout.operator("kb.hide_walkmeshes", icon='SURFACE_DATA')
        layout.operator("kb.hide_lights", icon='LIGHT')
        layout.operator("kb.hide_blockers", icon='INDIRECT_ONLY_OFF')
        layout.separator()
        layout.operator("kb.hide_charbones", icon='BONE_DATA')
        layout.operator("kb.hide_charnulls", icon='SHADING_BBOX')
        layout.separator()
        layout.operator("kb.unhide_walkmeshes", icon='OUTLINER_OB_SURFACE')
        layout.operator("kb.unhide_lights", icon='OUTLINER_OB_LIGHT')
        layout.operator("kb.unhide_blockers", icon='INDIRECT_ONLY_ON')
        layout.separator()
        layout.operator("kb.unhide_charbones", icon='BONE_DATA')
        layout.operator("kb.unhide_charnulls", icon='PIVOT_BOUNDBOX')
        layout.separator()
        layout.operator("kb.unhide_all")
