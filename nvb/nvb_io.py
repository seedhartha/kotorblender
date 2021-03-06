import os
import re

import bpy

from . import nvb_def, nvb_glob, nvb_mdl, nvb_utils


def _load_mdl(filepath, position = (0.0, 0.0, 0.0)):
    collection = bpy.context.collection

    # Try to load walkmeshes ... pwk (placeable) and dwk (door)
    # If the files are and the option is activated we'll import them
    wkm = None
    if nvb_glob.importWalkmesh:
        filetypes = ["pwk", "dwk", "wok"]
        (wkmPath, wkmFilename) = os.path.split(filepath)
        using_extra_extension = False
        if wkmFilename.endswith(".ascii"):
            wkmFilename = os.path.splitext(wkmFilename)[0]
            using_extra_extension = True
        for wkmType in filetypes:
            wkmFilepath = os.path.join(wkmPath,
                                       os.path.splitext(wkmFilename)[0] +
                                       "." + wkmType)
            fp = os.fsencode(wkmFilepath)
            if using_extra_extension or not os.path.isfile(fp):
                fp = os.fsencode(wkmFilepath + ".ascii")
            try:
                asciiLines = [line.strip().split() for line in open(fp, "r")]
                wkm = nvb_mdl.Xwk(wkmType)
                wkm.load_ascii(asciiLines)
            except IOError:
                print(
                    "KotorBlender: WARNING - no walkmesh found {}".format(
                        fp
                    )
                )
            except:
                print(
                    "KotorBlender: WARNING - invalid walkmesh found {}".format(
                        fp
                    )
                )

    # read the ascii mdl text
    fp = os.fsencode(filepath)
    ascii_mdl = ""
    f = open(fp, "r")
    ascii_mdl = f.read()
    f.close()

    # strip any comments from the text immediately,
    # newer method of text processing is not robust against comments
    ascii_mdl = re.sub(r'#.+$', "", ascii_mdl, flags=re.MULTILINE)

    # prepare the old style data
    asciiLines = [line.strip().split() for line in ascii_mdl.splitlines()]

    print("Importing: " + filepath)
    mdl = nvb_mdl.Mdl()
    mdl.load_ascii(ascii_mdl)
    mdl.import_to_collection(collection, wkm, position)

    # processing to use AABB node as trimesh for walkmesh file
    if wkm is not None and wkm.walkmeshType == "wok" and mdl.nodeDict and wkm.nodeDict:
        aabb = None
        wkmesh = None
        # find aabb node in model
        for (_, node) in mdl.nodeDict.items():
            if node.nodetype == "aabb":
                aabb = node
        # find mesh node in wkm
        for (_, node) in wkm.nodeDict.items():
            if node.nodetype == "aabb" or node.nodetype == "trimesh":
                wkmesh = node
        if aabb and wkmesh:
            aabb.compute_layout_position(wkmesh)
            if len(wkmesh.roomlinks):
                aabb.roomlinks = wkmesh.roomlinks
                aabb.set_room_links(collection.objects[aabb.name].data)


def load_mdl(operator,
            context,
            filepath = "",
            importGeometry = True,
            importWalkmesh = True,
            importSmoothGroups = True,
            importMaterials = True,
            importAnim = True,
            textureSearch = False,
            createArmature = False,
            minimapMode = False,
            minimapSkipFade = False):
    """
    Called from blender ui
    """
    nvb_glob.importGeometry = importGeometry
    nvb_glob.importWalkmesh = importWalkmesh
    nvb_glob.importSmoothGroups = importSmoothGroups
    nvb_glob.importMaterials = importMaterials
    nvb_glob.importAnim = importAnim
    nvb_glob.texturePath = os.path.dirname(filepath)
    nvb_glob.textureSearch = textureSearch
    nvb_glob.createArmature = createArmature
    nvb_glob.minimapMode = minimapMode
    nvb_glob.minimapSkipFade = minimapSkipFade

    _load_mdl(filepath)

    return {'FINISHED'}


