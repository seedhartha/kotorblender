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

FILE_VERSION = "V3.2"

FIELD_TYPE_DWORD = 4
FIELD_TYPE_FLOAT = 8
FIELD_TYPE_STRUCT = 14
FIELD_TYPE_LIST = 15


class KeyValue:
    def __init__(self, key, value):
        self.key = key
        self.value = value


class GffStruct:
    def __init__(self, type, data_or_data_offset, num_fields):
        self.type = type
        self.data_or_data_offset = data_or_data_offset
        self.num_fields = num_fields


class GffField:
    def __init__(self, type, label_idx, data_or_data_offset):
        self.type = type
        self.label_idx = label_idx
        self.data_or_data_offset = data_or_data_offset