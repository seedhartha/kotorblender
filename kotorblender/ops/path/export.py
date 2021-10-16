import bpy
import bpy_extras

from ... import kb_utils


class KB_OT_export_path(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export Odyssey Engine path (.pth.ascii)"""

    bl_idname = "kb.pthexport"
    bl_label  = "Export Odyssey PTH"

    filename_ext = ".ascii"

    filter_glob : bpy.props.StringProperty(
            default = "*.pth.ascii",
            options = {'HIDDEN'})

    def execute(self, context):
        with open(self.filepath, "w") as f:
            for o in bpy.data.objects:
                if kb_utils.is_path_point(o):
                    f.write("{} {:.7g} {:.7g} {:.7g} {}\n".format(o.name, *o.location, len(o.nvb.path_connections)))
                    for conn in o.nvb.path_connections:
                        f.write("  {}\n".format(conn.point))

        return {'FINISHED'}