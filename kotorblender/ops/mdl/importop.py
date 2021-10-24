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

import os

import bpy
import bpy_extras

from ...format.bwm.loader import BwmLoader
from ...format.mdl.loader import MdlLoader

from ... import glob


class KB_OT_import_mdl(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Odyssey Engine model (.mdl)"""

    bl_idname = "kb.mdlimport"
    bl_label = "Import Odyssey MDL"
    bl_options = {'UNDO'}

    filename_ext = ".mdl"

    filter_glob : bpy.props.StringProperty(
            default = "*.mdl",
            options = {'HIDDEN'})

    def execute(self, context):
        glob.texturePath = os.path.dirname(self.filepath)
        glob.textureSearch = True

        mdl = MdlLoader(self.filepath)
        model = mdl.load()

        wok_path = self.filepath[:-4] + ".wok"
        if os.path.exists(wok_path):
            bwm = BwmLoader(wok_path)
            bwm.load()

        pwk_path = self.filepath[:-4] + ".pwk"
        if os.path.exists(pwk_path):
            bwm = BwmLoader(pwk_path)
            bwm.load()

        dwk0_path = self.filepath[:-4] + "0.dwk"
        if os.path.exists(dwk0_path):
            bwm = BwmLoader(dwk0_path)
            bwm.load()

        dwk1_path = self.filepath[:-4] + "1.dwk"
        if os.path.exists(dwk1_path):
            bwm = BwmLoader(dwk1_path)
            bwm.load()

        dwk2_path = self.filepath[:-4] + "2.dwk"
        if os.path.exists(dwk2_path):
            bwm = BwmLoader(dwk2_path)
            bwm.load()

        model.add_to_collection()

        return {'FINISHED'}