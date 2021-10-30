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
import bpy_extras

from ... import defines, utils


class KB_OT_export_lyt(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export Odyssey Engine layout (.lyt)"""

    bl_idname = "kb.lytexport"
    bl_label  = "Export Odyssey LYT"

    filename_ext = ".lyt"

    filter_glob : bpy.props.StringProperty(
            default = "*.lyt",
            options = {'HIDDEN'})

    def describe_object(self, obj):
        parent = utils.get_mdl_root(obj)
        orientation = obj.rotation_euler.to_quaternion()
        return "{} {} {:.7g} {:.7g} {:.7g} {:.7g} {:.7g} {:.7g} {:.7g}".format(parent.name if parent else "NULL", obj.name, *obj.matrix_world.translation, *orientation)

    def execute(self, context):
        with open(self.filepath, "w") as f:
            rooms = []
            doors = []
            others = []

            objects = bpy.context.selected_objects if len(bpy.context.selected_objects) > 0 else bpy.context.collection.objects
            for obj in objects:
                if obj.type == 'EMPTY':
                    if obj.kb.dummytype == defines.Dummytype.MDLROOT:
                        rooms.append(obj)
                    elif obj.name.lower().startswith("door"):
                        doors.append(obj)
                    else:
                        others.append(obj)

            f.write("beginlayout\n")
            f.write("  roomcount {}\n".format(len(rooms)))
            for room in rooms:
                f.write("    {} {:.7g} {:.7g} {:.7g}\n".format(room.name, *room.location))
            f.write("  trackcount 0\n")
            f.write("  obstaclecount 0\n")
            f.write("  doorhookcount {}\n".format(len(doors)))
            for door in doors:
                f.write("    {}\n".format(self.describe_object(door)))
            f.write("  othercount {}\n".format(len(others)))
            for other in others:
                f.write("    {}\n".format(self.describe_object(other)))
            f.write("donelayout\n")

        return {'FINISHED'}
