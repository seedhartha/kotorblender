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

from ..defines import DummyType

from .. import utils

from . import mdl


def load_lyt(operator, filepath, options):
    operator.report({'INFO'}, "Loading area layout from '{}'".format(filepath))

    # Read lines
    fp = os.fsencode(filepath)
    f = open(fp, "r")
    lines = [line.strip() for line in f.read().splitlines()]
    f.close()

    # Parse room models
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

    # Load room models
    path, _ = os.path.split(filepath)
    for room in rooms:
        mdl_path = os.path.join(path, room[0] + ".mdl")
        if not os.path.exists(mdl_path):
            operator.report({'WARNING'}, "Room model '{}' not found".format(mdl_path))
            continue
        mdl.load_mdl(operator, mdl_path, options, room[1:])


def save_lyt(operator, filepath):

    def describe_object(obj):
        parent = utils.get_object_root(obj)
        orientation = obj.rotation_euler.to_quaternion()
        return "{} {} {:.7g} {:.7g} {:.7g} {:.7g} {:.7g} {:.7g} {:.7g}".format(parent.name if parent else "NULL", obj.name, *obj.matrix_world.translation, *orientation)

    operator.report({'INFO'}, "Saving area layout to '{}'".format(filepath))

    with open(filepath, "w") as f:
        rooms = []
        doors = []
        others = []

        objects = bpy.context.selected_objects if len(bpy.context.selected_objects) > 0 else bpy.context.collection.objects
        for obj in objects:
            if obj.type == 'EMPTY':
                if obj.kb.dummytype == DummyType.MDLROOT:
                    rooms.append(obj)
                elif obj.name.lower().startswith("door"):
                    doors.append(obj)
                elif obj.kb.dummytype not in [DummyType.PTHROOT, DummyType.PATHPOINT]:
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
