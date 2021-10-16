import bpy


class KB_OT_move_lightflare(bpy.types.Operator):
    """ Move an item in the flare list """

    bl_idname = "kb.lightflare_move"
    bl_label  = "Move an item in the flare list"

    direction : bpy.props.EnumProperty(items=(("UP", "Up", ""), ("DOWN", "Down", "")))

    @classmethod
    def poll(self, context):
        return len(context.object.nvb.flareList) > 0

    def move_index(self, context):
        flareList = context.object.nvb.flareList
        flareIdx  = context.object.nvb.flareListIdx

        listLength = len(flareList) - 1 # (index starts at 0)
        newIdx = 0
        if self.direction == "UP":
            newIdx = flareIdx - 1
        elif self.direction == "DOWN":
            newIdx = flareIdx + 1

        newIdx   = max(0, min(newIdx, listLength))
        context.object.nvb.flareListIdx = newIdx

    def execute(self, context):
        flareList = context.object.nvb.flareList
        flareIdx  = context.object.nvb.flareListIdx

        if self.direction == "DOWN":
            neighbour = flareIdx + 1
            flareList.move(flareIdx, neighbour)
            self.move_index(context)
        elif self.direction == "UP":
            neighbour = flareIdx - 1
            flareList.move(neighbour, flareIdx)
            self.move_index(context)
        else:
            return{'CANCELLED'}

        return{'FINISHED'}