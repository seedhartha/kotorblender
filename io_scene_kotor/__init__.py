﻿# ##### BEGIN GPL LICENSE BLOCK #####
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

import bpy

from .addonprefs import KotorBlenderAddonPreferences
from .ops.anim.add import KB_OT_add_animation
from .ops.anim.delete import KB_OT_delete_animation
from .ops.anim.event.add import KB_OT_add_anim_event
from .ops.anim.event.delete import KB_OT_delete_anim_event
from .ops.anim.event.move import KB_OT_move_anim_event
from .ops.anim.move import KB_OT_move_animation
from .ops.anim.play import KB_OT_play_animation
from .ops.armatureapplykeyframes import KB_OT_armature_apply_keyframes
from .ops.armatureunapplykeyframes import KB_OT_armature_unapply_keyframes
from .ops.bakelightmaps import (
    KB_OT_bake_lightmaps_auto,
    KB_OT_bake_lightmaps_manual,
)
from .ops.lensflare.add import KB_OT_add_lens_flare
from .ops.lensflare.delete import KB_OT_delete_lens_flare
from .ops.lensflare.move import KB_OT_move_lens_flare
from .ops.lyt.export import KB_OT_export_lyt
from .ops.lyt.importop import KB_OT_import_lyt
from .ops.mdl.export import KB_OT_export_mdl
from .ops.mdl.importop import KB_OT_import_mdl
from .ops.pth.addconnection import KB_OT_add_path_connection
from .ops.pth.export import KB_OT_export_pth
from .ops.pth.importop import KB_OT_import_pth
from .ops.pth.removeconnection import KB_OT_delete_path_connection
from .ops.rebuildallmaterials import KB_OT_rebuild_all_materials
from .ops.rebuildarmature import KB_OT_rebuild_armature
from .ops.rebuildmaterial import KB_OT_rebuild_material
from .ops.renderminimap import KB_OT_render_minimap_auto, KB_OT_render_minimap_manual
from .ops.showhideobjects import (
    KB_OT_hide_untextured,
    KB_OT_hide_char_bones,
    KB_OT_hide_char_dummies,
    KB_OT_hide_emitters,
    KB_OT_hide_lights,
    KB_OT_hide_unlightmapped,
    KB_OT_hide_walkmeshes,
    KB_OT_show_untextured,
    KB_OT_show_char_bones,
    KB_OT_show_char_dummies,
    KB_OT_show_emitters,
    KB_OT_show_lights,
    KB_OT_show_unlightmapped,
    KB_OT_show_walkmeshes,
)
from .ui.list.lensflares import KB_UL_lens_flares
from .ui.list.pathpoints import KB_UL_path_points
from .ui.menu.kotor import (
    KB_MT_kotor,
    KB_MT_kotor_lightmaps,
    KB_MT_kotor_minimap,
    KB_MT_kotor_showhide,
)
from .ui.panel.animations import (
    KB_PT_animations,
    KB_PT_animations_events,
    KB_PT_animations_armature,
)
from .ui.panel.modelnode.emitter import (
    KB_PT_emitter,
    KB_PT_emitter_particles,
    KB_PT_emitter_texture_anim,
    KB_PT_emitter_lighting,
    KB_PT_emitter_p2p,
    KB_PT_emitter_control_points,
)
from .ui.panel.modelnode.light import KB_PT_light, KB_PT_light_lens_flares
from .ui.panel.modelnode.mesh import (
    KB_PT_mesh,
    KB_PT_mesh_uv_anim,
    KB_PT_mesh_dirt,
    KB_PT_mesh_dangly,
    KB_PT_mesh_aabb,
)
from .ui.panel.model import KB_PT_model
from .ui.panel.modelnode.modelnode import KB_PT_modelnode
from .ui.panel.modelnode.reference import KB_PT_reference
from .ui.panel.pathpoint import KB_PT_path_point
from .ui.props.anim import AnimPropertyGroup
from .ui.props.animevent import AnimEventPropertyGroup
from .ui.props.image import ImagePropertyGroup
from .ui.props.lensflare import LensFlarePropertyGroup
from .ui.props.object import ObjectPropertyGroup
from .ui.props.pathconnection import PathConnectionPropertyGroup
from .ui.props.scene import ScenePropertyGroup

bl_info = {
    "name": "KotorBlender",
    "author": "seedhartha",
    "version": (4, 0, 3),
    "blender": (3, 6),
    "location": "File > Import-Export, Object Properties",
    "description": "Import, edit and export KotOR models",
    "category": "Import-Export",
}


def menu_func_import_mdl(self, context):
    self.layout.operator(KB_OT_import_mdl.bl_idname, text="KotOR Model (.mdl)")


