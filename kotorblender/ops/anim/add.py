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

from ... import utils

from ...scene.animation import Animation


class KB_OT_add_animation(bpy.types.Operator):
    bl_idname = "kb.add_animation"
    bl_label = "Add animation to the list"

    @classmethod
    def poll(cls, context):
        return utils.is_mdl_root(context.object)

    def execute(self, context):
        obj = context.object
        Animation.append_to_object(obj, "newanim", 0, 0.25, obj.name)

        return {'FINISHED'}
