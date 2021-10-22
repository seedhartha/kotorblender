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

def _i(asciiBlock, intList, numVals, initialFloat=True):
    """Parse a float and integers into a numVals tuple into intList"""
    l_float = float
    l_int = int
    for line in asciiBlock:
        vals = []
        for idx in range(0, numVals):
            if numVals < 2 or idx > 0 or not initialFloat:
                try:
                    vals.append(l_int(line[idx]))
                except ValueError:
                    vals.append(l_int(l_float(line[idx])))
            else:
                vals.append(l_float(line[idx]))
        if len(vals) > 1:
            intList.append(tuple(vals))
        else:
            intList.append(vals[0])


def _f(asciiBlock, floatList, numVals):
    """Parse floats into a numVals tuple into floatList"""
    l_float = float
    for line in asciiBlock:
        vals = []
        for idx in range(0, numVals):
            vals.append(l_float(line[idx]))
        if len(vals) > 1:
            floatList.append(tuple(vals))
        else:
            floatList.append(vals[0])


def f1(asciiBlock, floatList):
    """Parse a series on floats into a list."""
    _f(asciiBlock, floatList, 1)


def f2(asciiBlock, floatList):
    """Parse a series on float tuples into a list."""
    _f(asciiBlock, floatList, 2)


def f3(asciiBlock, floatList):
    """Parse a series on float 3-tuples into a list."""
    _f(asciiBlock, floatList, 3)


def f4(asciiBlock, floatList):
    """Parse a series on float 4-tuples into a list."""
    _f(asciiBlock, floatList, 4)


def f5(asciiBlock, floatList):
    """Parse a series on float 5-tuples into a list."""
    _f(asciiBlock, floatList, 5)


def i2(asciiBlock, intList):
    l_int = int
    for line in asciiBlock:
        intList.append((l_int(line[0]), l_int(line[1])))


def i3(asciiBlock, intList, initialFloat=True):
    _i(asciiBlock, intList, 3, initialFloat)


def txt(asciiBlock, txtBlock):
    # txtBlock = ['\n'+' '.join(l) for l in aciiBlock]
    for line in asciiBlock:
        txtBlock = txtBlock + "\n" + " ".join(line)
