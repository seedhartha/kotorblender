"""
Functions related to material building.
"""

import bpy

from . import nvb_glob, nvb_teximage, nvb_utils


def _get_material_name(obj):
    if nvb_utils.is_null(obj.nvb.bitmap) and nvb_utils.is_null(obj.nvb.bitmap2):
        diffuse = nvb_utils.color_to_hex(obj.nvb.diffuse)
        alpha = nvb_utils.int_to_hex(nvb_utils.float_to_byte(obj.nvb.alpha))
        name = "D{}__A{}".format(diffuse, alpha)
    else:
        name = obj.name
    return name


def _get_or_create_material(obj):
    name = _get_material_name(obj)
    if name in bpy.data.materials:
        material = bpy.data.materials[name]
    else:
        material = bpy.data.materials.new(name)
    return material


def _rebuild_material_simple(material, obj):
    material.use_nodes = False
    material.diffuse_color = [*obj.nvb.diffuse, 1.0]


def _rebuild_material_nodes(material, obj):
    material.use_nodes = True
    links = material.node_tree.links
    links.clear()
    nodes = material.node_tree.nodes
    nodes.clear()

    # Output node
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (1200, 0)

    # Shader node
    selfillumed = not nvb_utils.isclose_3f(obj.nvb.selfillumcolor, [0.0] * 3)
    if selfillumed:
        shader = nodes.new("ShaderNodeEmission")
    else:
        shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.location = (900, 0)

    # Multiply diffuse by lightmap node
    mul_diffuse_by_lightmap = nodes.new("ShaderNodeVectorMath")
    mul_diffuse_by_lightmap.location = (600, 0)
    mul_diffuse_by_lightmap.operation = 'MULTIPLY'
    mul_diffuse_by_lightmap.inputs[0].default_value = [1.0] * 3
    mul_diffuse_by_lightmap.inputs[1].default_value = [1.0] * 3

    # Alpha node
    mul_alpha = nodes.new("ShaderNodeMath")
    mul_alpha.location = (600, -300)
    mul_alpha.operation = 'MULTIPLY'
    mul_alpha.inputs[0].default_value = 1.0
    mul_alpha.inputs[1].default_value = obj.nvb.alpha

    # Diffuse map node
    if not nvb_utils.is_null(obj.nvb.bitmap):
        diffuse = nodes.new("ShaderNodeTexImage")
        diffuse.location = (300, 0)
        diffuse.image = nvb_teximage.load_texture_image(obj.nvb.bitmap)
        links.new(mul_diffuse_by_lightmap.inputs[0], diffuse.outputs[0])
        links.new(mul_alpha.inputs[0], diffuse.outputs[1])

    # Lightmap node
    if not nvb_utils.is_null(obj.nvb.bitmap2):
        lightmap_uv = nodes.new("ShaderNodeUVMap")
        lightmap_uv.location = (0, -300)
        lightmap_uv.uv_map = "UVMap_lm"

        lightmap = nodes.new("ShaderNodeTexImage")
        lightmap.location = (300, -300)
        lightmap.image = nvb_teximage.load_texture_image(obj.nvb.bitmap2)

        material.shadow_method = 'NONE'
        links.new(lightmap.inputs[0], lightmap_uv.outputs[0])
        links.new(mul_diffuse_by_lightmap.inputs[1], lightmap.outputs[0])

    if selfillumed:
        links.new(shader.inputs["Color"], mul_diffuse_by_lightmap.outputs[0])
    else:
        links.new(shader.inputs["Base Color"], mul_diffuse_by_lightmap.outputs[0])
        links.new(shader.inputs["Alpha"], mul_alpha.outputs[0])

    links.new(output.inputs[0], shader.outputs[0])


def rebuild_material(obj):
    """
    :param obj: object for which to rebuild the material
    """
    material = _get_or_create_material(obj)

    mesh = obj.data
    mesh.materials.clear()
    mesh.materials.append(material)

    # Only use nodes when object has at least one texture
    if (not nvb_utils.is_null(obj.nvb.bitmap)) or (not nvb_utils.is_null(obj.nvb.bitmap2)):
        _rebuild_material_nodes(material, obj)
    else:
        _rebuild_material_simple(material, obj)
