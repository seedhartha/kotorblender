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

from os import path
import bpy
import bpy_extras

from ...expando import Expando
from ...format.gff.saver import GffSaver

from ...utils import is_path_point


class KB_OT_export_path(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export Odyssey Engine path (.pth)"""

    bl_idname = "kb.pthexport"
    bl_label  = "Export Odyssey PTH"

    filename_ext = ".pth"

    filter_glob : bpy.props.StringProperty(
            default = "*.pth",
            options = {'HIDDEN'})

    def execute(self, context):
        point_objects = [obj for obj in bpy.data.objects if is_path_point(obj)]

        point_idx_by_name = dict()
        for idx, obj in enumerate(point_objects):
            point_idx_by_name[obj.name] = idx

        points = []
        conections = []
        for obj in point_objects:
            first_conection = len(conections)
            for object_connection in obj.kb.path_connections:
                conection = dict()
                conection["_type"] = 3
                conection["_fields"] = {
                    "Destination": 4
                    }
                conection["Destination"] = point_idx_by_name[object_connection.point]
                conections.append(conection)

            point = dict()
            point["_type"] = 2
            point["_fields"] = {
                "Conections": 4,
                "First_Conection": 4,
                "X": 8,
                "Y": 8
                }
            point["Conections"] = len(obj.kb.path_connections)
            point["First_Conection"] = first_conection
            point["X"] = obj.location[0]
            point["Y"] = obj.location[1]
            points.append(point)

        tree = dict()
        tree["_type"] = 0xFFFFFFFF
        tree["_fields"] = {
            "Path_Points": 15,
            "Path_Conections": 15
            }
        tree["Path_Points"] = points
        tree["Path_Conections"] = conections

        saver = GffSaver(tree, self.filepath, "PTH")
        saver.save()

        return {'FINISHED'}