"""TODO: DOC."""

import mathutils
import collections
import bpy
import re
from math import sqrt,asin,cos

from . import nvb_def
from . import nvb_utils
from . import nvb_parse


class Keys():
    def __init__(self):
        self.position       = []
        self.orientation    = []
        self.scale          = []
        self.selfillumcolor = []
        self.alpha          = []
        # Lights
        self.color  = []
        self.radius = []
        # Emitters
        self.alphastart = []
        self.alphamid = []
        self.alphaend = []
        self.birthrate = []
        self.m_frandombirthrate = []
        self.bounce_co = []
        self.combinetime = []
        self.drag = []
        self.fps = []
        self.frameend = []
        self.framestart = []
        self.grav = []
        self.lifeexp = []
        self.mass = []
        self.p2p_bezier2 = []
        self.p2p_bezier3 = []
        self.particlerot = []
        self.randvel = []
        self.sizestart = []
        self.sizemid = []
        self.sizeend = []
        self.sizestart_y = []
        self.sizemid_y = []
        self.sizeend_y = []
        self.spread = []
        self.threshold = []
        self.velocity = []
        self.xsize = []
        self.ysize = []
        self.blurlength = []
        self.lightningdelay = []
        self.lightningradius = []
        self.lightningsubdiv = []
        self.lightningscale = []
        self.lightningzigzag = []
        self.percentstart = []
        self.percentmid = []
        self.percentend = []
        self.targetsize = []
        self.numcontrolpts = []
        self.controlptradius = []
        self.controlptdelay = []
        self.tangentspread = []
        self.tangentlength = []
        self.colorstart = []
        self.colormid = []
        self.colorend = []
        # Unknown. Import as text
        self.rawascii = ''

    def hasAlpha(self):
        return len(self.alpha) > 0


