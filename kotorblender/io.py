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
import re

import bpy

from mathutils import Vector

from .format.bwm.loader import BwmLoader
from .format.mdl.loader import MdlLoader
from .scene.modelnode.aabb import AabbNode
from .scene.roomwalkmesh import RoomWalkmesh

from . import glob, utils


def load_mdl(
    operator,
    context,
    filepath = ""
    ):
    glob.importGeometry = True
    glob.importWalkmesh = False
    glob.importMaterials = True
    glob.importAnim = True
    glob.texturePath = os.path.dirname(filepath)
    glob.textureSearch = True
    glob.createArmature = True

    do_load_mdl(filepath)

    return {'FINISHED'}


def load_lyt(
    operator,
    context,
    filepath = "",
    importGeometry = True,
    importWalkmesh = True,
    importMaterials = True,
    importAnim = True,
    textureSearch = False
    ):
    """
    Called from blender ui
    """
    glob.importGeometry = importGeometry
    glob.importWalkmesh = importWalkmesh
    glob.importMaterials = importMaterials
    glob.importAnim = importAnim
    glob.texturePath = os.path.dirname(filepath)
    glob.textureSearch = textureSearch

    do_load_lyt(filepath)

    return {'FINISHED'}


def do_load_mdl(filepath, position = (0.0, 0.0, 0.0)):
    mdl = MdlLoader(filepath)
    model = mdl.load()
    walkmesh = None

    wok_path = filepath[:-4] + ".wok"
    if os.path.exists(wok_path):
        bwm = BwmLoader(wok_path)
        walkmesh = bwm.load()

    pwk_path = filepath[:-4] + ".pwk"
    if os.path.exists(pwk_path):
        bwm = BwmLoader(pwk_path)
        bwm.load()

    dwk0_path = filepath[:-4] + "0.dwk"
    if os.path.exists(dwk0_path):
        bwm = BwmLoader(dwk0_path)
        bwm.load()

    dwk1_path = filepath[:-4] + "1.dwk"
    if os.path.exists(dwk1_path):
        bwm = BwmLoader(dwk1_path)
        bwm.load()

    dwk2_path = filepath[:-4] + "2.dwk"
    if os.path.exists(dwk2_path):
        bwm = BwmLoader(dwk2_path)
        bwm.load()

    model.import_to_collection(bpy.context.collection, None, position)

    if isinstance(walkmesh, RoomWalkmesh):
        aabb = next((node for node in model.nodeDict.values() if isinstance(node, AabbNode)), None)
        if aabb:
            aabb.roomlinks = compute_room_links(aabb, walkmesh)
            aabb.set_room_links(bpy.context.collection.objects[aabb.name].data)

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

def compute_room_links(aabb, walkmesh):
    lyt_position = Vector()
    first_wok_face = walkmesh.faces[0]
    for i in range(len(aabb.facelist.faces)):
        mdl_mat_id = aabb.facelist.matId[i]
        if mdl_mat_id == first_wok_face.material_id:
            first_mdl_vert = aabb.verts[aabb.facelist.faces[i][0]]
            first_mdl_vert_from_root = aabb.fromRoot @ Vector(first_mdl_vert)
            first_wok_vert = Vector(walkmesh.verts[first_wok_face.vert_indices[0]])
            lyt_position = first_wok_vert - first_mdl_vert_from_root
            break

    room_links = []

    for edge in walkmesh.outerEdges:
        if edge[1] == 0xffffffff:
            continue
        wok_face = walkmesh.faces[edge[0] // 3]
        wok_verts = [walkmesh.verts[idx] for idx in wok_face.vert_indices]
        for face_idx, mdl_vert_indices in enumerate(aabb.facelist.faces):
            mdl_verts = [aabb.verts[idx] for idx in mdl_vert_indices]
            mdl_verts_from_root = [aabb.fromRoot @ Vector(vert) for vert in mdl_verts]
            mdl_verts_lyt_space = [vert + lyt_position for vert in mdl_verts_from_root]
            if all([utils.isclose_3f(wok_verts[i], mdl_verts_lyt_space[i]) for i in range(3)]):
                room_links.append((3 * face_idx + (edge[0] % 3), edge[1]))
                break

    return room_links
