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


class KB_OT_generate_smoothgroup(bpy.types.Operator):
    bl_idname = "kb.smoothgroup_generate"
    bl_label = "Smoothgroup generate"
    bl_options = {'UNDO'}

    action : bpy.props.EnumProperty(items=(
        ("ALL", "All Faces", "Generate smoothgroups for all faces, replacing current values"),
        ("EMPTY", "Empty Faces", "Generate smoothgroups for all faces without current assignments"),
        ("SEL", "Selected Faces", "Generate smoothgroups for all selected faces, replacing current values")
    ))

    def execute(self, context):
        ob = context.object

        # switch into object mode so that the mesh gets committed,
        # and sg layer is available and modifiable
        initial_mode = ob.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        # copy the mesh, applying modifiers w/ render settings
        mesh = ob.to_mesh(scene=context.scene, apply_modifiers=True, settings='RENDER')

        # get, or create, the smoothgroups data layer on the object mesh (not the copy)
        sg_list = ob.data.polygon_layers_int.get(defines.sg_layer_name)
        if sg_list is None:
            sg_list = ob.data.polygon_layers_int.new(name=defines.sg_layer_name)

        # make all the faces on mesh copy smooth,
        # allowing calc_smooth_groups to work
        for face in mesh.polygons:
            face.use_smooth = True
        (sg, _) = mesh.calc_smooth_groups(use_bitflags=True)

        # apply the calculated smoothgroups
        if self.action == "ALL":
            sg_list.data.foreach_set("value", sg)
        else:
            for face in mesh.polygons:
                if (self.action == "EMPTY" and \
                    sg_list.data[face.index].value == 0) or \
                   (self.action == "SEL" and face.select):
                    sg_list.data[face.index].value = sg[face.index]

        # return object to original mode
        bpy.ops.object.mode_set(mode=initial_mode)
        # remove the copied mesh
        bpy.data.meshes.remove(mesh)
        return {'FINISHED'}