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


class KB_OT_toggle_smoothgroup(bpy.types.Operator):
    bl_idname = "kb.smoothgroup_toggle"
    bl_label = "Smoothgroup toggle"
    bl_options = {'UNDO'}

    sg_number : bpy.props.IntProperty()
    activity : bpy.props.IntProperty(default=0)

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.object.data)
        # the smoothgroup data layer
        sg_layer = bm.faces.layers.int.get(defines.sg_layer_name)
        # convert sg_number to actual sg bitflag value
        sg_value = pow(2, self.sg_number)
        for face in bm.faces:
            if not face.select:
                continue
            if sg_value & face[sg_layer]:
                # turn off for face
                face[sg_layer] &= ~sg_value
            else:
                # turn on for face
                face[sg_layer] |= sg_value
        bmesh.update_edit_mesh(context.object.data)
        return {'FINISHED'}