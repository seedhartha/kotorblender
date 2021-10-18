import bpy

from .. import (defines, utils)


class KB_OT_render_minimap(bpy.types.Operator):
    bl_idname = "kb.render_minimap"
    bl_label  = "Render Minimap"

    def execute(self, context):
        """
        - Creates an camera and a light
        - Renders Minimap
        """
        obj   = context.object
        scene = bpy.context.scene
        if obj and (obj.type == 'EMPTY'):
            if (obj.nvb.dummytype == defines.Dummytype.MDLROOT):
                utils.setup_minimap_render(obj, scene)
                bpy.ops.render.render(use_viewport = True)

                self.report({'INFO'}, "Ready to render")
            else:
                self.report({'INFO'}, "A MDLROOT must be selected")
                return {'CANCELLED'}
        else:
            self.report({'INFO'}, "An Empty must be selected")
            return {'CANCELLED'}

        return {'FINISHED'}