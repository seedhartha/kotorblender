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

from ..defines import Dummytype
from ..format.gff.loader import GffLoader
from ..format.gff.saver import GffSaver

from .. import utils


def load_pth(operator, filepath):

    def get_point_name(idx):
        return "PathPoint{0:0>3}".format(idx)

    basename = os.path.basename(filepath)
    pathname = "Path_" + os.path.splitext(basename)[0]
    if pathname in bpy.data.objects:
        path_object = bpy.data.objects[pathname]
    else:
        path_object = bpy.data.objects.new(pathname, None)
        path_object.kb.dummytype = Dummytype.PTHROOT
        bpy.context.collection.objects.link(path_object)

    loader = GffLoader(filepath, "PTH")
    tree = loader.load()
    points = []

    for i, point in enumerate(tree["Path_Points"]):
        name = get_point_name(i)
        object = bpy.data.objects.new(name, None)
        object.parent = path_object
        object.location = [point["X"], point["Y"], 0.0]
        object.kb.dummytype = Dummytype.PATHPOINT
        bpy.context.collection.objects.link(object)
        points.append((point, object))

    for point, object in points:
        start = point["First_Conection"]
        stop = start + point["Conections"]
        conections = tree["Path_Conections"][start:stop]
        for conection in conections:
            name = get_point_name(conection["Destination"])
            if name in bpy.data.objects:
                connection = object.kb.path_connections.add()
                connection.point = name


def save_pth(operator, filepath):
    point_objects = [obj for obj in bpy.data.objects if utils.is_path_point(obj)]

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

    saver = GffSaver(tree, filepath, "PTH")
    saver.save()
