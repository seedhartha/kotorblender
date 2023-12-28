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

from ..format.tpc.reader import TpcReader
from ..utils import (
    is_null,
    is_not_null,
    color_to_hex,
    int_to_hex,
    float_to_byte,
    is_close_3,
)


class NodeName:
    DIFFUSE_TEX = "diffuse_tex"
    LIGHTMAP_TEX = "lightmap_tex"
    MUL_DIFFUSE_LIGHTMAP = "mul_diffuse_lightmap"
    MUL_DIFFUSE_SELFILLUM = "mul_diffuse_selfillum"
    DIFFUSE_BSDF = "diffuse_bsdf"
    DIFF_LM_EMISSION = "diff_lm_emission"
    SELFILLUM_EMISSION = "selfillum_emission"
    GLOSSY_BSDF = "glossy_bsdf"
    ADD_DIFFUSE_EMISSION = "add_diffuse_emission"
    MIX_MATTE_GLOSSY = "mix_matte_glossy"
    OBJECT_ALPHA = "object_alpha"
    TRANSPARENT_BSDF = "transparent_bsdf"
    MIX_OPAQUE_TRANSPARENT = "mix_opaque_transparent"


def rebuild_object_material(obj, texture_search_paths=[], lightmap_search_paths=[]):
    material = get_or_create_material(obj)

    mesh = obj.data
    mesh.materials.clear()
    mesh.materials.append(material)

    # Only use nodes when object has at least one texture
    if is_null(obj.kb.bitmap) and is_null(obj.kb.bitmap2):
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
    if is_null(obj.kb.bitmap) and is_null(obj.kb.bitmap2):
        diffuse = color_to_hex(obj.kb.diffuse)
        alpha = int_to_hex(float_to_byte(obj.kb.alpha))
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
    material.blend_method = "HASHED"
    if not is_close_3(obj.kb.selfillumcolor, (0.0, 0.0, 0.0)):
        material.shadow_method = "NONE"

    links = material.node_tree.links
    links.clear()

    nodes = material.node_tree.nodes
    nodes.clear()

    x = 0

    # Diffuse texture
    if is_not_null(obj.kb.bitmap):
        diffuse_tex = nodes.new("ShaderNodeTexImage")
        diffuse_tex.name = NodeName.DIFFUSE_TEX
        diffuse_tex.location = (x, 0)
        diffuse_tex.image = get_or_create_texture(
            obj.kb.bitmap, texture_search_paths
        ).image

    # Lightmap texture
    if is_not_null(obj.kb.bitmap2):
        lightmap_uv = nodes.new("ShaderNodeUVMap")
        lightmap_uv.location = (x - 300, -300)
        lightmap_uv.uv_map = "UVMap_lm"

        lightmap_tex = nodes.new("ShaderNodeTexImage")
        lightmap_tex.name = NodeName.LIGHTMAP_TEX
        lightmap_tex.location = (x, -300)
        lightmap_tex.image = get_or_create_texture(
            obj.kb.bitmap2, lightmap_search_paths
        ).image
        links.new(lightmap_tex.inputs[0], lightmap_uv.outputs[0])

    x += 300

    # Multiply diffuse color by lightmap color
    mul_diffuse_lightmap = nodes.new("ShaderNodeVectorMath")
    mul_diffuse_lightmap.name = NodeName.MUL_DIFFUSE_LIGHTMAP
    mul_diffuse_lightmap.location = (x, -300)
    mul_diffuse_lightmap.operation = "MULTIPLY"
    mul_diffuse_lightmap.inputs[1].default_value = [1.0] * 3
    links.new(mul_diffuse_lightmap.inputs[0], diffuse_tex.outputs[0])
    if is_not_null(obj.kb.bitmap2):
        links.new(mul_diffuse_lightmap.inputs[1], lightmap_tex.outputs[0])

    # Multiply diffuse color by self-illumination color
    mul_diffuse_selfillum = nodes.new("ShaderNodeVectorMath")
    mul_diffuse_selfillum.name = NodeName.MUL_DIFFUSE_SELFILLUM
    mul_diffuse_selfillum.location = (x, -600)
    mul_diffuse_selfillum.operation = "MULTIPLY"
    mul_diffuse_selfillum.inputs[1].default_value = obj.kb.selfillumcolor
    links.new(mul_diffuse_selfillum.inputs[0], diffuse_tex.outputs[0])

    x += 300

    # Diffuse BSDF
    diffuse_bsdf = nodes.new("ShaderNodeBsdfDiffuse")
    diffuse_bsdf.name = NodeName.DIFFUSE_BSDF
    diffuse_bsdf.location = (x, 0)
    links.new(diffuse_bsdf.inputs["Color"], diffuse_tex.outputs[0])

    # Emission from diffuse * lightmap
    diff_lm_emission = nodes.new("ShaderNodeEmission")
    diff_lm_emission.name = NodeName.DIFF_LM_EMISSION
    diff_lm_emission.location = (x, -300)
    links.new(diff_lm_emission.inputs["Color"], mul_diffuse_lightmap.outputs[0])

    # Emission from self-illumination
    selfillum_emission = nodes.new("ShaderNodeEmission")
    selfillum_emission.name = NodeName.SELFILLUM_EMISSION
    selfillum_emission.location = (x, -600)
    links.new(selfillum_emission.inputs["Color"], mul_diffuse_selfillum.outputs[0])

    x += 300

    # Glossy BSDF
    glossy_bsdf = nodes.new("ShaderNodeBsdfGlossy")
    glossy_bsdf.name = NodeName.GLOSSY_BSDF
    glossy_bsdf.location = (x, 0)

    # Combine diffuse or diffuse * lightmap, and self-illumination emission
    add_diffuse_emission = nodes.new("ShaderNodeAddShader")
    add_diffuse_emission.name = NodeName.ADD_DIFFUSE_EMISSION
    add_diffuse_emission.location = (x, -300)
    if obj.kb.lightmapped:
        links.new(add_diffuse_emission.inputs[0], diff_lm_emission.outputs[0])
    else:
        links.new(add_diffuse_emission.inputs[0], diffuse_bsdf.outputs[0])
    links.new(add_diffuse_emission.inputs[1], selfillum_emission.outputs[0])

    x += 300

    # Object alpha
    object_alpha = nodes.new("ShaderNodeValue")
    object_alpha.name = NodeName.OBJECT_ALPHA
    object_alpha.location = (x, 300)
    object_alpha.outputs[0].default_value = obj.kb.alpha

    # Transparent BSDF
    transparent_bsdf = nodes.new("ShaderNodeBsdfTransparent")
    transparent_bsdf.name = NodeName.TRANSPARENT_BSDF
    transparent_bsdf.location = (x, 0)

    # Mix matte and glossy
    mix_matte_glossy = nodes.new("ShaderNodeMixShader")
    mix_matte_glossy.name = NodeName.MIX_MATTE_GLOSSY
    mix_matte_glossy.location = (x, -300)
    links.new(mix_matte_glossy.inputs[0], diffuse_tex.outputs[1])
    links.new(mix_matte_glossy.inputs[1], glossy_bsdf.outputs[0])
    links.new(mix_matte_glossy.inputs[2], add_diffuse_emission.outputs[0])

    x += 300

    # Mix opaque and transparent
    mix_opaque_transparent = nodes.new("ShaderNodeMixShader")
    mix_opaque_transparent.name = NodeName.MIX_OPAQUE_TRANSPARENT
    mix_opaque_transparent.location = (x, -300)
    links.new(mix_opaque_transparent.inputs[0], object_alpha.outputs[0])
    links.new(mix_opaque_transparent.inputs[1], transparent_bsdf.outputs[0])
    links.new(mix_opaque_transparent.inputs[2], mix_matte_glossy.outputs[0])

    x += 300

    # Material output node
    material_output = nodes.new("ShaderNodeOutputMaterial")
    material_output.location = (x, 0)
    links.new(material_output.inputs[0], mix_opaque_transparent.outputs[0])


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
            tpc_image = TpcReader(path).load()
            image = bpy.data.images.new(name, tpc_image.w, tpc_image.h)
            image.pixels = tpc_image.pixels
            image.update()
            return image

    return bpy.data.images.new(name, 512, 512)
