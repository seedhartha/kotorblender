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

from enum import Enum
from struct import unpack

from ..binreader import BinaryReader, SeekOrigin


class TpcEncoding(Enum):
    GRAYSCALE = 1
    RGB = 2
    RGBA = 4


class TpcMip:
    def __init__(self, w, h, pixels):
        self.w = w
        self.h = h
        self.pixels = pixels


class TpcImage:
    def __init__(self, w, h, pixels):
        self.w = w
        self.h = h
        self.pixels = pixels
        self.txi_lines = []


class TpcReader:
    def __init__(self, path):
        self.reader = BinaryReader(path)

    def load(self):
        self.compressed_size = self.reader.read_uint32()
        self.compressed = self.compressed_size > 0
        self.reader.skip(4)
        image_w = self.reader.read_uint16()
        image_h = self.reader.read_uint16()
        self.encoding = TpcEncoding(self.reader.read_uint8())
        self.num_mips = self.reader.read_uint8()
        self.reader.seek(128)

        cubemap = image_h // image_w == 6
        if cubemap:
            sides = []
            for _ in range(0, 6):
                mips = self.read_mips(image_w, image_w)
                top_decomp = self.decompress_mip_if_compressed(mips[0])
                sides.append(top_decomp)
            mip = self.merge_cubemap(image_w, image_h, sides)
        else:
            mips = self.read_mips(image_w, image_h)
            mip = self.decompress_mip_if_compressed(mips[0])
        image = self.mip_to_image(mip)

        current = self.reader.tell()
        self.reader.seek(0, SeekOrigin.END)
        filesize = self.reader.tell()
        if filesize > current:
            self.reader.seek(current)
            image.txi_lines = (
                self.reader.read_bytes(filesize - current).decode("utf-8").splitlines()
            )

        return image

    def read_mips(self, image_w, image_h):
        mips = []
        for mip_level in range(0, self.num_mips):
            mip_w, mip_h = self.mip_size(image_w, image_h, mip_level)
            mip = self.read_mip(mip_w, mip_h, mip_level)
            mips.append(mip)
        return mips

    def mip_size(self, image_w, image_h, level):
        return (max(1, image_w >> level), max(1, image_h >> level))

    def read_mip(self, mip_w, mip_h, level):
        pixels_size = self.mip_pixels_size(level, mip_w, mip_h)
        pixels = self.reader.read_bytes(pixels_size)
        return TpcMip(mip_w, mip_h, pixels)

    def mip_pixels_size(self, mip_level, mip_w, mip_h):
        if self.compressed:
            if mip_level == 0:
                return self.compressed_size
            if self.encoding == TpcEncoding.RGB:
                return max(8, 8 * ((mip_w + 3) // 4) * ((mip_h + 3) // 4))
            if self.encoding == TpcEncoding.RGBA:
                return max(16, 16 * ((mip_w + 3) // 4) * ((mip_h + 3) // 4))
        else:
            if self.encoding == TpcEncoding.GRAYSCALE:
                return mip_w * mip_h
            if self.encoding == TpcEncoding.RGB:
                return 3 * mip_w * mip_h
            if self.encoding == TpcEncoding.RGBA:
                return 4 * mip_w * mip_h
        raise RuntimeError("Unable to calculate size of pixel buffer")

    def merge_cubemap(self, w, h, sides):
        pixels = []
        for side in sides:
            pixels.extend(side.pixels)
        return TpcMip(w, h, pixels)

    def mip_to_image(self, mip):
        if self.encoding == TpcEncoding.GRAYSCALE:
            pixels = []
            for i in range(0, mip.w * mip.h):
                val = mip.pixels[i]
                pixels.append(val / 255)
                pixels.append(val / 255)
                pixels.append(val / 255)
                pixels.append(1.0)
        elif self.encoding == TpcEncoding.RGB:
            pixels = []
            for i in range(0, mip.w * mip.h):
                r, g, b = mip.pixels[(3 * i) : (3 * i + 3)]
                pixels.append(r / 255)
                pixels.append(g / 255)
                pixels.append(b / 255)
                pixels.append(1.0)
        elif self.encoding == TpcEncoding.RGBA:
            pixels = [val / 255 for val in mip.pixels]
        else:
            raise RuntimeError("Unable to convert mip to image")
        return TpcImage(mip.w, mip.h, pixels)

    def decompress_mip_if_compressed(self, mip):
        if not self.compressed:
            return mip
        if self.encoding in [TpcEncoding.RGB, TpcEncoding.RGBA]:
            pixels = self.decompress_mip_dxt15(mip, self.encoding == TpcEncoding.RGBA)
            return TpcMip(mip.w, mip.h, pixels)
        raise RuntimeError("Unable to decompress mip")

    def decompress_mip_dxt15(self, mip, has_alpha):
        num_blocks_x = (mip.w + 3) // 4
        num_blocks_y = (mip.h + 3) // 4
        pixels_idx = 0
        out_pixels_size = mip.w * mip.h * (4 if has_alpha else 3)
        out_pixels = [None] * out_pixels_size
        for block_y in range(0, num_blocks_y):
            for block_x in range(0, num_blocks_x):
                self.decompress_dxt15_block(
                    mip.w,
                    mip.pixels,
                    pixels_idx + (16 if has_alpha else 8) * block_x,
                    has_alpha,
                    4 * block_x,
                    4 * block_y,
                    out_pixels,
                )
            pixels_idx += (16 if has_alpha else 8) * num_blocks_x
        return out_pixels

    def decompress_dxt15_block(
        self, mip_w, pixels, pixels_idx, has_alpha, pixel_x, pixel_y, out_pixels
    ):
        if has_alpha:
            alphas = pixels[pixels_idx : pixels_idx + 2]
            alpha_codes = unpack("<Q", pixels[pixels_idx + 2 : pixels_idx + 10])[0]
            colors = unpack("<HH", pixels[pixels_idx + 8 : pixels_idx + 12])
            color_codes = unpack("<L", pixels[pixels_idx + 12 : pixels_idx + 16])[0]
        else:
            colors = unpack("<HH", pixels[pixels_idx : pixels_idx + 4])
            color_codes = unpack("<L", pixels[pixels_idx + 4 : pixels_idx + 8])[0]
        r = []
        g = []
        b = []
        for i in range(0, 2):
            tmp = (colors[i] >> 11) * 255 + 16
            r.append((tmp // 32 + tmp) // 32)
            tmp = ((colors[i] & 0x07E0) >> 5) * 255 + 32
            g.append((tmp // 64 + tmp) // 64)
            tmp = (colors[i] & 0x001F) * 255 + 16
            b.append((tmp // 32 + tmp) // 32)
        for block_pixel_y in range(0, 4):
            for block_pixel_x in range(0, 4):
                if has_alpha:
                    alpha_code_idx = 3 * (4 * block_pixel_y + block_pixel_x)
                    alpha_code = (alpha_codes >> alpha_code_idx) & 0x07
                    if alpha_code == 0:
                        alpha = alphas[0]
                    elif alpha_code == 1:
                        alpha = alphas[1]
                    elif alphas[0] > alphas[1]:
                        alpha = (
                            (8 - alpha_code) * alphas[0] + (alpha_code - 1) * alphas[1]
                        ) // 7
                    elif alpha_code == 6:
                        alpha = 0
                    elif alpha_code == 7:
                        alpha = 255
                    else:
                        alpha = (
                            (6 - alpha_code) * alphas[0] + (alpha_code - 1) * alphas[1]
                        ) // 5
                else:
                    alpha = 255
                color_code_idx = 2 * (4 * block_pixel_y + block_pixel_x)
                color_code = (color_codes >> color_code_idx) & 0x03
                if has_alpha or colors[0] > colors[1]:
                    if color_code == 0:
                        rgb = (r[0], g[0], b[0])
                    elif color_code == 1:
                        rgb = (r[1], g[1], b[1])
                    elif color_code == 2:
                        rgb = (
                            (2 * r[0] + r[1]) // 3,
                            (2 * g[0] + g[1]) // 3,
                            (2 * b[0] + b[1]) // 3,
                        )
                    elif color_code == 3:
                        rgb = (
                            (r[0] + 2 * r[1]) // 3,
                            (g[0] + 2 * g[1]) // 3,
                            (b[0] + 2 * b[1]) // 3,
                        )
                else:
                    if color_code == 0:
                        rgb = (r[0], g[0], b[0])
                    elif color_code == 1:
                        rgb = (r[1], g[1], b[1])
                    elif color_code == 2:
                        rgb = (
                            (r[0] + r[1]) // 2,
                            (g[0] + g[1]) // 2,
                            (b[0] + b[1]) // 2,
                        )
                    elif color_code == 3:
                        rgb = (0, 0, 0)
                if pixel_x + block_pixel_x < mip_w:
                    out_pixels_idx = (pixel_y + block_pixel_y) * mip_w
                    out_pixels_idx += pixel_x + block_pixel_x
                    out_pixels_idx *= 4 if has_alpha else 3
                    out_pixels[out_pixels_idx + 0] = rgb[0]
                    out_pixels[out_pixels_idx + 1] = rgb[1]
                    out_pixels[out_pixels_idx + 2] = rgb[2]
                    if has_alpha:
                        out_pixels[out_pixels_idx + 3] = alpha
