import bpy


class KB_OT_texture_ops(bpy.types.Operator):
    bl_idname = "kb.texture_info_ops"
    bl_label = "Texture Info Operations"
    bl_property = "action"
    bl_options = {'UNDO'}

    action : bpy.props.EnumProperty(items=(
        ("RESET", "Reset", "Reset the property to default value. This will prevent it from being written to TXI file output."),
        ("NYI", "Other", "")
    ))
    propname : bpy.props.StringProperty(default="")

    def execute(self, context):
        if self.propname == "":
            return {'FINISHED'}
        if self.action == "RESET":
            attr_def = getattr(bpy.types.ImageTexture.nvb[1]["type"], self.propname)[1]
            if "default" in attr_def:
                setattr(context.texture.nvb, self.propname, attr_def["default"])
        return {'FINISHED'}