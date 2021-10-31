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
from kotorblender.scene.modelnode.trimesh import TrimeshNode

from .format.bwm.loader import BwmLoader
from .format.mdl.loader import MdlLoader
from .scene.modelnode.aabb import AabbNode

from . import glob


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

    return {'FINISHED'}


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

    return {'FINISHED'}


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
            wok_geom = wok_walkmesh.find_node(lambda n: isinstance(n, TrimeshNode))
            if aabb and wok_geom:
                aabb.compute_lyt_position(wok_geom)
                aabb.compute_room_links(wok_geom, wok_walkmesh.outer_edges)

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

    if wok_walkmesh:
        aabb = model.find_node(lambda n: isinstance(n, AabbNode))
        wok_geom = wok_walkmesh.find_node(lambda n: isinstance(n, TrimeshNode))
        if aabb and wok_geom:
            aabb.set_room_links(collection.objects[aabb.name].data)
    if pwk_walkmesh:
        pwk_walkmesh.import_to_collection(model_root, collection)
    if dwk_walkmesh1 and dwk_walkmesh2 and dwk_walkmesh3:
        dwk_walkmesh1.import_to_collection(model_root, collection)
        dwk_walkmesh2.import_to_collection(model_root, collection)
        dwk_walkmesh3.import_to_collection(model_root, collection)

    return {'FINISHED'}


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
