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

from kotorblender.ops import addskingroup


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
    reload(addpathconnectionop)
    reload(addskingroupop)
    reload(animeventprops)
    reload(animeventslist)
    reload(animlistpanel)
    reload(animlistspecialsmenu)
    reload(animprops)
    reload(animslist)
    reload(binreader)
    reload(binwriter)
    reload(childrensmoothgroupop)
    reload(cloneanimop)
    reload(cropanimop)
    reload(deleteanimeventop)
    reload(deleteanimop)
    reload(deletelightflareop)
    reload(emitterpanel)
    reload(emptypanel)
    reload(exportlytop)
    reload(exportmdlop)
    reload(exportpathop)
    reload(flareprops)
    reload(focusanimop)
    reload(generatesmoothgroupop)
    reload(gffloader)
    reload(gffsaver)
    reload(importlytop)
    reload(importmdlop)
    reload(importpathop)
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
    reload(kb_teximage)
    reload(kb_txi)
    reload(kb_utils)
    reload(lightflareslist)
    reload(lightpanel)
    reload(listitemprops)
    reload(loadwokmaterialsop)
    reload(mdlloader)
    reload(mdlsaver)
    reload(meshpanel)
    reload(moveanimeventop)
    reload(moveanimop)
    reload(movebackanimop)
    reload(movelightflareop)
    reload(newanimeventop)
    reload(newanimop)
    reload(newlightflareop)
    reload(objectprops)
    reload(padanimop)
    reload(pathconnectionprops)
    reload(pathpointpanel)
    reload(pathpointslist)
    reload(rebuildmaterialnodesop)
    reload(recreatearmatureop)
    reload(removepathconnection)
    reload(renderminimapop)
    reload(scaleanimop)
    reload(selectsmoothgroupop)
    reload(smoothgroupspanel)
    reload(textureboxtxiop)
    reload(textureiotxiop)
    reload(textureopstxiop)
    reload(texturepanel)
    reload(textureprops)
    reload(togglesmoothgroupop)
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
        addskingroup as addskingroupop,
        loadwokmaterials as loadwokmaterialsop,
        rebuildmaterialnodes as rebuildmaterialnodesop,
        recreatearmature as recreatearmatureop,
        renderminimap as renderminimapop)
    from .ops.anim import (
        clone as cloneanimop,
        crop as cropanimop,
        delete as deleteanimop,
        focus as focusanimop,
        move as moveanimop,
        moveback as movebackanimop,
        new as newanimop,
        pad as padanimop,
        scale as scaleanimop)
    from .ops.anim.event import (
        delete as deleteanimeventop,
        move as moveanimeventop,
        new as newanimeventop)
    from .ops.lightflare import (
        delete as deletelightflareop,
        move as movelightflareop,
        new as newlightflareop)
    from .ops.lyt import (
        export as exportlytop,
        importop as importlytop)
    from .ops.mdl import (
        export as exportmdlop,
        importop as importmdlop)
    from .ops.path import (
        addconnection as addpathconnectionop,
        export as exportpathop,
        importop as importpathop,
        removeconnection as removepathconnection)
    from .ops.smoothgroup import (
        children as childrensmoothgroupop,
        generate as generatesmoothgroupop,
        select as selectsmoothgroupop,
        toggle as togglesmoothgroupop)
    from .ops.txi import (
        textureboxops as textureboxtxiop,
        textureio as textureiotxiop,
        textureops as textureopstxiop)
    from .props import (
        anim as animprops,
        animevent as animeventprops,
        flare as flareprops,
        listitem as listitemprops,
        object as objectprops,
        pathconnection as pathconnectionprops,
        texture as textureprops)
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
    self.layout.operator(importmdlop.KB_OT_import_mdl.bl_idname, text="KotOR Model (.mdl)")


def menu_func_import_lyt(self, context):
    self.layout.operator(importlytop.KB_OT_import_lyt.bl_idname, text="KotOR Layout (.lyt)")


def menu_func_import_pth(self, context):
    self.layout.operator(importpathop.KB_OT_import_path.bl_idname, text="KotOR Path (.pth.ascii)")


def menu_func_export_mdl(self, context):
    self.layout.operator(exportmdlop.KB_OT_export_mdl.bl_idname, text="KotOR Model (.mdl)")


def menu_func_export_lyt(self, context):
    self.layout.operator(exportlytop.KB_OT_export_lyt.bl_idname, text="KotOR Layout (.lyt)")


def menu_func_export_pth(self, context):
    self.layout.operator(exportpathop.KB_OT_export_path.bl_idname, text="KotOR Path (.pth.ascii)")


classes = (
    # Property Groups

    pathconnectionprops.PathConnectionPropertyGroup,
    listitemprops.ListItemPropertyGroup,
    animeventprops.AnimEventPropertyGroup,
    animprops.AnimPropertyGroup,
    flareprops.FlarePropertyGroup,
    objectprops.ObjectPropertyGroup,
    textureprops.TexturePropertyGroup,

    # Operators

    addpathconnectionop.KB_OT_add_connection,
    childrensmoothgroupop.KB_OT_children_smoothgroup,
    cloneanimop.KB_OT_anim_clone,
    cropanimop.KB_OT_anim_crop,
    deleteanimeventop.KB_OT_anim_event_delete,
    deleteanimop.KB_OT_anim_delete,
    deletelightflareop.KB_OT_delete_lightflare,
    exportlytop.KB_OT_export_lyt,
    exportmdlop.KB_OT_export_mdl,
    exportpathop.KB_OT_export_path,
    focusanimop.KB_OT_anim_focus,
    generatesmoothgroupop.KB_OT_generate_smoothgroup,
    importlytop.KB_OT_import_lyt,
    importmdlop.KB_OT_import_mdl,
    importpathop.KB_OT_import_path,
    addskingroupop.KB_OT_add_skingroup,
    loadwokmaterialsop.KB_OT_load_wok_materials,
    rebuildmaterialnodesop.KB_OT_rebuild_material_nodes,
    recreatearmatureop.KB_OT_recreate_armature,
    renderminimapop.KB_OT_render_minimap,
    moveanimeventop.KB_OT_anim_event_move,
    moveanimop.KB_OT_anim_move,
    movebackanimop.KB_OT_anim_moveback,
    movelightflareop.KB_OT_move_lightflare,
    newanimeventop.KB_OT_anim_event_new,
    newanimop.KB_OT_anim_new,
    newlightflareop.KB_OT_new_lightflare,
    padanimop.KB_OT_anim_pad,
    removepathconnection.KB_OT_remove_connection,
    scaleanimop.KB_OT_anim_scale,
    selectsmoothgroupop.KB_OT_select_smoothgroup,
    textureboxtxiop.KB_OT_texture_box_ops,
    textureiotxiop.KB_OT_texture_io,
    textureopstxiop.KB_OT_texture_ops,
    togglesmoothgroupop.KB_OT_toggle_smoothgroup,

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

    bpy.types.Object.nvb = bpy.props.PointerProperty(type=objectprops.ObjectPropertyGroup)
    bpy.types.ImageTexture.nvb = bpy.props.PointerProperty(type=textureprops.TexturePropertyGroup)

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
