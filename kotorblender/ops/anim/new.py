import bpy

from ... import utils


class KB_OT_anim_new(bpy.types.Operator):
    """Add a new animation to the animation list"""

    bl_idname = "kb.anim_new"
    bl_label = "Create new animation"

    @classmethod
    def poll(self, context):
        """Prevent execution if no object is selected."""
        mdl_base = utils.get_mdl_root_from_object(context.object)
        return (mdl_base is not None)

    def execute(self, context):
        """Create the animation"""
        mdl_base = utils.get_mdl_root_from_object(context.object)
        anim = utils.create_anim_list_item(mdl_base, True)
        anim.root_obj = mdl_base.name
        # Create an unique name
        name_list = [an.name for an in mdl_base.kb.animList]
        name_idx = 0
        new_name = "anim.{:0>3d}".format(name_idx)
        while new_name in name_list:
            name_idx += 1
            new_name = "anim.{:0>3d}".format(name_idx)
        anim.name = new_name
        return {'FINISHED'}