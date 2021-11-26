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

import bpy

from .ops.anim.delete import KB_OT_delete_animation
from .ops.anim.event.add import KB_OT_add_anim_event
from .ops.anim.event.delete import KB_OT_delete_anim_event
from .ops.anim.event.move import KB_OT_move_anim_event
from .ops.anim.add import KB_OT_add_animation
from .ops.anim.move import KB_OT_move_animation
from .ops.anim.play import KB_OT_play_animation
from .ops.assignnodenumbers import KB_OT_assign_node_numbers
from .ops.lensflare.add import KB_OT_add_lens_flare
from .ops.lensflare.delete import KB_OT_delete_lens_flare
from .ops.lensflare.move import KB_OT_move_lens_flare
from .ops.loadwokmaterials import KB_OT_load_wok_materials
from .ops.lyt.export import KB_OT_export_lyt
from .ops.lyt.importop import KB_OT_import_lyt
from .ops.mdl.export import KB_OT_export_mdl
from .ops.mdl.importop import KB_OT_import_mdl
from .ops.pth.addconnection import KB_OT_add_path_connection
from .ops.pth.export import KB_OT_export_pth
from .ops.pth.importop import KB_OT_import_pth
from .ops.pth.removeconnection import KB_OT_delete_path_connection
from .ops.rebuildarmature import KB_OT_rebuild_armature
from .ops.rebuildmaterials import KB_OT_rebuild_materials
from .props.anim import AnimPropertyGroup
from .props.animevent import AnimEventPropertyGroup
from .props.lensflare import LensFlarePropertyGroup
from .props.object import ObjectPropertyGroup
from .props.pathconnection import PathConnectionPropertyGroup
from .ui.list.lensflares import KB_UL_lens_flares
from .ui.list.pathpoints import KB_UL_path_points
from .ui.panel.animations import KB_PT_animations, KB_PT_anim_events
from .ui.panel.modelnode.emitter import (
    KB_PT_emitter,
    KB_PT_emitter_particles,
    KB_PT_emitter_texture_anim,
    KB_PT_emitter_lighting,
    KB_PT_emitter_p2p,
    KB_PT_emitter_control_points
)
from .ui.panel.modelnode.light import KB_PT_light, KB_PT_light_lens_flares
from .ui.panel.modelnode.mesh import (
    KB_PT_mesh,
    KB_PT_mesh_uv_anim,
    KB_PT_mesh_dirt,
    KB_PT_mesh_dangly,
    KB_PT_mesh_aabb
)
from .ui.panel.modelnode.reference import KB_PT_reference
from .ui.panel.model import KB_PT_model
from .ui.panel.modelnode.modelnode import KB_PT_modelnode
from .ui.panel.pathpoint import KB_PT_path_point

bl_info = {
    "name": "KotorBlender",
    "author": "Attila Gyoerkoes & J.W. Brandon & Vsevolod Kremianskii",
    "version": (3, 4, 2),
    "blender": (2, 93, 0),
    "location": "File > Import-Export, Object Properties",
    "description": "Import, edit and export KotOR models",
    "category": "Import-Export"}


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


classes = (
    # Property Groups

    PathConnectionPropertyGroup,
    AnimEventPropertyGroup,
    AnimPropertyGroup,
    LensFlarePropertyGroup,
    ObjectPropertyGroup,

    # Operators

    KB_OT_assign_node_numbers,
    KB_OT_export_lyt,
    KB_OT_export_mdl,
    KB_OT_export_pth,
    KB_OT_import_lyt,
    KB_OT_import_mdl,
    KB_OT_import_pth,
    KB_OT_load_wok_materials,
    KB_OT_rebuild_armature,
    KB_OT_rebuild_materials,

    KB_OT_add_anim_event,
    KB_OT_move_anim_event,
    KB_OT_delete_anim_event,

    KB_OT_add_animation,
    KB_OT_move_animation,
    KB_OT_delete_animation,
    KB_OT_play_animation,

    KB_OT_add_lens_flare,
    KB_OT_move_lens_flare,
    KB_OT_delete_lens_flare,

    KB_OT_add_path_connection,
    KB_OT_delete_path_connection,

    # Panels

    KB_PT_model,

    KB_PT_animations,  # child of KB_PT_model
    KB_PT_anim_events,

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
    KB_UL_path_points
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.kb = bpy.props.PointerProperty(type=ObjectPropertyGroup)

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

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
