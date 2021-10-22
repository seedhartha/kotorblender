import os

import bpy
import bpy_extras

from ...format.gff.loader import GffLoader

from ... import defines


class KB_OT_import_path(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Odyssey Engine path (.pth)"""

    bl_idname = "kb.pthimport"
    bl_label  = "Import Odyssey PTH"

    filename_ext = ".pth"

    filter_glob : bpy.props.StringProperty(
            default = "*.pth",
            options = {'HIDDEN'})

    def execute(self, context):
        basename = os.path.basename(self.filepath)
        pathname = "Path_" + os.path.splitext(basename)[0]
        if pathname in bpy.data.objects:
            path_object = bpy.data.objects[pathname]
        else:
            path_object = bpy.data.objects.new(pathname, None)
            bpy.context.collection.objects.link(path_object)

        loader = GffLoader(self.filepath, "PTH")
        tree = loader.load()
        points = []

        for i, point in enumerate(tree["Path_Points"]):
            name = self.get_point_name(i)
            object = bpy.data.objects.new(name, None)
            object.parent = path_object
            object.location = [point["X"], point["Y"], 0.0]
            object.kb.dummytype = defines.Dummytype.PATHPOINT
            bpy.context.collection.objects.link(object)
            points.append((point, object))

        for point, object in points:
            start = point["First_Conection"]
            stop = start + point["Conections"]
            conections = tree["Path_Conections"][start:stop]
            for conection in conections:
                name = self.get_point_name(conection["Destination"])
                if name in bpy.data.objects:
                    connection = object.kb.path_connections.add()
                    connection.point = name

        return {'FINISHED'}

    def get_point_name(self, idx):
        return "PathPoint{0:0>3}".format(idx)