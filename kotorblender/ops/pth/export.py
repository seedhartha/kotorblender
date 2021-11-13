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

import traceback

import bpy

from bpy_extras.io_utils import ExportHelper

from ...io import pth


class KB_OT_export_pth(bpy.types.Operator, ExportHelper):
    bl_idname = "kb.pthexport"
    bl_label = "Export Odyssey PTH"

    filename_ext = ".pth"

    filter_glob: bpy.props.StringProperty(
        default="*.pth",
        options={'HIDDEN'})

    def execute(self, context):
        try:
            pth.save_pth(self, self.filepath)
        except Exception as e:
            print(traceback.format_exc())
            self.report({'ERROR'}, str(e))

        return {'FINISHED'}
