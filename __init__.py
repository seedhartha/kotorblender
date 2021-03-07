# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "KotORBlender",
    "author": "Attila Gyoerkoes & J.W. Brandon & Vsevolod Kremianskii",
    "version": (2, 0, 0),
    "blender": (2, 80, 0),
    "location": "File > Import-Export, Object Properties",
    "description": "Import, export and edit Odyssey (KotOR) ASCII MDL format",
    'warning': "cannot be used with Neverblender enabled",
    "wiki_url": ""
                "",
    "tracker_url": "",
    "category": "Import-Export"}


if 'bpy' in locals():
    import importlib
    importlib.reload(nvb.nvb_anim)
    importlib.reload(nvb.nvb_animnode)
    importlib.reload(nvb.nvb_def)
    importlib.reload(nvb.nvb_io)
    importlib.reload(nvb.nvb_light)
    importlib.reload(nvb.nvb_material)
    importlib.reload(nvb.nvb_mdl)
    importlib.reload(nvb.nvb_node)
    importlib.reload(nvb.nvb_ops_anim)
    importlib.reload(nvb.nvb_ops)
    importlib.reload(nvb.nvb_props)
    importlib.reload(nvb.nvb_teximage)
    importlib.reload(nvb.nvb_ui)
    importlib.reload(nvb.nvb_utils)
else:
    from kotorblender.nvb import nvb_anim
    from kotorblender.nvb import nvb_animnode
    from kotorblender.nvb import nvb_def
    from kotorblender.nvb import nvb_io
    from kotorblender.nvb import nvb_light
    from kotorblender.nvb import nvb_material
    from kotorblender.nvb import nvb_mdl
    from kotorblender.nvb import nvb_node
    from kotorblender.nvb import nvb_ops
    from kotorblender.nvb import nvb_ops_anim
    from kotorblender.nvb import nvb_props
    from kotorblender.nvb import nvb_teximage
    from kotorblender.nvb import nvb_ui
    from kotorblender.nvb import nvb_utils

import addon_utils
import bpy


def menu_func_export(self, context):
    self.layout.operator(nvb_ops.NVB_OP_Export.bl_idname, text="Odyssey (KotOR) (.mdl)")


def menu_func_import(self, context):
    self.layout.operator(nvb_ops.NVB_OP_Import.bl_idname, text="Odyssey (KotOR) (.mdl)")


classes = (
    nvb_props.NVB_PG_ANIMEVENT,
    nvb_props.NVB_PG_FLARE,

    nvb_props.KB_PG_animevent,
    nvb_props.KB_PG_anim,
    nvb_props.KB_PG_OBJECT,
    nvb_props.KB_PG_TEXTURE.PropListItem,
    nvb_props.KB_PG_TEXTURE,

    nvb_ops.LoadWokMaterials,
    nvb_ops.NVB_LIST_OT_AnimEvent_Delete,
    nvb_ops.NVB_LIST_OT_AnimEvent_Move,
    nvb_ops.NVB_LIST_OT_AnimEvent_New,
    nvb_ops.NVB_LIST_OT_LightFlare_Delete,
    nvb_ops.NVB_LIST_OT_LightFlare_Move,
    nvb_ops.NVB_LIST_OT_LightFlare_New,
    nvb_ops.NVB_OP_Export,
    nvb_ops.NVB_OP_Import,
    nvb_ops.NVBCHILDREN_SMOOTHGROUP,
    nvb_ops.NVBOBJECT_OT_AnimsceneAdd,
    nvb_ops.NVBOBJECT_OT_AnimsceneRename,
    nvb_ops.NVBOBJECT_OT_RenderMinimap,
    nvb_ops.NVBOBJECT_OT_SkingroupAdd,
    nvb_ops.NVBSKIN_BONE_OPS,
    nvb_ops.NVBSMOOTHGROUP_GENERATE,
    nvb_ops.NVBSMOOTHGROUP_SELECT,
    nvb_ops.NVBSMOOTHGROUP_TOGGLE,
    nvb_ops.NVBTEXTURE_BOX_OPS,
    nvb_ops.NVBTEXTURE_IO,
    nvb_ops.NVBTEXTURE_OPS,

    nvb_ops_anim.NVB_OT_amt_event_delete,
    nvb_ops_anim.NVB_OT_amt_event_new,
    nvb_ops_anim.NVB_OT_anim_clone,
    nvb_ops_anim.NVB_OT_anim_crop,
    nvb_ops_anim.NVB_OT_anim_delete,
    nvb_ops_anim.NVB_OT_anim_event_delete,
    nvb_ops_anim.NVB_OT_anim_event_move,
    nvb_ops_anim.NVB_OT_anim_event_new,
    nvb_ops_anim.NVB_OT_anim_focus,
    nvb_ops_anim.NVB_OT_anim_move,
    nvb_ops_anim.NVB_OT_anim_moveback,
    nvb_ops_anim.NVB_OT_anim_new,
    nvb_ops_anim.NVB_OT_anim_pad,
    nvb_ops_anim.NVB_OT_anim_scale,

    nvb_ui.NVB_PT_animlist,
    nvb_ui.NVB_PT_EMITTER,
    nvb_ui.NVB_PT_EMPTY,
    nvb_ui.NVB_PT_LIGHT,
    nvb_ui.NVB_PT_MESH,
    nvb_ui.NVB_PT_SMOOTHGROUPS,
    nvb_ui.NVB_PT_TEXTURE,
    nvb_ui.NVB_UL_ANIMEVENTS,
    nvb_ui.NVB_UL_LIGHTFLARES,

    nvb_ui.KB_MT_animlist_specials,
    nvb_ui.KB_UL_anim_events,
    nvb_ui.KB_UL_anims,
)

def register():
    (load_dflt, nvb_loaded) = addon_utils.check('neverblender')
    if nvb_loaded:
        raise Exception('Do not enable both KotORBlender and Neverblender at the same time!')

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.nvb = bpy.props.PointerProperty(type=nvb_props.KB_PG_OBJECT)
    bpy.types.ImageTexture.nvb = bpy.props.PointerProperty(type=nvb_props.KB_PG_TEXTURE)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

    # gracefully co-exist with neverblender, within reason.
    # if neverblender is enabled and disabled while kotorblender
    # is enabled, kotorblender will be left in an error state
    # and must be re-enabled to resume normal functionality
    try:
        (load_dflt, nvb_loaded) = addon_utils.check('neverblender')
        if nvb_loaded:
            # this will cleanly reload neverblender so that nvb
            # will function after kotorblender has been disabled
            # NOTE: the user was warned not to do this, but help anyway
            import neverblender
            neverblender.unregister()
            # these are the attributes we share with nvb,
            # we could rename, but it would change a great deal of code,
            # it is better to keep the code similar enough to contribute
            if 'nvb' in dir(bpy.types.Object):
                del bpy.types.Object.nvb
            if 'nvb' in dir(bpy.types.ImageTexture):
                del bpy.types.ImageTexture.nvb
            neverblender.register()
    except:
        del bpy.types.Object.nvb
        del bpy.types.ImageTexture.nvb

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
