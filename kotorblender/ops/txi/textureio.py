import bpy

from ...format import txi as txiformat


class KB_OT_texture_io(bpy.types.Operator):
    bl_idname = "kb.texture_info_io"
    bl_label = "Texture Info"
    bl_property = "action"
    bl_options = {'UNDO'}

    action : bpy.props.EnumProperty(items=(
        ("LOAD", "Load", "Import TXI file for this texture"),
        ("SAVE", "Save", "Export TXI file for this texture")
    ))

    def execute(self, context):
        if self.action == "SAVE":
            txiformat.save_txi(context.texture, self)
        else:
            txiformat.load_txi(context.texture, self)
        return {'FINISHED'}