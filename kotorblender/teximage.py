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

"""
Image/texture helper functions.
"""

import bpy

from bpy_extras import image_utils

from .format import txi as txiformat

from . import glob


def _create_image(name, path):
    image = image_utils.load_image(
        name + ".tga",
        path,
        recursive=glob.textureSearch,
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
            image = _create_image(name, glob.texturePath)

        texture = bpy.data.textures.new(name, type='IMAGE')
        texture.image = image
        texture.use_fake_user = True
        txiformat.load_txi(texture)

    return texture.image
