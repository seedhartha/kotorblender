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

from ..constants import MeshType, DummyType
from ..utils import (
    is_null,
    is_dwk_root,
    is_pwk_root,
    is_dummy_type,
    is_char_dummy,
    is_char_bone,
    is_mesh_type,
    is_skin_mesh,
)


class KB_OT_hide_walkmeshes(bpy.types.Operator):
    bl_idname = "kb.hide_walkmeshes"
    bl_label = "Hide Walkmeshes"
    bl_description = "Hides all walkmeshes in the scene"

    def execute(self, context):
        # Deselect everything in the scene first.
        bpy.ops.object.select_all(action="DESELECT")

        # Loop through every object in the scene and hide it if it's a walkmesh.
        for obj in bpy.context.scene.objects:
            if is_mesh_type(obj, MeshType.AABB) or is_dwk_root(obj) or is_pwk_root(obj):
                obj.hide_set(True)

        return {"FINISHED"}


class KB_OT_hide_lights(bpy.types.Operator):
    bl_idname = "kb.hide_lights"
    bl_label = "Hide Lights"
    bl_description = "Hides all lights in the scene"

    def execute(self, context):
        # Deselect everything in the scene first.
        bpy.ops.object.select_all(action="DESELECT")

        # Loop through every object in the scene and hide it if it's a light.
        for obj in bpy.context.scene.objects:
            if obj.type == "LIGHT":
                obj.hide_set(True)

        return {"FINISHED"}


class KB_OT_hide_emitters(bpy.types.Operator):
    bl_idname = "kb.hide_emitters"
    bl_label = "Hide Emitters"
    bl_description = "Hides all emitters in the scene"

    def execute(self, context):
        # Deselect everything in the scene first.
        bpy.ops.object.select_all(action="DESELECT")

        # Loop through every object in the scene and hide it if it's an emitter.
        for obj in bpy.context.scene.objects:
            if is_mesh_type(obj, MeshType.EMITTER):
                obj.hide_set(True)

        return {"FINISHED"}


class KB_OT_hide_blockers(bpy.types.Operator):
    bl_idname = "kb.hide_blockers"
    bl_label = "Hide Blockers"
    bl_description = "Hides all untextured blocker trimeshes in the scene"

    def execute(self, context):
        # Deselect everything in the scene first.
        bpy.ops.object.select_all(action="DESELECT")

        # Loop through every object in the scene and hide it if it's an untextured trimesh.
        for obj in bpy.context.scene.objects:
            if (
                is_mesh_type(obj, MeshType.TRIMESH)
                and not is_skin_mesh(obj)
                and obj.kb.render == 1
            ):
                if is_null(obj.kb.bitmap) and is_null(obj.kb.bitmap2):
                    obj.hide_set(True)

        return {"FINISHED"}


class KB_OT_hide_charbones(bpy.types.Operator):
    bl_idname = "kb.hide_charbones"
    bl_label = "Hide Character Bones"
    bl_description = "Hides all humanoid rig bones in the scene"

    def execute(self, context):
        # Deselect everything in the scene first.
        bpy.ops.object.select_all(action="DESELECT")

        # Loop through every object in the scene and hide it if it's a bone matching the name of those in a character rig.
        for obj in bpy.context.scene.objects:
            if is_char_bone(obj):
                obj.hide_set(True)

        return {"FINISHED"}


class KB_OT_hide_charnulls(bpy.types.Operator):
    bl_idname = "kb.hide_charnulls"
    bl_label = "Hide Character Dummies"
    bl_description = "Hides all humanoid rig dummy/null objects in the scene"

    def execute(self, context):
        # Deselect everything in the scene first.
        bpy.ops.object.select_all(action="DESELECT")

        # Loop through every object in the scene and hide it if it's a dummy/null matching the name of those in a character rig.
        for obj in bpy.context.scene.objects:
            if is_char_dummy(obj):
                obj.hide_set(True)

        return {"FINISHED"}


class KB_OT_unhide_walkmeshes(bpy.types.Operator):
    bl_idname = "kb.unhide_walkmeshes"
    bl_label = "Unhide Walkmeshes"
    bl_description = "Unhides all walkmeshes in the scene"

    def execute(self, context):
        # Deselect everything in the scene first.
        bpy.ops.object.select_all(action="DESELECT")

        # Loop through every object in the scene and unhide it if it's a walkmesh.
        for obj in bpy.context.scene.objects:
            if is_mesh_type(obj, MeshType.AABB) or is_dwk_root(obj) or is_pwk_root(obj):
                obj.hide_set(False)

        return {"FINISHED"}


class KB_OT_unhide_lights(bpy.types.Operator):
    bl_idname = "kb.unhide_lights"
    bl_label = "Unhide Lights"
    bl_description = "Unhides all lights in the scene"

    def execute(self, context):
        # Deselect everything in the scene first.
        bpy.ops.object.select_all(action="DESELECT")

        # Loop through every object in the scene and unhide it if it's a light.
        for obj in bpy.context.scene.objects:
            if obj.type == "LIGHT":
                obj.hide_set(False)

        return {"FINISHED"}


class KB_OT_unhide_emitters(bpy.types.Operator):
    bl_idname = "kb.unhide_emitters"
    bl_label = "Unhide Emitters"
    bl_description = "Unhides all emitters in the scene"

    def execute(self, context):
        # Deselect everything in the scene first.
        bpy.ops.object.select_all(action="DESELECT")

        # Loop through every object in the scene and unhide it if it's an emitter.
        for obj in bpy.context.scene.objects:
            if is_mesh_type(obj, MeshType.EMITTER):
                obj.hide_set(False)

        return {"FINISHED"}


class KB_OT_unhide_blockers(bpy.types.Operator):
    bl_idname = "kb.unhide_blockers"
    bl_label = "Unhide Blockers"
    bl_description = "Unhides all untextured blocker trimeshes in the scene"

    def execute(self, context):
        # Deselect everything in the scene first.
        bpy.ops.object.select_all(action="DESELECT")

        # Loop through every object in the scene and unhide it if it's an untextured trimesh.
        for obj in bpy.context.scene.objects:
            if (
                is_mesh_type(obj, MeshType.TRIMESH)
                and not is_skin_mesh(obj)
                and obj.kb.render == 1
            ):
                if is_null(obj.kb.bitmap) and is_null(obj.kb.bitmap2):
                    obj.hide_set(False)

        return {"FINISHED"}


class KB_OT_unhide_charbones(bpy.types.Operator):
    bl_idname = "kb.unhide_charbones"
    bl_label = "Unhide Character Bones"
    bl_description = "Unhides all humanoid rig bones in the scene"

    def execute(self, context):
        # Deselect everything in the scene first.
        bpy.ops.object.select_all(action="DESELECT")

        # Loop through every object in the scene and unhide it if it's a bone matching the name of those in a character rig.
        for obj in bpy.context.scene.objects:
            if is_char_bone(obj):
                obj.hide_set(False)

        return {"FINISHED"}


class KB_OT_unhide_charnulls(bpy.types.Operator):
    bl_idname = "kb.unhide_charnulls"
    bl_label = "Unhide Character Dummies"
    bl_description = "Unhides all humanoid rig dummy/null objects in the scene"

    def execute(self, context):
        # Deselect everything in the scene first.
        bpy.ops.object.select_all(action="DESELECT")

        # Loop through every object in the scene and unhide it if it's a dummy/null matching the name of those in a character rig.
        for obj in bpy.context.scene.objects:
            if is_char_dummy(obj):
                obj.hide_set(False)

        return {"FINISHED"}
