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

NULL = "NULL"

# Number of frames to the left of animation, where to create a rest pose
ANIM_REST_POSE_OFFSET = 5

# Number of frames between two consecutive animations
ANIM_PADDING = 60

FPS = 30

WOK_MATERIALS = [
    ["wok_NotDefined", (0.400, 0.400, 0.400), 0.0],
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
    ["wok_StoneBridge", (0.081, 0.108, 0.139), 0.0],
]

# A list of dummy/null objects used in human character rigs (male and female) in both games.
# Used for the hide/unhide menu functions. Store in lowercase.
CHAR_DUMMY_NAMES = [
    "camerahook",
    "cutscenedummy",
    "deflecthook",
    "dummy01",
    "dummy02",
    "freelookhook",
    "gogglehook",
    "handconjure",
    "headconjure",
    "headhook",
    "hturn_g",
    "hturn_g",
    "impact",
    "impact_bolt",
    "lcollar_dum",
    "lforearm",
    "lhand",
    "lightsaberhook",
    "maskhook",
    "rcollar_dum",
    "revmask1hook",
    "revmask2hook",
    "rhand",
    "rootdummy",
    "talkdummy",
]

# A list of trimesh bones used in human character rigs (male and female) in both games.
# Used for the hide/unhide menu functions. Store in lowercase.
CHAR_BONE_NAMES = [
    "breastbone",
    "f_jaw_g",
    "f_lbrw_g",
    "f_llm_g",
    "f_llweye_g",
    "f_lmc_g",
    "f_lns_g",
    "f_mdbrw_g",
    "f_rbrw_g",
    "f_rlm_g",
    "f_rlweye_g",
    "f_rmc_g",
    "f_rns_g",
    "f_tonguetip_g",
    "f_um_g",
    "frobe1_g",
    "frobe2_g",
    "head_g",
    "lafngrb_g",
    "lafngrt_g",
    "lbfngrb_g",
    "lbfngrt_g",
    "lbicep_g",
    "lbicep_gl",
    "lbicepl_g",
    "lcfngrb_g",
    "lcfngrt_g",
    "lcollar_g",
    "ldfngrb_g",
    "ldfngrt_g",
    "lfoot_g",
    "lfoott_g",
    "lforearm_g",
    "lhand_g",
    "lrobe1_g",
    "lrobe2_g",
    "lrobe3_g",
    "lshin_g",
    "lsleeve1_g",
    "lsleeve2_g",
    "lthigh_g",
    "lthumbb_g",
    "lthumbt_g",
    "mrobe1_g",
    "mrobe2_g",
    "mrobe3_g",
    "neck_g",
    "necklwr_g",
    "pelvis_g",
    "rafngrb_g",
    "rafngrt_g",
    "rbfngrb_g",
    "rbfngrt_g",
    "rbicep_g",
    "rbicep_gl",
    "rbicepl_g",
    "rcfngrb_g",
    "rcfngrt_g",
    "rcollar_g",
    "rdfngrb_g",
    "rdfngrt_g",
    "rfoot_g",
    "rfoott_g",
    "rforearm_g",
    "rhand_g",
    "rrobe1_g",
    "rrobe2_g",
    "rrobe3_g",
    "rshin_g",
    "rsleeve1_g",
    "rsleeve2_g",
    "rthigh_g",
    "rthumbb_g",
    "rthumbt_g",
    "torsoupr_g",
    "torso_g",
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


class ImportOptions:
    def __init__(self):
        self.import_geometry = True
        self.import_animations = True
        self.import_walkmeshes = True
        self.build_materials = True
        self.build_armature = False
        self.texture_search_paths = []
        self.lightmap_search_paths = []


class ExportOptions:
    def __init__(self):
        self.export_for_tsl = False
        self.export_for_xbox = False
        self.export_animations = True
        self.export_walkmeshes = True
