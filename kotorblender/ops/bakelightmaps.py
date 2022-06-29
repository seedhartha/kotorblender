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
from ..scene.material import ALPHA_NODE_NAME, DIFFUSE_BY_LIGHTMAP_NODE_NAME

UV_MAP_LIGHTMAP = "UVMap_lm"


class KB_OT_bake_lightmaps(bpy.types.Operator):
    bl_idname = "kb.bake_lightmaps"
    bl_label = "Bake"

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
        if not bakeable_objects:
            return {'CANCELLED'}
        context.view_layer.objects.active = bakeable_objects[0]

        # Bake lightmaps
        context.scene.cycles.samples = context.scene.kb.bake_samples
        bpy.ops.object.bake(
            margin=context.scene.kb.bake_margin,
            use_clear=True)

        for obj in bakeable_objects:
            self.postprocess_bakeable_object(obj)

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
            self.report({'WARNING'}, "Object '{}' does not contain lightmap UV map".format(obj.name))
            return False

        # Must contain certain material nodes
        if not obj.active_material.use_nodes:
            self.report({'WARNING'}, "Object '{}' material is not using nodes".format(obj.name))
            return False
        node_tree = obj.active_material.node_tree
        nodes = node_tree.nodes
        output_node = next((node for node in nodes if node.type == 'OUTPUT_MATERIAL'), None)
        if not output_node:
            self.report({'WARNING'}, "Object '{}' material does not contain output material node".format(obj.name))
            return False
        bsdf_node = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
        if not bsdf_node:
            self.report({'WARNING'}, "Object '{}' material does not contain BSDF node".format(obj.name))
            return False
        diffuse_by_lightmap_node = next((node for node in nodes if node.name == DIFFUSE_BY_LIGHTMAP_NODE_NAME), None)
        if not diffuse_by_lightmap_node:
            self.report({'WARNING'}, "Object '{}' material does not contain diffuse by lightmap node".format(obj.name))
            return False
        alpha_node = next((node for node in nodes if node.name == ALPHA_NODE_NAME), None)
        if not alpha_node:
            self.report({'WARNING'}, "Object '{}' material does not contain alpha node".format(obj.name))
            return False
        lightmap_node = next((node for node in nodes if node.type == 'TEX_IMAGE' and node.image.name == obj.kb.bitmap2), None)
        if not lightmap_node:
            self.report({'WARNING'}, "Object '{}' material does not contain lightmap texture node".format(obj.name))
            return False

        return True

    def preprocess_object(self, obj, bakeable):
        if bakeable:
            # Activate lightmap UV map
            uv_layer = obj.data.uv_layers[UV_MAP_LIGHTMAP]
            uv_layer.active = True

            node_tree = obj.active_material.node_tree
            nodes = node_tree.nodes

            # Remove node links
            bsdf_node = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
            diffuse_by_lightmap_node = next((node for node in nodes if node.name == DIFFUSE_BY_LIGHTMAP_NODE_NAME), None)
            alpha_node = next((node for node in nodes if node.name == ALPHA_NODE_NAME), None)
            links = node_tree.links
            base_color_link = next((link for link in links if link.from_node == diffuse_by_lightmap_node and link.to_node == bsdf_node), None)
            if base_color_link:
                links.remove(base_color_link)
            alpha_link = next((link for link in links if link.from_node == alpha_node and link.to_node == bsdf_node), None)
            if alpha_link:
                links.remove(alpha_link)

            # Activate lightmap material node
            lightmap_node = next((node for node in nodes if node.type == 'TEX_IMAGE' and node.image.name == obj.kb.bitmap2), None)
            nodes.active = lightmap_node

        if obj.type == 'MESH' and obj.kb.meshtype == MeshType.AABB:
            obj.hide_render = True

        return True

    def postprocess_bakeable_object(self, obj):
        # Restore node links
        node_tree = obj.active_material.node_tree
        nodes = node_tree.nodes
        links = node_tree.links
        bsdf_node = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
        diffuse_by_lightmap_node = next((node for node in nodes if node.name == DIFFUSE_BY_LIGHTMAP_NODE_NAME), None)
        alpha_node = next((node for node in nodes if node.name == ALPHA_NODE_NAME), None)
        links.new(bsdf_node.inputs["Base Color"], diffuse_by_lightmap_node.outputs[0])
        links.new(bsdf_node.inputs["Alpha"], alpha_node.outputs[0])
