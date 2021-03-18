"""TODO: DOC."""

import os
import re
import bpy

from . import nvb_glob
from . import nvb_def
from . import nvb_mdl
from . import nvb_utils


def _load_mdl(filepath, importWalkmesh, position = (0.0, 0.0, 0.0)):
    scene = bpy.context.scene

    # Try to load walkmeshes ... pwk (placeable) and dwk (door)
    # If the files are and the option is activated we'll import them
    wkm = None
    if importWalkmesh:
        filetypes = ['pwk', 'dwk', 'wok']
        (wkmPath, wkmFilename) = os.path.split(filepath)
        using_extra_extension = False
        if wkmFilename.endswith('.ascii'):
            wkmFilename = os.path.splitext(wkmFilename)[0]
            using_extra_extension = True
        for wkmType in filetypes:
            wkmFilepath = os.path.join(wkmPath,
                                       os.path.splitext(wkmFilename)[0] +
                                       '.' + wkmType)
            fp = os.fsencode(wkmFilepath)
            if using_extra_extension or not os.path.isfile(fp):
                fp = os.fsencode(wkmFilepath + '.ascii')
            try:
                asciiLines = [line.strip().split() for line in open(fp, 'r')]
                wkm = nvb_mdl.Xwk(wkmType)
                wkm.loadAscii(asciiLines)
                # adding walkmesh to scene has to be done within mdl import now
                #wkm.importToScene(scene)
            except IOError:
                print(
                    "Kotorblender - WARNING: No walkmesh found {}".format(
                        fp
                    )
                )
            except:
                print(
                    "Kotorblender - WARNING: Invalid walkmesh found {}".format(
                        fp
                    )
                )

    # read the ascii mdl text
    fp = os.fsencode(filepath)
    ascii_mdl = ''
    f = open(fp, 'r')
    ascii_mdl = f.read()
    f.close()

    # strip any comments from the text immediately,
    # newer method of text processing is not robust against comments
    ascii_mdl = re.sub(r'#.+$', '', ascii_mdl, flags=re.MULTILINE)

    # prepare the old style data
    asciiLines = [line.strip().split() for line in ascii_mdl.splitlines()]

    print('Importing: ' + filepath)
    mdl = nvb_mdl.Mdl()
    #mdl.loadAscii(asciiLines)
    mdl.loadAscii(ascii_mdl)
    mdl.importToScene(scene, wkm, position)

    # processing to use AABB node as trimesh for walkmesh file
    if wkm is not None and wkm.walkmeshType == 'wok' and mdl.nodeDict and wkm.nodeDict:
        aabb = None
        wkmesh = None
        # find aabb node in model
        for (nodeKey, node) in mdl.nodeDict.items():
            if node.nodetype == 'aabb':
                aabb = node
        # find mesh node in wkm
        for (nodeKey, node) in wkm.nodeDict.items():
            if node.nodetype == 'aabb' or node.nodetype == 'trimesh':
                wkmesh = node
        if aabb and wkmesh:
            #print(aabb.lytposition)
            aabb.computeLayoutPosition(wkmesh)
            #print(aabb.lytposition)
            if len(wkmesh.roomlinks):
                aabb.roomlinks = wkmesh.roomlinks
                aabb.setRoomLinks(scene.objects[aabb.name].data)


def _load_lyt(filepath, importWalkmesh):
    # Read lines from LYT
    fp = os.fsencode(filepath)
    f = open(fp, 'r')
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
        elif tokens[0].startswith('roomcount'):
            rooms_to_read = int(tokens[1])

    (path, _) = os.path.split(filepath)

    for room in rooms:
        # MDLedit appends .ascii extension to decompiled models - try that first
        mdl_path = os.path.join(path, room[0] + '.mdl.ascii')
        if not os.path.exists(mdl_path):
            mdl_path = os.path.join(path, room[0] + '-ascii.mdl')
        if os.path.exists(mdl_path):
            _load_mdl(mdl_path, importWalkmesh, room[1:])
        else:
            print('Kotorblender - WARNING: room model not found: ' + mdl_path)


def loadMdl(operator,
            context,
            filepath = '',
            importGeometry = True,
            importWalkmesh = True,
            importSmoothGroups = True,
            importAnim = True,
            materialMode = 'SIN',
            textureSearch = False,
            minimapMode = False,
            minimapSkipFade = False):
    '''
    Called from blender ui
    '''
    nvb_glob.importGeometry     = importGeometry
    nvb_glob.importSmoothGroups = importSmoothGroups
    nvb_glob.importAnim         = importAnim


    nvb_glob.materialMode = materialMode

    nvb_glob.texturePath   = os.path.dirname(filepath)
    nvb_glob.textureSearch = textureSearch

    nvb_glob.minimapMode     = minimapMode
    nvb_glob.minimapSkipFade = minimapSkipFade

    # Load LYT or MDL depending of file extension
    (_, filename) = os.path.split(filepath)
    if filename.endswith('.lyt'):
        _load_lyt(filepath, importWalkmesh)
    else:
        _load_mdl(filepath, importWalkmesh)

    return {'FINISHED'}


