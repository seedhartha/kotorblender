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

from ..scene import armature

from .. import utils


class KB_OT_recreate_armature(bpy.types.Operator):
    """Recreate an armature from bone nodes."""

    bl_idname = "kb.recreate_armature"
    bl_label = "Recreate Armature"

    def execute(self, context):
        obj = context.object
        if utils.is_root_dummy(obj):
            armature_object = armature.recreate_armature(obj)
            if armature_object:
                armature.create_armature_animations(obj, armature_object)

        return {'FINISHED'}
