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

import math

import bpy

from bpy.types import Operator
from mathutils import Vector

from ..constants import NAME_TO_WALKMESH_MATERIAL
from ..scene.material import WalkmeshNodeName
from ..utils import is_aabb_mesh

MINIMAP_SCALE = 1.5
MINIMAP_WIDTH = 512
MINIMAP_HEIGHT = 256
WALKMESH_Z_OFFSET = 10.0


def get_or_create_camera_object(name):
    if name in bpy.data.objects:
        return bpy.data.objects[name]

    if name in bpy.data.cameras:
        data = bpy.data.cameras[name]
    else:
        data = bpy.data.cameras.new(name)

    return bpy.data.objects.new(name, data)


def get_or_create_text(name):
    if name in bpy.data.texts:
        return bpy.data.texts[name]
    else:
        return bpy.data.texts.new(name)


class RenderMinimapOperator(Operator):
    def __init__(self, reset_render=False, hide_untextured=False):
        self.reset_render = reset_render
        self.hide_untextured = hide_untextured

    def execute(self, context):
        aabbs = [obj for obj in context.scene.objects if is_aabb_mesh(obj)]
        if not aabbs:
            return {"CANCELLED"}

        if self.hide_untextured:
            bpy.ops.kb.hide_untextured()

        # Set walkmesh materials opacity
        for aabb in aabbs:
            for material in aabb.data.materials:
                if not material.name in NAME_TO_WALKMESH_MATERIAL:
                    continue
                _, _, walkable = NAME_TO_WALKMESH_MATERIAL[material.name]
                if not material.use_nodes:
                    continue
                nodes = material.node_tree.nodes
                if (
                    WalkmeshNodeName.COLOR not in nodes
                    or WalkmeshNodeName.OPACITY not in nodes
                ):
                    continue
                color_node = nodes[WalkmeshNodeName.COLOR]
                color_node.outputs[0].default_value = [1.0] * 4
                opacity = nodes[WalkmeshNodeName.OPACITY]
                opacity.outputs[0].default_value = 0.15 if walkable else 0.0

        north_axis = 0
        camera = get_or_create_camera_object("MinimapCamera")

        # Calculate center of walkmesh geometry and move walkmeshes on top to avoid Z-fighting
        min_world = [1e5] * 3
        max_world = [-1e5] * 3
        accum = Vector([0.0] * 3)
        total_weight = 0
        for aabb in aabbs:
            aabb.delta_location.z += WALKMESH_Z_OFFSET
            aabb_center = Vector([0.0] * 3)
            num_corners = 0
            for corner in aabb.bound_box:
                center_world = aabb.matrix_world @ Vector(corner)
                min_world = [min(center_world[i], min_world[i]) for i in range(3)]
                max_world = [max(center_world[i], max_world[i]) for i in range(3)]
                aabb_center += center_world
                num_corners += 1
            aabb_center /= num_corners  # always 8
            weight = aabb.dimensions.x * aabb.dimensions.y
            accum += weight * aabb_center
            total_weight += weight
        if total_weight > 0.0:
            accum /= total_weight

        camera.location = [*accum[:2], max_world[2]]

        size_x = max_world[0] - min_world[0]
        size_y = max_world[1] - min_world[1]
        if size_y > size_x:
            # north_axis = 1
            # camera.rotation_euler.z = math.radians(180)
            # north_axis = 2
            # camera.rotation_euler.z = -math.radians(90)
            north_axis = 3
            camera.rotation_mode = "XYZ"
            camera.rotation_euler.z = math.radians(90.0)
            size_x, size_y = size_y, size_x

        aspect = MINIMAP_WIDTH // MINIMAP_HEIGHT
        camera.data.type = "ORTHO"
        camera.data.ortho_scale = MINIMAP_SCALE * max(size_x, aspect * size_y)

        if not camera.name in bpy.context.scene.objects:
            bpy.context.scene.collection.objects.link(camera)
        bpy.context.scene.camera = camera

        if self.reset_render:
            bpy.context.scene.render.resolution_x = MINIMAP_WIDTH
            bpy.context.scene.render.resolution_y = MINIMAP_HEIGHT
        bpy.ops.render.render(write_still=True)

        view_frame = camera.data.view_frame(scene=bpy.context.scene)
        corners_world = [camera.matrix_world @ corner for corner in view_frame]
        _, bottom_right, _, top_left = corners_world
        coords_text = get_or_create_text("MinimapCoords")
        lines = (
            "NorthAxis={}".format(north_axis),
            "WorldPt1X={}".format(top_left.x),
            "WorldPt1Y={}".format(top_left.y),
            "WorldPt2X={}".format(bottom_right.x),
            "WorldPt2Y={}".format(bottom_right.y),
            "MapPt1X={}".format(0.0),
            "MapPt1Y={}".format(0.0),
            "MapPt2X={}".format(1.0 / (440.0 / 512.0)),
            "MapPt2Y={}".format(1.0),
        )
        coords_text.from_string("\n".join(lines))

        # Restore walkmesh locations and materials
        for aabb in aabbs:
            aabb.delta_location.z -= WALKMESH_Z_OFFSET
            for material in aabb.data.materials:
                if not material.name in NAME_TO_WALKMESH_MATERIAL:
                    continue
                _, color, _ = NAME_TO_WALKMESH_MATERIAL[material.name]
                if not material.use_nodes:
                    continue
                nodes = material.node_tree.nodes
                if (
                    WalkmeshNodeName.COLOR not in nodes
                    or WalkmeshNodeName.OPACITY not in nodes
                ):
                    continue
                color_node = nodes[WalkmeshNodeName.COLOR]
                color_node.outputs[0].default_value = [*color, 1.0]
                opacity = nodes[WalkmeshNodeName.OPACITY]
                opacity.outputs[0].default_value = 1.0

        return {"FINISHED"}


class KB_OT_render_minimap_auto(RenderMinimapOperator):
    bl_idname = "kb.render_minimap_auto"
    bl_label = "Render Minimap (auto)"
    bl_description = "Render scene to an image, hiding untextures meshes and resetting render properties"

    def __init__(self):
        self.reset_render = True
        self.hide_untextured = True


class KB_OT_render_minimap_manual(RenderMinimapOperator):
    bl_idname = "kb.render_minimap_manual"
    bl_label = "Render Minimap (manual)"
    bl_description = "Render scene to an image, user is responsible for setting render properties and object visibility"

    def __init__(self):
        self.reset_render = False
        self.hide_untextured = False