def saveMdl(operator,
         context,
         filepath = '',
         exports = {'ANIMATION', 'WALKMESH'},
         exportSmoothGroups = True,
         exportTxi = True,
         applyModifiers = True,
         ):
    '''
    Called from blender ui
    '''
    nvb_glob.exports            = exports
    nvb_glob.exportSmoothGroups = exportSmoothGroups
    nvb_glob.exportTxi          = exportTxi
    nvb_glob.applyModifiers     = applyModifiers
    # temporary forced options:
    frame_set_zero              = True

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    # reset exported status to false because save operation about to begin
    if exportTxi:
        for texture in bpy.data.textures:
            try:
                if texture.type == 'IMAGE' and texture.image:
                    texture.nvb.exported_in_save = False
            except:
                pass

    # Set frame to zero, if specified in options
    frame_set_current = None
    if frame_set_zero and bpy.context.scene:
        frame_set_current = bpy.context.scene.frame_current
        # this technique does not work, docs say use frame_set
        #options.scene.frame_current = 0
        #bpy.context.scene.update()
        bpy.context.scene.frame_set(0)
        #print('frame set to 0 for export')

    mdlRoot = nvb_utils.get_mdl_base(scene=bpy.context.scene)
    if mdlRoot:
        print('Kotorblender: Exporting ' + mdlRoot.name)
        mdl = nvb_mdl.Mdl()
        asciiLines = []
        mdl.generateAscii(asciiLines, mdlRoot)
        with open(os.fsencode(filepath), 'w') as f:
            f.write('\n'.join(asciiLines))

        if 'WALKMESH' in exports:
            wkmRoot = None
            aabb = nvb_utils.searchNode(mdlRoot, lambda x: x.nvb.meshtype == nvb_def.Meshtype.AABB)
            if aabb is not None:
                wkm     = nvb_mdl.Wok()
                wkmRoot = aabb
                wkmType = 'wok'
            else:
                # We need to look for a walkmesh rootdummy
                wkmRootName = mdl.name + '_pwk'
                if (wkmRootName in bpy.data.objects):
                    wkmRoot = bpy.data.objects[wkmRootName]
                    wkm     = nvb_mdl.Xwk('pwk')
                wkmRootName = mdl.name + '_PWK'
                if (not wkmRoot) and (wkmRootName in bpy.data.objects):
                    wkmRoot = bpy.data.objects[wkmRootName]
                    wkm     = nvb_mdl.Xwk('pwk')

                wkmRootName = mdl.name + '_dwk'
                if (not wkmRoot) and (wkmRootName in bpy.data.objects):
                    wkmRoot = bpy.data.objects[wkmRootName]
                    wkm     = nvb_mdl.Xwk('dwk')
                wkmRootName = mdl.name + '_DWK'
                if (not wkmRoot) and (wkmRootName in bpy.data.objects):
                    wkmRoot = bpy.data.objects[wkmRootName]
                    wkm     = nvb_mdl.Xwk('dwk')

            if wkmRoot:
                asciiLines = []
                wkm.generateAscii(asciiLines, wkmRoot)

                (wkmPath, wkmFilename) = os.path.split(filepath)
                wkmType = wkm.walkmeshType
                if wkmFilename.endswith('.ascii'):
                    wkmFilename = os.path.splitext(wkmFilename)[0]
                    wkmType += '.ascii'
                wkmFilepath = os.path.join(wkmPath, os.path.splitext(wkmFilename)[0] + '.' + wkmType)
                with open(os.fsencode(wkmFilepath), 'w') as f:
                    f.write('\n'.join(asciiLines))
        # reset exported status to false because save operation is concluding
        if exportTxi:
            for texture in bpy.data.textures:
                try:
                    if texture.type == 'IMAGE' and texture.image:
                        texture.nvb.exported_in_save = False
                except:
                    pass

    # Return frame to pre-export, if specified in options
    if frame_set_current is not None and bpy.context.scene:
        #print('current frame restored to {}'.format(frame_set_current))
        bpy.context.scene.frame_set(frame_set_current)

    return {'FINISHED'}
