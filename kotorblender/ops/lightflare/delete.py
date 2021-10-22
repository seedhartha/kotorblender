import bpy


class KB_OT_delete_lightflare(bpy.types.Operator):
    """ Delete the selected item from the flare list """

    bl_idname = "kb.lightflare_delete"
    bl_label = "Deletes a flare from the light"

    @classmethod
    def poll(self, context):
        """ Enable only if the list isn't empty """
        return len(context.object.kb.flareList) > 0

    def execute(self, context):
        flareList = context.object.kb.flareList
        flareIdx  = context.object.kb.flareListIdx

        flareList.remove(flareIdx)
        if flareIdx > 0:
            flareIdx =flareIdx - 1

        return{"FINISHED"}