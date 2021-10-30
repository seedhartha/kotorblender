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

from .. import light

from .geometry import GeometryNode


class FlareList():
    def __init__(self):
        self.textures    = []
        self.sizes       = []
        self.positions   = []
        self.colorshifts = []


class LightNode(GeometryNode):

    def __init__(self, name = "UNNAMED"):
        GeometryNode.__init__(self, name)
        self.nodetype = "light"

        self.shadow        = 1
        self.radius        = 5.0
        self.multiplier    = 1
        self.lightpriority = 5
        self.color         = (0.0, 0.0, 0.0)
        self.ambientonly   = 1
        self.ndynamictype  = 0
        self.isdynamic     = 0
        self.affectdynamic = 1
        self.negativelight = 0
        self.fadinglight   = 1
        self.lensflares    = 0
        self.flareradius   = 1.0
        self.flare_list     = FlareList()

    def add_to_collection(self, collection):
        light = self.create_light(self.name)
        obj = bpy.data.objects.new(self.name, light)
        self.set_object_data(obj)
        collection.objects.link(obj)
        return obj

    def create_light(self, name):
        light = bpy.data.lights.new(name, 'POINT')
        light.color = self.color
        light.use_shadow = self.shadow != 0
        return light

    def set_object_data(self, obj):
        GeometryNode.set_object_data(self, obj)

        switch = {"ml1": "MAINLIGHT1",
                  "ml2": "MAINLIGHT2",
                  "sl1": "SOURCELIGHT1",
                  "sl2": "SOURCELIGHT2"}
        #TODO: Check light names when exporting tiles
        obj.kb.multiplier    = self.multiplier
        obj.kb.radius        = self.radius
        obj.kb.ambientonly   = (self.ambientonly >= 1)
        obj.kb.lighttype     = switch.get(self.name[-3:], "NONE")
        obj.kb.shadow        = (self.shadow >= 1)
        obj.kb.lightpriority = self.lightpriority
        obj.kb.fadinglight   = (self.fadinglight >= 1)
        obj.kb.isdynamic     = self.ndynamictype
        if obj.kb.isdynamic == 0 and self.isdynamic >= 1:
            obj.kb.isdynamic = 1
        obj.kb.affectdynamic = (self.affectdynamic >= 1)

        if (self.flareradius > 0) or (self.lensflares >= 1):
            obj.kb.lensflares = True
            num_flares = len(self.flare_list.textures)
            for i in range(num_flares):
                newItem = obj.kb.flare_list.add()
                newItem.texture    = self.flare_list.textures[i]
                newItem.colorshift = self.flare_list.colorshifts[i]
                newItem.size       = self.flare_list.sizes[i]
                newItem.position   = self.flare_list.positions[i]

        obj.kb.flareradius = self.flareradius
        light.calc_light_power(obj)
