"""TXI texture properties file support"""
import os
from datetime import datetime

import bpy


# these should probably live in defines sometime,
# and separate lists is not necessarily a great way to do it,
# a hash might be better...
tokens = [
    "proceduretype",
    "filter",
    "filerange",                # not in vanilla corpus
    "defaultwidth",
    "defaultheight",
    "downsamplemax",
    "downsamplemin",
    "mipmap",
    "maptexelstopixels",        # not in vanilla corpus
    "gamma",                    # not in vanilla corpus
    "isbumpmap",
    "blending",
    "clamp",
    "alphamean",
    "isdiffusebumpmap",
    "isspecularbumpmap",
    "bumpmapscaling",
    "specularcolor",
    "islightmap",
    "compresstexture",
    "fps",
    "numx",
    "numy",
    "cube",
    "bumpintensity",
    "temporary",                # not in vanilla corpus
    "useglobalalpha",           # not in vanilla corpus
    "isenvironmentmapped",
    "envmapalpha",
    "diffusebumpintensity",     # not in vanilla corpus
    "specularbumpintensity",    # not in vanilla corpus
    "bumpmaptexture",
    "bumpyshinytexture",
    "envmaptexture",
    "decal",
    "renderbmlmtype",           # not in vanilla corpus
    "wateralpha",
    "arturowidth",
    "arturoheight",
    "forcecyclespeed",          # not in vanilla corpus
    "anglecyclespeed",          # not in vanilla corpus
    "waterwidth",
    "waterheight",
    "channelscale",
    "channeltranslate",
    "distort",
    "distortangle",             # not in vanilla corpus
    "distortionamplitude",
    "speed",
    "channelscale0",
    "channelscale1",
    "channelscale2",
    "channelscale3",
    "channeltranslate0",
    "channeltranslate1",
    "channeltranslate2",
    "channeltranslate3",
    "numchars",
    "fontheight",
    "baselineheight",
    "texturewidth",
    "upperleftcoords",
    "lowerrightcoords",
    "spacingR",
    "spacingB"
]
bool_tokens = [
    "mipmap",
    "maptexelstopixels",
    "isbumpmap",
    "isdiffusebumpmap",
    "isspecularbumpmap",
    "islightmap",
    "compresstexture",
    "cube",
    "temporary",
    "useglobalalpha",
    "isenvironmentmapped",
    "decal",
    "filter",
    "renderbmlmtype",
    "waterwidth",
    "waterheight",
    "distort",
    "distortangle"
]
int_tokens = [
    "filerange",
    "defaultwidth",
    "defaultheight",
    "downsamplemax",
    "downsamplemin",
    "maptexelstopixels",
    "clamp",
    "fps",
    "numx",
    "numy",
    "arturowidth",
    "arturoheight",
    "channelscale",
    "channeltranslate",
    "numchars",
    "upperleftcoords",
    "lowerrightcoords",
]
float_tokens = [
    "gamma",
    "alphamean",
    "bumpmapscaling",
    "bumpintensity",
    "envmapalpha",
    "diffusebumpintensity",
    "specularbumpintensity",
    "specularcolor",
    "wateralpha",
    "forcecyclespeed",
    "distortionamplitude",
    "speed",
    "channelscale0",
    "channelscale1",
    "channelscale2",
    "channelscale3",
    "channeltranslate0",
    "channeltranslate1",
    "channeltranslate2",
    "channeltranslate3",
    "fontheight",
    "baselineheight",
    "texturewidth",
    "spacingR",
    "spacingB"
]


