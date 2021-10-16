import bpy


class KB_OT_add_skingroup(bpy.types.Operator):
    bl_idname = "kb.skingroup_add"
    bl_label  = "Add new Skingroup"

    def execute(self, context):
        obj        = context.object
        skingrName = obj.nvb.skingroup_obj
        # Check if there is already a vertex group with this name
        if skingrName:
            if (skingrName not in obj.vertex_groups.keys()):
                # Create the vertex group
                obj.vertex_groups.new(name=skingrName)
                obj.nvb.skingroup_obj = ""

                self.report({'INFO'}, "Created vertex group " + skingrName)
                return{'FINISHED'}
            else:
                self.report({'INFO'}, "Duplicate Name")
                return {'CANCELLED'}
        else:
            self.report({'INFO'}, "Empty Name")
            return {'CANCELLED'}