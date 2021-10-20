import bpy
import bpy_extras

from ... import io


class KB_OT_import_mdl(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Odyssey Engine model (.mdl)"""

    bl_idname = "kb.mdlimport"
    bl_label = "Import Odyssey MDL"
    bl_options = {'UNDO'}

    filename_ext = ".mdl"

    filter_glob : bpy.props.StringProperty(
            default = "*.mdl;*.mdl.ascii",
            options = {'HIDDEN'})

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

    createArmature : bpy.props.BoolProperty(
            name = "Import Armature",
            description = "Import armature from bone nodes",
            default = False)

    textureSearch : bpy.props.BoolProperty(
            name = "Image search",
            description = "Search for images in subdirectories" \
                          " (Warning, may be slow)",
            default = False)

    def execute(self, context):
        return io.load_mdl(self, context, **self.as_keywords(ignore=("filter_glob",)))