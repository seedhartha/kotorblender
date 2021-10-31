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

from ...defines import Classification


MODEL_FN_PTR_1_K1_PC = 4273776
MODEL_FN_PTR_1_K2_PC = 4285200
MODEL_FN_PTR_2_K1_PC = 4216096
MODEL_FN_PTR_2_K2_PC = 4216320

CLASS_OTHER = 0x00
CLASS_EFFECT = 0x01
CLASS_TILE = 0x02
CLASS_CHARACTER = 0x04
CLASS_DOOR = 0x08
CLASS_LIGHTSABER = 0x10
CLASS_PLACEABLE = 0x20
CLASS_FLYER = 0x40

CLASS_BY_VALUE = {
    CLASS_OTHER: Classification.UNKNOWN,
    CLASS_EFFECT: Classification.EFFECT,
    CLASS_TILE: Classification.TILE,
    CLASS_CHARACTER: Classification.CHARACTER,
    CLASS_DOOR: Classification.DOOR,
    CLASS_LIGHTSABER: Classification.SABER,
    CLASS_PLACEABLE: Classification.DOOR,
    CLASS_FLYER: Classification.FLYER
}

NODE_BASE = 0x0001
NODE_LIGHT = 0x0002
NODE_EMITTER = 0x0004
NODE_REFERENCE = 0x0010
NODE_MESH = 0x0020
NODE_SKIN = 0x0040
NODE_DANGLY = 0x0100
NODE_AABB = 0x0200
NODE_SABER = 0x0800
