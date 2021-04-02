"""TODO: DOC."""

import collections
import bpy

from . import nvb_def
from . import nvb_utils
from . import nvb_animnode


class Animation():
    """TODO: DOC."""

    def __init__(self, name = 'UNNAMED', ascii_data=None):
        self.name      = name
        self.length    = 1.0
        self.transtime = 1.0
        self.root      = nvb_def.null
        self.eventList = []
        self.nodeList  = collections.OrderedDict()

        self.nodes = []
        self.events = []

        if ascii_data:
            self.loadAscii(ascii_data)


    @staticmethod
    def createRestPose(obj, frame=1):
        """TODO: DOC."""
        nvb_animnode.Animnode.create_restpose(obj, frame)


    def create(self, mdl_base, options={}):
        """Create animations with a list of imported objects."""
        # Check for existing animations:
        #if options.anim_ignore_existing and \
        #        self.name in mdl_base.nvb.animList.keys():
        #    return
        # Add new animation to list
        #fps = options.scene.render.fps
        fps = nvb_def.fps
        new_anim = nvb_utils.create_anim_list_item(mdl_base)
        new_anim.name = self.name
        # new_anim.ttime = self.transtime
        new_anim.transtime = fps * self.transtime
        # new_anim.root = self.animroot
        #new_anim.root_obj = noderesolver.get_obj(self.animroot, -1)
        search_result = nvb_utils.searchNode(
            mdl_base,
            lambda o, name=self.animroot: o.name.lower() == name.lower()
        )
        if not search_result:
            search_result = mdl_base
            print("retargeted animation from {} to {}".format(
                self.animroot, mdl_base.name
            ))
        new_anim.root = new_anim.root_obj = search_result.name
        new_anim.frameEnd = nvb_utils.nwtime2frame(self.length) + new_anim.frameStart
        # events
        for ev_time, ev_name in self.events:
            newEvent = new_anim.eventList.add()
            newEvent.name = ev_name
            newEvent.frame = nvb_utils.nwtime2frame(ev_time) + new_anim.frameStart
        # Load the animation into the objects/actions
        for node in self.nodes:
            obj = nvb_utils.searchNode(
                mdl_base,
                lambda o, name=node.name: o.name.lower() == name.lower()
            )
            #obj = noderesolver.get_obj(node.name, node.nodeidx)
            if obj:
                node.create(obj, new_anim, self.length, {"mdlname":mdl_base.name})
                if options.get("anim_restpose"):
                    Animation.createRestPose(obj, new_anim.frameStart-5)


    def getAnimNode(self, nodeName, parentName = nvb_def.null):
        key = parentName + nodeName
        if key in self.nodeList:
            return self.nodeList[key]
        else:
            return None

    def addAsciiNode(self, asciiBlock):
        node = nvb_animnode.Node()
        node.loadAscii(asciiBlock)
        key  = node.parentName + node.name
        if key in self.nodeList:
            #TODO: Should probably raise an exception
            pass
        else:
            self.nodeList[key] = node

    def addEvent(self, event):
        self.eventList.append(event)


    def addEventsToObject(self, rootDummy):
        for event in self.eventList:
            newItem = rootDummy.nvb.eventList.add()
            newItem.frame = nvb_utils.nwtime2frame(event[0])
            newItem.name  = event[1]

    def getAnimFromScene(self, scene, rootDummyName = ''):
        pass

    def getAnimFromAscii(self, asciiBlock):
        blockStart = -1
        for idx, line in enumerate(asciiBlock):
            try:
                label = line[0].lower()
            except IndexError:
                # Probably empty line or whatever, skip it
                continue
            if (label == 'newanim'):
                self.name = nvb_utils.getName(line[1])
            elif (label == 'length'):
                self.length = float(line[1])
            elif (label == 'transtime'):
                self.transtime = float(line[1])
            elif (label == 'animroot'):
                try:
                    self.root = line[1]
                except:
                    self.root = 'undefined'
            elif (label == 'event'):
                self.addEvent((float(line[1]), line[2]))
            elif (label == 'eventlist'):
                numEvents = next((i for i, v in enumerate(asciiBlock[idx+1:]) if not nvb_utils.isNumber(v[0])), -1)
                list(map(self.addEvent, ((float(v[0]), v[1]) for v in asciiBlock[idx+1:idx+1+numEvents])))
            elif (label == 'node'):
                blockStart = idx
            elif (label == 'endnode'):
                if (blockStart > 0):
                    self.addAsciiNode(asciiBlock[blockStart:idx+1])
                    blockStart = -1
                elif (label == 'node'):
                    raise nvb_def.MalformedMdlFile('Unexpected "endnode"')

    def loadAscii(self, ascii_data):
        """Load an animation from a block from an ascii mdl file."""
        self.getAnimFromAscii([l.strip().split() for l in ascii_data.splitlines()])
        animNodesStart = ascii_data.find('node ')
        if (animNodesStart > -1):
            self.loadAsciiAnimHeader(ascii_data[:animNodesStart-1])
            self.loadAsciiAnimNodes(ascii_data[animNodesStart:])
        else:
            print('Neverblender - WARNING: Failed to load an animation.')


    def loadAsciiAnimHeader(self, ascii_data):
        """TODO: DOC."""
        ascii_lines = [l.strip().split() for l in ascii_data.splitlines()]
        for line in ascii_lines:
            try:
                label = line[0].lower()
            except (IndexError, AttributeError):
                continue  # Probably empty line, skip it
            if (label == 'newanim'):
                self.name = nvb_utils.str2identifier(line[1])
            elif (label == 'length'):
                self.length = float(line[1])
            elif (label == 'transtime'):
                self.transtime = float(line[1])
            elif (label == 'animroot'):
                try:
                    self.animroot = line[1].lower()
                except (ValueError, IndexError):
                    self.animroot = ''
            elif (label == 'event'):
                self.events.append((float(line[1]), line[2]))

    def loadAsciiAnimNodes(self, ascii_data):
        """TODO: DOC."""
        dlm = 'node '
        node_list = [dlm + s for s in ascii_data.split(dlm) if s != '']
        for idx, ascii_node in enumerate(node_list):
            ascii_lines = [l.strip().split() for l in ascii_node.splitlines()]
            node = nvb_animnode.Animnode()
            node.load_ascii(ascii_lines, idx)
            self.nodes.append(node)

    def animNodeToAscii(self, bObject, asciiLines):
        node = nvb_animnode.Node()
        node.toAscii(bObject, asciiLines, self.name)

        '''
        for child in bObject.children:
            self.animNodeToAscii(child, asciiLines)
        '''
        # If this mdl was imported, we need to retain the order of the
        # objects in the original mdl file. Unfortunately this order is
        # seemingly arbitrary so we need to save it at import
        # Otherwise supermodels don't work correctly.
        childList = []
        for child in bObject.children:
            childList.append((child.nvb.imporder, child))
        childList.sort(key=lambda tup: tup[0])

        for (imporder, child) in childList:
            self.animNodeToAscii(child, asciiLines)


    @staticmethod
    def generateAsciiNodes(obj, anim, ascii_lines, options):
        """TODO: Doc."""
        nvb_animnode.Animnode.generate_ascii(obj, anim, ascii_lines, options)

        # Sort children to restore original order before import
        # (important for supermodels/animations to work)
        children = [c for c in obj.children]
        children.sort(key=lambda c: c.name)
        children.sort(key=lambda c: c.nvb.imporder)
        for c in children:
            Animation.generateAsciiNodes(c, anim, ascii_lines, options)


    @staticmethod
    def generateAscii(animRootDummy, anim, ascii_lines, options):
        fps = nvb_def.fps
        ascii_lines.append("newanim {} {}".format(anim.name, animRootDummy.name))
        ascii_lines.append(
            "  length {}".format(
                round((anim.frameEnd - anim.frameStart)/fps, 5)
            )
        )
        ascii_lines.append(
            "  transtime {}".format(round(anim.ttime, 3))
        )
        ascii_lines.append(
            "  animroot {}".format(anim.root)
        )
        # Get animation events
        for event in anim.eventList:
            event_time = (event.frame - anim.frameStart) / fps
            ascii_lines.append(
                "  event {} {}".format(round(event_time, 3), event.name)
            )

        Animation.generateAsciiNodes(animRootDummy, anim, ascii_lines, options)

        ascii_lines.append("doneanim {} {}".format(anim.name, animRootDummy.name))
        ascii_lines.append("")

    def toAscii(self, animScene, animRootDummy, asciiLines, mdlName = ''):
        self.name      = animRootDummy.nvb.animname
        self.length    = nvb_utils.frame2nwtime(animScene.frame_end, animScene.render.fps)
        self.transtime = animRootDummy.nvb.transtime
        self.root      = animRootDummy.nvb.animroot

        asciiLines.append('newanim ' + self.name + ' ' + mdlName)
        asciiLines.append('  length ' + str(round(self.length, 5)))
        asciiLines.append('  transtime ' + str(round(self.transtime, 3)))
        asciiLines.append('  animroot ' + self.root)

        for event in animRootDummy.nvb.eventList:
            eventTime = nvb_utils.frame2nwtime(event.frame, animScene.render.fps)
            asciiLines.append('  event ' + str(round(eventTime, 5)) + ' ' + event.name)

        self.animNodeToAscii(animRootDummy, asciiLines)
        asciiLines.append('doneanim ' + self.name + ' ' + mdlName)
        asciiLines.append('')
