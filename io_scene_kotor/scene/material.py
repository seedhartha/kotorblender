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

import os

import bpy

from bpy_extras import image_utils

from .. import utils

from ..format.tpc.loader import TpcLoader

DIFFUSE_BY_LIGHTMAP_NODE_NAME = "Diffuse By Lightmap"
ALPHA_NODE_NAME = "Multiply Alpha"


def rebuild_object_material(obj, texture_search_paths=[], lightmap_search_paths=[]):
    material = get_or_create_material(obj)

    mesh = obj.data
    mesh.materials.clear()
    mesh.materials.append(material)

    # Only use nodes when object has at least one texture
    if utils.is_null(obj.kb.bitmap) and utils.is_null(obj.kb.bitmap2):
        rebuild_material_simple(material, obj)
    else:
        rebuild_material_nodes(
            material, obj, texture_search_paths, lightmap_search_paths
        )


def get_or_create_material(obj):
    name = get_material_name(obj)
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    else:
        return bpy.data.materials.new(name)


def get_material_name(obj):
    if utils.is_null(obj.kb.bitmap) and utils.is_null(obj.kb.bitmap2):
        diffuse = utils.color_to_hex(obj.kb.diffuse)
        alpha = utils.int_to_hex(utils.float_to_byte(obj.kb.alpha))
        name = "D{}__A{}".format(diffuse, alpha)
    else:
        name = obj.name
    return name


def rebuild_material_simple(material, obj):
    material.use_nodes = False
    material.diffuse_color = [*obj.kb.diffuse, 1.0]


def rebuild_material_nodes(material, obj, texture_search_paths, lightmap_search_paths):
    material.use_nodes = True
    material.use_backface_culling = True
    links = material.node_tree.links
    links.clear()
    nodes = material.node_tree.nodes
    nodes.clear()

    # Output node
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (1200, 0)

    # Shader node
    selfillumed = not utils.is_close_3(obj.kb.selfillumcolor, [0.0] * 3, 0.1)
    if selfillumed:
        shader = nodes.new("ShaderNodeEmission")
    else:
        shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.location = (900, 0)

    # Multiply diffuse by lightmap node
    mul_diffuse_by_lightmap = nodes.new("ShaderNodeVectorMath")
    mul_diffuse_by_lightmap.name = DIFFUSE_BY_LIGHTMAP_NODE_NAME
    mul_diffuse_by_lightmap.location = (600, 0)
    mul_diffuse_by_lightmap.operation = "MULTIPLY"
    mul_diffuse_by_lightmap.inputs[0].default_value = [1.0] * 3
    mul_diffuse_by_lightmap.inputs[1].default_value = [1.0] * 3

    # Alpha node
    mul_alpha = nodes.new("ShaderNodeMath")
    mul_alpha.name = ALPHA_NODE_NAME
    mul_alpha.location = (600, -300)
    mul_alpha.operation = "MULTIPLY"
    mul_alpha.inputs[0].default_value = 1.0
    mul_alpha.inputs[1].default_value = obj.kb.alpha

    # Diffuse map node
    if utils.is_not_null(obj.kb.bitmap):
        diffuse = nodes.new("ShaderNodeTexImage")
        diffuse.location = (300, 0)
        diffuse.image = get_or_create_texture(obj.kb.bitmap, texture_search_paths).image
        links.new(mul_diffuse_by_lightmap.inputs[0], diffuse.outputs[0])
        links.new(mul_alpha.inputs[0], diffuse.outputs[1])

    # Lightmap node
    if utils.is_not_null(obj.kb.bitmap2):
        lightmap_uv = nodes.new("ShaderNodeUVMap")
        lightmap_uv.location = (0, -300)
        lightmap_uv.uv_map = "UVMap_lm"

        lightmap = nodes.new("ShaderNodeTexImage")
        lightmap.location = (300, -300)
        lightmap.image = get_or_create_texture(
            obj.kb.bitmap2, lightmap_search_paths
        ).image

        material.shadow_method = "NONE"
        links.new(lightmap.inputs[0], lightmap_uv.outputs[0])
        links.new(mul_diffuse_by_lightmap.inputs[1], lightmap.outputs[0])

    if selfillumed:
        links.new(shader.inputs["Color"], mul_diffuse_by_lightmap.outputs[0])
    else:
        links.new(shader.inputs["Base Color"], mul_diffuse_by_lightmap.outputs[0])
        links.new(shader.inputs["Alpha"], mul_alpha.outputs[0])

    links.new(output.inputs[0], shader.outputs[0])


def get_or_create_texture(name, search_paths):
    if name in bpy.data.textures:
        return bpy.data.textures[name]

    if name in bpy.data.images:
        image = bpy.data.images[name]
    else:
        image = create_image(name, search_paths)

    texture = bpy.data.textures.new(name, type="IMAGE")
    texture.image = image
    texture.use_fake_user = True

    return texture


def create_image(name, search_paths):
    tpc_filename = (name + ".tpc").lower()
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
        image = image_utils.load_image(name + ".tga", search_path, recursive=True)
        if image:
            image.name = name
            return image
        for filename in os.listdir(search_path):
            if filename.lower() != tpc_filename:
                continue
            path = os.path.join(search_path, filename)
            print("Loading TPC image: " + path)
            tpc_image = TpcLoader(path).load()
            image = bpy.data.images.new(name, tpc_image.w, tpc_image.h)
            image.pixels = tpc_image.pixels
            image.update()
            return image

    return bpy.data.images.new(name, 512, 512)
