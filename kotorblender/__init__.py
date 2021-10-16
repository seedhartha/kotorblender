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
    "version": (2, 1, 0),
    "blender": (2, 80, 0),
    "location": "File > Import-Export, Object Properties",
    "description": "Import, export and edit Odyssey (KotOR) ASCII MDL format",
    "warning": "cannot be used with NeverBlender enabled",
    "wiki_url": ""
                "",
    "tracker_url": "",
    "category": "Import-Export"}

if 'bpy' in locals():
    from importlib import reload
    reload(animeventslist)
    reload(animlistpanel)
    reload(animlistspecialsmenu)
    reload(animops)
    reload(animslist)
    reload(binreader)
    reload(binwriter)
    reload(emitterpanel)
    reload(emptypanel)
    reload(gffloader)
    reload(gffsaver)
    reload(kb_aabb)
    reload(kb_anim)
    reload(kb_animnode)
    reload(kb_armature)
    reload(kb_def)
    reload(kb_glob)
    reload(kb_io)
    reload(kb_light)
    reload(kb_material)
    reload(kb_mdl)
    reload(kb_minimap)
    reload(kb_node)
    reload(kb_parse)
    reload(kb_props)
    reload(kb_teximage)
    reload(kb_txi)
    reload(kb_utils)
    reload(lightflareslist)
    reload(lightpanel)
    reload(mainops)
    reload(mdlloader)
    reload(mdlsaver)
    reload(meshpanel)
    reload(pathops)
    reload(pathpointpanel)
    reload(pathpointslist)
    reload(smoothgroupspanel)
    reload(texturepanel)
else:
    from . import (
        kb_aabb,
        kb_anim,
        kb_animnode,
        kb_armature,
        kb_def,
        kb_glob,
        kb_io,
        kb_light,
        kb_material,
        kb_mdl,
        kb_minimap,
        kb_node,
        kb_parse,
        kb_props,
        kb_teximage,
        kb_txi,
        kb_utils)
    from .format import (
        binreader,
        binwriter)
    from .format.gff import (
        loader as gffloader,
        saver as gffsaver)
    from .format.mdl import (
        loader as mdlloader,
        saver as mdlsaver)
    from .ops import (
        anim as animops,
        main as mainops,
        path as pathops)
    from .ui.list import (
        animevents as animeventslist,
        anims as animslist,
        lightflares as lightflareslist,
        pathpoints as pathpointslist)
    from .ui.menu import animlistspecials as animlistspecialsmenu
    from .ui.panel import (
        animlist as animlistpanel,
        emitter as emitterpanel,
        empty as emptypanel,
        light as lightpanel,
        mesh as meshpanel,
        pathpoint as pathpointpanel,
        smoothgroups as smoothgroupspanel,
        texture as texturepanel)

import addon_utils
import bpy


def menu_func_import_mdl(self, context):
    self.layout.operator(mainops.KB_OT_import_mdl.bl_idname, text="KotOR Model (.mdl)")


def menu_func_import_lyt(self, context):
    self.layout.operator(mainops.KB_OT_import_lyt.bl_idname, text="KotOR Layout (.lyt)")


def menu_func_import_pth(self, context):
    self.layout.operator(pathops.KB_OT_import_path.bl_idname, text="KotOR Path (.pth.ascii)")


def menu_func_export_mdl(self, context):
    self.layout.operator(mainops.KB_OT_export_mdl.bl_idname, text="KotOR Model (.mdl)")


def menu_func_export_lyt(self, context):
    self.layout.operator(mainops.KB_OT_export_lyt.bl_idname, text="KotOR Layout (.lyt)")


def menu_func_export_pth(self, context):
    self.layout.operator(pathops.KB_OT_export_path.bl_idname, text="KotOR Path (.pth.ascii)")


classes = (
    kb_props.ObjectPropertyGroup.PathConnection,
    kb_props.TexturePropertyGroup.PropListItem,

    # Property Groups

    kb_props.AnimEventPropertyGroup,
    kb_props.AnimPropertyGroup,
    kb_props.FlarePropertyGroup,
    kb_props.ObjectPropertyGroup,
    kb_props.TexturePropertyGroup,

    # Operators

    mainops.KB_OT_add_skingroup,
    mainops.KB_OT_children_smoothgroup,
    mainops.KB_OT_delete_lightflare,
    mainops.KB_OT_export_lyt,
    mainops.KB_OT_export_mdl,
    mainops.KB_OT_generate_smoothgroup,
    mainops.KB_OT_import_lyt,
    mainops.KB_OT_import_mdl,
    mainops.KB_OT_load_wok_materials,
    mainops.KB_OT_move_lightflare,
    mainops.KB_OT_new_lightflare,
    mainops.KB_OT_rebuild_material_nodes,
    mainops.KB_OT_recreate_armature,
    mainops.KB_OT_render_minimap,
    mainops.KB_OT_select_smoothgroup,
    mainops.KB_OT_texture_box_ops,
    mainops.KB_OT_texture_io,
    mainops.KB_OT_texture_ops,
    mainops.KB_OT_toggle_smoothgroup,

    # Animation Operators

    animops.KB_OT_amt_event_delete,
    animops.KB_OT_amt_event_new,
    animops.KB_OT_anim_clone,
    animops.KB_OT_anim_crop,
    animops.KB_OT_anim_delete,
    animops.KB_OT_anim_event_delete,
    animops.KB_OT_anim_event_move,
    animops.KB_OT_anim_event_new,
    animops.KB_OT_anim_focus,
    animops.KB_OT_anim_move,
    animops.KB_OT_anim_moveback,
    animops.KB_OT_anim_new,
    animops.KB_OT_anim_pad,
    animops.KB_OT_anim_scale,

    # Path Operators

    pathops.KB_OT_add_connection,
    pathops.KB_OT_export_path,
    pathops.KB_OT_import_path,
    pathops.KB_OT_remove_connection,

    # Panels

    animlistpanel.KB_PT_animlist,
    emitterpanel.KB_PT_emitter,
    emptypanel.KB_PT_empty,
    lightpanel.KB_PT_light,
    meshpanel.KB_PT_mesh,
    pathpointpanel.KB_PT_path_point,
    smoothgroupspanel.KB_PT_smoothgroups,
    texturepanel.KB_PT_texture,

    # Menus

    animlistspecialsmenu.KB_MT_animlist_specials,

    # UI Lists

    animeventslist.KB_UL_anim_events,
    animslist.KB_UL_anims,
    lightflareslist.KB_UL_lightflares,
    pathpointslist.KB_UL_path_points
    )


def register():
    (_, kb_loaded) = addon_utils.check('neverblender')
    if kb_loaded:
        raise Exception("Do not enable both KotorBlender and NeverBlender at the same time!")

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.nvb = bpy.props.PointerProperty(type=kb_props.ObjectPropertyGroup)
    bpy.types.ImageTexture.nvb = bpy.props.PointerProperty(type=kb_props.TexturePropertyGroup)

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
