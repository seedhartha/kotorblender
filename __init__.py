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
    "name": "KotorBlender",
    "author": "Attila Gyoerkoes & J.W. Brandon & Vsevolod Kremianskii",
    "version": (2, 0, 0),
    "blender": (2, 80, 0),
    "location": "File > Import-Export, Object Properties",
    "description": "Import, export and edit Odyssey (KotOR) ASCII MDL format",
    "warning": "cannot be used with NeverBlender enabled",
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
    importlib.reload(nvb.nvb_minimap)
    importlib.reload(nvb.nvb_node)
    importlib.reload(nvb.nvb_ops_anim)
    importlib.reload(nvb.nvb_ops_path)
    importlib.reload(nvb.nvb_ops)
    importlib.reload(nvb.nvb_props)
    importlib.reload(nvb.nvb_teximage)
    importlib.reload(nvb.nvb_ui)
    importlib.reload(nvb.nvb_utils)
else:
    from kotorblender.nvb import (nvb_anim, nvb_animnode, nvb_def, nvb_io,
                                  nvb_light, nvb_material, nvb_mdl, nvb_minimap,
                                  nvb_node, nvb_ops, nvb_ops_anim, nvb_ops_path,
                                  nvb_props, nvb_teximage, nvb_ui, nvb_utils)

import addon_utils
import bpy


def menu_func_import_mdl(self, context):
    self.layout.operator(nvb_ops.NVB_OT_import_mdl.bl_idname, text="KotOR Model (.mdl)")


def menu_func_import_lyt(self, context):
    self.layout.operator(nvb_ops.NVB_OT_import_lyt.bl_idname, text="KotOR Layout (.lyt)")


def menu_func_import_pth(self, context):
    self.layout.operator(nvb_ops_path.KB_OT_import_path.bl_idname, text="KotOR Path (.pth)")


def menu_func_export_mdl(self, context):
    self.layout.operator(nvb_ops.NVB_OT_export_mdl.bl_idname, text="KotOR Model (.mdl)")


def menu_func_export_lyt(self, context):
    self.layout.operator(nvb_ops.NVB_OT_export_lyt.bl_idname, text="KotOR Layout (.lyt)")


def menu_func_export_pth(self, context):
    self.layout.operator(nvb_ops_path.KB_OT_export_path.bl_idname, text="KotOR Path (.pth)")


classes = (
    nvb_props.KB_PG_OBJECT.PathConnection,
    nvb_props.KB_PG_TEXTURE.PropListItem,

    # Property Groups

    nvb_props.NVB_PG_ANIMEVENT,
    nvb_props.NVB_PG_FLARE,

    nvb_props.KB_PG_animevent,
    nvb_props.KB_PG_anim,
    nvb_props.KB_PG_OBJECT,
    nvb_props.KB_PG_TEXTURE,

    # Operators

    nvb_ops.KB_OT_load_wok_materials,
    nvb_ops.NVB_OT_delete_animevent,
    nvb_ops.NVB_OT_move_animevent,
    nvb_ops.NVB_OT_new_animevent,
    nvb_ops.NVB_OT_delete_lightflare,
    nvb_ops.NVB_OT_move_lightflare,
    nvb_ops.NVB_OT_new_lightflare,
    nvb_ops.NVB_OT_export_lyt,
    nvb_ops.NVB_OT_export_mdl,
    nvb_ops.NVB_OT_import_lyt,
    nvb_ops.NVB_OT_import_mdl,
    nvb_ops.NVB_OT_children_smoothgroup,
    nvb_ops.NVB_OT_add_animscene,
    nvb_ops.NVB_OT_rename_animscene,
    nvb_ops.NVB_OT_render_minimap,
    nvb_ops.NVB_OT_add_skingroup,
    nvb_ops.NVB_OT_skin_bone_ops,
    nvb_ops.NVB_OT_generate_smoothgroup,
    nvb_ops.NVB_OT_select_smoothgroup,
    nvb_ops.NVB_OT_toggle_smoothgroup,
    nvb_ops.NVB_OT_texture_box_ops,
    nvb_ops.NVB_OT_texture_io,
    nvb_ops.NVB_OT_texture_ops,

    nvb_ops.KB_OT_rebuild_material_nodes,

    # Animation Operators

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

    # Path Operators

    nvb_ops_path.KB_OT_add_connection,
    nvb_ops_path.KB_OT_export_path,
    nvb_ops_path.KB_OT_import_path,
    nvb_ops_path.KB_OT_remove_connection,

    # Panels

    nvb_ui.NVB_PT_animlist,
    nvb_ui.NVB_PT_emitter,
    nvb_ui.NVB_PT_empty,
    nvb_ui.NVB_PT_light,
    nvb_ui.NVB_PT_mesh,
    nvb_ui.NVB_PT_path_point,
    nvb_ui.NVB_PT_smoothgroups,
    nvb_ui.NVB_PT_texture,

    # Menus

    nvb_ui.KB_MT_animlist_specials,

    # UI Lists

    nvb_ui.NVB_UL_animevents,
    nvb_ui.NVB_UL_lightflares,

    nvb_ui.KB_UL_anim_events,
    nvb_ui.KB_UL_anims,
    nvb_ui.KB_UL_path_points
)

def register():
    (load_dflt, nvb_loaded) = addon_utils.check('neverblender')
    if nvb_loaded:
        raise Exception("Do not enable both KotorBlender and NeverBlender at the same time!")

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.nvb = bpy.props.PointerProperty(type=nvb_props.KB_PG_OBJECT)
    bpy.types.ImageTexture.nvb = bpy.props.PointerProperty(type=nvb_props.KB_PG_TEXTURE)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_mdl)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_lyt)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_pth)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_mdl)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_lyt)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_pth)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_pth)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_lyt)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_mdl)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_pth)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_lyt)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_mdl)

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
