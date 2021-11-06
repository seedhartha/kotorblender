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
    """
    Property panel for additional properties needed for the mdl file
    format. This is only available for EMPTY objects.
    It is located under the object data panel in the properties window
    """
    bl_label = "Odyssey Dummy Properties"
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
            col.label(text="Ignore Fog:")
            col.label(text="Animation Root:")
            col.label(text="Animation Scale:")
            col = split.column()
            col.prop(obj.kb, "classification", text="")
            col.prop(obj.kb, "supermodel", text="")
            col.prop(obj.kb, "ignorefog", text="")
            col.prop(obj.kb, "animroot", text="")
            col.prop(obj.kb, "animscale", text="")
            layout.separator()

        elif (obj.kb.dummytype == defines.Dummytype.PWKROOT):
            pass

        elif (obj.kb.dummytype == defines.Dummytype.DWKROOT):
            pass

        elif (obj.kb.dummytype == defines.Dummytype.REFERENCE):
            row = layout.row()
            box = row.box()

            row = box.row()
            row.prop(obj.kb, "refmodel")
            row = box.row()
            row.prop(obj.kb, "reattachable")

        else:
            row = layout.row()
            box = row.box()

            row = box.row()
            row.prop(obj.kb, "dummysubtype")
