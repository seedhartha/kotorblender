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

import bpy

from mathutils import Matrix, Quaternion

from ... import defines


class GeometryNode:

    def __init__(self, name = "UNNAMED"):
        self.nodetype = "undefined"

        self.roottype = "mdl"
        self.rootname = "undefined"

        self.name        = name
        self.parentName  = defines.null
        self.position    = (0.0, 0.0, 0.0)
        self.orientation = (1.0, 0.0, 0.0, 0.0)
        self.scale       = 1.0
        self.wirecolor   = (0.0, 0.0, 0.0)

        self.fromRoot = Matrix()

        self.objref = ""

    def add_to_collection(self, collection):
        obj = bpy.data.objects.new(self.name, None)
        self.set_object_data(obj)
        collection.objects.link(obj)
        return obj

    def set_object_data(self, obj):
        self.objref = obj.name  # used to resolve naming conflicts
        obj.rotation_mode       = 'QUATERNION'
        obj.rotation_quaternion = Quaternion(self.orientation)
        obj.kb.restrot          = self.orientation
        obj.scale               = (self.scale, self.scale, self.scale)
        obj.location            = self.position
        obj.kb.restloc          = obj.location
        obj.kb.wirecolor        = self.wirecolor
