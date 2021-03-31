"""
Material management, including composing and traversing of shader node trees.
"""

import bpy

from . import nvb_glob, nvb_teximage, nvb_utils


def _get_material_name(node):
    """
    Get material name of the model node.
    """
    # Diffuse texture or diffuse color
    if not nvb_utils.isNull(node.bitmap):
        result = "D" + node.bitmap
    else:
        result = "D" + nvb_utils.colorToHex(node.diffuse)

    # Alpha
    result += "__A" + nvb_utils.intToHex(nvb_utils.floatToByte(node.alpha))

    return result


def load_material(node, name):
    """
    Get or create a material.
    """
    # If material reuse is enabled, search for existing material
    if nvb_glob.materialMode == 'SIN' and node.lightmapped == 0:
        material_name = _get_material_name(node)
        if material_name in bpy.data.materials:
            material = bpy.data.materials[material_name]
            if material:
                return material
    else:
        material_name = name

    material = bpy.data.materials.new(material_name)
    rebuild_material(material, node)

    return material


def rebuild_material(material, node):
    if (not nvb_utils.isNull(node.bitmap)) or (not nvb_utils.isNull(node.bitmap2)):
        material.use_nodes = True
        links = material.node_tree.links
        links.clear()
        nodes = material.node_tree.nodes
        nodes.clear()

        mul_alpha = nodes.new('ShaderNodeMath')
        mul_alpha.location = (600, -300)
        mul_alpha.operation = 'MULTIPLY'
        mul_alpha.inputs[0].default_value = 1.0
        mul_alpha.inputs[1].default_value = node.alpha

        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (900, 0)

        links.new(bsdf.inputs['Alpha'], mul_alpha.outputs[0])

        output = nodes.new('ShaderNodeOutputMaterial')
        output.location = (1200, 0)

        links.new(output.inputs[0], bsdf.outputs[0])

        mul_diffuse_by_lightmap = nodes.new('ShaderNodeVectorMath')
        mul_diffuse_by_lightmap.location = (600, 0)
        mul_diffuse_by_lightmap.operation = 'MULTIPLY'
        mul_diffuse_by_lightmap.inputs[0].default_value = [1.0] * 3
        mul_diffuse_by_lightmap.inputs[1].default_value = [1.0] * 3

        links.new(bsdf.inputs['Base Color'], mul_diffuse_by_lightmap.outputs[0])

        # Diffuse texture
        if not nvb_utils.isNull(node.bitmap):
            diffuse = nodes.new('ShaderNodeTexImage')
            diffuse.location = (300, 0)
            diffuse.image = nvb_teximage.load_texture_image(node.bitmap)
            links.new(mul_diffuse_by_lightmap.inputs[0], diffuse.outputs[0])
            links.new(mul_alpha.inputs[0], diffuse.outputs[1])

        # Lightmap texture
        if not nvb_utils.isNull(node.bitmap2):
            material.shadow_method = 'NONE'

            lightmap_uv = nodes.new('ShaderNodeUVMap')
            lightmap_uv.location = (0, -300)
            lightmap_uv.uv_map = 'UVMap_lm'

            lightmap = nodes.new('ShaderNodeTexImage')
            lightmap.location = (300, -300)
            lightmap.image = nvb_teximage.load_image(node.bitmap2)

            links.new(lightmap.inputs[0], lightmap_uv.outputs[0])
            links.new(mul_diffuse_by_lightmap.inputs[1], lightmap.outputs[0])
    else:
        material.use_nodes = False
        material.diffuse_color = [*node.diffuse, 1.0]
