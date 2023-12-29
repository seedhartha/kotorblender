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

from bpy.props import BoolProperty

from ..constants import MeshType
from ..scene.modelnode.trimesh import UV_MAP_LIGHTMAP
from ..scene.material import NodeName
from ..utils import is_null, is_mesh_type


class KB_OT_bake_lightmaps(bpy.types.Operator):
    bl_idname = "kb.bake_lightmaps"
    bl_label = "Bake Lightmaps"
    bl_description = "Bakes lighting and shadows into lightmap textures, optionally hiding non-lightmapped objects from render"

    lightmapped_only: BoolProperty(
        name="Bake only lightmapped objects and lights", default=True
    )

    def execute(self, context):
        # Find bake targets
        targets = [
            obj
            for obj in (
                context.selected_objects
                if context.selected_objects
                else context.collection.objects
            )
            if self.is_bake_target(obj)
        ]
        if not targets:
            return {"CANCELLED"}

        # Only bake lightmapped objects and lights, if enabled
        if self.lightmapped_only:
            target_names = set([obj.name for obj in targets])
            for obj in context.collection.objects:
                obj.hide_render = obj.type != "LIGHT" and not obj.name in target_names
        else:
            for target in targets:
                target.hide_render = False

        for obj in targets:
            self.preprocess_target(obj)

        # Select only bake targets
        bpy.ops.object.select_all(action="DESELECT")
        for obj in targets:
            obj.select_set(True)
        context.view_layer.objects.active = targets[0]

        context.scene.render.engine = "CYCLES"
        # context.scene.cycles.device = "GPU"
        if context.scene.cycles.samples > 512:
            context.scene.cycles.samples = 4
        bpy.ops.object.bake(margin=2, uv_layer=UV_MAP_LIGHTMAP)

        for obj in targets:
            self.postprocess_target(obj)

        return {"FINISHED"}

    def is_bake_target(self, obj):
        # TODO: support AABB (grass)
        if not is_mesh_type(obj, MeshType.TRIMESH):
            return False
        if not obj.kb.render:
            return False
        if not obj.kb.lightmapped:
            return False
        if is_null(obj.kb.bitmap):
            return False
        if is_null(obj.kb.bitmap2):
            return False
        if not UV_MAP_LIGHTMAP in obj.data.uv_layers:
            return False
        material = obj.active_material
        if not material or not material.use_nodes:
            return False
        nodes = obj.active_material.node_tree.nodes
        if not NodeName.DIFFUSE_TEX in nodes:
            return False
        if not NodeName.LIGHTMAP_TEX in nodes:
            return False
        if not NodeName.WHITE in nodes:
            return False
        if not NodeName.DIFFUSE_BSDF in nodes:
            return False
        if not NodeName.DIFF_LM_EMISSION in nodes:
            return False
        if not NodeName.ADD_DIFFUSE_EMISSION in nodes:
            return False
        return True

    def preprocess_target(self, obj):
        material = obj.active_material
        nodes = material.node_tree.nodes
        links = material.node_tree.links

        # Replace diffuse * lightmap shader by diffuse
        add_diffuse_emission = nodes[NodeName.ADD_DIFFUSE_EMISSION]
        if add_diffuse_emission.inputs[0].is_linked:
            links.remove(add_diffuse_emission.inputs[0].links[0])
        diffuse_bsdf = nodes[NodeName.DIFFUSE_BSDF]
        links.new(add_diffuse_emission.inputs[0], diffuse_bsdf.outputs[0])

        # Replace diffuse color by white
        if diffuse_bsdf.inputs[0].is_linked:
            links.remove(diffuse_bsdf.inputs[0].links[0])
        white = nodes[NodeName.WHITE]
        links.new(diffuse_bsdf.inputs[0], white.outputs[0])

        # Select only lightmap texture node and make it active
        for node in nodes:
            node.select = False
        lightmap_tex = nodes[NodeName.LIGHTMAP_TEX]
        lightmap_tex.select = True
        nodes.active = lightmap_tex

    def postprocess_target(self, obj):
        material = obj.active_material
        nodes = material.node_tree.nodes
        links = material.node_tree.links

        # Replace diffuse shader by diffuse * lightmap
        add_diffuse_emission = nodes[NodeName.ADD_DIFFUSE_EMISSION]
        diff_lm_emission = nodes[NodeName.DIFF_LM_EMISSION]
        if add_diffuse_emission.inputs[0].is_linked:
            links.remove(add_diffuse_emission.inputs[0].links[0])
        links.new(add_diffuse_emission.inputs[0], diff_lm_emission.outputs[0])

        # Replace white by diffuse color
        diffuse_bsdf = nodes[NodeName.DIFFUSE_BSDF]
        if diffuse_bsdf.inputs[0].is_linked:
            links.remove(diffuse_bsdf.inputs[0].links[0])
        diffuse_tex = nodes[NodeName.DIFFUSE_TEX]
        links.new(diffuse_bsdf.inputs[0], diffuse_tex.outputs[0])
