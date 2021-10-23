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

import bmesh
import bpy

from ... import defines


class KB_PT_smoothgroups(bpy.types.Panel):
    bl_label = "Smoothgroups"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(self, context):
        ob = context.object
        try:
            return ob and ob.mode == 'EDIT' and ob.type == 'MESH'
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        custom_icon = 'NONE'

        layout = self.layout

        me = context.object.data
        bm = bmesh.from_edit_mesh(me)

        # smoothgroups are a face-level phenomenon, insist on being in face mode
        if bm.select_mode != {'FACE'}:
            layout.label("Face select only", icon = 'INFO')
            return

        # the smoothgroup data layer
        sg_layer = bm.faces.layers.int.get(defines.sg_layer_name)
        # count of faces per smoothgroup in this mesh
        sg = { i: 0 for i in range(32) }
        # smoothgroups in use on selected faces
        sg_selected = set()
        for face in bm.faces:
            if sg_layer is None:
                continue
            face_sg = face[sg_layer]
            for power in sg.keys():
                sg_val = pow(2, power)
                if face_sg & sg_val:
                    sg[power] += 1
                    if face.select:
                        sg_selected.add(power + 1)

        # display readout of smoothgroups in use on selected faces
        row = layout.row()
        row.label(text="Selection: {}".format(
            ", ".join(str(x) for x in sorted(sg_selected))
        ))

        # display readout of smoothgroups in use on this mesh
        for i in range(32):
            if sg[i]:
                row = layout.row(align=True)
                row.label("{}: {} faces".format(i + 1, sg[i]))
                op = row.operator("kb.smoothgroup_select", text="", icon='EDIT')
                op.sg_number = i
                op.action = "SEL"
                op = row.operator("kb.smoothgroup_select", text="", icon='X')
                op.sg_number = i
                op.action = "DESEL"

        # individual smoothgroup toggle buttons, apply to all selected faces
        row = layout.row(align=True)
        row.label(text="Toggle")
        row = layout.row(align=True)
        op = row.operator("kb.smoothgroup_toggle", text = "1", icon=custom_icon)
        op.sg_number = 0
        op.activity = int(sg[1])
        op = row.operator("kb.smoothgroup_toggle", text = "2", icon=custom_icon)
        op.sg_number = 1
        op.activity = int(sg[2])
        op = row.operator("kb.smoothgroup_toggle", text = "3", icon=custom_icon)
        op.sg_number = 2
        op.activity = int(sg[3])
        row = layout.row(align=True)
        op = row.operator("kb.smoothgroup_toggle", text = "4", icon=custom_icon)
        op.sg_number = 3
        op.activity = int(sg[4])
        op = row.operator("kb.smoothgroup_toggle", text = "5", icon=custom_icon)
        op.sg_number = 4
        op.activity = int(sg[5])
        op = row.operator("kb.smoothgroup_toggle", text = "6", icon=custom_icon)
        op.sg_number = 5
        op.activity = int(sg[6])
        row = layout.row(align=True)
        op = row.operator("kb.smoothgroup_toggle", text = "7", icon=custom_icon)
        op.sg_number = 6
        op.activity = int(sg[7])
        op = row.operator("kb.smoothgroup_toggle", text = "8", icon=custom_icon)
        op.sg_number = 7
        op.activity = int(sg[8])
        op = row.operator("kb.smoothgroup_toggle", text = "9", icon=custom_icon)
        op.sg_number = 8
        op.activity = int(sg[9])

        # smoothgroup generation tools, same process as 'auto' during export
        row = layout.row(align=True)
        row.label(text="Generate")
        row = layout.row(align=True)
        row.operator_enum("kb.smoothgroup_generate", "action")