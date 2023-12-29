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

from bpy.types import Menu


class KB_MT_kotor_lightmaps(Menu):
    bl_label = "Lightmaps"

    def draw(self, context):
        layout = self.layout
        layout.operator("kb.bake_lightmaps", text="Bake").lightmapped_only = False
        layout.operator("kb.bake_lightmaps", text="Bake lightmapped only")


class KB_MT_kotor_showhide(Menu):
    bl_label = "Show/Hide"

    def draw(self, context):
        layout = self.layout

        layout.operator("kb.show_walkmeshes", icon="OUTLINER_OB_SURFACE")
        layout.operator("kb.show_lights", icon="OUTLINER_OB_LIGHT")
        layout.operator("kb.show_emitters", icon="OUTLINER_OB_CURVES")
        layout.operator("kb.show_blockers", icon="INDIRECT_ONLY_ON")
        layout.operator("kb.show_char_bones", icon="BONE_DATA")
        layout.operator("kb.show_char_dummies", icon="PIVOT_BOUNDBOX")
        layout.separator()
        layout.operator("kb.hide_walkmeshes", icon="SURFACE_DATA")
        layout.operator("kb.hide_lights", icon="LIGHT")
        layout.operator("kb.hide_emitters", icon="CURVES_DATA")
        layout.operator("kb.hide_blockers", icon="INDIRECT_ONLY_OFF")
        layout.operator("kb.hide_char_bones", icon="BONE_DATA")
        layout.operator("kb.hide_char_dummies", icon="SHADING_BBOX")


class KB_MT_kotor(Menu):
    bl_label = "KotOR"

    def draw(self, context):
        layout = self.layout
        layout.menu("KB_MT_kotor_lightmaps")
        layout.menu("KB_MT_kotor_showhide")
