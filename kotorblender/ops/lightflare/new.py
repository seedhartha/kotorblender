import bpy


class KB_OT_new_lightflare(bpy.types.Operator):
    """ Add a new item to the flare list """

    bl_idname = "kb.lightflare_new"
    bl_label  = "Add a new flare to a light"

    def execute(self, context):
        if (context.object.type == 'LIGHT'):
            context.object.kb.flareList.add()

        return{'FINISHED'}