class Node():
    KEY_TYPE = {
        'position': {
            'values': 3,
            'axes': 3,
            'objdata': 'location',
        },
        'orientation': {
            'values': 4,
            'axes': 3,
            'objdata': 'rotation_euler',
        },
        'scale': {
            'values': 1,
            'axes': 3,
            'objdata': 'scale',
        },
        'alpha': {
            'values': 1,
            'axes': 1,
            'objdata': 'nvb.alpha',
        },
        'selfillumcolor': {
            'values': 3,
            'axes': 3,
            'objdata': 'nvb.selfillumcolor',
        },
        'color': {
            'values': 3,
            'axes': 3,
            'objdata': 'color',
        },
        'radius': {
            'values': 1,
            'axes': 1,
            'objdata': 'distance',
        },
    }
    EMITTER_KEY_TYPE = {
        "alphaStart": {
            "values": 1,
            "axes": 1,
        },
        "alphaMid": {
            "values": 1,
            "axes": 1,
        },
        "alphaEnd": {
            "values": 1,
            "axes": 1,
        },
        "birthrate": {
            "values": 1,
            "axes": 1,
            "conversion":float,
        },
        "m_fRandomBirthRate": {
            "values": 1,
            "axes": 1,
            "conversion":float,
        },
        "bounce_co": {
            "values": 1,
            "axes": 1,
        },
        "combinetime": {
            "values": 1,
            "axes": 1,
        },
        "drag": {
            "values": 1,
            "axes": 1,
        },
        "fps": {
            "values": 1,
            "axes": 1,
            "conversion":int,
        },
        "frameEnd": {
            "values": 1,
            "axes": 1,
            "conversion":int,
        },
        "frameStart": {
            "values": 1,
            "axes": 1,
            "conversion":int,
        },
        "grav": {
            "values": 1,
            "axes": 1,
        },
        "lifeExp": {
            "values": 1,
            "axes": 1,
        },
        "mass": {
            "values": 1,
            "axes": 1,
        },
        "p2p_bezier2": {
            "values": 1,
            "axes": 1,
        },
        "p2p_bezier3": {
            "values": 1,
            "axes": 1,
        },
        "particleRot": {
            "values": 1,
            "axes": 1,
        },
        "randvel": {
            "values": 1,
            "axes": 1,
        },
        "sizeStart": {
            "values": 1,
            "axes": 1,
        },
        "sizeMid": {
            "values": 1,
            "axes": 1,
        },
        "sizeEnd": {
            "values": 1,
            "axes": 1,
        },
        "sizeStart_y": {
            "values": 1,
            "axes": 1,
        },
        "sizeMid_y": {
            "values": 1,
            "axes": 1,
        },
        "sizeEnd_y": {
            "values": 1,
            "axes": 1,
        },
        "spread": {
            "values": 1,
            "axes": 1,
        },
        "threshold": {
            "values": 1,
            "axes": 1,
        },
        "velocity": {
            "values": 1,
            "axes": 1,
        },
        "xsize": {
            "values": 1,
            "axes": 1,
            "conversion":int,
        },
        "ysize": {
            "values": 1,
            "axes": 1,
            "conversion":int,
        },
        "blurlength": {
            "values": 1,
            "axes": 1,
        },
        "lightningDelay": {
            "values": 1,
            "axes": 1,
        },
        "lightningRadius": {
            "values": 1,
            "axes": 1,
        },
        "lightningSubDiv": {
            "values": 1,
            "axes": 1,
            "conversion":int,
        },
        "lightningScale": {
            "values": 1,
            "axes": 1,
        },
        "lightningzigzag": {
            "values": 1,
            "axes": 1,
            "conversion":int,
        },
        "percentStart": {
            "values": 1,
            "axes": 1,
        },
        "percentMid": {
            "values": 1,
            "axes": 1,
        },
        "percentEnd": {
            "values": 1,
            "axes": 1,
        },
        "targetsize": {
            "values": 1,
            "axes": 1,
            "conversion":int,
        },
        "numcontrolpts": {
            "values": 1,
            "axes": 1,
            "conversion":int,
        },
        "controlptradius": {
            "values": 1,
            "axes": 1,
        },
        "controlptdelay": {
            "values": 1,
            "axes": 1,
            "conversion":int,
        },
        "tangentspread": {
            "values": 1,
            "axes": 1,
            "conversion":int,
        },
        "tangentlength": {
            "values": 1,
            "axes": 1,
        },
        "colorStart": {
            "values": 3,
            "axes": 3,
        },
        "colorMid": {
            "values": 3,
            "axes": 3,
        },
        "colorEnd": {
            "values": 3,
            "axes": 3,
        },
    }

    def __init__(self, name = 'UNNAMED'):
        self.name       = name
        self.nodetype   = 'dummy'
        self.parentName = nvb_def.null

        # Keyed
        self.keys = Keys()

        self.isEmpty = True

    def __bool__(self):
        """
        Return false if the node is empty, i.e. it has no anims attached
        """
        return not self.isEmpty

    def requiresUniqueData(self):
        return self.keys.hasAlpha()

    def parseKeys9f(self, asciiBlock, keyList):
        """
        Parse animation keys containing 9 floats (not counting the time value)
        """
        nvb_parse._f(asciiBlock, keyList, 10)
        self.isEmpty = False

    def parseKeys3f(self, asciiBlock, keyList):
        """
        Parse animation keys containing 3 floats (not counting the time value)
        """
        nvb_parse.f4(asciiBlock, keyList)
        self.isEmpty = False


    def parseKeys4f(self, asciiBlock, keyList):
        """
        Parse animation keys containing 4 floats (not counting the time value)
        """
        nvb_parse.f5(asciiBlock, keyList)
        self.isEmpty = False


    def parseKeys1f(self, asciiBlock, keyList):
        """
        Parse animation keys containing 1 float (not counting the time value)
        """
        nvb_parse.f2(asciiBlock, keyList)
        self.isEmpty = False


    def parseKeysIncompat(self, asciiBlock):
        """
        Parse animation keys incompatible with blender. They will be saved
        as plain text.
        """
        for line in asciiBlock:
            self.keys.rawascii = self.keys.rawascii + '\n' + ' '.join(line)
        self.isEmpty = False

    @staticmethod
    def findEnd(asciiBlock):
        """
        We don't know when a list of keys of keys will end. We'll have to
        search for the first non-numeric value
        """
        l_isNumber = nvb_utils.isNumber
        return next((i for i, v in enumerate(asciiBlock) if len(v) and not l_isNumber(v[0])), -1)

    def loadAscii(self, asciiBlock):
        l_float    = float
        l_int      = int
        l_isNumber = nvb_utils.isNumber
        for idx, line in enumerate(asciiBlock):
            try:
                label = line[0].lower()
            except IndexError:
                # Probably empty line or whatever, skip it
                continue
            if label == 'node':
                self.nodeType = line[1].lower()
                self.name = nvb_utils.getName(line[2])
            elif label == 'endnode':
                return
            elif label == 'endlist':
                # Can't rely on that being here. We have our own way to get
                # the end of a key list
                pass
            elif label == 'parent':
                self.parentName = nvb_utils.getName(line[1])
            elif label in self.KEY_TYPE.keys() or \
                 label in (attr + 'key' for attr in self.KEY_TYPE.keys()) or \
                 label in (attr + 'bezierkey' for attr in self.KEY_TYPE.keys()):
                # Parse all controllers: unkeyed, keyed, or bezierkeyed
                attrname = [attr for attr in self.KEY_TYPE.keys() if label.startswith(attr)][0]
                attr_type = self.KEY_TYPE[attrname]
                key_type = ''
                key_type = 'key' if label.endswith('key') else key_type
                key_type = 'bezierkey' if label.endswith('bezierkey') else key_type
                #print('found {}{} {:d} values'.format(attrname, key_type, attr_type['values']))
                numVals = attr_type['values']
                if key_type:
                    if key_type == 'bezierkey':
                        numVals *= 3
                    numKeys = type(self).findEnd(asciiBlock[idx+1:])
                    subblock = asciiBlock[idx+1:idx+numKeys+1]
                else:
                    numKeys = 1
                    subblock = [[0.0] + line[1:]]
                # parse numvals plus one for time
                nvb_parse._f(subblock, getattr(self.keys, attrname), numVals + 1)
                self.isEmpty = False
            elif label in (attr.lower() for attr in self.EMITTER_KEY_TYPE.keys()) or \
                 label in (attr.lower() + 'key' for attr in self.EMITTER_KEY_TYPE.keys()) or \
                 label in (attr.lower() + 'bezierkey' for attr in self.EMITTER_KEY_TYPE.keys()):
                # Parse all controllers: unkeyed, keyed, or bezierkeyed
                attrname = [attr for attr in self.EMITTER_KEY_TYPE.keys() if attr.lower() in label][0]
                propname = attrname.lower()
                attr_type = self.EMITTER_KEY_TYPE[attrname]
                key_type = ''
                key_type = 'key' if label.endswith('key') else key_type
                key_type = 'bezierkey' if label.endswith('bezierkey') else key_type
                #print('found {}{} {:d} values'.format(attrname, key_type, attr_type['values']))
                numVals = attr_type['values']
                if key_type:
                    if key_type == 'bezierkey':
                        numVals *= 3
                    numKeys = type(self).findEnd(asciiBlock[idx+1:])
                    subblock = asciiBlock[idx+1:idx+numKeys+1]
                else:
                    numKeys = 1
                    subblock = [[0.0] + line[1:]]
                # parse numvals plus one for time
                if 'conversion' in attr_type and attr_type['conversion'] is int:
                    nvb_parse._i(subblock, getattr(self.keys, propname), numVals + 1)
                    #print(getattr(self.keys, attrname))
                else:
                    nvb_parse._f(subblock, getattr(self.keys, propname), numVals + 1)
                #print(attrname + ' ' + label)
                self.isEmpty = False
            # Some unknown text.
            # Probably keys for emitters = incompatible with blender. Import as text.
            elif not l_isNumber(line[0]):
                numKeys = type(self).findEnd(asciiBlock[idx+1:])
                if numKeys:
                    self.parseKeysIncompat(asciiBlock[idx:idx+numKeys+1])
                    self.isEmpty = False


    def addKeyframeToCurve(self, curve, key_coll, key_idx, value_idx, num_values):
        """
        Add Keyframe to animation F-Curve, in bezier or linear style
        """
        key = key_coll[key_idx]
        frame = nvb_utils.nwtime2frame(key[0])
        kfp = curve.keyframe_points.insert(frame, key[value_idx])
        kfp.interpolation = 'LINEAR'
        if len(key) > num_values + 1:
            kfp.interpolation = 'BEZIER'
            kfp.handle_left_type = 'FREE'
            kfp.handle_right_type = 'FREE'
            if key_idx > 0 and len(key_coll):
                prevframe = nvb_utils.nwtime2frame(key_coll[key_idx - 1][0])
                cp1frame = frame - ((frame - prevframe) / 3.0)
                kfp.handle_left[:] = [ cp1frame, key[value_idx + num_values] + key[value_idx] ]
            if key_idx < len(key_coll) - 1:
                nextframe = nvb_utils.nwtime2frame(key_coll[key_idx + 1][0])
                cp2frame = frame + ((nextframe - frame) / 3.0)
                kfp.handle_right[:] = [ cp2frame, key[value_idx + (2 * num_values)] + key[value_idx] ]


    def addAnimToObject(self, targetObject, animName = ''):
        """
        Add the animations in this node to target object
        """
        #actionName           = animName + '.' + targetObject.name
        actionName           = targetObject.name
        action               = bpy.data.actions.new(name=actionName)
        action.use_fake_user = True

        # test for all key types, if present, create timelines for them
        for attrname in self.KEY_TYPE.keys():
            if not getattr(self.keys, attrname) or \
               not self.KEY_TYPE[attrname]['objdata']:
                continue
            key_type = self.KEY_TYPE[attrname]
            curves = []
            # one fcurve per 'axis' (xyz, rgb, etc.)
            for x in range(0, key_type['axes']):
                curves.append(action.fcurves.new(data_path=key_type['objdata'], index=x))
            if attrname == 'orientation':
                currEul = None
                prevEul = None
                eulVals = []
            # handle each keyframe
            for index, key in enumerate(getattr(self.keys, attrname)):
                frame = nvb_utils.nwtime2frame(key[0])
                if attrname == 'orientation':
                    # orientation is special
                    eul   = nvb_utils.nwangle2euler(key[1:5])
                    currEul = nvb_utils.eulerFilter(eul, prevEul)
                    prevEul = currEul
                    kfs = []
                    for x in range(0, key_type['axes']):
                        kfs.append(curves[x].keyframe_points.insert(frame, currEul[x]))
                        kfs[x].interpolation = 'LINEAR'
                else:
                    # handle each axis, matching values to curves
                    for x in range(0, key_type['axes']):
                        # handle key/bezierkey for all types in addKeyframeToCurve
                        self.addKeyframeToCurve(
                            curves[x], getattr(self.keys, attrname), index,
                            min(x + 1, key_type['values']), key_type['values'])
        # test for all key types, if present, create timelines for them
        for attrname in self.EMITTER_KEY_TYPE.keys():
            propname = attrname.lower()
            if not getattr(self.keys, propname):
                continue
            #print('emitter ' + propname)
            key_type = self.EMITTER_KEY_TYPE[attrname]
            curves = []
            # one fcurve per 'axis' (xyz, rgb, etc.)
            for x in range(0, key_type['axes']):
                curves.append(action.fcurves.new(data_path='nvb.' + propname, index=x))
            # handle each keyframe
            for index, key in enumerate(getattr(self.keys, propname)):
                frame = nvb_utils.nwtime2frame(key[0])
                # handle each axis, matching values to curves
                for x in range(0, key_type['axes']):
                    # handle key/bezierkey for all types in addKeyframeToCurve
                    self.addKeyframeToCurve(
                        curves[x], getattr(self.keys, propname), index,
                        min(x + 1, key_type['values']), key_type['values'])

        # Add imcompatible animations (emitters) as a text object
        if (self.keys.rawascii):
            txt = bpy.data.texts.new(targetObject.name)
            txt.write(self.keys.rawascii)
            targetObject.nvb.rawascii = txt.name

        targetObject.animation_data_create()
        targetObject.animation_data.action = action


    @staticmethod
    def getKeysFromAction(anim, action, keyDict):
        for fcurve in action.fcurves:
            # Get the sub dict for this particlar type of fcurve
            axis     = fcurve.array_index
            dataPath = fcurve.data_path
            name     = ''
            #print(dataPath)
            for keyname in Node.KEY_TYPE.keys():
                ktype = Node.KEY_TYPE[keyname]
                if ktype['objdata'] is not None and \
                   dataPath == ktype['objdata']:
                    name = keyname + 'key'
                    break
            for keyname in Node.EMITTER_KEY_TYPE.keys():
                if dataPath == 'nvb.' + keyname.lower():
                    ktype = Node.EMITTER_KEY_TYPE[keyname]
                    name = keyname + 'key'
                    break

            # does this fcurve have points in this animation?
            # if not, skip it
            if not len([
                kfp for kfp in fcurve.keyframe_points \
                if kfp.co[0] >= anim.frameStart and kfp.co[0] <= anim.frameEnd
            ]):
                continue

            for kfp in fcurve.keyframe_points:
                if name.startswith('orientation'):
                    # bezier keyed orientation animation currently unsupported
                    break
                if kfp.interpolation == 'BEZIER':
                    name = re.sub(r'^(.+)key$', r'\1bezierkey', name)
                    break

            for kfkey, kfp in enumerate(fcurve.keyframe_points):
                #frame = int(round(kfp.co[0])) - anim.frameStart
                frame = int(round(kfp.co[0]))
                if frame < anim.frameStart or frame > anim.frameEnd:
                    continue
                if name not in keyDict:
                    keyDict[name] = collections.OrderedDict()
                keys  = keyDict[name]
                if frame in keys:
                    values = keys[frame]
                else:
                    values = [0.0, 0.0, 0.0, 0.0]
                values[axis] = values[axis] + kfp.co[1]
                #print(values)
                if name.endswith('bezierkey'):
                    if kfp.interpolation == 'BEZIER':
                        values[ktype['axes'] + (axis * 2):(ktype['axes'] + 1) + (axis * 2)] = \
                            [ kfp.handle_left[1] - kfp.co[1], kfp.handle_right[1] - kfp.co[1] ]
                    elif kfp.interpolation == 'LINEAR':
                        # do the linear emulation,
                        # distance between keyframes / 3 point on linear interpolation @ frame
                        # y = y0 + ((x - x0) * ((y1 - y0)/(x1 - x0)))
                        # right handle is on the segment controlled by this keyframe
                        if kfkey < len(fcurve.keyframe_points) - 1:
                            next_kfp = fcurve.keyframe_points[kfkey + 1]
                            next_frame = int(round((next_kfp.co[0] - kfp.co[0]) / 3.0))
                            right_handle = kfp.co[1] + (
                                (next_frame - frame) * (
                                    (next_kfp.co[1] - kfp.co[1]) / (next_kfp.co[0] - kfp.co[0])
                                )
                            )
                            # make exported right handle value relative to keyframe value:
                            right_handle = right_handle - kfp.co[1]
                        else:
                            right_handle = 0.0
                        # left handle is on the segment controlled by the previous keyframe
                        if kfkey > 0 and fcurve.keyframe_points[kfkey - 1].interpolation == 'LINEAR':
                            prev_kfp = fcurve.keyframe_points[kfkey - 1]
                            prev_frame = int(round((kfp.co[0] - prev_kfp.co[0]) / 3.0))
                            left_handle = prev_kfp.co[1] + (
                                (prev_frame - prev_kfp.co[0]) * (
                                    (kfp.co[1] - prev_kfp.co[1]) / (kfp.co[0] - prev_kfp.co[0])
                                )
                            )
                            # make exported left handle value relative to keyframe value:
                            left_handle = left_handle - kfp.co[1]
                        elif kfkey > 0 and kfp.handle_left and kfp.handle_left[1]:
                            left_handle = kfp.handle_left[1] - kfp.co[1]
                        else:
                            left_handle = 0.0
                        values[ktype['axes'] + (axis * 2):(ktype['axes'] + 1) + (axis * 2)] = \
                            [ left_handle, right_handle ]
                    else:
                        # somebody mixed an unknown keyframe type ...
                        # give them some bad data
                        values[ktype['axes'] + (axis * 2):(ktype['axes'] + 1) + (axis * 2)] = [ 0.0, 0.0 ]
                        #values.extend([ 0.0, 0.0 ])
                keys[frame] = values


    def addKeysToAsciiIncompat(self, obj, asciiLines):
        return Node.generate_ascii_keys_incompat(obj, asciiLines)

    @staticmethod
    def generate_ascii_keys_incompat(obj, asciiLines, options={}):
        #if obj.nvb.meshtype != nvb_def.Meshtype.EMITTER:
        #    return
        if obj.nvb.rawascii not in bpy.data.texts:
            return
        txt      = bpy.data.texts[obj.nvb.rawascii]
        txtLines = [l.split() for l in txt.as_string().split('\n')]
        for line in txtLines:
            try:
                label = line[0].lower()
            except IndexError:
                # Probably empty line or whatever, skip it
                continue
            if  (label == 'node') or (label  == 'endnode') or \
                (label == 'parent') or (label == 'position'):
                # We don't need any of this
                pass
            else:
                # We'll take everything that doesn't start with a #
                if label[0] != '#':
                    if nvb_utils.isNumber(label):
                        asciiLines.append('      ' + ' '.join(line))
                    else:
                        asciiLines.append('    ' + ' '.join(line))


    @staticmethod
    def generate_ascii_keys(animObj, anim, asciiLines, options={}):
        keyDict = {}

        # Object Data
        if animObj.animation_data:
            action = animObj.animation_data.action
            if action:
                Node.getKeysFromAction(anim, action, keyDict)

        # Material/ texture data (= texture alpha_factor)
        if animObj.active_material and animObj.active_material.animation_data:
            action = animObj.active_material.animation_data.action
            if action:
                Node.getKeysFromAction(anim, action, keyDict)

        # Light Data
        if animObj.data and animObj.data.animation_data:
            action = animObj.data.animation_data.action
            if action:
                Node.getKeysFromAction(anim, action, keyDict)

        l_str   = str
        l_round = round

        for attrname in Node.KEY_TYPE.keys():
            bezname = attrname + 'bezierkey'
            keyname = attrname + 'key'
            if (bezname not in keyDict or not len(keyDict[bezname])) and \
               (keyname not in keyDict or not len(keyDict[keyname])):
                continue
            ktype = Node.KEY_TYPE[attrname]
            # using a bezierkey
            if bezname in keyDict and len(keyDict[bezname]):
                keyname = bezname
            asciiLines.append('    {} {}'.format(keyname, l_str(len(keyDict[keyname]))))
            for frame, key in keyDict[keyname].items():
                # convert raw frame number to animation-relative time
                time = l_round(nvb_utils.frame2nwtime(frame - anim.frameStart), 5)
                # orientation value conversion
                if keyname.startswith('orientation'):
                    key = nvb_utils.euler2nwangle(mathutils.Euler((key[0:3]), 'XYZ'))
                # export title and
                line = '      {: .7g}' + (' {: .7g}' * ktype['values'])
                s = line.format(time, *key[0:ktype['values']])
                # export bezierkey control points
                if keyname == bezname:
                    # left control point(s)
                    s += (' {: .7g}' * ktype['values']).format(*key[ktype['axes']::2])
                    # right control point(s)
                    s += (' {: .7g}' * ktype['values']).format(*key[ktype['axes'] + 1::2])
                asciiLines.append(s)
        for attrname in Node.EMITTER_KEY_TYPE.keys():
            bezname = attrname + 'bezierkey'
            keyname = attrname + 'key'
            if (bezname not in keyDict or not len(keyDict[bezname])) and \
               (keyname not in keyDict or not len(keyDict[keyname])):
                continue
            ktype = Node.EMITTER_KEY_TYPE[attrname]
            # using a bezierkey
            if bezname in keyDict and len(keyDict[bezname]):
                keyname = bezname
            asciiLines.append('    {} {}'.format(keyname, l_str(len(keyDict[keyname]))))
            for frame, key in keyDict[keyname].items():
                # convert raw frame number to animation-relative time
                time = l_round(nvb_utils.frame2nwtime(frame - anim.frameStart), 5)
                # orientation value conversion
                # export title and
                value_str = " {: .7g}"
                if "conversion" in ktype and ktype["conversion"] is int:
                    #print(attrname)
                    #print(key)
                    #print(ktype)
                    value_str = " {: d}"
                    key[0:ktype['values']] = [int(k) for k in key[0:ktype['values']]]
                    #print('converted')
                    #print(key)
                line = '      {: .7g}' + (value_str * ktype['values'])
                s = line.format(time, *key[0:ktype['values']])
                # export bezierkey control points
                if keyname == bezname:
                    # left control point(s)
                    s += (' {: .7g}' * ktype['values']).format(*key[ktype['axes']::2])
                    # right control point(s)
                    s += (' {: .7g}' * ktype['values']).format(*key[ktype['axes'] + 1::2])
                asciiLines.append(s)


    @staticmethod
    def getOriginalName(nodeName, animName):
        """
        A bit messy due to compatibility concerns
        """
        if nodeName.endswith(animName):
            orig = nodeName[:len(nodeName)-len(animName)]
            if orig.endswith('.'):
                orig = orig[:len(orig)-1]
            return orig

        # Try to separate the name by the first '.'
        # This is unsafe, but we have no choice if we want to maintain some
        # flexibility. It will be up to the user to name the object properly
        orig = nodeName.partition('.')[0]
        if orig:
            return orig

        # Couldn't find anything ? Return the string itself
        return nodeName

    @staticmethod
    def exportNeeded(animObj, anim):
        """
        Test whether this node should be included in exported ASCII model
        """
        # this is the root node, must be included
        if animObj.parent is None:
            return True
        # test for object controllers, loc/rot/scale/selfillum
        objects = [animObj]
        try:
            # this is for light controllers, radius/color:
            if animObj.data:
                objects.append(animObj.data)
            # this is for secondary obj controller, alpha:
            if animObj.active_material:
                objects.append(animObj.active_material)
        except:
            pass
        # test the found objects for animation controllers
        for obj in objects:
            if ((obj.animation_data and \
                 obj.animation_data.action and \
                 obj.animation_data.action.fcurves and \
                 len(obj.animation_data.action.fcurves) > 0 and \
                 len(list(filter(
                    lambda fc: len([
                        kfp for kfp in fc.keyframe_points \
                        if kfp.co[0] >= anim.frameStart and \
                        kfp.co[0] <= anim.frameEnd
                    ]),
                    obj.animation_data.action.fcurves
                 ))))):
                # this node has animation controllers, include it
                #XXX match actual controllers sometime
                # (current will match ANY animation)
                #print('exportNeeded for ' + animObj.name)
                return True
        # if any children of this node will be included, this node must be
        for child in animObj.children:
            if Node.exportNeeded(child, anim):
                print('exportNeeded as parent for ' + animObj.name)
                return True
        # no reason to include this node
        return False

    def toAscii(self, animObj, asciiLines, animName):
        originalName = Node.getOriginalName(animObj.name, animName)
        originalObj  = bpy.data.objects[originalName]

        # test whether this node should be exported,
        # previous behavior was to export all nodes for all animations
        if not Node.exportNeeded(animObj):
            return

        originalParent = nvb_def.null
        if animObj.parent:
            originalParent = Node.getOriginalName(animObj.parent.name, animName)

        if originalObj.nvb.meshtype == nvb_def.Meshtype.EMITTER:
            asciiLines.append('  node emitter ' + originalName)
            asciiLines.append('    parent ' + originalParent)
            #self.addKeysToAsciiIncompat(animObj, asciiLines)
        else:
            asciiLines.append('  node dummy ' + originalName)
            asciiLines.append('    parent ' + originalParent)
        self.addKeysToAscii(animObj, originalObj, asciiLines)
        self.addKeysToAsciiIncompat(animObj, asciiLines)
        asciiLines.append('  endnode')

