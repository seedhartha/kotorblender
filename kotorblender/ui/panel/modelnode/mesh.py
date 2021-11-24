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

from ....defines import MeshType

from .... import utils


class KB_PT_mesh(bpy.types.Panel):
    bl_label = "Mesh"
    bl_parent_id = "KB_PT_modelnode"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and obj.kb.meshtype != MeshType.EMITTER

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.use_property_split = True

        row = layout.row()
        row.prop(obj.kb, "bitmap")
        row = layout.row()
        row.prop(obj.kb, "bitmap2")
        row = layout.row()
        row.prop(obj.kb, "diffuse")
        row = layout.row()
        row.prop(obj.kb, "ambient")
        row = layout.row()
        row.prop(obj.kb, "selfillumcolor")
        row = layout.row()
        row.prop(obj.kb, "alpha")
        row = layout.row()
        row.prop(obj.kb, "transparencyhint")

        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "render")
        col.prop(obj.kb, "shadow")
        col.prop(obj.kb, "lightmapped")
        col.prop(obj.kb, "tangentspace")
        col.prop(obj.kb, "background_geometry")
        col.prop(obj.kb, "beaming")
        col.prop(obj.kb, "rotatetexture")
        col.prop(obj.kb, "animateuv")

        row = layout.row()
        col = row.column(align=True, heading="TSL only")
        col.prop(obj.kb, "hologram_donotdraw")
        col.prop(obj.kb, "dirt_enabled")

        row = layout.row()
        row.operator("kb.rebuild_materials")


class KB_PT_mesh_uv_anim(bpy.types.Panel):
    bl_label = "UV animation"
    bl_parent_id = "KB_PT_mesh"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @ classmethod
    def poll(cls, context):
        obj = context.object
        return (obj and
                obj.type == 'MESH' and
                obj.kb.meshtype != MeshType.EMITTER and
                obj.kb.animateuv)

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.use_property_split = True

        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "uvdirectionx", text="Direction X")
        col.prop(obj.kb, "uvdirectiony", text="Y")
        row = layout.row()
        col = row.column(align=True)
        col.prop(obj.kb, "uvjitter", text="Jitter Amount")
        col.prop(obj.kb, "uvjitterspeed", text="Speed")


class KB_PT_mesh_dirt(bpy.types.Panel):
    bl_label = "Dirt"
    bl_parent_id = "KB_PT_mesh"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @ classmethod
    def poll(cls, context):
        obj = context.object
        return (obj and
                obj.type == 'MESH' and
                obj.kb.meshtype != MeshType.EMITTER and
                obj.kb.dirt_enabled)

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.use_property_split = True

        row = layout.row()
        row.prop(obj.kb, "dirt_texture")
        row = layout.row()
        row.prop(obj.kb, "dirt_worldspace")


class KB_PT_mesh_dangly(bpy.types.Panel):
    bl_label = "Danglymesh"
    bl_parent_id = "KB_PT_mesh"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @ classmethod
    def poll(cls, context):
        obj = context.object
        return utils.is_mesh_type(obj, MeshType.DANGLYMESH)

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.use_property_split = True

        row = layout.row()
        row.prop_search(obj.kb, "constraints", obj, "vertex_groups", text="Constraints")
        row = layout.row()
        row.prop(obj.kb, "period")
        row = layout.row()
        row.prop(obj.kb, "tightness")
        row = layout.row()
        row.prop(obj.kb, "displacement")


class KB_PT_mesh_aabb(bpy.types.Panel):
    bl_label = "AABB"
    bl_parent_id = "KB_PT_mesh"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @ classmethod
    def poll(cls, context):
        obj = context.object
        return utils.is_mesh_type(obj, MeshType.AABB)

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.use_property_split = True

        row = layout.row()
        row.prop(obj.kb, "lytposition")
        row = layout.row()
        row.operator("kb.load_wok_mats", icon='NONE')
