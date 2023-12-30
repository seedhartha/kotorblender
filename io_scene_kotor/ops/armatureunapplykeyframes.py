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

from ..constants import Classification
from ..scene import armature
from ..utils import is_mdl_root, is_skin_mesh, find_objects


class KB_OT_armature_unapply_keyframes(bpy.types.Operator):
    bl_idname = "kb.armature_unapply_keyframes"
    bl_label = "Unapply Object Keyframes"
    bl_description = "Recreate bone object keyframes from armature"

    @classmethod
    def poll(cls, context):
        return (
            is_mdl_root(context.object)
            and context.object.kb.classification == Classification.CHARACTER
            and find_objects(
                context.object,
                lambda obj: is_skin_mesh(obj)
                and any(mod.type == "ARMATURE" for mod in obj.modifiers),
            )
        )

    def execute(self, context):
        stack = [context.object]
        while stack:
            obj = stack.pop()
            if is_skin_mesh(obj):
                armature_mod = next(
                    iter(mod for mod in obj.modifiers if mod.type == "ARMATURE")
                )
                armature_obj = armature_mod.object
                if not armature_obj:
                    return {"CANCELLED"}
                armature.unapply_object_keyframes(context.object, armature_obj)
                break
            for child in obj.children:
                stack.insert(0, child)
        return {"FINISHED"}
