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


class KB_OT_texture_ops(bpy.types.Operator):
    bl_idname = "kb.texture_info_ops"
    bl_label = "Texture Info Operations"
    bl_property = "action"
    bl_options = {'UNDO'}

    action : bpy.props.EnumProperty(items=(
        ("RESET", "Reset", "Reset the property to default value. This will prevent it from being written to TXI file output."),
        ("NYI", "Other", "")
    ))
    propname : bpy.props.StringProperty(default="")

    def execute(self, context):
        if self.propname == "":
            return {'FINISHED'}
        if self.action == "RESET":
            attr_def = getattr(bpy.types.ImageTexture.kb[1]["type"], self.propname)[1]
            if "default" in attr_def:
                setattr(context.texture.kb, self.propname, attr_def["default"])
        return {'FINISHED'}