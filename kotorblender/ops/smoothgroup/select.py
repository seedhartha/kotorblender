import bmesh
import bpy

from ... import kb_def

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
        sg_layer = bm.faces.layers.int.get(kb_def.sg_layer_name)
        # convert sg_number to actual sg bitflag value
        sg_value = pow(2, self.sg_number)

        for face in bm.faces:
            if sg_value & face[sg_layer]:
                # select/deselect face
                face.select_set(self.action == "SEL")
        # required to get the selection change to show in the 3D view
        bmesh.update_edit_mesh(context.object.data)
        return {'FINISHED'}