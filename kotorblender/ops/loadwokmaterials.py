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

from .. import defines


class KB_OT_load_wok_materials(bpy.types.Operator):
    """
    Load all materials for aabb walkmeshes for the selected object. Current
    material slots will be deleted.
    """
    bl_idname = "kb.load_wok_mats"
    bl_label  = "Load walkmesh materials"

    def execute(self, context):
        """
        - Deletes all current materials
        - adds walkmesh materials
        """
        selected_object = context.object
        if (selected_object) and (selected_object.type == 'MESH'):
            object_mesh = selected_object.data

            # Remove all current material slots
            for _ in range(len(selected_object.material_slots)):
                bpy.ops.object.material_slot_remove()

            # Create materials
            for matDef in defines.wok_materials:
                matName = matDef[0]

                # Walkmesh materials should be shared across multiple
                # walkmeshes, as they always identical
                if matName in bpy.data.materials.keys():
                    mat = bpy.data.materials[matName]
                else:
                    mat = bpy.data.materials.new(matName)

                    mat.diffuse_color      = [*matDef[1], 1.0]
                    mat.specular_color     = (0.0,0.0,0.0)
                    mat.specular_intensity = matDef[2]

                object_mesh.materials.append(mat)
        else:
            self.report({'INFO'}, "A mesh must be selected")
            return {'CANCELLED'}

        return {'FINISHED'}