import copy

from . import nvb_node

class Animnode():
    """TODO: DOC."""

    # Keys that go into particle system settings
    #emitter_properties = nvb_node.Emitter.property_dict
    # Keys that go directly into objects
    object_properties = {'position': ('', 3, float,  # Needs conversion
                                      ' {:> 6.5f}'),
                         'orientation': ('', 4, float,  # Needs conversion
                                         ' {:> 6.5f}'),
                         'scale': ('', 1, float,  # Needs conversion
                                   ' {:> 6.5f}'),
                         'color': ('color', 3, float,
                                   ' {:>4.2f}'),
                         'radius': ('distance', 1, float,
                                    ' {:>6.5f}'),
                         'selfillumcolor': ('nvb.selfillumcolor', 3, float,
                                            ' {:>4.2f}'),
                         'setfillumcolor': ('nvb.selfillumcolor', 3, float,
                                            ' {:>4.2f}')}
    # Keys that go into materials
    material_properties = {'alpha': ('', 1, float,  # Needs conversion
                                     ' {:>4.2f}')}

    def __init__(self, name='UNNAMED'):
        """TODO: DOC."""
        self.nodeidx = -1
        self.nodetype = nvb_def.Nodetype.DUMMY
        self.name = name
        self.parent = nvb_def.null

        self.emitter_data = dict()
        self.object_data = dict()

        # Animesh Data
        self.sampleperiod = 0.0
        self.animtverts = []
        self.animverts = []

        self.uvdata = False  # Animmesh, uv animations present
        self.shapedata = False  # Animmesh, vertex animations present

    def __bool__(self):
        """Return false if the node is empty, i.e. no anims attached."""
        return self.object_data or self.emitter_data

    @staticmethod
    def insert_kfp(frames, values, action, dp, dp_dim, action_group=None):
        """TODO: DOC."""
        if not frames or not values:
            return
        fcu = [nvb_utils.get_fcurve(action, dp, i, action_group)
               for i in range(dp_dim)]
        kfp_list = [fcu[i].keyframe_points for i in range(dp_dim)]
        kfp_cnt = list(map(lambda x: len(x), kfp_list))
        list(map(lambda x: x.add(len(values)), kfp_list))
        for i, (frm, val) in enumerate(zip(frames, values)):
            #print(
            #    "{} dim {} v{} f{}".format(dp, dp_dim, len(val), frm)
            #)
            for d in range(dp_dim):
                p = kfp_list[d][kfp_cnt[d]+i]
                p.co = frm, val[d]
                p.interpolation = 'LINEAR'
                # could do len == dp_dim * 3...
                if len(val) > dp_dim:
                    p.interpolation = 'BEZIER'
                    p.handle_left_type = 'FREE'
                    p.handle_right_type = 'FREE'
                    # initialize left and right handle x positions
                    h_left_frame = frm - nvb_def.fps
                    h_right_frame = frm + nvb_def.fps
                    # adjust handle x positions based on previous/next keyframes
                    if i > 0:
                        p_left = frames[i - 1]
                        print(" left {} frm {}".format(p_left, frm))
                        # place 1/3 into the distance from current keyframe
                        # to previous keyframe
                        h_left_frame = frm - ((frm - p_left) / 3.0)
                    if i < len(values) - 1:
                        p_right = frames[i + 1]
                        print("right {} frm {}".format(p_right, frm))
                        # place 1/3 into the distance from current keyframe
                        # to next keyframe
                        h_right_frame = frm + ((p_right - frm) / 3.0)
                    # set bezier handle positions,
                    # y values are relative, so added to initial value
                    p.handle_left[:] = [
                        h_left_frame,
                        val[d + dp_dim] + val[d]
                    ]
                    p.handle_right[:] = [
                        h_right_frame,
                        val[d + (2 * dp_dim)] + val[d]
                    ]
        list(map(lambda c: c.update(), fcu))

    def load_ascii(self, ascii_lines, nodeidx=-1):
        """TODO: DOC."""
        def find_end(ascii_lines):
            """Find the end of a key list.

            We don't know when a list of keys of keys will end. We'll have to
            search for the first non-numeric value
            """
            l_isNumber = nvb_utils.isNumber
            return next((i for i, v in enumerate(ascii_lines)
                         if not l_isNumber(v[0])), -1)

        self.nodeidx = nodeidx
        '''
        properties_list = [  # For easier parsing
            [type(self).emitter_properties, self.emitter_data],
            [type(self).material_properties, self.material_data],
            [type(self).object_properties, self.object_data]]
        '''
        key_data = {}
        l_isNumber = nvb_utils.isNumber
        for i, line in enumerate(ascii_lines):
            try:
                label = line[0].lower()
            except (IndexError, AttributeError):
                continue  # Probably empty line, skip it
            else:
                if l_isNumber(label):
                    continue
            if label == 'node':
                self.nodetype = line[1].lower()
                self.name = nvb_utils.str2identifier(line[2])
            elif label == 'endnode':
                return
            elif label == 'parent':
                self.parentName = nvb_utils.str2identifier(line[1])
            # Animeshes
            elif label == 'sampleperiod':
                self.sampleperiod = float(line[1])
            elif label == 'animverts':
                if not self.animverts:
                    valcnt = int(line[1])
                    self.animverts = [list(map(float, v))
                                      for v in ascii_lines[i+1:i+valcnt+1]]
                    self.shapedata = True
            elif label == 'animtverts':
                if not self.animtverts:
                    valcnt = int(line[1])
                    self.animtverts = [list(map(float, v))
                                       for v in ascii_lines[i+1:i+valcnt+1]]
                    self.uvdata = True
            else:  # Check for keys
                key_name = label
                key_is_single = True
                key_type = ""
                if key_name.endswith('key'):
                    key_is_single = False
                    key_name = key_name[:-3]
                    key_type = 'key'
                if key_name.endswith('bezier'):
                    key_name = key_name[:-6]
                    key_type = 'bezierkey'
                if key_name in Node.KEY_TYPE.keys() or \
                   key_name in [k.lower() for k in Node.EMITTER_KEY_TYPE.keys()]:
                    attr_name = key_name
                    key_data = self.object_data
                    attr_type = None
                    if attr_name not in Node.KEY_TYPE:
                        # emitter property
                        attr_name = [
                            attr for attr in Node.EMITTER_KEY_TYPE.keys() \
                                if attr.lower() in label
                        ][0]
                        key_data = self.emitter_data
                        attr_type = Node.EMITTER_KEY_TYPE[attr_name]
                    else:
                        # object property
                        attr_type = Node.KEY_TYPE[attr_name]
                    numVals = attr_type['values']
                    numKeys = 0
                    if key_type:
                        if key_type == 'bezierkey':
                            numVals *= 3
                        numKeys = Node.findEnd(ascii_lines[i+1:])
                        subblock = ascii_lines[i + 1:i + numKeys + 1]
                    else:
                        numKeys = 1
                        subblock = [[0.0] + line[1:]]
                    #key_data[key_name] = [
                    converter = float
                    if 'conversion' in attr_type:
                        converter = attr_type['conversion']
                        #print('used converter for ' + attr_name)
                    key_data[key_name] = [
                        [
                            # time followed by values, for each line
                            [float(v[0])] + \
                            list(map(
                                converter, v[1:numVals+1]
                            )) for v in subblock
                        ],
                        attr_type['objdata'] if 'objdata' in attr_type else '',
                        numVals
                    ]
                '''
                for key_def, key_data in properties_list:
                    if key_name in key_def and key_name not in key_data:
                        data_path = key_def[key_name][0]
                        data_dim = key_def[key_name][1]
                        # key_converter = key_def[key_name][2]
                        if key_is_single:
                            data = [[0.0] + list(map(float,
                                    line[1:data_dim+1]))]
                        else:
                            keycnt = find_end(ascii_lines[i+1:])
                            data = [list(map(float, v[:data_dim+1]))
                                    for v in ascii_lines[i+1:i+keycnt+1]]
                        # values = \
                        # [[float(v[0])] + list(map(key_converter, v[1:]))
                        #  for v in values]
                        key_data[key_name] = [data, data_path, data_dim]
                        break
                '''


    def create_data_object(self, obj, anim, options={}):
        """Creates animations in object actions."""
        def data_conversion(label, obj, vals, options={}):
            #print("data conversion {}".format(label))
            if label == 'orientation':
                if obj.rotation_mode == 'AXIS_ANGLE':
                    dp = 'rotation_axis_angle'
                    #print(dp)
                    dp_dim = 4
                    new_values = [[v[3], v[0], v[1], v[2]] for v in vals]
                elif obj.rotation_mode == 'QUATERNION':
                    dp = 'rotation_quaternion'
                    #print(dp)
                    dp_dim = 4
                    quats = [mathutils.Quaternion(v[0:3], v[3]) for v in vals]
                    new_values = [[q.w, q.x, q.y, q.z] for q in quats]
                else:
                    dp = 'rotation_euler'
                    #print(dp)
                    dp_dim = 3
                    # Run an euler filter
                    prev_eul = mathutils.Euler()
                    new_values = []
                    for v in vals:
                        quat = mathutils.Quaternion(v[0:3], v[3])
                        eul = quat.to_euler('XYZ', prev_eul)
                        #  eul = nvb_utils.eulerFilter(quat.to_euler(),
                        #  prev_eul)
                        new_values.append(eul)
                        prev_eul = eul
            elif label == 'position':
                #XXX need MDL animation scale here
                #scl = options.anim_scale
                scl = 1.0
                dp = 'location'
                dp_dim = 3
                if scl:
                    new_values = [[l * scl for l in loc] for loc in vals]
                else:
                    new_values = vals
            elif label == 'scale':
                dp = 'scale'
                dp_dim = 3
                new_values = [[v[0]] * dp_dim for v in vals]
            return new_values, dp, dp_dim

        #fps = options.scene.render.fps
        fps = nvb_def.fps
        frame_start = anim.frameStart
        action = nvb_utils.get_action(obj, options['mdlname'] + '.' + obj.name)
        for label, (data, data_path, data_dim) in self.object_data.items():
            frames = [fps * d[0] + frame_start for d in data]
            #print(label + ' ' + data_path)
            use_action = action
            '''
            try:
                getattr(obj, data_path)
            except:
                #XXX hack to get light data to apply and show up on correct object
                #XXX no-go because Object has 'color'
                use_action = nvb_utils.get_action(obj.data, options['mdlname'] + '.' + obj.name)
            '''
            if obj.type == 'LIGHT' and label in ['radius', 'color']:
                use_action = nvb_utils.get_action(
                    # Light object, not Object object
                    obj.data,
                    options['mdlname'] + '.' + obj.name
                )
            #XXX temp disable data path here to get conversion
            if label in ['orientation', 'position', 'scale']:
                data_path = ''
            if not data_path:  # Needs conversion
                values, dp, dp_dim = data_conversion(
                    label, obj, [d[1:data_dim+1] for d in data], options)
            else:
                values = [d[1:data_dim+1] for d in data]
                dp = data_path
                dp_dim = data_dim
            Animnode.insert_kfp(frames, values, use_action, dp, dp_dim)

    def create_data_emitter(self, obj, anim, options={}):
        """Creates animations in emitter actions."""

        #part_sys = obj.particle_systems.active
        #if not part_sys:
        #    return
        #part_settings = part_sys.settings
        #if not part_settings:
        #    return
        #fps = options.scene.render.fps
        fps = nvb_def.fps
        frame_start = anim.frameStart
        #action = nvb_utils.get_action(part_settings, part_settings.name)
        action = nvb_utils.get_action(obj, options['mdlname'] + '.' + obj.name)
        for label, (data, data_path, data_dim) in self.emitter_data.items():
            frames = [fps * d[0] + frame_start for d in data]
            values = [d[1:data_dim+1] for d in data]
            #dp = data_path
            dp = 'nvb.{}'.format(label)
            dp_dim = data_dim
            #print(dp)
            Animnode.insert_kfp(frames, values, action, dp, dp_dim,
                                'Odyssey Emitter')
            '''
            if dp.startswith('nvb'):  # Group custom properties
                Animnode.insert_kfp(frames, values, action, dp, dp_dim,
                                    'Aurora Emitter')
            else:
                Animnode.insert_kfp(frames, values, action, dp, dp_dim)
            '''

    def create_data_shape(self, obj, anim, animlength, options={}):
        """Import animated vertices as shapekeys."""
        #fps = options.scene.render.fps
        fps = nvb_def.fps
        if not obj.data:
            return
        # Sanity check: Sample period can't be 0
        if self.sampleperiod < 0.001:
            return
        # Sanity check: animation length has to be a multiple of
        #               sampleperiod
        if animlength % self.sampleperiod > 0.0:
            return
        numSamples = int(animlength / self.sampleperiod) + 1
        # Sanity check: Number of animtverts = number verts * numSamples
        numVerts = len(obj.data.vertices)
        if (len(self.animverts) != numVerts * numSamples):
            print("Neverblender: WARNING - animvert sample size mismatch: " +
                  obj.name)
            return
        sampleDistance = fps * self.sampleperiod
        # Get the shape key name
        if obj.nvb.aurorashapekey:
            shapekeyname = obj.nvb.aurorashapekey
        else:
            shapekeyname = nvb_def.shapekeyname
        # Create a basis shapekey
        obj.shape_key_add(name='basis', from_mix=False)
        # Get or create the shape key to hold the animation
        if obj.data.shape_keys and \
           shapekeyname in obj.data.shape_keys.key_blocks:
            keyBlock = obj.data.shape_keys.key_blocks[shapekeyname]
        else:
            keyBlock = obj.shape_key_add(name=shapekeyname,
                                         from_mix=False)
            keyBlock.value = 1.0
            obj.active_shape_key_index = 1
            obj.nvb.aurorashapekey = keyBlock.name
        # Get animation data, create it if necessary
        animData = obj.data.shape_keys.animation_data
        if not animData:
            animData = obj.data.shape_keys.animation_data_create()
        # Get action, create one if necessary
        action = animData.action
        if not action:
            action = bpy.data.actions.new(name=obj.name)
            action.use_fake_user = True
            animData.action = action
        # Insert keyframes
        # We need to create three curves for each vert, one for each coordinate
        kfOptions = {'FAST'}
        frameStart = anim.frameStart
        dpPrefix = 'key_blocks["' + keyBlock.name + '"].data['
        for vertIdx in range(numVerts):
            dp = dpPrefix + str(vertIdx) + '].co'
            curveX = nvb_utils.get_fcurve(action, dp, 0)
            curveY = nvb_utils.get_fcurve(action, dp, 1)
            curveZ = nvb_utils.get_fcurve(action, dp, 2)
            samples = self.animverts[vertIdx::numVerts]
            for sampleIdx, co in enumerate(samples):
                frame = frameStart + (sampleIdx * sampleDistance)
                curveX.keyframe_points.insert(frame, co[0], options=kfOptions)
                curveY.keyframe_points.insert(frame, co[1], options=kfOptions)
                curveZ.keyframe_points.insert(frame, co[2], options=kfOptions)

    def create_data_uv(self, obj, anim, animlength, options={}):
        """Import animated texture coordinates."""
        fps = options.scene.render.fps
        if not obj.data:
            return
        if not obj.data.uv_layers.active:
            return
        uvlayer = obj.data.uv_layers.active
        # Check if the original uv/tvert order was saved
        if obj.data.name not in nvb_def.tvert_order:
            return
        tvert_order = [v for sl in nvb_def.tvert_order[obj.data.name]
                       for v in sl]
        # Sanity check: Sample period can't be 0
        if self.sampleperiod <= 0.00001:
            return
        # Sanity check: animation length has to be a multiple of
        #               sampleperiod
        if animlength % self.sampleperiod > 0.0:
            return
        numSamples = int(animlength / self.sampleperiod) + 1
        # Sanity check: Number of animtverts = number tverts * numSamples
        numTVerts = len(tvert_order)
        if (len(self.animtverts) != numTVerts * numSamples):
            print("Neverblender: WARNING - animtvert sample size mismatch: " +
                  obj.name)
            return
        sampleDistance = fps * self.sampleperiod

        # Get animation data, create it if necessary
        animData = obj.data.animation_data
        if not animData:
            animData = obj.data.animation_data_create()
        # Get action, create one if necessary
        action = animData.action
        if not action:
            action = bpy.data.actions.new(name=obj.name)
            action.use_fake_user = True
            animData.action = action
        # Insert keyframes
        # We need to create two curves for each uv, one for each coordinate
        kfOptions = {'FAST'}
        frameStart = anim.frameStart
        dpPrefix = 'uv_layers["' + uvlayer.name + '"].data['
        # uvIdx = order in blender, tvertIdx = order in mdl
        for uvIdx, tvertIdx in enumerate(tvert_order):
            dp = dpPrefix + str(uvIdx) + '].uv'
            curveU = nvb_utils.get_fcurve(action, dp, 0)
            curveV = nvb_utils.get_fcurve(action, dp, 1)
            samples = self.animtverts[tvertIdx::numTVerts]
            for sampleIdx, co in enumerate(samples):
                frame = frameStart + (sampleIdx * sampleDistance)
                curveU.keyframe_points.insert(frame, co[0], options=kfOptions)
                curveV.keyframe_points.insert(frame, co[1], options=kfOptions)

    @staticmethod
    def create_restpose(obj, frame=1):
        """TODO: DOC."""
        def insert_kfp(fcurves, frame, val, dim):
            """TODO: DOC."""
            # dim = len(val)
            for j in range(dim):
                kf = fcurves[j].keyframe_points.insert(frame, val[j], options={'FAST'})
                kf.interpolation = 'LINEAR'
        # Get animation data
        animData = obj.animation_data
        if not animData:
            return  # No data = no animation = no need for rest pose
        # Get action
        action = animData.action
        if not action:
            return  # No action = no animation = no need for rest pose
        if obj.rotation_mode == 'AXIS_ANGLE':
            dp = 'rotation_axis_angle'
            fcu = [action.fcurves.find(dp, index=i) for i in range(4)]
            if fcu.count(None) < 1:
                rr = obj.nvb.restrot
                insert_kfp(fcu, frame, [rr[3], rr[0], rr[1], rr[2]], 4)
        elif obj.rotation_mode == 'QUATERNION':
            dp = 'rotation_quaternion'
            fcu = [action.fcurves.find(dp, index=i) for i in range(4)]
            if fcu.count(None) < 1:
                rr = obj.nvb.restrot
                q = mathutils.Quaternion((rr[0], rr[1], rr[2]), rr[3])
                insert_kfp(fcu, frame, [q.w, q.x, q.y, q.z], 4)
        else:
            dp = 'rotation_euler'
            fcu = [action.fcurves.find(dp, index=i) for i in range(3)]
            if fcu.count(None) < 1:
                eul = mathutils.Quaternion(obj.nvb.restrot[:3],
                                           obj.nvb.restrot[3]).to_euler()
                insert_kfp(fcu, frame, eul, 3)
        fcu = [action.fcurves.find('location', index=i) for i in range(3)]
        if fcu.count(None) < 1:
            insert_kfp(fcu, frame, obj.nvb.restloc, 3)
        fcu = [action.fcurves.find('scale', index=i) for i in range(3)]
        if fcu.count(None) < 1:
            insert_kfp(fcu, frame, [obj.nvb.restscl] * 3, 3)

    def create(self, obj, anim, animlength, options={}):
        """TODO:Doc."""
        if self.object_data:
            self.create_data_object(obj, anim, options)
        if self.emitter_data:
            self.create_data_emitter(obj, anim, options)
        if self.uvdata:
            self.create_data_uv(obj, anim, animlength, options)
        if self.shapedata:
            self.create_data_shape(obj, anim, animlength, options)

    @staticmethod
    def generate_ascii(obj, anim, asciiLines, options={}):
        if not obj or not Node.exportNeeded(obj, anim):
            return
        # Type + Name
        #node_type = nvb_utils.getNodeType(obj)
        #node_name = nvb_utils.generate_node_name(obj, options.strip_trailing)
        node_type = "dummy"
        if obj.nvb.meshtype == nvb_def.Meshtype.EMITTER:
            node_type = "emitter"
        node_name = Node.getOriginalName(obj.name, anim.name)
        asciiLines.append('  node ' + node_type + ' ' + node_name)
        # Parent
        #parent_name = nvb_utils.generate_node_name(obj.parent,
        #                                           options.strip_trailing)
        parent_name = nvb_def.null
        if obj.parent:
            parent_name = Node.getOriginalName(obj.parent.name, anim.name)
        asciiLines.append('    parent ' + parent_name)
        Node.generate_ascii_keys(obj, anim, asciiLines, options)
        #Node.generate_ascii_keys_incompat(obj, anim, asciiLines, options)
        asciiLines.append('  endnode')
