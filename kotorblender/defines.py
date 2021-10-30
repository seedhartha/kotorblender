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

# Null value for parents, textures, etc.
null = "NULL"

# Some presets
# Frame at which to start all animations
anim_globstart = 1
# Offset between two imported animations (minimum)
anim_offset = 60
fps = 30
wok_materials = [ ["wok_NotDefined"    , (0.400, 0.400, 0.400), 0.0], \
                  ["wok_Dirt"          , (0.610, 0.235, 0.050), 0.0], \
                  ["wok_Obscuring"     , (0.100, 0.100, 0.100), 0.5], \
                  ["wok_Grass"         , (0.000, 0.600, 0.000), 0.0], \
                  ["wok_Stone"         , (0.162, 0.216, 0.279), 0.0], \
                  ["wok_Wood"          , (0.258, 0.059, 0.007), 0.0], \
                  ["wok_Water"         , (0.000, 0.000, 1.000), 0.0], \
                  ["wok_Nonwalk"       , (1.000, 0.000, 0.000), 0.0], \
                  ["wok_Transparent"   , (1.000, 1.000, 1.000), 1.0], \
                  ["wok_Carpet"        , (1.000, 0.000, 1.000), 0.0], \
                  ["wok_Metal"         , (0.434, 0.552, 0.730), 1.0], \
                  ["wok_Puddles"       , (0.509, 0.474, 0.147), 0.0], \
                  ["wok_Swamp"         , (0.216, 0.216, 0.000), 0.0], \
                  ["wok_Mud"           , (0.091, 0.147, 0.028), 0.0], \
                  ["wok_Leaves"        , (1.000, 0.262, 0.000), 0.0], \
                  ["wok_Lava"          , (0.300, 0.000, 0.000), 0.3], \
                  ["wok_BottomlessPit" , (0.000, 0.000, 0.000), 0.0], \
                  ["wok_DeepWater"     , (0.000, 0.000, 0.216), 0.0], \
                  ["wok_Door"          , (0.000, 0.000, 0.000), 0.0], \
                  ["wok_Snow"          , (0.800, 0.800, 0.800), 0.0], \
                  ["wok_Sand"          , (1.000, 1.000, 0.000), 0.0], \
                  ["wok_BareBones"     , (0.500, 0.500, 0.100), 0.0], \
                  ["wok_StoneBridge"   , (0.081, 0.108, 0.139), 0.0] ]


class WkmMaterial():
    DIRT                = 1
    OBSCURING           = 2
    GRASS               = 3
    STONE               = 4
    WOOD                = 5
    WATER               = 6
    NONWALK             = 7
    TRANSPARENT         = 8
    CARPET              = 9
    METAL               = 10
    PUDDLES             = 11
    SWAMP               = 12
    MUD                 = 13
    LEAVES              = 14
    LAVA                = 15
    BOTTOMLESSPIT       = 16
    DEEPWATER           = 17
    DOOR                = 18
    SNOW                = 19
    SAND                = 20

    NONWALKABLE = [ NONWALK, OBSCURING, SNOW, TRANSPARENT, DEEPWATER, LAVA ]


class DummySubtype():
    NONE      = "NONE"
    HAND      = "HAND"
    HEAD      = "HEAD"
    HEAD_HIT  = "HHIT"
    IMPACT    = "IMPC"
    GROUND    = "GRND"
    USE1      = "USE1"
    USE2      = "USE2"
    OPEN1_01  = "O101"
    OPEN1_02  = "O102"
    OPEN2_01  = "O201"
    OPEN2_02  = "O202"
    CLOSED_01 = "CL01"
    CLOSED_02 = "CL02"

    SUFFIX_LIST = [ ("use01",     USE1), \
                    ("use02",     USE2), \
                    ("hand",      HAND), \
                    ("head",      HEAD), \
                    ("head_hit",  HEAD_HIT), \
                    ("hhit",      HEAD_HIT), \
                    ("impact",    IMPACT), \
                    ("impc",      IMPACT), \
                    ("ground",    GROUND), \
                    ("grnd",      GROUND), \
                    ("open1_01",  OPEN1_01), \
                    ("open1_02",  OPEN1_02), \
                    ("open2_01",  OPEN2_01), \
                    ("open2_02",  OPEN2_02), \
                    ("closed_01", CLOSED_01), \
                    ("closed_02", CLOSED_02) ]

    SUFFIX_PWK = {  NONE     : "", \
                    HAND     : "hand", \
                    HEAD     : "head", \
                    HEAD_HIT : "head_hit", \
                    IMPACT   : "impact", \
                    GROUND   : "ground", \
                    USE1     : "use01", \
                    USE2     : "use02" }

    SUFFIX_DWK = {  NONE      : "", \
                    HAND      : "hand", \
                    HEAD      : "head", \
                    HEAD_HIT  : "hhit", \
                    IMPACT    : "impc", \
                    GROUND    : "grnd", \
                    USE1      : "use01", \
                    USE2      : "use02", \
                    OPEN1_01  : "open1_01", \
                    OPEN1_02  : "open1_02", \
                    OPEN2_01  : "open2_01", \
                    OPEN2_02  : "open2_02", \
                    CLOSED_01 : "closed_01", \
                    CLOSED_01 : "closed_02" }


class Meshtype():
    TRIMESH    = "TRI"
    DANGLYMESH = "DAN"
    LIGHTSABER = "SAB"
    SKIN       = "SKI"
    AABB       = "AAB"
    EMITTER    = "EMT"

    ALL = {TRIMESH, DANGLYMESH, LIGHTSABER, SKIN, AABB, EMITTER}


class Dummytype():
    NONE      = "NON"
    DWKROOT   = "DWK"
    MDLROOT   = "MDL"
    PWKROOT   = "PWK"
    REFERENCE = "REF"
    PATHPOINT = "PTH"

    ALL = {NONE, DWKROOT, MDLROOT, PWKROOT, REFERENCE, PATHPOINT}


class Classification():
    UNKNOWN   = "Other"
    TILE      = "Tile"
    CHARACTER = "Character"
    DOOR      = "Door"
    EFFECT    = "Effect"
    GUI       = "Gui"
    SABER     = "Lightsaber"
    ITEM      = "Placeable"
    FLYER     = "Flyer"

    ALL = {UNKNOWN, TILE, CHARACTER, DOOR, EFFECT, GUI, SABER, ITEM, FLYER}


class Nodetype():
    DUMMY       = "dummy"
    REFERENCE   = "reference"
    TRIMESH     = "trimesh"
    DANGLYMESH  = "danglymesh"
    SKIN        = "skin"
    EMITTER     = "emitter"
    LIGHT       = "light"
    AABB        = "aabb"
    LIGHTSABER  = "lightsaber"