def menu_func_import_lyt(self, context):
    self.layout.operator(KB_OT_import_lyt.bl_idname, text="KotOR Layout (.lyt)")


def menu_func_import_pth(self, context):
    self.layout.operator(KB_OT_import_pth.bl_idname, text="KotOR Path (.pth)")


def menu_func_export_mdl(self, context):
    self.layout.operator(KB_OT_export_mdl.bl_idname, text="KotOR Model (.mdl)")


def menu_func_export_lyt(self, context):
    self.layout.operator(KB_OT_export_lyt.bl_idname, text="KotOR Layout (.lyt)")


def menu_func_export_pth(self, context):
    self.layout.operator(KB_OT_export_pth.bl_idname, text="KotOR Path (.pth)")


def menu_func_kotor(self, context):
    self.layout.menu("KB_MT_kotor")


classes = (
    KotorBlenderAddonPreferences,
    # Property Groups
    PathConnectionPropertyGroup,
    AnimEventPropertyGroup,
    AnimPropertyGroup,
    LensFlarePropertyGroup,
    ObjectPropertyGroup,
    ScenePropertyGroup,
    ImagePropertyGroup,
    # Operators
    KB_OT_add_anim_event,
    KB_OT_add_animation,
    KB_OT_add_lens_flare,
    KB_OT_add_path_connection,
    KB_OT_armature_apply_keyframes,
    KB_OT_armature_unapply_keyframes,
    KB_OT_bake_lightmaps_auto,
    KB_OT_bake_lightmaps_manual,
    KB_OT_delete_anim_event,
    KB_OT_delete_animation,
    KB_OT_delete_lens_flare,
    KB_OT_delete_path_connection,
    KB_OT_export_lyt,
    KB_OT_export_mdl,
    KB_OT_export_pth,
    KB_OT_hide_untextured,
    KB_OT_hide_char_bones,
    KB_OT_hide_char_dummies,
    KB_OT_hide_emitters,
    KB_OT_hide_lights,
    KB_OT_hide_unlightmapped,
    KB_OT_hide_walkmeshes,
    KB_OT_import_lyt,
    KB_OT_import_mdl,
    KB_OT_import_pth,
    KB_OT_move_anim_event,
    KB_OT_move_animation,
    KB_OT_move_lens_flare,
    KB_OT_play_animation,
    KB_OT_rebuild_all_materials,
    KB_OT_rebuild_armature,
    KB_OT_rebuild_material,
    KB_OT_render_minimap_auto,
    KB_OT_render_minimap_manual,
    KB_OT_show_untextured,
    KB_OT_show_char_bones,
    KB_OT_show_char_dummies,
    KB_OT_show_emitters,
    KB_OT_show_lights,
    KB_OT_show_unlightmapped,
    KB_OT_show_walkmeshes,
    # Panels
    KB_PT_model,
    KB_PT_animations,
    KB_PT_animations_events,
    KB_PT_animations_armature,
    KB_PT_modelnode,
    KB_PT_reference,  # child of KB_PT_modelnode
    KB_PT_path_point,  # child of KB_PT_modelnode
    KB_PT_mesh,  # child of KB_PT_modelnode
    KB_PT_mesh_uv_anim,
    KB_PT_mesh_dirt,
    KB_PT_mesh_dangly,
    KB_PT_mesh_aabb,
    KB_PT_light,  # child of KB_PT_modelnode
    KB_PT_light_lens_flares,
    KB_PT_emitter,  # child of KB_PT_modelnode
    KB_PT_emitter_particles,
    KB_PT_emitter_texture_anim,
    KB_PT_emitter_lighting,
    KB_PT_emitter_p2p,
    KB_PT_emitter_control_points,
    # UI Lists
    KB_UL_lens_flares,
    KB_UL_path_points,
    # Menus
    KB_MT_kotor,
    KB_MT_kotor_lightmaps,
    KB_MT_kotor_minimap,
    KB_MT_kotor_showhide,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.kb = bpy.props.PointerProperty(type=ObjectPropertyGroup)
    bpy.types.Scene.kb = bpy.props.PointerProperty(type=ScenePropertyGroup)
    bpy.types.Image.kb = bpy.props.PointerProperty(type=ImagePropertyGroup)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_mdl)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_lyt)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_pth)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_mdl)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_lyt)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_pth)

    bpy.types.TOPBAR_MT_editor_menus.append(menu_func_kotor)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_pth)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_lyt)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_mdl)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_pth)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_lyt)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_mdl)

    bpy.types.TOPBAR_MT_editor_menus.remove(menu_func_kotor)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
