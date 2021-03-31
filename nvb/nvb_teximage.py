"""
Image/texture helper functions.
"""

import bpy
import bpy_extras

from . import nvb_glob, nvb_txi


def _create_image(name, path):
    image = bpy_extras.image_utils.load_image(
        name + '.tga',
        path,
        recursive=nvb_glob.textureSearch,
        place_holder=False,
        ncase_cmp=True)

    if image is None:
        print("Kotorblender - WARNING: Could not load image '{}' from '{}'".format(name, path))
        image = bpy.data.images.new(name, 512, 512)
    else:
        image.name = name

    return image


def load_image(name):
    """
    Get or create an image data-block by name.
    """
    if name in bpy.data.images:
        return bpy.data.images[name]
    else:
        return _create_image(name, nvb_glob.texturePath)


def load_texture_image(name):
    """
    Get or create a texture data-block by name.

    :returns: textures image
    """
    if name in bpy.data.textures:
        texture = bpy.data.textures[name]
    else:
        texture = bpy.data.textures.new(name, type='IMAGE')
        texture.image = _create_image(name, nvb_glob.texturePath)
        texture.use_fake_user = True
        nvb_txi.loadTxi(texture)

    return texture.image

def get_texture_by_image(image):
    for tex in bpy.data.textures:
        if tex.type == 'IMAGE' and tex.image == image:
            return tex

    return None