def _load_lyt(filepath):
    # Read lines from LYT
    fp = os.fsencode(filepath)
    f = open(fp, "r")
    lines = [line.strip() for line in f.read().splitlines()]
    f.close()

    rooms = []
    rooms_to_read = 0

    for line in lines:
        tokens = line.split()
        if rooms_to_read > 0:
            room_name = tokens[0].lower()
            x = float(tokens[1])
            y = float(tokens[2])
            z = float(tokens[3])
            rooms.append((room_name, x, y, z))
            rooms_to_read -= 1
            if rooms_to_read == 0:
                break
        elif tokens[0].startswith("roomcount"):
            rooms_to_read = int(tokens[1])

    (path, _) = os.path.split(filepath)

    for room in rooms:
        # MDLedit appends .ascii extension to decompiled models - try that first
        mdl_path = os.path.join(path, room[0] + ".mdl.ascii")
        if not os.path.exists(mdl_path):
            mdl_path = os.path.join(path, room[0] + "-ascii.mdl")
        if os.path.exists(mdl_path):
            _load_mdl(mdl_path, room[1:])
        else:
            print("KotorBlender: WARNING - room model not found: " + mdl_path)


def load_lyt(operator,
            context,
            filepath = "",
            importGeometry = True,
            importWalkmesh = True,
            importSmoothGroups = True,
            importMaterials = True,
            importAnim = True,
            textureSearch = False):
    """
    Called from blender ui
    """
    nvb_glob.importGeometry = importGeometry
    nvb_glob.importWalkmesh = importWalkmesh
    nvb_glob.importSmoothGroups = importSmoothGroups
    nvb_glob.importMaterials = importMaterials
    nvb_glob.importAnim = importAnim
    nvb_glob.texturePath = os.path.dirname(filepath)
    nvb_glob.textureSearch = textureSearch

    _load_lyt(filepath)

    return {'FINISHED'}


def save_mdl(operator,
         context,
         filepath = "",
         exports = {"ANIMATION", "WALKMESH"},
         exportSmoothGroups = True,
         applyModifiers = True,
         ):
    """
    Called from blender ui
    """
    nvb_glob.exports            = exports
    nvb_glob.exportSmoothGroups = exportSmoothGroups
    nvb_glob.applyModifiers     = applyModifiers
    # temporary forced options:
    frame_set_zero              = True

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    # Set frame to zero, if specified in options
    frame_set_current = None
    if frame_set_zero and bpy.context.scene:
        frame_set_current = bpy.context.scene.frame_current
        bpy.context.scene.frame_set(0)

    mdlRoot = nvb_utils.get_mdl_root_from_context()
    if mdlRoot:
        print("KotorBlender: Exporting " + mdlRoot.name)
        mdl = nvb_mdl.Mdl()
        asciiLines = []
        mdl.generate_ascii(asciiLines, mdlRoot)
        with open(os.fsencode(filepath), "w") as f:
            f.write("\n".join(asciiLines))

        if "WALKMESH" in exports:
            wkmRoot = None
            aabb = nvb_utils.search_node(mdlRoot, lambda x: x.nvb.meshtype == nvb_def.Meshtype.AABB)
            if aabb is not None:
                wkm     = nvb_mdl.Wok()
                wkmRoot = aabb
                wkmType = "wok"
            else:
                # We need to look for a walkmesh rootdummy
                wkmRootName = mdl.name + "_pwk"
                if (wkmRootName in bpy.data.objects):
                    wkmRoot = bpy.data.objects[wkmRootName]
                    wkm     = nvb_mdl.Xwk("pwk")
                wkmRootName = mdl.name + "_PWK"
                if (not wkmRoot) and (wkmRootName in bpy.data.objects):
                    wkmRoot = bpy.data.objects[wkmRootName]
                    wkm     = nvb_mdl.Xwk("pwk")

                wkmRootName = mdl.name + "_dwk"
                if (not wkmRoot) and (wkmRootName in bpy.data.objects):
                    wkmRoot = bpy.data.objects[wkmRootName]
                    wkm     = nvb_mdl.Xwk("dwk")
                wkmRootName = mdl.name + "_DWK"
                if (not wkmRoot) and (wkmRootName in bpy.data.objects):
                    wkmRoot = bpy.data.objects[wkmRootName]
                    wkm     = nvb_mdl.Xwk("dwk")

            if wkmRoot:
                asciiLines = []
                wkm.generate_ascii(asciiLines, wkmRoot)

                (wkmPath, wkmFilename) = os.path.split(filepath)
                wkmType = wkm.walkmeshType
                if wkmFilename.endswith(".ascii"):
                    wkmFilename = os.path.splitext(wkmFilename)[0]
                    wkmType += ".ascii"
                wkmFilepath = os.path.join(wkmPath, os.path.splitext(wkmFilename)[0] + "." + wkmType)
                with open(os.fsencode(wkmFilepath), "w") as f:
                    f.write("\n".join(asciiLines))

    # Return frame to pre-export, if specified in options
    if frame_set_current is not None and bpy.context.scene:
        bpy.context.scene.frame_set(frame_set_current)

    return {'FINISHED'}
