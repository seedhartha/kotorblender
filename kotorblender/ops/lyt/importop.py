import bpy
import bpy_extras

from ... import kb_io


class KB_OT_import_lyt(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Odyssey Engine layout (.lyt)"""

    bl_idname = "kb.lytimport"
    bl_label = "Import Odyssey LYT"
    bl_options = {'UNDO'}

    filename_ext = ".lyt"

    filter_glob : bpy.props.StringProperty(
        default="*.lyt",
        options={'HIDDEN'})

    importGeometry : bpy.props.BoolProperty(
            name = "Import Geometry",
            description = "Disable if only animations are needed",
            default = True)

    importSmoothGroups : bpy.props.BoolProperty(
            name = "Import Smooth Groups",
            description = "Import smooth groups as sharp edges",
            default = True)

    importMaterials : bpy.props.BoolProperty(
            name = "Import Materials",
            description = "Import materials",
            default = True)

    importAnim : bpy.props.BoolProperty(
            name = "Import Animations",
            description = "Import animations",
            default = True)

    importWalkmesh : bpy.props.BoolProperty(
            name = "Import Walkmesh",
            description = "Attempt to load placeable and door walkmeshes",
            default = True)

    textureSearch : bpy.props.BoolProperty(
            name="Image search",
            description="Search for images in subdirectories" \
                        " (Warning, may be slow)",
            default=False)

    def execute(self, context):
        return kb_io.load_lyt(self, context, **self.as_keywords(ignore=("filter_glob",)))