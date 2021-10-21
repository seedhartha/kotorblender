import bpy
import bpy_extras


class KB_OT_export_mdl(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export Odyssey Engine model (.mdl)"""

    bl_idname = "kb.mdlexport"
    bl_label  = "Export Odyssey MDL"

    filename_ext = ".mdl"

    filter_glob : bpy.props.StringProperty(
            default = "*.mdl",
            options = {'HIDDEN'})

    def execute(self, context):
        return {'FINISHED'}