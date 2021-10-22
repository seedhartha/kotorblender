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


class KB_OT_texture_box_ops(bpy.types.Operator):
    """ Hide/show Texture Info sub-groups"""
    bl_idname = "kb.texture_info_box_ops"
    bl_label = "Box Controls"
    bl_description = "Show/hide this property list"

    boxname : bpy.props.StringProperty(default="")

    def execute(self, context):
        if self.boxname == "":
            return {'FINISHED'}
        attrname = "box_visible_" + self.boxname
        texture = context.texture
        current_state = getattr(texture.kb, attrname)
        setattr(texture.kb, attrname, not current_state)
        return {'FINISHED'}