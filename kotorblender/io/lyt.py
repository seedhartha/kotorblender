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

from ..defines import Dummytype, NormalsAlgorithm

from .. import glob, utils

from . import mdl


def load_lyt(
    filepath="",
    import_animations=True,
    import_walkmeshes=True,
    build_materials=True,
    normals_algorithm=NormalsAlgorithm.CUSTOM,
    sharp_edge_angle=10.0,
    texture_search_recursive=False
):
    glob.import_animations = import_animations
    glob.import_walkmeshes = import_walkmeshes
    glob.build_materials = build_materials
    glob.build_armature = False
    glob.normals_algorithm = normals_algorithm
    glob.sharp_edge_angle = sharp_edge_angle
    glob.texture_path = os.path.dirname(filepath)
    glob.texture_search_recursive = texture_search_recursive

    # Read lines from LYT
    fp = os.fsencode(filepath)
    f = open(fp, "r")
    lines = [line.strip() for line in f.read().splitlines()]
    f.close()

    rooms = []
    rooms_to_read = 0

    for line in lines:
        tokens = line.split()
        if rooms_to_read > 0:
            room_name = tokens[0].lower()
            x = float(tokens[1])
            y = float(tokens[2])
            z = float(tokens[3])
            rooms.append((room_name, x, y, z))
            rooms_to_read -= 1
            if rooms_to_read == 0:
                break
        elif tokens[0].startswith("roomcount"):
            rooms_to_read = int(tokens[1])

    (path, _) = os.path.split(filepath)

    for room in rooms:
        mdl_path = os.path.join(path, room[0] + ".mdl")
        if not os.path.exists(mdl_path):
            print("KotorBlender: WARNING - room model not found: " + mdl_path)
        mdl.do_load_mdl(mdl_path, room[1:])


def save_lyt(filepath):
    def describe_object(obj):
        parent = utils.get_object_root(obj)
        orientation = obj.rotation_euler.to_quaternion()
        return "{} {} {:.7g} {:.7g} {:.7g} {:.7g} {:.7g} {:.7g} {:.7g}".format(parent.name if parent else "NULL", obj.name, *obj.matrix_world.translation, *orientation)

    with open(filepath, "w") as f:
        rooms = []
        doors = []
        others = []

        objects = bpy.context.selected_objects if len(bpy.context.selected_objects) > 0 else bpy.context.collection.objects
        for obj in objects:
            if obj.type == 'EMPTY':
                if obj.kb.dummytype == Dummytype.MDLROOT:
                    rooms.append(obj)
                elif obj.name.lower().startswith("door"):
                    doors.append(obj)
                elif obj.kb.dummytype not in [Dummytype.PTHROOT, Dummytype.PATHPOINT]:
                    others.append(obj)

        f.write("beginlayout\n")
        f.write("  roomcount {}\n".format(len(rooms)))
        for room in rooms:
            f.write("    {} {:.7g} {:.7g} {:.7g}\n".format(room.name, *room.location))
        f.write("  trackcount 0\n")
        f.write("  obstaclecount 0\n")
        f.write("  doorhookcount {}\n".format(len(doors)))
        for door in doors:
            f.write("    {}\n".format(describe_object(door)))
        f.write("  othercount {}\n".format(len(others)))
        for other in others:
            f.write("    {}\n".format(describe_object(other)))
        f.write("donelayout\n")
