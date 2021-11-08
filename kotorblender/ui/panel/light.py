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
    """
    Property panel for additional light properties. This
    holds all properties not supported by blender at the moment,
    but used by OpenGL and the aurora engine. This is only available
    for LIGHT objects.
    It is located under the object data panel in the properties window
    """
    bl_label = "Odyssey Light"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'LIGHT')

    def draw(self, context):
        obj = context.object
        layout = self.layout

        row = layout.row()
        row.prop(obj.kb, "node_number")
        row = layout.row()
        row.prop(obj.kb, "export_order")

        layout.separator()

        row = layout.row()
        box = row.box()

        row = box.row()
        row.prop(obj.kb, "lightpriority", text="Priority")
        row = box.row()
        row.prop(obj.kb, "radius", text="Radius")
        row = box.row()
        row.prop(obj.kb, "multiplier", text="Multiplier")

        split = box.split()
        col = split.column(align=True)
        col.prop(obj.kb, "ambientonly", text="Ambient Only")
        col.prop(obj.kb, "shadow", text="Shadows")
        col = split.column(align=True)
        col.prop(obj.kb, "fadinglight", text="Fading")
        col.prop(obj.kb, "isdynamic", text="Dynamic Type")
        col.prop(obj.kb, "affectdynamic", text="Affect dynamic")

        layout.separator()

        # Lens flares
        row = layout.row()
        box = row.box()
        row = box.row()
        row.prop(obj.kb, "lensflares")
        sub = row.row(align=True)
        sub.active = obj.kb.lensflares
        sub.prop(obj.kb, "flareradius", text="Radius")
        row = box.row()
        row.active = obj.kb.lensflares
        row.template_list("KB_UL_lightflares", "The_List", obj.kb, "flare_list", obj.kb, "flare_listIdx")
        col = row.column(align=True)
        col.operator("kb.lightflare_new", icon='ADD', text="")
        col.operator("kb.lightflare_delete", icon='REMOVE', text="")
        col.separator()
        col.operator("kb.lightflare_move", icon='TRIA_UP', text="").direction = "UP"
        col.operator("kb.lightflare_move", icon='TRIA_DOWN', text="").direction = "DOWN"
        if obj.kb.flare_listIdx >= 0 and len(obj.kb.flare_list) > 0:
            item = obj.kb.flare_list[obj.kb.flare_listIdx]
            row = box.row()
            row.active = obj.kb.lensflares
            row.prop(item, "texture")
            row = box.row()
            row.active = obj.kb.lensflares
            row.prop(item, "colorshift")
            row = box.row()
            row.active = obj.kb.lensflares
            row.prop(item, "size")
            row.prop(item, "position")