def load_txi(imagetexture, operator=None):
    try:
        filepath = imagetexture.image.filepath
    except:
        return False
    filepath = os.path.splitext(filepath)[0]
    if os.path.exists(filepath + ".txi"):
        filepath = filepath + ".txi"
    elif os.path.exists(filepath + ".TXI"):
        filepath = filepath + ".TXI"
    else:
        return False

    fp = os.fsencode(filepath)
    asciiLines = [line.strip().split() for line in open(fp, "r")]

    for line_idx, line in enumerate(asciiLines):
        try:
            if line[0] in tokens:
                value = line[1]
                # special types
                if line[0] == "specularcolor":
                    value = (line[1], line[2], line[3])
                elif line[0] == "channelscale":
                    for scale_counter in range(0,int(line[1])):
                        setattr(imagetexture.kb,
                                "channelscale" + str(scale_counter),
                                asciiLines[line_idx + 1 + scale_counter][0])
                elif line[0] == "channeltranslate":
                    for scale_counter in range(0,int(line[1])):
                        setattr(imagetexture.kb,
                                "channeltranslate" + str(scale_counter),
                                asciiLines[line_idx + 1 + scale_counter][0])
                # the generalized types
                elif line[0] in bool_tokens:
                    if value == "TRUE" or value == "true" or int(value) >= 1:
                        value = True
                    else:
                        value = False
                elif line[0] in int_tokens:
                    value = int(value)
                elif line[0] in float_tokens:
                    value = float(value)
                setattr(imagetexture.kb, line[0], value)
        except:
            pass
    
    if operator is not None:
        operator.report({'INFO'}, "Imported {}".format(os.path.basename(filepath)))

    return True


def save_txi(imagetexture, operator=None):
    try:
        if imagetexture.image.filepath.startswith("//") and \
           not bpy.context.blend_data.is_saved:
            if operator is not None:
                operator.report(
                    {'WARNING'},
                    "Save blend file to export TXI with relative image path"
                )
            return False
        # use of abspath for windows compatibility
        filepath = bpy.path.abspath(imagetexture.image.filepath)
    except:
        return False
    filepath = os.path.splitext(filepath)[0] + ".new.txi"

    if len(imagetexture.kb.modified_properties) < 1:
        # do not write empty files
        return False

    exported = {}
    export_names = []

    asciiLines = []
    asciiLines.append("# Exported from blender " + datetime.now().strftime("%A, %Y-%m-%d"))
    # filter modified to unique, reduce channel{scale,translate}
    for _, propname in enumerate(imagetexture.kb.modified_properties):
        propname = propname.name
        if propname == "channelscale" or \
           propname == "channelscale0" or \
           propname == "channelscale1" or \
           propname == "channelscale2" or \
           propname == "channelscale3":
            if "channelscale" in exported:
                continue
            export_names.append("channelscale")
        elif propname == "channeltranslate" or \
           propname == "channeltranslate0" or \
           propname == "channeltranslate1" or \
           propname == "channeltranslate2" or \
           propname == "channeltranslate3":
            if "channeltranslate" in exported:
                continue
            export_names.append("channeltranslate")
        else:
            export_names.append(propname)
            exported[propname] = True
    # construct ascii output lines
    for propname in export_names:
        if propname == "channelscale":
            asciiLines.extend([
                "channelscale 4",
                str(imagetexture.kb.channelscale0),
                str(imagetexture.kb.channelscale1),
                str(imagetexture.kb.channelscale2),
                str(imagetexture.kb.channelscale3),
                ""
            ])
            continue
        if propname == "channeltranslate":
            asciiLines.extend([
                "channeltranslate 4",
                str(imagetexture.kb.channeltranslate0),
                str(imagetexture.kb.channeltranslate1),
                str(imagetexture.kb.channeltranslate2),
                str(imagetexture.kb.channeltranslate3),
                ""
            ])
            continue
        value = getattr(imagetexture.kb, propname)
        if propname == "specularcolor":
            value = tuple(propname)
            value = "{} {} {}".format(*value)
        if isinstance(value, bool):
            value = 1 if value else 0
        asciiLines.append("{} {}".format(propname, str(value)))

    # write txi file, join on CRLF for the windows people
    with open(os.fsencode(filepath), "w") as f:
        f.write("\r\n".join(asciiLines) + "\r\n")

    if operator is not None:
        operator.report({'INFO'}, "Exported {}".format(os.path.basename(filepath)))

    return True
