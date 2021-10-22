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

import addon_utils
import bpy

from .ops.addskingroup import KB_OT_add_skingroup
from .ops.anim.clone import KB_OT_anim_clone
from .ops.anim.crop import KB_OT_anim_crop
from .ops.anim.delete import KB_OT_anim_delete
from .ops.anim.event.delete import KB_OT_anim_event_delete
from .ops.anim.event.move import KB_OT_anim_event_move
from .ops.anim.event.new import KB_OT_anim_event_new
from .ops.anim.focus import KB_OT_anim_focus
from .ops.anim.move import KB_OT_anim_move
from .ops.anim.moveback import KB_OT_anim_moveback
from .ops.anim.new import KB_OT_anim_new
from .ops.anim.pad import KB_OT_anim_pad
from .ops.anim.scale import KB_OT_anim_scale
from .ops.lightflare.delete import KB_OT_delete_lightflare
from .ops.lightflare.move import KB_OT_move_lightflare
from .ops.lightflare.new import KB_OT_new_lightflare
from .ops.loadwokmaterials import KB_OT_load_wok_materials
from .ops.lyt.export import KB_OT_export_lyt
from .ops.lyt.importop import KB_OT_import_lyt
from .ops.mdl.ascii.export import KB_OT_export_ascii_mdl
from .ops.mdl.ascii.importop import KB_OT_import_ascii_mdl
from .ops.mdl.export import KB_OT_export_mdl
from .ops.mdl.importop import KB_OT_import_mdl
from .ops.path.addconnection import KB_OT_add_connection
from .ops.path.export import KB_OT_export_path
from .ops.path.importop import KB_OT_import_path
from .ops.path.removeconnection import KB_OT_remove_connection
from .ops.rebuildmaterialnodes import KB_OT_rebuild_material_nodes
from .ops.recreatearmature import KB_OT_recreate_armature
from .ops.smoothgroup.children import KB_OT_children_smoothgroup
from .ops.smoothgroup.generate import KB_OT_generate_smoothgroup
from .ops.smoothgroup.select import KB_OT_select_smoothgroup
from .ops.smoothgroup.toggle import KB_OT_toggle_smoothgroup
from .ops.txi.textureboxops import KB_OT_texture_box_ops
from .ops.txi.textureio import KB_OT_texture_io
from .ops.txi.textureops import KB_OT_texture_ops
from .props.anim import AnimPropertyGroup
from .props.animevent import AnimEventPropertyGroup
from .props.flare import FlarePropertyGroup
from .props.listitem import ListItemPropertyGroup
from .props.object import ObjectPropertyGroup
from .props.pathconnection import PathConnectionPropertyGroup
from .props.texture import TexturePropertyGroup
from .ui.list.animevents import KB_UL_anim_events
from .ui.list.anims import KB_UL_anims
from .ui.list.lightflares import KB_UL_lightflares
from .ui.list.pathpoints import KB_UL_path_points
from .ui.menu.animlistspecials import KB_MT_animlist_specials
from .ui.panel.animlist import KB_PT_animlist
from .ui.panel.emitter import KB_PT_emitter
from .ui.panel.empty import KB_PT_empty
from .ui.panel.light import KB_PT_light
from .ui.panel.mesh import KB_PT_mesh
from .ui.panel.pathpoint import KB_PT_path_point
from .ui.panel.smoothgroups import KB_PT_smoothgroups
from .ui.panel.texture import KB_PT_texture

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


def menu_func_import_mdl(self, context):
    self.layout.operator(KB_OT_import_mdl.bl_idname, text="KotOR Model (.mdl)")


def menu_func_import_ascii_mdl(self, context):
    self.layout.operator(KB_OT_import_ascii_mdl.bl_idname, text="KotOR Model (.mdl.ascii)")


def menu_func_import_lyt(self, context):
    self.layout.operator(KB_OT_import_lyt.bl_idname, text="KotOR Layout (.lyt)")


def menu_func_import_pth(self, context):
    self.layout.operator(KB_OT_import_path.bl_idname, text="KotOR Path (.pth)")


def menu_func_export_mdl(self, context):
    self.layout.operator(KB_OT_export_mdl.bl_idname, text="KotOR Model (.mdl)")


def menu_func_export_ascii_mdl(self, context):
    self.layout.operator(KB_OT_export_ascii_mdl.bl_idname, text="KotOR Model (.mdl.ascii)")


def menu_func_export_lyt(self, context):
    self.layout.operator(KB_OT_export_lyt.bl_idname, text="KotOR Layout (.lyt)")


def menu_func_export_pth(self, context):
    self.layout.operator(KB_OT_export_path.bl_idname, text="KotOR Path (.pth)")


classes = (
    # Property Groups

    PathConnectionPropertyGroup,
    ListItemPropertyGroup,
    AnimEventPropertyGroup,
    AnimPropertyGroup,
    FlarePropertyGroup,
    ObjectPropertyGroup,
    TexturePropertyGroup,

    # Operators

    KB_OT_add_connection,
    KB_OT_children_smoothgroup,
    KB_OT_anim_clone,
    KB_OT_anim_crop,
    KB_OT_anim_event_delete,
    KB_OT_anim_delete,
    KB_OT_delete_lightflare,
    KB_OT_export_ascii_mdl,
    KB_OT_export_lyt,
    KB_OT_export_mdl,
    KB_OT_export_path,
    KB_OT_anim_focus,
    KB_OT_generate_smoothgroup,
    KB_OT_import_ascii_mdl,
    KB_OT_import_lyt,
    KB_OT_import_mdl,
    KB_OT_import_path,
    KB_OT_add_skingroup,
    KB_OT_load_wok_materials,
    KB_OT_rebuild_material_nodes,
    KB_OT_recreate_armature,
    KB_OT_anim_event_move,
    KB_OT_anim_move,
    KB_OT_anim_moveback,
    KB_OT_move_lightflare,
    KB_OT_anim_event_new,
    KB_OT_anim_new,
    KB_OT_new_lightflare,
    KB_OT_anim_pad,
    KB_OT_remove_connection,
    KB_OT_anim_scale,
    KB_OT_select_smoothgroup,
    KB_OT_texture_box_ops,
    KB_OT_texture_io,
    KB_OT_texture_ops,
    KB_OT_toggle_smoothgroup,

    # Panels

    KB_PT_animlist,
    KB_PT_emitter,
    KB_PT_empty,
    KB_PT_light,
    KB_PT_mesh,
    KB_PT_path_point,
    KB_PT_smoothgroups,
    KB_PT_texture,

    # Menus

    KB_MT_animlist_specials,

    # UI Lists

    KB_UL_anim_events,
    KB_UL_anims,
    KB_UL_lightflares,
    KB_UL_path_points
    )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.kb = bpy.props.PointerProperty(type=ObjectPropertyGroup)
    bpy.types.ImageTexture.kb = bpy.props.PointerProperty(type=TexturePropertyGroup)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_mdl)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_ascii_mdl)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_lyt)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_pth)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_mdl)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_ascii_mdl)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_lyt)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_pth)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_pth)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_lyt)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_ascii_mdl)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_mdl)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_pth)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_lyt)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_mdl)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
