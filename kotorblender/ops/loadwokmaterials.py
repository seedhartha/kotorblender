import bpy

from .. import kb_def


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
            for matDef in kb_def.wok_materials:
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