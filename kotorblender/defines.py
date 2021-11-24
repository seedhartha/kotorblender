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

from math import radians

NULL = "NULL"

# Number of frames to the left of animation, where to create a rest pose
ANIM_REST_POSE_OFFSET = 5

# Number of frames between two consecutive animations
ANIM_PADDING = 60

FPS = 30

WOK_MATERIALS = [["wok_NotDefined", (0.400, 0.400, 0.400), 0.0],
                 ["wok_Dirt", (0.610, 0.235, 0.050), 0.0],
                 ["wok_Obscuring", (0.100, 0.100, 0.100), 0.5],
                 ["wok_Grass", (0.000, 0.600, 0.000), 0.0],
                 ["wok_Stone", (0.162, 0.216, 0.279), 0.0],
                 ["wok_Wood", (0.258, 0.059, 0.007), 0.0],
                 ["wok_Water", (0.000, 0.000, 1.000), 0.0],
                 ["wok_Nonwalk", (1.000, 0.000, 0.000), 0.0],
                 ["wok_Transparent", (1.000, 1.000, 1.000), 1.0],
                 ["wok_Carpet", (1.000, 0.000, 1.000), 0.0],
                 ["wok_Metal", (0.434, 0.552, 0.730), 1.0],
                 ["wok_Puddles", (0.509, 0.474, 0.147), 0.0],
                 ["wok_Swamp", (0.216, 0.216, 0.000), 0.0],
                 ["wok_Mud", (0.091, 0.147, 0.028), 0.0],
                 ["wok_Leaves", (1.000, 0.262, 0.000), 0.0],
                 ["wok_Lava", (0.300, 0.000, 0.000), 0.3],
                 ["wok_BottomlessPit", (0.000, 0.000, 0.000), 0.0],
                 ["wok_DeepWater", (0.000, 0.000, 0.216), 0.0],
                 ["wok_Door", (0.000, 0.000, 0.000), 0.0],
                 ["wok_Snow", (0.800, 0.800, 0.800), 0.0],
                 ["wok_Sand", (1.000, 1.000, 0.000), 0.0],
                 ["wok_BareBones", (0.500, 0.500, 0.100), 0.0],
                 ["wok_StoneBridge", (0.081, 0.108, 0.139), 0.0]
                 ]


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


class WalkmeshMaterial:
    DIRT = 1
    OBSCURING = 2
    GRASS = 3
    STONE = 4
    WOOD = 5
    WATER = 6
    NONWALK = 7
    TRANSPARENT = 8
    CARPET = 9
    METAL = 10
    PUDDLES = 11
    SWAMP = 12
    MUD = 13
    LEAVES = 14
    LAVA = 15
    BOTTOMLESSPIT = 16
    DEEPWATER = 17
    DOOR = 18
    SNOW = 19
    SAND = 20

    NONWALKABLE = [NONWALK, OBSCURING, SNOW, TRANSPARENT, DEEPWATER, LAVA]


class NormalsAlgorithm:
    NONE = "NONE"
    CUSTOM = "CUSTOM"
    SHARP_EDGES = "SHARP_EDGES"


class ImportOptions:
    def __init__(self):
        self.import_geometry = True
        self.import_animations = True
        self.import_walkmeshes = True
        self.build_materials = True
        self.build_armature = False
        self.normals_algorithm = NormalsAlgorithm.CUSTOM
        self.sharp_edge_angle = radians(10.0)
        self.texture_path = ""
        self.texture_search_recursive = False


class ExportOptions:
    def __init__(self):
        self.export_for_tsl = False
        self.export_for_xbox = False
        self.export_animations = True
        self.export_walkmeshes = True
        self.export_custom_normals = True
