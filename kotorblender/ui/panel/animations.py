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

from ... import utils


class KB_PT_animations(bpy.types.Panel):
    bl_label = "Animations"
    bl_parent_id = "KB_PT_model"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return utils.is_mdl_root(context.object)

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.use_property_split = True

        # Animation List
        row = layout.row()
        row.template_list("UI_UL_list", "animations", obj.kb, "anim_list", obj.kb, "anim_list_idx", rows=7)
        col = row.column(align=True)
        col.operator("kb.add_animation", icon='ADD', text="")
        col.operator("kb.delete_animation", icon='REMOVE', text="")
        col.separator()
        col.operator("kb.move_animation", icon='TRIA_UP', text="").direction = "UP"
        col.operator("kb.move_animation", icon='TRIA_DOWN', text="").direction = "DOWN"
        col.separator()
        col.operator("kb.play_animation", icon='PLAY', text="")

        # Selected Animation
        anim_list = obj.kb.anim_list
        anim_list_idx = obj.kb.anim_list_idx
        if anim_list_idx >= 0 and anim_list_idx < len(anim_list):
            anim = anim_list[anim_list_idx]
            row = layout.row()
            col = row.column(align=True)
            col.prop(anim, "frame_start", text="Frame Start")
            col.prop(anim, "frame_end", text="End")
            row = layout.row()
            row.prop(anim, "transtime")
            row = layout.row()
            row.prop_search(anim, "root", context.collection, "objects")


class KB_PT_anim_events(bpy.types.Panel):
    bl_label = "Events"
    bl_parent_id = "KB_PT_animations"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        obj = context.object
        anim_list_idx = obj.kb.anim_list_idx
        return (utils.is_mdl_root(obj) and
                anim_list_idx >= 0 and
                anim_list_idx < len(obj.kb.anim_list))

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.use_property_split = True

        # Event List
        anim = obj.kb.anim_list[obj.kb.anim_list_idx]
        row = layout.row()
        row.template_list("UI_UL_list", "anim_events", anim, "event_list", anim, "event_list_idx")
        col = row.column(align=True)
        col.operator("kb.add_anim_event", text="", icon='ADD')
        col.operator("kb.delete_anim_event", text="", icon='REMOVE')
        col.separator()
        col.operator("kb.move_anim_event", icon='TRIA_UP', text="").direction = "UP"
        col.operator("kb.move_anim_event", icon='TRIA_DOWN', text="").direction = "DOWN"

        # Selected Animation
        event_list = anim.event_list
        event_list_idx = anim.event_list_idx
        if event_list_idx >= 0 and event_list_idx < len(event_list):
            event = event_list[event_list_idx]
            row = layout.row()
            row.prop(event, "frame")
