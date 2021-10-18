"""
Image/texture helper functions.
"""

import bpy

from bpy_extras import image_utils

from .format import txi as txiformat

from . import kb_glob


def _create_image(name, path):
    image = image_utils.load_image(
        name + ".tga",
        path,
        recursive=kb_glob.textureSearch,
        place_holder=False,
        ncase_cmp=True)

    if image is None:
        print("KotorBlender: WARNING - could not load image '{}' from '{}'".format(name, path))
        image = bpy.data.images.new(name, 512, 512)
    else:
        image.name = name

    return image


def load_texture_image(name):
    """
    Get or create a texture data-block by name.

    :returns: textures image
    """
    if name in bpy.data.textures:
        texture = bpy.data.textures[name]
    else:
        if name in bpy.data.images:
            image = bpy.data.images[name]
        else:
            image = _create_image(name, kb_glob.texturePath)

        texture = bpy.data.textures.new(name, type='IMAGE')
        texture.image = image
        texture.use_fake_user = True
        txiformat.load_txi(texture)

    return texture.image
