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

from bpy_extras.io_utils import ImportHelper

from ...io import pth


class KB_OT_import_pth(bpy.types.Operator, ImportHelper):
    bl_idname = "kb.pthimport"
    bl_label = "Import Odyssey PTH"

    filename_ext = ".pth"

    filter_glob: bpy.props.StringProperty(
        default="*.pth",
        options={'HIDDEN'})

    def execute(self, context):
        try:
            pth.load_pth(self.filepath)
        except Exception as e:
            self.report({'ERROR'}, str(e))

        return {'FINISHED'}
