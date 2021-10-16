import os

import bpy
import bpy_extras

from .. import kb_def, kb_utils


class KB_OT_add_connection(bpy.types.Operator):
    bl_idname = "kb.add_path_connection"
    bl_label = "Add Odyssey Path Connection"

    @classmethod
    def poll(cls, context):
        return kb_utils.is_path_point(context.object)

    def execute(self, context):
        context.object.nvb.path_connections.add()
        return {'FINISHED'}


class KB_OT_remove_connection(bpy.types.Operator):
    bl_idname = "kb.remove_path_connection"
    bl_label = "Remove Odyssey Path Connection"

    @classmethod
    def poll(cls, context):
        return kb_utils.is_path_point(context.object) and (len(context.object.nvb.path_connections) > 0)

    def execute(self, context):
        context.object.nvb.path_connections.remove(context.object.nvb.active_path_connection)
        return {'FINISHED'}


class KB_OT_import_path(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Odyssey Engine path (.pth.ascii)"""

    bl_idname = "kb.pthimport"
    bl_label  = "Import Odyssey PTH"

    filename_ext = ".ascii"

    filter_glob : bpy.props.StringProperty(
            default = "*.pth.ascii",
            options = {'HIDDEN'})

    def execute(self, context):
        lines = [line.strip().split() for line in open(self.filepath, "r")]

        basename = os.path.basename(self.filepath)
        pathname = "Path_" + os.path.splitext(basename)[0]
        if pathname in bpy.data.objects:
            path_object = bpy.data.objects[pathname]
        else:
            path_object = bpy.data.objects.new(pathname, None)
            bpy.context.collection.objects.link(path_object)

        # First pass: read points, create point objects
        for line in lines:
            if len(line) == 5:
                point_object = bpy.data.objects.new(line[0], None)
                point_object.parent = path_object
                point_object.location = [float(x) for x in line[1:4]]
                point_object.nvb.dummytype = kb_def.Dummytype.PATHPOINT
                bpy.context.collection.objects.link(point_object)

        # Second pass: read connections, append to point objects
        point = None
        for line in lines:
            if len(line) == 5: # point
                name = line[0]
                if name in bpy.data.objects:
                    point = bpy.data.objects[name]
            elif len(line) == 1: # connection
                name = line[0]
                if name in bpy.data.objects:
                    conn = point.nvb.path_connections.add()
                    conn.point = name

        return {'FINISHED'}


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
