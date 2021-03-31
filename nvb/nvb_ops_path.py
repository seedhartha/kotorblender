import bpy
import bpy_extras

from . import nvb_utils


class KB_OT_add_connection(bpy.types.Operator):
    bl_idname = 'kb.add_path_connection'
    bl_label = "Add Odyssey Path Connection"

    @classmethod
    def poll(cls, context):
        return nvb_utils.isPathPoint(context.object)

    def execute(self, context):
        context.object.nvb.path_connections.add()
        return {'FINISHED'}


class KB_OT_remove_connection(bpy.types.Operator):
    bl_idname = 'kb.remove_path_connection'
    bl_label = "Remove Odyssey Path Connection"

    @classmethod
    def poll(cls, context):
        return nvb_utils.isPathPoint(context.object) and (len(context.object.nvb.path_connections) > 0)

    def execute(self, context):
        context.object.nvb.path_connections.remove(context.object.nvb.active_path_connection)
        return {'FINISHED'}


class KB_OT_export_path(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    '''Export Odyssey Engine path (.pth)'''

    bl_idname = 'kb.pthexport'
    bl_label  = 'Export Odyssey PTH'

    filename_ext = '.pth'

    filter_glob : bpy.props.StringProperty(
            default = '*.pth',
            options = {'HIDDEN'})

    def execute(self, context):
        with open(self.filepath, 'w') as f:
            for o in bpy.data.objects:
                if nvb_utils.isPathPoint(o):
                    f.write('{} {:.7f} {:.7f} {:.7f} {}\n'.format(o.name, *o.location, len(o.nvb.path_connections)))
                    for conn in o.nvb.path_connections:
                        f.write('  {}\n'.format(conn.point))

        return {'FINISHED'}
