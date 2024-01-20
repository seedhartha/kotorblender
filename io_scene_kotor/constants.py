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

PACKAGE_NAME = __package__

NULL = "NULL"

ANIM_REST_POSE_OFFSET = 5
ANIM_PADDING = 60
ANIM_FPS = 30

WALKMESH_MATERIALS = [
    ["wok_NotDefined", (0.400, 0.400, 0.400), False],
    ["wok_Dirt", (0.610, 0.235, 0.050), True],
    ["wok_Obscuring", (0.100, 0.100, 0.100), False],
    ["wok_Grass", (0.000, 0.600, 0.000), True],
    ["wok_Stone", (0.162, 0.216, 0.279), True],
    ["wok_Wood", (0.258, 0.059, 0.007), True],
    ["wok_Water", (0.000, 0.000, 1.000), True],
    ["wok_Nonwalk", (1.000, 0.000, 0.000), False],
    ["wok_Transparent", (1.000, 1.000, 1.000), False],
    ["wok_Carpet", (1.000, 0.000, 1.000), True],
    ["wok_Metal", (0.434, 0.552, 0.730), True],
    ["wok_Puddles", (0.509, 0.474, 0.147), True],
    ["wok_Swamp", (0.216, 0.216, 0.000), True],
    ["wok_Mud", (0.091, 0.147, 0.028), True],
    ["wok_Leaves", (1.000, 0.262, 0.000), True],
    ["wok_Lava", (0.300, 0.000, 0.000), False],
    ["wok_BottomlessPit", (0.000, 0.000, 0.000), True],
    ["wok_DeepWater", (0.000, 0.000, 0.216), False],
    ["wok_Door", (0.000, 0.000, 0.000), True],
    ["wok_Snow", (0.800, 0.800, 0.800), False],
    ["wok_Sand", (1.000, 1.000, 0.000), True],
    ["wok_BareBones", (0.500, 0.500, 0.100), True],
    ["wok_StoneBridge", (0.081, 0.108, 0.139), True],
]
NAME_TO_WALKMESH_MATERIAL = {mat[0]: mat for mat in WALKMESH_MATERIALS}
NON_WALKABLE = [mat_idx for mat_idx, mat in enumerate(WALKMESH_MATERIALS) if not mat[2]]

UV_MAP_MAIN = "UVMap"
UV_MAP_LIGHTMAP = "UVMap_lm"


class Classification:
    OTHER = "OTHER"
    TILE = "TILE"
    CHARACTER = "CHARACTER"
    DOOR = "DOOR"
    EFFECT = "EFFECT"
    GUI = "GUI"
    LIGHTSABER = "LIGHTSABER"
    PLACEABLE = "PLACEABLE"
    FLYER = "FLYER"


class RootType:
    MODEL = "MODEL"
    WALKMESH = "WALKMESH"


class NodeType:
    DUMMY = "DUMMY"
    REFERENCE = "REFERENCE"
    TRIMESH = "TRIMESH"
    DANGLYMESH = "DANGLYMESH"
    SKIN = "SKIN"
    EMITTER = "EMITTER"
    LIGHT = "LIGHT"
    AABB = "AABB"
    LIGHTSABER = "LIGHTSABER"


class DummyType:
    NONE = "NONE"
    MDLROOT = "MDLROOT"
    PWKROOT = "PWKROOT"
    DWKROOT = "DWKROOT"
    PTHROOT = "PTHROOT"
    REFERENCE = "REFERENCE"
    PATHPOINT = "PATHPOINT"
    USE1 = "USE1"
    USE2 = "USE2"


class MeshType:
    TRIMESH = "TRIMESH"
    DANGLYMESH = "DANGLYMESH"
    LIGHTSABER = "LIGHTSABER"
    SKIN = "SKIN"
    AABB = "AABB"
    EMITTER = "EMITTER"


class WalkmeshType:
    WOK = "WOK"
    PWK = "PWK"
    DWK = "DWK"


class ImportOptions:
    def __init__(self):
        self.import_geometry = True
        self.import_animations = True
        self.import_walkmeshes = True
        self.build_materials = True
        self.build_armature = False


class ExportOptions:
    def __init__(self):
        self.export_for_tsl = False
        self.export_for_xbox = False
        self.export_animations = True
        self.export_walkmeshes = True
        self.compress_quaternions = False
