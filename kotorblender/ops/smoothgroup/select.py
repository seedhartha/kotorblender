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

class KB_OT_select_smoothgroup(bpy.types.Operator):
    bl_idname = "kb.smoothgroup_select"
    bl_label = "Smoothgroup select"
    bl_options = {'UNDO'}

    sg_number : bpy.props.IntProperty()
    action : bpy.props.EnumProperty(items=(
        ("SEL", "Select", "Select faces with this smoothgroup"),
        ("DESEL", "Deselect", "Deselect faces with this smoothgroup")
    ))

    @classmethod
    def description(self, context, properties):
        if self.action == "SEL":
            return "Select faces with this smoothgroup"
        else:
            return "Deselect faces with this smoothgroup"

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.object.data)
        bm.faces.ensure_lookup_table()
        # the smoothgroup data layer
        sg_layer = bm.faces.layers.int.get(defines.sg_layer_name)
        # convert sg_number to actual sg bitflag value
        sg_value = pow(2, self.sg_number)

        for face in bm.faces:
            if sg_value & face[sg_layer]:
                # select/deselect face
                face.select_set(self.action == "SEL")
        # required to get the selection change to show in the 3D view
        bmesh.update_edit_mesh(context.object.data)
        return {'FINISHED'}