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

from .format.bwm.loader import BwmLoader
from .format.bwm.saver import BwmSaver
from .format.gff.loader import GffLoader
from .format.gff.saver import GffSaver
from .format.mdl.loader import MdlLoader
from .format.mdl.saver import MdlSaver
from .scene.model import Model
from .scene.modelnode.aabb import AabbNode
from .scene.walkmesh import Walkmesh

from .defines import Dummytype

from . import defines, glob, utils


def load_mdl(
    filepath="",
    import_animations=True,
    import_walkmeshes=True,
    import_materials=True,
    import_armatures=True,
    texture_search_recursive=False
):
    glob.import_animations = import_animations
    glob.import_walkmeshes = import_walkmeshes
    glob.import_materials = import_materials
    glob.import_armatures = import_armatures
    glob.texture_path = os.path.dirname(filepath)
    glob.texture_search_recursive = texture_search_recursive

    do_load_mdl(filepath)


def load_lyt(
    filepath="",
    import_animations=True,
    import_walkmeshes=True,
    import_materials=True,
    texture_search_recursive=False
):
    glob.import_animations = import_animations
    glob.import_walkmeshes = import_walkmeshes
    glob.import_materials = import_materials
    glob.import_armatures = False
    glob.texture_path = os.path.dirname(filepath)
    glob.texture_search_recursive = texture_search_recursive

    do_load_lyt(filepath)


def load_pth(
    filepath=""
):
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


def save_mdl(filepath, export_for_tsl=False):
    # Reset Pose
    bpy.context.scene.frame_set(defines.ANIM_GLOBSTART)

    mdl_root = next(iter(obj for obj in bpy.context.selected_objects if utils.is_mdl_root(obj)), None)
    if not mdl_root:
        mdl_root = next(iter(obj for obj in bpy.context.collection.objects if utils.is_mdl_root(obj)), None)
    if not mdl_root:
        return

    # Export MDL
    model = Model.from_mdl_root(mdl_root)
    mdl = MdlSaver(filepath, model, export_for_tsl)
    mdl.save()

    # Export WOK
    aabb_node = model.find_node(lambda node: isinstance(node, AabbNode))
    if aabb_node:
        base_path, _ = os.path.splitext(filepath)
        wok_path = base_path + ".wok"
        walkmesh = Walkmesh.from_aabb_node(aabb_node)
        bwm = BwmSaver(wok_path, walkmesh)
        bwm.save()

    # Export PWK, DWK
    xwk_roots = utils.get_children_recursive(mdl_root, lambda obj: utils.is_pwk_root(obj) or utils.is_dwk_root(obj))
    for xwk_root in xwk_roots:
        base_path, _ = os.path.splitext(filepath)
        if utils.is_pwk_root(xwk_root):
            xwk_path = base_path + ".pwk"
        else:
            if xwk_root.name.endswith("open1"):
                dwk_state = 0
            elif xwk_root.name.endswith("open2"):
                dwk_state = 1
            elif xwk_root.name.endswith("closed"):
                dwk_state = 2
            xwk_path = "{}{}.dwk".format(base_path, dwk_state)
        walkmesh = Walkmesh.from_root_object(xwk_root)
        bwm = BwmSaver(xwk_path, walkmesh)
        bwm.save()


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


def save_pth(filepath):
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


def do_load_mdl(filepath, position=(0.0, 0.0, 0.0)):
    collection = bpy.context.collection

    mdl = MdlLoader(filepath)
    model = mdl.load()

    wok_walkmesh = None
    pwk_walkmesh = None
    dwk_walkmesh1 = None
    dwk_walkmesh2 = None
    dwk_walkmesh3 = None

    if glob.import_walkmeshes:
        wok_path = filepath[:-4] + ".wok"
        if os.path.exists(wok_path):
            wok = BwmLoader(wok_path, model.name)
            wok_walkmesh = wok.load()
            aabb = model.find_node(lambda n: isinstance(n, AabbNode))
            aabb_wok = wok_walkmesh.find_node(lambda n: isinstance(n, AabbNode))
            if aabb and aabb_wok:
                aabb.compute_lyt_position(aabb_wok)
                aabb.compute_room_links(aabb_wok, wok_walkmesh.outer_edges)

        pwk_path = filepath[:-4] + ".pwk"
        if os.path.exists(pwk_path):
            pwk = BwmLoader(pwk_path, model.name)
            pwk_walkmesh = pwk.load()

        dwk0_path = filepath[:-4] + "0.dwk"
        dwk1_path = filepath[:-4] + "1.dwk"
        dwk2_path = filepath[:-4] + "2.dwk"
        if os.path.exists(dwk0_path) and os.path.exists(dwk1_path) and os.path.exists(dwk2_path):
            dwk1 = BwmLoader(dwk0_path, model.name)
            dwk2 = BwmLoader(dwk1_path, model.name)
            dwk3 = BwmLoader(dwk2_path, model.name)
            dwk_walkmesh1 = dwk1.load()
            dwk_walkmesh2 = dwk2.load()
            dwk_walkmesh3 = dwk3.load()

    model_root = model.import_to_collection(collection, position)

    if pwk_walkmesh:
        pwk_walkmesh.import_to_collection(model_root, collection)
    if dwk_walkmesh1 and dwk_walkmesh2 and dwk_walkmesh3:
        dwk_walkmesh1.import_to_collection(model_root, collection)
        dwk_walkmesh2.import_to_collection(model_root, collection)
        dwk_walkmesh3.import_to_collection(model_root, collection)

    # reset pose
    bpy.context.scene.frame_set(defines.ANIM_GLOBSTART)


def do_load_lyt(filepath):
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
        do_load_mdl(mdl_path, room[1:])
