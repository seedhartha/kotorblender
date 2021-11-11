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

from ... import defines


class KB_PT_empty(bpy.types.Panel):
    bl_label = "Odyssey Dummy"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'EMPTY')

    def draw(self, context):
        obj = context.object
        layout = self.layout

        row = layout.row()
        row.prop(obj.kb, "dummytype", text="Type")
        row = layout.row()
        row.prop(obj.kb, "node_number")
        row = layout.row()
        row.prop(obj.kb, "export_order")
        layout.separator()

        # Display properties depending on type of the empty
        if obj.kb.dummytype == defines.Dummytype.MDLROOT:
            row = layout.row()
            box = row.box()
            split = box.split()
            col = split.column()
            col.label(text="Classification:")
            col.label(text="Supermodel:")
            col.label(text="Affected by Fog:")
            col.label(text="Animation Root:")
            col.label(text="Animation Scale:")
            col = split.column()
            col.prop(obj.kb, "classification", text="")
            col.prop(obj.kb, "supermodel", text="")
            col.prop(obj.kb, "affected_by_fog", text="")
            col.prop_search(obj.kb, "animroot", context.collection, "objects", text="")
            col.prop(obj.kb, "animscale", text="")
            layout.separator()
            row = box.row()
            row.operator("kb.rebuild_armature")

        elif (obj.kb.dummytype == defines.Dummytype.REFERENCE):
            row = layout.row()
            box = row.box()
            row = box.row()
            row.prop(obj.kb, "refmodel")
            row = box.row()
            row.prop(obj.kb, "reattachable")
