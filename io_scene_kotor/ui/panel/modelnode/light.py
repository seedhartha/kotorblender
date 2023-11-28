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


class KB_PT_light(bpy.types.Panel):
    bl_label = "Light"
    bl_parent_id = "KB_PT_modelnode"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'LIGHT'

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.use_property_split = True

        row = layout.row()
        row.prop(obj.kb, "lightpriority")
        row = layout.row()
        row.prop(obj.kb, "radius")
        row = layout.row()
        row.prop(obj.kb, "multiplier")
        row = layout.row()
        row.prop(obj.kb, "dynamictype")
        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "ambientonly")
        col.prop(obj.kb, "affectdynamic")
        col.prop(obj.kb, "shadow")
        col.prop(obj.kb, "fadinglight")
        col.prop(obj.kb, "lensflares")
        col.prop(obj.kb, "negativelight")


class KB_PT_light_lens_flares(bpy.types.Panel):
    bl_label = "Lens Flares"
    bl_parent_id = "KB_PT_light"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'LIGHT' and obj.kb.lensflares

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.use_property_split = True

        row = layout.row()
        row.prop(obj.kb, "flareradius", text="Radius")
        row = layout.row()
        row.template_list("KB_UL_lens_flares", "lens_flares", obj.kb, "flare_list", obj.kb, "flare_list_idx")
        col = row.column(align=True)
        col.operator("kb.add_lens_flare", icon='ADD', text="")
        col.operator("kb.delete_lens_flare", icon='REMOVE', text="")
        col.separator()
        col.operator("kb.move_lens_flare", icon='TRIA_UP', text="").direction = "UP"
        col.operator("kb.move_lens_flare", icon='TRIA_DOWN', text="").direction = "DOWN"

        if obj.kb.flare_list_idx >= 0 and obj.kb.flare_list_idx < len(obj.kb.flare_list):
            flare = obj.kb.flare_list[obj.kb.flare_list_idx]
            row = layout.row()
            row.prop(flare, "texture")
            row = layout.row()
            row.prop(flare, "colorshift")
            row = layout.row()
            row.prop(flare, "size")
            row = layout.row()
            row.prop(flare, "position")
