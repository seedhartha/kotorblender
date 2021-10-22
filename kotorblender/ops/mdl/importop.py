import bpy
import bpy_extras

from ...format.mdl.loader import MdlLoader


class KB_OT_import_mdl(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Odyssey Engine model (.mdl)"""

    bl_idname = "kb.mdlimport"
    bl_label = "Import Odyssey MDL"
    bl_options = {'UNDO'}

    filename_ext = ".mdl"

    filter_glob : bpy.props.StringProperty(
            default = "*.mdl",
            options = {'HIDDEN'})

    def execute(self, context):
        loader = MdlLoader(self.filepath)
        model = loader.load()
        self.add_model_to_collection(model)

        return {'FINISHED'}

    def add_model_to_collection(self, model):
        self.add_model_node_to_collection(model.root_node, None)

    def add_model_node_to_collection(self, node, parent):
        obj = bpy.data.objects.new(node.name, None)
        obj.parent = parent

        bpy.context.collection.objects.link(obj)

        for child in node.children:
            self.add_model_node_to_collection(child, obj)