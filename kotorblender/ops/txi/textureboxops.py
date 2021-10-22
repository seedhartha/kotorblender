import bpy


class KB_OT_texture_box_ops(bpy.types.Operator):
    """ Hide/show Texture Info sub-groups"""
    bl_idname = "kb.texture_info_box_ops"
    bl_label = "Box Controls"
    bl_description = "Show/hide this property list"

    boxname : bpy.props.StringProperty(default="")

    def execute(self, context):
        if self.boxname == "":
            return {'FINISHED'}
        attrname = "box_visible_" + self.boxname
        texture = context.texture
        current_state = getattr(texture.kb, attrname)
        setattr(texture.kb, attrname, not current_state)
        return {'FINISHED'}