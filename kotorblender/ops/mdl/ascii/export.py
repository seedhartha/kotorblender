import bpy
import bpy_extras

from .... import io


class KB_OT_export_ascii_mdl(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export Odyssey Engine model (.mdl.ascii)"""

    bl_idname = "kb.asciimdlexport"
    bl_label  = "Export Odyssey ASCII MDL"

    filename_ext = ".mdl.ascii"

    filter_glob : bpy.props.StringProperty(
            default = "*.mdl.ascii",
            options = {'HIDDEN'})

    exports : bpy.props.EnumProperty(
            name = "Export",
            options = {'ENUM_FLAG'},
            items = (("ANIMATION", "Animations", "Export animations"),
                     ("WALKMESH", "Walkmesh", "Attempt to create walkmesh file (.pwk, .dwk or .wok depending on classification)"),
                     ),
            default = {"ANIMATION", "WALKMESH"})

    exportSmoothGroups : bpy.props.BoolProperty(
            name="Export Smooth Groups",
            description="Generate smooth groups from sharp edges" \
                        "(When disabled every face belongs to the same group)",
            default=True)

    applyModifiers : bpy.props.BoolProperty(
            name="Apply Modifiers",
            description="Apply Modifiers before exporting",
            default=True)

    def execute(self, context):
        return io.save_mdl(self, context, **self.as_keywords(ignore=("filter_glob","check_existing")))