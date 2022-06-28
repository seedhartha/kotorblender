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

UV_MAP_LIGHTMAP = "UVMap_lm"


class KB_OT_bake_lightmaps(bpy.types.Operator):
    bl_idname = "kb.bake_lightmaps"
    bl_label = "Bake Lightmaps"

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        bakeable_objects = []
        for obj in context.selected_objects:
            if not self.can_bake_object_lightmap(obj):
                continue
            if not self.prepare_object(obj):
                continue
            bakeable_objects.append(obj)

        # Select only bakeable objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bakeable_objects:
            obj.select_set(True)

        # Bake lightmaps
        bpy.ops.object.bake()

        return {'FINISHED'}

    def can_bake_object_lightmap(self, obj):
        if obj.type == 'MESH' and obj.kb.lightmapped or utils.is_not_null(obj.kb.bitmap2):
            return True
        else:
            return False

    def prepare_object(self, obj):
        mesh = obj.data

        # Activate lightmap UV map
        if not UV_MAP_LIGHTMAP in mesh.uv_layers:
            return False
        uv_layer = mesh.uv_layers[UV_MAP_LIGHTMAP]
        uv_layer.active = True

        # Activate lightmap material node
        if not obj.active_material.use_nodes:
            return False
        nodes = obj.active_material.node_tree.nodes
        lm_node = next((node for node in nodes if node.type == 'TEX_IMAGE' and node.image.name == obj.kb.bitmap2), None)
        if not lm_node:
            return False
        nodes.active = lm_node

        return True
