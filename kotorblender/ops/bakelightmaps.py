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

from .. import utils

from ..defines import MeshType

UV_MAP_LIGHTMAP = "UVMap_lm"


class KB_OT_bake_lightmaps(bpy.types.Operator):
    bl_idname = "kb.bake_lightmaps"
    bl_label = "Bake Lightmaps"

    def execute(self, context):
        objects = context.selected_objects if len(context.selected_objects) > 0 else context.collection.objects

        bakeable_objects = []
        for obj in objects:
            bakeable = self.is_bakeable_object(obj)
            if bakeable:
                bakeable_objects.append(obj)
            self.preprocess_object(obj, bakeable)

        # Select only bakeable objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bakeable_objects:
            obj.select_set(True)

        # Bake lightmaps
        bpy.ops.object.bake()

        return {'FINISHED'}

    def is_bakeable_object(self, obj):
        if obj.type != 'MESH':
            return False
        if not obj.kb.lightmapped:
            return False
        if utils.is_null(obj.kb.bitmap2):
            return False

        # Must contain lightmap UV map
        if not UV_MAP_LIGHTMAP in obj.data.uv_layers:
            return False

        # Must contain lightmap material node
        if not obj.active_material.use_nodes:
            return False
        nodes = obj.active_material.node_tree.nodes
        lightmap_node = next((node for node in nodes if node.type == 'TEX_IMAGE' and node.image.name == obj.kb.bitmap2), None)
        if not lightmap_node:
            return False

        return True

    def preprocess_object(self, obj, bakeable):
        if bakeable:
            # Activate lightmap UV map
            uv_layer = obj.data.uv_layers[UV_MAP_LIGHTMAP]
            uv_layer.active = True

            # Activate lightmap material node
            nodes = obj.active_material.node_tree.nodes
            lightmap_node = next((node for node in nodes if node.type == 'TEX_IMAGE' and node.image.name == obj.kb.bitmap2), None)
            nodes.active = lightmap_node

        if obj.type == 'MESH':
            if obj.kb.meshtype == MeshType.AABB:
                obj.hide_render = True

        return True
