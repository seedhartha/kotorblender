import bmesh
import bpy

from ... import kb_def


class KB_OT_toggle_smoothgroup(bpy.types.Operator):
    bl_idname = "kb.smoothgroup_toggle"
    bl_label = "Smoothgroup toggle"
    bl_options = {'UNDO'}

    sg_number : bpy.props.IntProperty()
    activity : bpy.props.IntProperty(default=0)

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.object.data)
        # the smoothgroup data layer
        sg_layer = bm.faces.layers.int.get(kb_def.sg_layer_name)
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