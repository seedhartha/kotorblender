import re

import bmesh
import bpy
import bpy_extras.image_utils
from bpy_extras.io_utils import unpack_face_list, unpack_list
from mathutils import Color, Matrix, Vector

from . import (nvb_aabb, nvb_def, nvb_glob, nvb_light, nvb_material, nvb_parse,
               nvb_teximage, nvb_txi, nvb_utils)


class FaceList():
    def __init__(self):
        self.faces = []  # int 3-tuple, vertex indices
        self.shdgr = []  # int, shading group for this face
        self.uvIdx = []  # int 3-tuple, texture/uv vertex indices
        self.matId = []  # int, material index


class FlareList():
    def __init__(self):
        self.textures    = []
        self.sizes       = []
        self.positions   = []
        self.colorshifts = []


class GeometryNode():
    """
    Basic node from which every other is derived
    """
    def __init__(self, name = "UNNAMED"):
        self.nodetype = "undefined"

        self.roottype = "mdl"
        self.rootname = "undefined"

        self.name        = name
        self.parentName  = nvb_def.null
        self.position    = (0.0, 0.0, 0.0)
        self.orientation = (0.0, 0.0, 0.0, 0.0)
        self.scale       = 1.0
        self.wirecolor   = (0.0, 0.0, 0.0)

        # Name of the corresponding object in blender
        # (used to resolve naming conflicts)
        self.objref   = ""
        # Parsed lines (by number), allow last parser to include unhandled data
        self.parsed_lines = [];
        self.rawascii         = "" # unprocessed directives

    def __eq__(self, other):
        if isinstance(other, Base):
            return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(self, other)

    def __str__(self):
        return "node " + self.nodetype + " " + self.name

    def parse1f(self, asciiBlock, floatList):
        l_float = float
        for line in asciiBlock:
            floatList.append(l_float(line[0]))

    def parse2f(self, asciiBlock, floatList):
        l_float = float
        for line in asciiBlock:
            floatList.append( (l_float(line[0]), l_float(line[1])) )

    def parse3f(self, asciiBlock, floatList):
        l_float = float
        for line in asciiBlock:
            floatList.append( (l_float(line[0]), l_float(line[1]), l_float(line[2])) )

    def load_ascii(self, asciiNode):
        l_float = float
        l_is_number = nvb_utils.is_number

        for index, line in enumerate(asciiNode):
            try:
                label = line[0].lower()
            except IndexError:
                # Probably empty line or whatever, skip it
                continue

            if not l_is_number(label):
                if (label == "node"):
                    self.name = nvb_utils.get_name(line[2])
                    self.parsed_lines.append(index)
                elif (label == "endnode"):
                    self.parsed_lines.append(index)
                    return
                elif (label == "parent"):
                    self.parentName = nvb_utils.get_name(line[1])
                    self.parsed_lines.append(index)
                elif (label == "position"):
                    self.position = (l_float(line[1]),
                                     l_float(line[2]),
                                     l_float(line[3]))
                    self.parsed_lines.append(index)
                elif (label == "orientation"):
                    self.orientation = (l_float(line[1]),
                                        l_float(line[2]),
                                        l_float(line[3]),
                                        l_float(line[4]))
                    self.parsed_lines.append(index)
                elif (label == "scale"):
                    self.scale = l_float(line[1])
                    self.parsed_lines.append(index)
                elif (label == "wirecolor"):
                    self.wirecolor = (l_float(line[1]),
                                      l_float(line[2]),
                                      l_float(line[3]))
                    self.parsed_lines.append(index)

    def set_object_data(self, obj):
        self.objref = obj.name  # used to resolve naming conflicts
        nvb_utils.set_object_rotation_aurora(obj, self.orientation)
        obj.nvb.restrot   = self.orientation
        obj.scale         = (self.scale, self.scale, self.scale)
        obj.location      = self.position
        obj.nvb.restloc   = obj.location
        obj.nvb.wirecolor = self.wirecolor
        # add unprocessed data as text objects
        if (len(self.rawascii)):
            txt = bpy.data.texts.new(obj.name)
            txt.write(self.rawascii)
            obj.nvb.rawascii = txt.name

    def add_to_collection(self, collection):
        obj = bpy.data.objects.new(self.name, None)
        self.set_object_data(obj)
        collection.objects.link(obj)
        return obj

    def get_adjusted_matrix(self, obj):
        if obj.parent:
            parent_mw = obj.parent.matrix_world
        else:
            parent_mw = Matrix()

        p_mw_scale = parent_mw.to_scale()

        scaled = obj.matrix_local.copy()
        scaled[0][3] = scaled[0][3] * p_mw_scale[0]
        scaled[1][3] = scaled[1][3] * p_mw_scale[1]
        scaled[2][3] = scaled[2][3] * p_mw_scale[2]
        return scaled

    def add_data_to_ascii(self, obj, asciiLines, classification = nvb_def.Classification.UNKNOWN, simple = False, nameDict = None):
        if obj.parent and nameDict and obj.parent.name in nameDict:
            asciiLines.append("  parent " + nameDict[obj.parent.name])
        elif obj.parent:
            asciiLines.append("  parent " + obj.parent.name)
        else:
            asciiLines.append("  parent " + nvb_def.null)
        # Scaling fix
        transmat = self.get_adjusted_matrix(obj)
        loc = transmat.to_translation()
        s = "  position {: .7g} {: .7g} {: .7g}".format(round(loc[0], 7), round(loc[1], 7), round(loc[2], 7))
        asciiLines.append(s)

        rot = nvb_utils.get_aurora_rot_from_object(obj)
        s = "  orientation {: .7g} {: .7g} {: .7g} {: .7g}".format(round(rot[0], 7), round(rot[1], 7), round(rot[2], 7), round(rot[3], 7))
        asciiLines.append(s)

        color = obj.nvb.wirecolor
        asciiLines.append("  wirecolor " + str(round(color[0], 2)) + " " +
                                           str(round(color[1], 2)) + " " +
                                           str(round(color[2], 2)) )
        scale = round(nvb_utils.get_aurora_scale(obj), 3)
        if (scale != 1.0):
            asciiLines.append("  scale " + str(scale))

        # Write out the unprocessed data
        if obj.nvb.rawascii and obj.nvb.rawascii in bpy.data.texts:
            asciiLines.append("  " + "\n  ".join(bpy.data.texts[obj.nvb.rawascii].as_string().strip().split("\n")))

    def to_ascii(self, obj, asciiLines, classification = nvb_def.Classification.UNKNOWN, simple = False, nameDict = None):
        if nameDict and obj.name in nameDict:
            asciiLines.append("node " + self.nodetype + " " + nameDict[obj.name])
        else:
            asciiLines.append("node " + self.nodetype + " " + obj.name)
        self.add_data_to_ascii(obj, asciiLines, classification, simple, nameDict=nameDict)
        asciiLines.append("endnode")

    def add_unparsed_to_raw(self, asciiNode):
        for idx, line in enumerate(asciiNode):
            if idx in self.parsed_lines or not len("".join(line).strip()):
                continue
            self.rawascii += "\n" + " ".join(line)


class Dummy(GeometryNode):
    def __init__(self, name = "UNNAMED"):
        GeometryNode.__init__(self, name)
        self.nodetype  = "dummy"

        self.dummytype = nvb_def.Dummytype.NONE

    def load_ascii(self, asciiNode):
        GeometryNode.load_ascii(self, asciiNode)

    def set_object_data(self, obj):
        GeometryNode.set_object_data(self, obj)

        obj.nvb.dummytype = self.dummytype

        obj.nvb.dummysubtype = nvb_def.DummySubtype.NONE
        subtypes = nvb_def.DummySubtype.SUFFIX_LIST
        for element in subtypes:
            if self.name.endswith(element[0]):
                obj.nvb.dummysubtype = element[1]
                break

    def add_data_to_ascii(self, obj, asciiLines, classification = nvb_def.Classification.UNKNOWN, simple = False, nameDict=None):
        if obj.parent and nameDict and obj.parent.name in nameDict:
            asciiLines.append("  parent " + nameDict[obj.parent.name])
        elif obj.parent:
            asciiLines.append("  parent " + obj.parent.name)
        else:
            asciiLines.append("  parent " + nvb_def.null)

        dummytype = obj.nvb.dummytype
        if dummytype == nvb_def.Dummytype.MDLROOT:
            # Only parent for rootdummys
            return

        # scale = round(nvb_utils.get_aurora_scale(obj), 3)
        # Scaling fix
        asciiLines.append("  scale 1.0")

        # Scaling fix
        transmat = self.get_adjusted_matrix(obj)
        loc = transmat.to_translation()
        s = "  position {: .7g} {: .7g} {: .7g}".format(round(loc[0], 7), round(loc[1], 7), round(loc[2], 7))
        asciiLines.append(s)

        rot = nvb_utils.quat2nwangle(transmat.to_quaternion())
        s = "  orientation {: .7g} {: .7g} {: .7g} {: .7g}".format(round(rot[0], 7), round(rot[1], 7), round(rot[2], 7), round(rot[3], 7))
        asciiLines.append(s)

        color = obj.nvb.wirecolor
        asciiLines.append("  wirecolor " + str(round(color[0], 2)) + " " +
                                           str(round(color[1], 2)) + " " +
                                           str(round(color[2], 2)) )

        # TODO: Handle types and subtypes, i.e. Check and modify name
        subtype = obj.nvb.dummysubtype
        if subtype == nvb_def.Dummytype.NONE:
            pass


class Patch(GeometryNode):
    """Same as a plain Dummy."""

    def __init__(self, name = "UNNAMED"):
        GeometryNode.__init__(self, name)
        self.nodetype = "patch"

        self.dummytype = nvb_def.Dummytype.PATCH

    def set_object_data(self, obj):
        GeometryNode.set_object_data(self, obj)

        obj.nvb.dummytype = self.dummytype


class Reference(GeometryNode):
    """Contains a reference to another mdl."""

    def __init__(self, name = "UNNAMED"):
        GeometryNode.__init__(self, name)
        self.nodetype = "reference"

        self.dummytype = nvb_def.Dummytype.REFERENCE
        self.refmodel     = nvb_def.null
        self.reattachable = 0

    def load_ascii(self, asciiNode):
        GeometryNode.load_ascii(self, asciiNode)
        l_is_number = nvb_utils.is_number

        for idx, line in enumerate(asciiNode):
            try:
                label = line[0].lower()
            except IndexError:
                # Probably empty line or whatever, skip it
                continue
            if not l_is_number(label):
                if (label == "refmodel"):
                    # self.refmodel = line[1].lower()
                    self.refmodel = line[1]
                    self.parsed_lines.append(idx)
                elif (label == "reattachable"):
                    self.reattachable = int(line[1])
                    self.parsed_lines.append(idx)
        if (self.nodetype == "reference"):
            self.add_unparsed_to_raw(asciiNode)

    def set_object_data(self, obj):
        GeometryNode.set_object_data(self, obj)
        obj.nvb.dummytype    = self.dummytype
        obj.nvb.refmodel     = self.refmodel
        obj.nvb.reattachable = (self.reattachable == 1)

    def add_data_to_ascii(self, obj, asciiLines, classification = nvb_def.Classification.UNKNOWN, simple = False, nameDict=None):
        GeometryNode.add_data_to_ascii(self, obj, asciiLines, classification, nameDict=nameDict)
        asciiLines.append("  refmodel " + obj.nvb.refmodel)
        asciiLines.append("  reattachable " + str(int(obj.nvb.reattachable)))


class Trimesh(GeometryNode):
    def __init__(self, name = "UNNAMED"):
        GeometryNode.__init__(self, name)
        self.nodetype = "trimesh"

        self.meshtype         = nvb_def.Meshtype.TRIMESH
        self.center           = (0.0, 0.0, 0.0) # Unused ?
        self.lightmapped      = 0
        self.render           = 1
        self.shadow           = 1
        self.beaming          = 0
        self.inheritcolor     = 0  # Unused ?
        self.m_bIsBackgroundGeometry = 0
        self.dirt_enabled     = 0
        self.dirt_texture     = 1
        self.dirt_worldspace  = 1
        self.hologram_donotdraw = 0
        self.animateuv        = 0
        self.uvdirectionx     = 1.0
        self.uvdirectiony     = 1.0
        self.uvjitter         = 0.0
        self.uvjitterspeed    = 0.0
        self.alpha            = 1.0
        self.transparencyhint = 0
        self.selfillumcolor   = (0.0, 0.0, 0.0)
        self.ambient          = (0.0, 0.0, 0.0)
        self.diffuse          = (0.0, 0.0, 0.0)
        self.bitmap           = nvb_def.null
        self.bitmap2          = nvb_def.null
        self.tangentspace     = 0
        self.rotatetexture    = 0
        self.verts            = [] # list of vertices
        self.facelist         = FaceList()
        self.tverts           = [] # list of texture vertices
        self.tverts1          = [] # list of texture vertices
        self.texindices1      = [] # list of texture vertex indices
        self.roomlinks        = [] # walkmesh only
        self.lytposition      = (0.0, 0.0, 0.0)

    def load_ascii(self, asciiNode):
        GeometryNode.load_ascii(self, asciiNode)

        l_int   = int
        l_float = float
        l_is_number = nvb_utils.is_number
        for idx, line in enumerate(asciiNode):
            try:
                label = line[0].lower()
            except IndexError:
                # Probably empty line or whatever, skip it
                continue

            if not l_is_number(label):
                if (label == "render"):
                    self.render = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "shadow"):
                    self.shadow = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "lightmapped"):
                    self.lightmapped = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "beaming"):
                    self.beaming = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "inheritcolor "):
                    self.inheritcolor = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "tangentspace"):
                    self.tangentspace = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "rotatetexture"):
                    self.rotatetexture = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "m_bisbackgroundgeometry"):
                    self.m_bIsBackgroundGeometry = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "dirt_enabled"):
                    self.dirt_enabled = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "dirt_texture"):
                    self.dirt_texture = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "dirt_worldspace"):
                    self.dirt_worldspace = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "hologram_donotdraw"):
                    self.hologram_donotdraw = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "animateuv"):
                    self.animateuv = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "uvdirectionx"):
                    self.uvdirectionx = l_float(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "uvdirectiony"):
                    self.uvdirectiony = l_float(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "uvjitter"):
                    self.uvjitter = l_float(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "uvjitterspeed"):
                    self.uvjitterspeed = l_float(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "alpha"):
                    self.alpha = l_float(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "transparencyhint"):
                    self.transparencyhint = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "selfillumcolor"):  # Self illumination color
                    self.selfillumcolor = (l_float(line[1]),
                                           l_float(line[2]),
                                           l_float(line[3]))
                    self.parsed_lines.append(idx)
                elif (label == "ambient"):
                    self.ambient = (l_float(line[1]),
                                    l_float(line[2]),
                                    l_float(line[3]))
                    self.parsed_lines.append(idx)
                elif (label == "diffuse"):
                    self.diffuse = (l_float(line[1]),
                                    l_float(line[2]),
                                    l_float(line[3]))
                    self.parsed_lines.append(idx)
                elif (label == "center"):
                    # Unused ? Becuase we don't do anything with this
                    try:
                        self.center = (l_float(line[1]),
                                       l_float(line[2]),
                                       l_float(line[3]))
                        self.parsed_lines.append(idx)
                    except:
                        # Probably an "undefined" string which cannot be
                        # converted to float
                        pass
                elif (label == "bitmap"):
                    self.bitmap = line[1].lower()
                    self.parsed_lines.append(idx)
                elif (label == "bitmap2"):
                    self.bitmap2 = line[1].lower()
                    self.parsed_lines.append(idx)
                elif (label == "verts"):
                    numVals = l_int(line[1])
                    nvb_parse.f3(asciiNode[idx+1:idx+numVals+1], self.verts)
                    self.parsed_lines.extend(range(idx,idx+numVals+1))
                elif (label == "faces"):
                    numVals = l_int(line[1])
                    self.parse_face_list(asciiNode[idx+1:idx+numVals+1])
                    self.parsed_lines.extend(range(idx,idx+numVals+1))
                elif (label == "tverts"):
                    numVals = l_int(line[1])
                    nvb_parse.f2(asciiNode[idx+1:idx+numVals+1], self.tverts)
                    self.parsed_lines.extend(range(idx,idx+numVals+1))
                elif (label == "tverts1"):
                    numVals = l_int(line[1])
                    nvb_parse.f2(asciiNode[idx+1:idx+numVals+1], self.tverts1)
                    self.parsed_lines.extend(range(idx,idx+numVals+1))
                elif (label == "texindices1"):
                    numVals = l_int(line[1])
                    nvb_parse.i3(asciiNode[idx+1:idx+numVals+1], self.texindices1, initialFloat=False)
                    self.parsed_lines.extend(range(idx,idx+numVals+1))
                elif (label == "roomlinks"):
                    try:
                        numVals = l_int(line[1])
                    except:
                        numVals = next((i for i, v in enumerate(asciiNode[idx+1:]) if not l_is_number(v[0])), -1)
                    nvb_parse.i2(asciiNode[idx+1:idx+numVals+1], self.roomlinks)
                    self.parsed_lines.extend(range(idx,idx+numVals+1))
        if (self.nodetype == "trimesh"):
            self.add_unparsed_to_raw(asciiNode)

    def parse_face_list(self, asciiFaces):
        l_int = int
        for line in asciiFaces:
            self.facelist.faces.append((l_int(line[0]),
                                        l_int(line[1]),
                                        l_int(line[2])))
            self.facelist.shdgr.append(l_int(line[3]))
            self.facelist.uvIdx.append((l_int(line[4]),
                                        l_int(line[5]),
                                        l_int(line[6])))
            self.facelist.matId.append(l_int(line[7]))

    def create_mesh(self, name):
        # Create the mesh itself
        mesh = bpy.data.meshes.new(name)
        mesh.vertices.add(len(self.verts))
        mesh.vertices.foreach_set("co", unpack_list(self.verts))
        num_faces = len(self.facelist.faces)
        mesh.loops.add(3 * num_faces)
        mesh.loops.foreach_set("vertex_index", unpack_list(self.facelist.faces))
        mesh.polygons.add(num_faces)
        mesh.polygons.foreach_set("loop_start", range(0, 3 * num_faces, 3))
        mesh.polygons.foreach_set("loop_total", (3,) * num_faces)

        # Special handling for mesh in walkmesh files
        if self.roottype in ["pwk", "dwk", "wok"]:
            # Create walkmesh materials
            for wokMat in nvb_def.wok_materials:
                matName = wokMat[0]
                # Walkmesh materials will be shared across multiple walkmesh
                # objects
                if matName in bpy.data.materials:
                    material = bpy.data.materials[matName]
                else:
                    material = bpy.data.materials.new(matName)
                    material.diffuse_color      = [*wokMat[1], 1.0]
                    material.specular_color     = (0.0,0.0,0.0)
                    material.specular_intensity = wokMat[2]
                mesh.materials.append(material)

            # Apply the walkmesh materials to each face
            for idx, polygon in enumerate(mesh.polygons):
                polygon.material_index = self.facelist.matId[idx]

        # Create UV map
        if len(self.tverts) > 0:
            uv = unpack_list([self.tverts[i] for indices in self.facelist.uvIdx for i in indices])
            uv_layer = mesh.uv_layers.new(name="UVMap", do_init=False)
            uv_layer.data.foreach_set("uv", uv)

        # Create lightmap UV map
        if len(self.tverts1) > 0:
            if len(self.texindices1) > 0:
                uv = unpack_list([self.tverts1[i] for indices in self.texindices1 for i in indices])
            else:
                uv = unpack_list([self.tverts1[i] for indices in self.facelist.uvIdx for i in indices])

            uv_layer = mesh.uv_layers.new(name="UVMap_lm", do_init=False)
            uv_layer.data.foreach_set("uv", uv)

        # Import smooth groups as sharp edges
        if nvb_glob.importSmoothGroups:
            bm = bmesh.new()
            mesh.update()
            bm.from_mesh(mesh)
            if hasattr(bm.edges, "ensure_lookup_table"):
                bm.edges.ensure_lookup_table()
            # Mark edge as sharp if its faces belong to different smooth groups
            for e in bm.edges:
                f = e.link_faces
                if (len(f) > 1) and not (self.facelist.shdgr[f[0].index] & self.facelist.shdgr[f[1].index]):
                    edgeIdx = e.index
                    mesh.edges[edgeIdx].use_edge_sharp = True
            bm.free()
            del bm
            mesh.update()
            # load all smoothgroup numbers into a mesh data layer per-poly
            mesh_sg_list = mesh.polygon_layers_int.new(name=nvb_def.sg_layer_name)
            mesh_sg_list.data.foreach_set("value", self.facelist.shdgr)

        if self.roottype == "wok" and len(self.roomlinks):
            self.set_room_links(mesh)

        mesh.update()
        return mesh

    def set_room_links(self, mesh, skipNonWalkable=True):
        if not "RoomLinks" in mesh.vertex_colors:
            room_vert_colors = mesh.vertex_colors.new(name="RoomLinks")
        else:
            room_vert_colors = mesh.vertex_colors["RoomLinks"]
        for link in self.roomlinks:
            # edge indices don't really match up, but face order does
            faceIdx = int(link[0] / 3)
            edgeIdx = link[0] % 3
            room_color = [ 0.0 / 255, (200 + link[1]) / 255.0, 0.0 / 255 ]
            realIdx = 0
            for face_idx, face in enumerate(mesh.polygons):
                if skipNonWalkable and (face.material_index not in nvb_def.WkmMaterial.NONWALKABLE):
                    if realIdx == faceIdx:
                        faceIdx = face_idx
                        break
                    else:
                        realIdx += 1
            face = mesh.polygons[faceIdx]
            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                if vert_idx in face.edge_keys[edgeIdx]:
                    room_vert_colors.data[loop_idx].color = [*room_color, 1.0]

    def get_room_links(self, mesh):
        """Construct list of room links from vertex colors, for wok files"""
        if not "RoomLinks" in mesh.vertex_colors:
            return
        room_vert_colors = mesh.vertex_colors["RoomLinks"]
        self.roomlinks = []
        face_bonus = 0
        for face_idx, face in enumerate(mesh.polygons):
            verts = {}
            # when the wok is compiled, these faces will be sorted past
            # the walkable faces, so take the index delta into account
            if self.nodetype != "aabb" and face.material_index in nvb_def.WkmMaterial.NONWALKABLE:
                face_bonus -= 1
                continue
            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                room = int(round(room_vert_colors.data[loop_idx].color[1] * 255, 0)) - 200
                # we use color space for links to 55 rooms,
                # which is likely more than the game could handle
                if room < 0 or room > 54:
                    continue
                verts[vert_idx] = room
            if len(verts) < 2:
                continue
            vertIndices = list(verts.keys())
            for edge_idx, edge in enumerate(face.edge_keys):
                if vertIndices[0] in edge and vertIndices[1] in edge:
                    self.roomlinks.append(((face_idx + face_bonus) * 3 + edge_idx, verts[vertIndices[0]]))

    def set_object_data(self, obj):
        GeometryNode.set_object_data(self, obj)

        obj.nvb.meshtype         = self.meshtype
        obj.nvb.bitmap           = self.bitmap if not nvb_utils.is_null(self.bitmap) else ""
        obj.nvb.bitmap2          = self.bitmap2 if not nvb_utils.is_null(self.bitmap2) else ""
        obj.nvb.alpha            = self.alpha
        obj.nvb.lightmapped      = (self.lightmapped == 1)
        obj.nvb.render           = (self.render == 1)
        obj.nvb.shadow           = (self.shadow == 1)
        obj.nvb.beaming          = (self.beaming == 1)
        obj.nvb.tangentspace     = (self.tangentspace == 1)
        obj.nvb.inheritcolor     = (self.inheritcolor == 1)
        obj.nvb.rotatetexture    = (self.rotatetexture == 1)
        obj.nvb.m_bIsBackgroundGeometry = (self.m_bIsBackgroundGeometry == 1)
        obj.nvb.dirt_enabled     = (self.dirt_enabled == 1)
        obj.nvb.dirt_texture     = self.dirt_texture
        obj.nvb.dirt_worldspace  = self.dirt_worldspace
        obj.nvb.hologram_donotdraw = (self.hologram_donotdraw == 1)
        obj.nvb.animateuv        = (self.animateuv == 1)
        obj.nvb.uvdirectionx     = self.uvdirectionx
        obj.nvb.uvdirectiony     = self.uvdirectiony
        obj.nvb.uvjitter         = self.uvjitter
        obj.nvb.uvjitterspeed    = self.uvjitterspeed
        obj.nvb.transparencyhint = self.transparencyhint
        obj.nvb.selfillumcolor   = self.selfillumcolor
        obj.nvb.diffuse          = self.diffuse
        obj.nvb.ambient          = self.ambient
        obj.nvb.lytposition      = self.lytposition

    def add_to_collection(self, collection):
        if nvb_glob.minimapMode and not self.render:
            # Fading objects won't be imported in minimap mode
            # We may need it for the tree stucture, so import it as an empty
            return Dummy.add_to_collection(self, collection)

        mesh = self.create_mesh(self.name)
        obj  = bpy.data.objects.new(self.name, mesh)
        self.set_object_data(obj)

        if nvb_glob.importMaterials and self.roottype == "mdl":
            nvb_material.rebuild_material(obj)

        collection.objects.link(obj)
        return obj

    def add_material_data_to_ascii(self, obj, asciiLines):
        asciiLines.append("  alpha " + str(round(obj.nvb.alpha, 2)))

        asciiLines.append("  diffuse " + str(round(obj.nvb.diffuse[0], 2)) + " " +
                                         str(round(obj.nvb.diffuse[1], 2)) + " " +
                                         str(round(obj.nvb.diffuse[2], 2)))

        tangentspace = 1 if obj.nvb.tangentspace else 0
        asciiLines.append("  tangentspace " + str(tangentspace))

        imgName = obj.nvb.bitmap if obj.nvb.bitmap else nvb_def.null
        asciiLines.append("  bitmap " + imgName)

        imgName = obj.nvb.bitmap2 if obj.nvb.bitmap2 else nvb_def.null
        asciiLines.append("  bitmap2 " + imgName)

    def add_uv_to_list(self, uv, uvList, vert, vertList):
        """Helper function to keep UVs unique."""
        if uv in uvList and vert in vertList:
            return uvList.index(uv)
        else:
            uvList.append(uv)
            vertList.append(vert)
            return (len(uvList)-1)

    def get_export_mesh(self, obj):
        """
        Get the export mesh for an object,
        This mesh has modifiers applied as requested.
        TODO: retain the mesh across contexts instead of recreating every time.
        """
        if obj is None:
            return None

        if nvb_glob.applyModifiers:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            obj_eval = obj.evaluated_get(depsgraph)
            mesh = obj_eval.to_mesh()
        else:
            mesh = obj.to_mesh()

        mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))

        # Triangulation (doing it with bmesh to retain edges marked as sharp)
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()

        return mesh

    def add_mesh_data_to_ascii(self, obj, asciiLines, simple = False):
        mesh = self.get_export_mesh(obj)

        # Calculate smooth groups
        smoothGroups    = []
        numSmoothGroups = 0
        if (obj.nvb.smoothgroup == "SEPR") or (not nvb_glob.exportSmoothGroups):
            # 0 = Do not use smoothgroups
            smoothGroups    = [0] * len(mesh.polygons)
            numSmoothGroups = 1
        elif (obj.nvb.smoothgroup == "SING"):
            # All faces belong to smooth group 1
            smoothGroups    = [1] * len(mesh.polygons)
            numSmoothGroups = 1
        else:
            (smoothGroups, numSmoothGroups) = mesh.calc_smooth_groups(use_bitflags=True)

        faceList = [] # List of triangle faces
        uvList   = [] # List of uv indices
        uvVertList = [] # Temp list of uv verts used for each geometry vert
        # separate lists for the lightmap UVs if they exist
        uvListLM     = [] # List of uv indices
        uvVertListLM = [] # Temp list of uv verts used for each geometry vert

        abs_pos = (0.0, 0.0, 0.0)
        if self.roottype == "wok" and obj.nvb.lytposition:
            abs_pos = (obj.nvb.lytposition[0] + obj.location[0],
                       obj.nvb.lytposition[1] + obj.location[1],
                       obj.nvb.lytposition[2] + obj.location[2])
        # Add vertices
        asciiLines.append("  verts " + str(len(mesh.vertices)))
        l_round = round
        formatString = "    {: .7g} {: .7g} {: .7g}"
        for v in mesh.vertices:
            s = formatString.format(l_round(v.co[0] + abs_pos[0], 7),
                                    l_round(v.co[1] + abs_pos[1], 7),
                                    l_round(v.co[2] + abs_pos[2], 7))
            asciiLines.append(s)

        # Add faces and corresponding tverts and shading groups
        smgroups_layer = mesh.polygon_layers_int.get(nvb_def.sg_layer_name)

        uv_layer = None
        uv_layer_lm = None
        if len(mesh.uv_layers) > 0:
            # AABB nodes only have lightmap UV
            if mesh.uv_layers[0].name.endswith("_lm"):
                uv_layer_lm = mesh.uv_layers[0]
            else:
                uv_layer = mesh.uv_layers[0]
        if uv_layer_lm is None and len(mesh.uv_layers) > 1:
            uv_layer_lm = mesh.uv_layers[1]

        for i in range(len(mesh.polygons)):
            polygon = mesh.polygons[i]
            smGroup = smoothGroups[i]
            if obj.nvb.smoothgroup == "DRCT" and smgroups_layer is not None and smgroups_layer.data[i].value != 0:
                smGroup = smgroups_layer.data[i].value
            if uv_layer:
                uv1 = self.add_uv_to_list(uv_layer.data[3 * i + 0].uv, uvList, polygon.vertices[0], uvVertList)
                uv2 = self.add_uv_to_list(uv_layer.data[3 * i + 1].uv, uvList, polygon.vertices[1], uvVertList)
                uv3 = self.add_uv_to_list(uv_layer.data[3 * i + 2].uv, uvList, polygon.vertices[2], uvVertList)
            else:
                uv1 = 0
                uv2 = 0
                uv3 = 0
            matIdx = polygon.material_index
            if uv_layer_lm:
                uv1LM = self.add_uv_to_list(uv_layer_lm.data[3 * i + 0].uv, uvListLM, polygon.vertices[0], uvVertListLM)
                uv2LM = self.add_uv_to_list(uv_layer_lm.data[3 * i + 1].uv, uvListLM, polygon.vertices[1], uvVertListLM)
                uv3LM = self.add_uv_to_list(uv_layer_lm.data[3 * i + 2].uv, uvListLM, polygon.vertices[2], uvVertListLM)
            else:
                uv1LM = 0
                uv2LM = 0
                uv3LM = 0
            faceList.append([*polygon.vertices[:3], smGroup, uv1, uv2, uv3, matIdx, uv1LM, uv2LM, uv3LM])

        # Check a texture, we don't want uv's when there is no texture
        if simple or len(uvList) < 1:
            asciiLines.append("  faces " + str(len(faceList)))

            vertDigits        = str(len(str(len(mesh.vertices))))
            smoothGroupDigits = str(len(str(numSmoothGroups)))
            formatString = "    {:" + vertDigits + "d} {:" + vertDigits + "d} {:" + vertDigits + "d}  " + \
                               "{:" + smoothGroupDigits + "d}  " + \
                               "0 0 0  " + \
                               "{:2d}"
            for f in faceList:
                s = formatString.format(f[0], f[1], f[2], f[3], f[7])
                asciiLines.append(s)
        else:
            asciiLines.append("  faces " + str(len(faceList)))

            vertDigits        = str(len(str(len(mesh.vertices))))
            smoothGroupDigits = str(len(str(numSmoothGroups)))
            uvDigits          = str(len(str(len(uvList))))
            formatString = "    {:" + vertDigits + "d} {:" + vertDigits + "d} {:" + vertDigits + "d}  " + \
                               "{:" + smoothGroupDigits + "d}  " + \
                               "{:" + uvDigits + "d} {:" + uvDigits + "d} {:" + uvDigits + "d}  " + \
                               "{:2d}"
            for f in faceList:
                s = formatString.format(f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7])
                asciiLines.append(s)

            if (len(uvList) > 0):
                asciiLines.append("  tverts " + str(len(uvList)))
                formatString = "    {: .7g} {: .7g}"
                for uv in uvList:
                    s = formatString.format(round(uv[0], 7), round(uv[1], 7))
                    asciiLines.append(s)

            if (len(uvListLM) > 0):
                asciiLines.append("  tverts1 " + str(len(uvListLM)))
                formatString = "    {: .7g} {: .7g} 0"
                for uv in uvListLM:
                    s = formatString.format(round(uv[0], 7), round(uv[1], 7))
                    asciiLines.append(s)
                asciiLines.append("  texindices1 " + str(len(faceList)))
                formatString = "    {:3d} {:3d} {:3d}"
                for f in faceList:
                    asciiLines.append(formatString.format(f[8], f[9], f[10]))

            if len(mesh.vertex_colors.keys()) and \
               ("RoomLinks" not in mesh.vertex_colors or len(mesh.vertex_colors.keys()) > 1):
                # get dict key for first vertex color layer that is not RoomLinks
                colorKey = [k for k in mesh.vertex_colors.keys() if k != "RoomLinks"][0]
                # insert the vertex colors
                asciiLines.append("  colors " + str(len(mesh.vertices)))
                formatString = "    {: .7g} {: .7g} {: .7g}"
                for face in mesh.polygons:
                    for loop_idx in face.loop_indices:
                        s = formatString.format(mesh.vertex_colors[colorKey].data[loop_idx].color[0],
                                                mesh.vertex_colors[colorKey].data[loop_idx].color[1],
                                                mesh.vertex_colors[colorKey].data[loop_idx].color[2])
                        asciiLines.append(s)
                # insert vertex color indices
                asciiLines.append("  colorindices " + str(len(faceList)))
                for f in faceList:
                    s = formatString.format(f[0], f[1], f[2])
                    asciiLines.append(s)

        if self.roottype == "wok" or self.nodetype == "aabb":
            if self.nodetype == "aabb":
                self.get_room_links(mesh)
            if len(self.roomlinks):
                asciiLines.append("  roomlinks " + str(len(self.roomlinks)))
                for link in self.roomlinks:
                    asciiLines.append("    {:d} {:d}".format(link[0], link[1]))

    def add_data_to_ascii(self, obj, asciiLines, classification = nvb_def.Classification.UNKNOWN, simple = False, nameDict=None):
        GeometryNode.add_data_to_ascii(self, obj, asciiLines, classification, simple, nameDict=nameDict)

        color = obj.nvb.ambient
        asciiLines.append("  ambient " +    str(round(color[0], 2)) + " " +
                                            str(round(color[1], 2)) + " " +
                                            str(round(color[2], 2))  )
        self.add_material_data_to_ascii(obj, asciiLines)
        if not simple:


            color = obj.nvb.selfillumcolor
            asciiLines.append("  selfillumcolor " + str(round(color[0], 2)) + " " +
                                                    str(round(color[1], 2)) + " " +
                                                    str(round(color[2], 2))  )

            asciiLines.append("  render " + str(int(obj.nvb.render)))
            asciiLines.append("  shadow " + str(int(obj.nvb.shadow)))
            asciiLines.append("  lightmapped " + str(int(obj.nvb.lightmapped)))
            asciiLines.append("  beaming " + str(int(obj.nvb.beaming)))
            asciiLines.append("  inheritcolor " + str(int(obj.nvb.inheritcolor)))
            asciiLines.append("  m_bIsBackgroundGeometry " + str(int(obj.nvb.m_bIsBackgroundGeometry)))
            asciiLines.append("  dirt_enabled " + str(int(obj.nvb.dirt_enabled)))
            asciiLines.append("  dirt_texture " + str(obj.nvb.dirt_texture))
            asciiLines.append("  dirt_worldspace " + str(obj.nvb.dirt_worldspace))
            asciiLines.append("  hologram_donotdraw " + str(int(obj.nvb.hologram_donotdraw)))
            asciiLines.append("  animateuv " + str(int(obj.nvb.animateuv)))
            asciiLines.append("  uvdirectionx " + str(obj.nvb.uvdirectionx))
            asciiLines.append("  uvdirectiony " + str(obj.nvb.uvdirectiony))
            asciiLines.append("  uvjitter " + str(obj.nvb.uvjitter))
            asciiLines.append("  uvjitterspeed " + str(obj.nvb.uvjitterspeed))
            asciiLines.append("  transparencyhint " + str(obj.nvb.transparencyhint))
            # These two are for tiles only
            if classification == "TILE":
                asciiLines.append("  rotatetexture " + str(int(obj.nvb.rotatetexture)))

        self.add_mesh_data_to_ascii(obj, asciiLines, simple)


class Danglymesh(Trimesh):
    def __init__(self, name = "UNNAMED"):
        Trimesh.__init__(self, name)
        self.nodetype = "danglymesh"

        self.meshtype     = nvb_def.Meshtype.DANGLYMESH
        self.period       = 1.0
        self.tightness    = 1.0
        self.displacement = 1.0
        self.constraints  = []

    def load_ascii(self, asciiNode):
        Trimesh.load_ascii(self, asciiNode)

        l_int   = int
        l_float = float
        l_is_number = nvb_utils.is_number
        for idx, line in enumerate(asciiNode):
            try:
                label = line[0].lower()
            except IndexError:
                # Probably empty line or whatever, skip it
                continue

            if not l_is_number(label):
                if   (label == "period"):
                    self.period = l_float(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "tightness"):
                    self.tightness = l_float(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "displacement"):
                    self.displacement = l_float(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "constraints"):
                    numVals = l_int(line[1])
                    nvb_parse.f1(asciiNode[idx+1:idx+numVals+1], self.constraints)
                    self.parsed_lines.extend(range(idx,idx+numVals+1))
        if (self.nodetype == "danglymesh"):
            self.add_unparsed_to_raw(asciiNode)

    def add_constraints_to_object(self, obj):
        """
        Creates a vertex group for the object to contain the vertex
        weights for the danglymesh. The weights are called "constraints"
        in NWN. Range is [0.0, 255.0] as opposed to [0.0, 1.0] in Blender
        """
        vgroup = obj.vertex_groups.new(name="constraints")
        for vertexIdx, constraint in enumerate(self.constraints):
            weight = constraint/255
            vgroup.add([vertexIdx], weight, 'REPLACE')
        obj.nvb.constraints = vgroup.name

    def set_object_data(self, obj):
        Trimesh.set_object_data(self, obj)

        obj.nvb.period       = self.period
        obj.nvb.tightness    = self.tightness
        obj.nvb.displacement = self.displacement
        self.add_constraints_to_object(obj)

    def add_constraints_to_ascii(self, obj, asciiLines):
        vgroupName = obj.nvb.constraints
        vgroup     = obj.vertex_groups[vgroupName]

        mesh = self.get_export_mesh(obj)

        asciiLines.append(
            "  constraints {}".format(len(mesh.vertices))
        )
        for v in mesh.vertices:
            # In case vertex is not weighted with dangly constraint
            weight = 0.0
            for vg in v.groups:
                if vg.group != vgroup.index:
                    continue
                weight = round(vg.weight * 255, 3)
            asciiLines.append("    {}".format(weight))

    def add_data_to_ascii(self, obj, asciiLines, classification = nvb_def.Classification.UNKNOWN, simple = False, nameDict=None):
        Trimesh.add_data_to_ascii(self, obj, asciiLines, classification, nameDict=nameDict)

        asciiLines.append("  period "       + str(round(obj.nvb.period, 3)))
        asciiLines.append("  tightness "    + str(round(obj.nvb.tightness, 3)))
        asciiLines.append("  displacement " + str(round(obj.nvb.displacement, 3)))
        self.add_constraints_to_ascii(obj, asciiLines)


class Lightsaber(Trimesh):
    def __init__(self, name = "UNNAMED"):
        Trimesh.__init__(self, name)
        self.nodetype = "lightsaber"

        self.meshtype     = nvb_def.Meshtype.LIGHTSABER

    def create_mesh(self, name):
            # Create the mesh itself
            mesh = Trimesh.create_mesh(self, name)
            return mesh


class Skinmesh(Trimesh):
    """Skinmeshes are Trimeshes where every vertex has a weight."""

    def __init__(self, name = "UNNAMED"):
        Trimesh.__init__(self, name)
        self.nodetype = "skin"

        self.meshtype = nvb_def.Meshtype.SKIN
        self.weights = []

    def load_ascii(self, asciiNode):
        Trimesh.load_ascii(self, asciiNode)
        l_int      = int
        l_is_number = nvb_utils.is_number
        for idx, line in enumerate(asciiNode):
            try:
                label = line[0].lower()
            except IndexError:
                # Probably empty line or whatever, skip it
                continue

            if not l_is_number(label):
                if (label == "weights"):
                    numVals = l_int(line[1])
                    self.get_weights_from_ascii(asciiNode[idx+1:idx+numVals+1])
                    self.parsed_lines.extend(range(idx,idx+numVals+1))
                    break  # Only one value here, abort loop when read
        if (self.nodetype == "skin"):
            self.add_unparsed_to_raw(asciiNode)

    def get_weights_from_ascii(self, asciiBlock):
        lfloat = float
        lchunker = nvb_utils.chunker
        for line in asciiBlock:
            # A line looks like this
            # [group_name, vertex_weight, group_name, vertex_weight]
            # We create a list looking like this:
            # [[group_name, vertex_weight], [group_name, vertex_weight]]
            memberships = []
            for chunk in lchunker(line, 2):
                memberships.append([chunk[0], lfloat(chunk[1])])

            self.weights.append(memberships)

    def add_skin_groups_to_object(self, obj):
        skinGroupDict = {}
        for vertIdx, vertMemberships in enumerate(self.weights):
            for membership in vertMemberships:
                if membership[0] in skinGroupDict:
                    skinGroupDict[membership[0]].add([vertIdx], membership[1], 'REPLACE')
                else:
                    vgroup = obj.vertex_groups.new(name=membership[0])
                    skinGroupDict[membership[0]] = vgroup
                    vgroup.add([vertIdx], membership[1], 'REPLACE')

    def set_object_data(self, obj):
        Trimesh.set_object_data(self, obj)

        self.add_skin_groups_to_object(obj)

    def add_weights_to_ascii(self, obj, asciiLines):
        # Get a list of skingroups for this object:
        # A vertex group is a skingroup if there is an object in the mdl
        # with the same name as the group
        skingroups = {}
        for group in obj.vertex_groups:
            if nvb_utils.search_node_in_model(
                obj,
                lambda o, test_name=group.name:
                    o.name == test_name or \
                    re.match(r'{}\.\d\d\d'.format(test_name), o.name)):
                skingroups[group.index] = group

        mesh = self.get_export_mesh(obj)

        vertexWeights = []
        for v in mesh.vertices:
            weights = []
            for vg in v.groups:
                if not vg.group in skingroups:
                    # vertex group is not for bone weights, skip
                    continue
                group = skingroups[vg.group]
                weights.append([group.name, vg.weight])
            if len(weights) > 4:
                # 4 is the maximum number of influencing bones per vertex
                # for MDL format, therefore we will remove the smallest
                # influences now to make the vertex format compliant
                weights = sorted(weights, key=lambda w: w[1], reverse=True)[0:4]
            total_weight = sum([w[1] for w in weights])
            if total_weight > 0.0 and round(total_weight, 3) != 1.0:
                # normalize weights to equal 1.0
                for w in weights:
                    w[1] /= total_weight
            vertexWeights.append(weights)

        numVerts = len(mesh.vertices)
        asciiLines.append("  weights " + str(numVerts))
        for weights in vertexWeights:
            line = "  "
            if weights:
                for w in weights:
                    line += "  " + w[0] + " " + str(round(w[1], 6))
            else:
                # No weights for this vertex ... this is a problem
                print("KotorBlender: WARNING - missing vertex weight in " + obj.name)
                line = "ERROR: no weight"
            asciiLines.append(line)

    def add_data_to_ascii(self, obj, asciiLines, classification = nvb_def.Classification.UNKNOWN, simple = False, nameDict=None):
        Trimesh.add_data_to_ascii(self, obj, asciiLines, classification, nameDict=nameDict)

        self.add_weights_to_ascii(obj, asciiLines)


class Emitter(GeometryNode):
    emitter_attrs = [
        "deadspace",
        "blastradius",
        "blastlength",
        "numBranches",
        "controlptsmoothing",
        "xgrid",
        "ygrid",
        "spawntype",
        "update",
        "render",
        "blend",
        "texture",
        "chunkName",
        "twosidedtex",
        "loop",
        "renderorder",
        "m_bFrameBlending",
        "m_sDepthTextureName",
        "p2p",
        "p2p_sel",
        "affectedByWind",
        "m_isTinted",
        "bounce",
        "random",
        "inherit",
        "inheritvel",
        "inherit_local",
        "splat",
        "inherit_part",
        "depth_texture",
        "alphastart",
        "alphamid",
        "alphaend",
        "birthrate",
        "m_frandombirthrate",
        "bounce_co",
        "combinetime",
        "drag",
        "fps",
        "frameend",
        "framestart",
        "grav",
        "lifeexp",
        "mass",
        "p2p_bezier2",
        "p2p_bezier3",
        "particlerot",
        "randvel",
        "sizestart",
        "sizemid",
        "sizeend",
        "sizestart_y",
        "sizemid_y",
        "sizeend_y",
        "spread",
        "threshold",
        "velocity",
        "xsize",
        "ysize",
        "blurlength",
        "lightningdelay",
        "lightningradius",
        "lightningsubdiv",
        "lightningscale",
        "lightningzigzag",
        "percentstart",
        "percentmid",
        "percentend",
        "targetsize",
        "numcontrolpts",
        "controlptradius",
        "controlptdelay",
        "tangentspread",
        "tangentlength",
        "colorstart",
        "colormid",
        "colorend"]

    def __init__(self, name = "UNNAMED"):
        GeometryNode.__init__(self, name)
        self.nodetype = "emitter"

        self.meshtype = nvb_def.Meshtype.EMITTER
        # object data
        self.deadspace = 0.0
        self.blastradius = 0.0
        self.blastlength = 0.0
        self.numBranches = 0
        self.controlptsmoothing = 0
        self.xgrid = 0
        self.ygrid = 0
        self.spawntype = ""
        self.update = ""
        self.render = ""
        self.blend = ""
        self.texture = ""
        self.chunkName = ""
        self.twosidedtex = False
        self.loop = False
        self.renderorder = 0
        self.m_bFrameBlending = False
        self.m_sDepthTextureName = nvb_def.null
        # flags
        self.p2p = False
        self.p2p_sel = False
        self.affectedByWind = False
        self.m_isTinted = False
        self.bounce = False
        self.random = False
        self.inherit = False
        self.inheritvel = False
        self.inherit_local = False
        self.splat = False
        self.inherit_part = False
        self.depth_texture = False
        # controllers
        self.alphastart = 0.0
        self.alphamid = 0.0
        self.alphaend = 0.0
        self.birthrate = 0.0
        self.m_frandombirthrate = 0.0
        self.bounce_co = 0.0
        self.combinetime = 0.0
        self.drag = 0.0
        self.fps = 0
        self.frameend = 0
        self.framestart = 0
        self.grav = 0.0
        self.lifeexp = 0.0
        self.mass = 0.0
        self.p2p_bezier2 = 0.0
        self.p2p_bezier3 = 0.0
        self.particlerot = 0.0
        self.randvel = 0.0
        self.sizestart = 0.0
        self.sizemid = 0.0
        self.sizeend = 0.0
        self.sizestart_y = 0.0
        self.sizemid_y = 0.0
        self.sizeend_y = 0.0
        self.spread = 0.0
        self.threshold = 0.0
        self.velocity = 0.0
        self.xsize = 2
        self.ysize = 2
        self.blurlength = 0.0
        self.lightningdelay = 0.0
        self.lightningradius = 0.0
        self.lightningsubdiv = 0
        self.lightningscale = 0.0
        self.lightningzigzag = 0
        self.percentstart = 0.0
        self.percentmid = 0.0
        self.percentend = 0.0
        self.targetsize = 0
        self.numcontrolpts = 0
        self.controlptradius = 0.0
        self.controlptdelay = 0
        self.tangentspread = 0
        self.tangentlength = 0.0
        self.colorstart = (1.0, 1.0, 1.0)
        self.colormid = (1.0, 1.0, 1.0)
        self.colorend = (1.0, 1.0, 1.0)
        # unidentified stuff
        self.rawascii = ""

    def load_ascii(self, asciiNode):
        l_float = float
        l_is_number = nvb_utils.is_number

        for line in asciiNode:
            try:
                label = line[0].lower()
            except IndexError:
                # Probably empty line or whatever, skip it
                continue

            if not l_is_number(label):
                if (label == "node"):
                    self.name = nvb_utils.get_name(line[2])
                elif (label == "endnode"):
                    return
                elif (label == "parent"):
                    self.parentName = nvb_utils.get_name(line[1])
                elif (label == "position"):
                    self.position = (l_float(line[1]),
                                     l_float(line[2]),
                                     l_float(line[3]))
                elif (label == "orientation"):
                    self.orientation = (l_float(line[1]),
                                        l_float(line[2]),
                                        l_float(line[3]),
                                        l_float(line[4]))
                elif (label == "scale"):
                    self.scale = l_float(line[1])
                elif (label == "wirecolor"):
                    self.wirecolor = (l_float(line[1]),
                                      l_float(line[2]),
                                      l_float(line[3]))
                elif (label in list(map(lambda x: x.lower(), dir(self)))):
                    # this block covers all object data and controllers
                    attrname = [name for name in dir(self) if name.lower() == label][0]
                    default_value = getattr(self, attrname)
                    try:
                        if isinstance(default_value, str):
                            setattr(self, attrname, line[1])
                        elif isinstance(default_value, bool):
                            setattr(self, attrname, bool(int(line[1])))
                        elif isinstance(default_value, int):
                            setattr(self, attrname, int(line[1]))
                        elif isinstance(default_value, float):
                            setattr(self, attrname, float(line[1]))
                        elif isinstance(default_value, tuple):
                            setattr(self, attrname, tuple(map(float, line[1:])))
                    except:
                        continue
                else:
                    self.rawascii += "\n  " + " ".join(line)

    def create_mesh(self, objName):
        # Create the mesh itself
        mesh = bpy.data.meshes.new(objName)
        a_bmesh = bmesh.new(use_operators=False)
        a_bmesh.verts.new(( (self.xsize/2) / 100.0,  (self.ysize/2) / 100.0, 0.0))
        a_bmesh.verts.new(( (self.xsize/2) / 100.0, (-self.ysize/2) / 100.0, 0.0))
        a_bmesh.verts.new(((-self.xsize/2) / 100.0, (-self.ysize/2) / 100.0, 0.0))
        a_bmesh.verts.new(((-self.xsize/2) / 100.0,  (self.ysize/2) / 100.0, 0.0))
        a_bmesh.verts.ensure_lookup_table()
        face_verts = [a_bmesh.verts[i] for i in range(4)]
        a_bmesh.faces.new((*face_verts, ))
        a_bmesh.to_mesh(mesh)
        a_bmesh.free()
        return mesh

    def add_raw_ascii(self, obj):
        txt = bpy.data.texts.new(obj.name)
        txt.write(self.rawascii)
        obj.nvb.rawascii = txt.name

    def set_object_data(self, obj):
        GeometryNode.set_object_data(self, obj)

        obj.nvb.meshtype = self.meshtype

        for attrname in self.emitter_attrs:
            value = getattr(self, attrname)
            # Enum translation is not pretty...
            if attrname == "spawntype":
                if value == "0":
                    value = "Normal"
                elif value == "1":
                    value = "Trail"
                else:
                    value = "NONE"
            elif attrname == "update":
                if value.title() not in ["Fountain", "Single", "Explosion", "Lightning"]:
                    value = "NONE"
                else:
                    value = value.title()
            elif attrname == "render":
                attrname = "render_emitter"
                if value not in ["Normal", "Billboard_to_Local_Z", "Billboard_to_World_Z",
                                 "Aligned_to_World_Z", "Aligned_to_Particle_Dir", "Motion_Blur"]:
                    value = "NONE"
            elif attrname == "blend":
                if value.lower() == "punchthrough":
                    value = "Punch-Through"
                elif value.title() not in ["Lighten", "Normal", "Punch-Through"]:
                    value = "NONE"
            # translate p2p_sel to metaproperty p2p_type
            elif attrname == "p2p_sel":
                if self.p2p_sel:
                    obj.nvb.p2p_type = "Bezier"
                else:
                    obj.nvb.p2p_type = "Gravity"
                # p2p_type has update method, sets p2p_sel
                # except it doesn't seem to initially
                obj.nvb.p2p_sel = self.p2p_sel
                continue
            setattr(obj.nvb, attrname, value)

    def add_to_collection(self, collection):
        if nvb_glob.minimapMode:
            # We don't need emitters in minimap mode
            # We may need it for the tree stucture, so import it as an empty
            return GeometryNode.add_to_collection(self, collection)

        mesh = self.create_mesh(self.name)
        obj  = bpy.data.objects.new(self.name, mesh)

        self.set_object_data(obj)
        collection.objects.link(obj)
        return obj

    def add_data_to_ascii(self, obj, asciiLines, classification = nvb_def.Classification.UNKNOWN, simple = False, nameDict=None):
        GeometryNode.add_data_to_ascii(self, obj, asciiLines, classification, simple, nameDict=nameDict)

        # export the copious amounts of emitter data
        for attrname in self.emitter_attrs:
            if attrname == "render":
                value = obj.nvb.render_emitter
            else:
                value = getattr(obj.nvb, attrname)
            if attrname == "spawntype":
                if value == "Normal":
                    value = 0
                elif value == "Trail":
                    value = 1
            if isinstance(value, Color):
                value = " ".join(list(map(lambda x: "{:.6g}".format(x), value)))
            elif isinstance(value, tuple):
                value = " ".join(list(map(lambda x: "{:.6g}".format(x), value)))
            elif isinstance(value, float):
                value = "{:.7g}".format(value)
            elif isinstance(value, bool):
                value = str(int(value))
            elif isinstance(value, str) and (not value or value == "NONE"):
                continue
            else:
                value = str(value)
            asciiLines.append("  {} {}".format(attrname, value))


class Light(GeometryNode):
    def __init__(self, name = "UNNAMED"):
        GeometryNode.__init__(self, name)
        self.nodetype = "light"

        self.shadow        = 1
        self.radius        = 5.0
        self.multiplier    = 1
        self.lightpriority = 5
        self.color         = (0.0, 0.0, 0.0)
        self.ambientonly   = 1
        self.ndynamictype  = 0
        self.isdynamic     = 0
        self.affectdynamic = 1
        self.negativelight = 0
        self.fadinglight   = 1
        self.lensflares    = 0
        self.flareradius   = 1.0
        self.flareList     = FlareList()

    def load_ascii(self, asciiNode):
        GeometryNode.load_ascii(self, asciiNode)

        flareTextureNamesStart = 0
        numFlares              = 0
        numVals                = 0

        l_int = int
        l_float = float
        l_is_number = nvb_utils.is_number
        for idx, line in enumerate(asciiNode):
            try:
                label = line[0].lower()
            except IndexError:
                # Probably empty line or whatever, skip it
                continue

            if not l_is_number(label):
                if (label == "radius"):
                    self.radius = l_float(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "shadow"):
                    self.shadow = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "multiplier"):
                    self.multiplier = l_float(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "color"):
                    self.color = (l_float(line[1]),
                                  l_float(line[2]),
                                  l_float(line[3]))
                    self.parsed_lines.append(idx)
                elif (label == "ambientonly"):
                    self.ambientonly = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "ndynamictype"):
                    self.ndynamictype = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "isdynamic"):
                    self.isdynamic = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "affectdynamic"):
                    self.affectdynamic = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "negativelight"):
                    self.negativelight = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "lightpriority"):
                    self.lightpriority = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "fadinglight"):
                    self.fadinglight = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "lensflares"):
                    self.lensflares = l_int(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "flareradius"):
                    self.flareradius = l_float(line[1])
                    self.parsed_lines.append(idx)
                elif (label == "texturenames"):
                    # List of names follows, but we don't necessarily know how
                    # many flares there are
                    # We 'll need to read them later. For now save the index
                    flareTextureNamesStart = idx+1
                    self.parsed_lines.append(idx)
                elif (label == "flaresizes"):
                    # List of floats
                    numVals = next((i for i, v in enumerate(asciiNode[idx+1:]) if not l_is_number(v[0])), -1)
                    nvb_parse.f1(asciiNode[idx+1:idx+numVals+1], self.flareList.sizes)
                    self.parsed_lines.extend(range(idx,idx+numVals+1))
                elif (label == "flarepositions"):
                    # List of floats
                    numVals = next((i for i, v in enumerate(asciiNode[idx+1:]) if not l_is_number(v[0])), -1)
                    nvb_parse.f1(asciiNode[idx+1:idx+numVals+1], self.flareList.positions)
                    self.parsed_lines.extend(range(idx,idx+numVals+1))
                elif (label == "flarecolorshifts"):
                    # List of float 3-tuples
                    numVals = next((i for i, v in enumerate(asciiNode[idx+1:]) if not l_is_number(v[0])), -1)
                    nvb_parse.f3(asciiNode[idx+1:idx+numVals+1], self.flareList.colorshifts)
                    self.parsed_lines.extend(range(idx,idx+numVals+1))

        # Load flare texture names:
        numFlares = min(len(self.flareList.sizes),
                        min(len(self.flareList.colorshifts),
                            len(self.flareList.positions)))
        for i in range(numFlares):
            texName = asciiNode[flareTextureNamesStart+i][0]
            self.flareList.textures.append(texName)
            self.parsed_lines.append(flareTextureNamesStart+i)

        if (self.nodetype == "light"):
            self.add_unparsed_to_raw(asciiNode)

    def create_light(self, name):
        light = bpy.data.lights.new(name, 'POINT')
        light.color = self.color
        light.use_shadow = self.shadow != 0
        return light

    def set_object_data(self, obj):
        GeometryNode.set_object_data(self, obj)

        switch = {"ml1": "MAINLIGHT1",
                  "ml2": "MAINLIGHT2",
                  "sl1": "SOURCELIGHT1",
                  "sl2": "SOURCELIGHT2"}
        #TODO: Check light names when exporting tiles
        obj.nvb.multiplier    = self.multiplier
        obj.nvb.radius        = self.radius
        obj.nvb.ambientonly   = (self.ambientonly >= 1)
        obj.nvb.lighttype     = switch.get(self.name[-3:], "NONE")
        obj.nvb.shadow        = (self.shadow >= 1)
        obj.nvb.lightpriority = self.lightpriority
        obj.nvb.fadinglight   = (self.fadinglight >= 1)
        obj.nvb.isdynamic     = self.ndynamictype
        if obj.nvb.isdynamic == 0 and self.isdynamic >= 1:
            obj.nvb.isdynamic = 1
        obj.nvb.affectdynamic = (self.affectdynamic >= 1)

        if (self.flareradius > 0) or (self.lensflares >= 1):
            obj.nvb.lensflares = True
            numFlares = len(self.flareList.textures)
            for i in range(numFlares):
                newItem = obj.nvb.flareList.add()
                newItem.texture    = self.flareList.textures[i]
                newItem.colorshift = self.flareList.colorshifts[i]
                newItem.size       = self.flareList.sizes[i]
                newItem.position   = self.flareList.positions[i]

        obj.nvb.flareradius = self.flareradius
        nvb_light.calc_light_power(obj)

    def add_to_collection(self, collection):
        if nvb_glob.minimapMode:
            # We don't need lights in minimap mode
            # We may need it for the tree stucture, so import it as an empty
            return GeometryNode.add_to_collection(self, collection)
        light = self.create_light(self.name)
        obj  = bpy.data.objects.new(self.name, light)
        self.set_object_data(obj)
        collection.objects.link(obj)
        return obj

    def add_flares_to_ascii(self, obj, asciiLines):
        if obj.nvb.lensflares:
            num_flares = int(obj.nvb.lensflares)
            asciiLines.append("  lensflares " + str(num_flares))
            if len(obj.nvb.flareList) > 0:

                # TODO: Clean this up
                asciiLines.append("  texturenames " + str(num_flares))
                for flare in obj.nvb.flareList:
                    asciiLines.append("    " + flare.texture)
                asciiLines.append("  flarepositions " + str(num_flares))
                for flare in obj.nvb.flareList:
                    asciiLines.append("    " + str(round(flare.position, 7)))
                asciiLines.append("  flaresizes " + str(num_flares))
                for flare in obj.nvb.flareList:
                    asciiLines.append("    " + str(flare.size))
                asciiLines.append("  flarecolorshifts " + str(num_flares))
                for flare in obj.nvb.flareList:
                    asciiLines.append("    " +  str(round(flare.colorshift[0], 2)) + " " +
                                                str(round(flare.colorshift[1], 2)) + " " +
                                                str(round(flare.colorshift[2], 2)) )
        asciiLines.append("  flareradius " + str(round(obj.nvb.flareradius, 1)))

    def add_data_to_ascii(self, obj, asciiLines, classification = nvb_def.Classification.UNKNOWN, simple = False, nameDict=None):
        GeometryNode.add_data_to_ascii(self, obj, asciiLines, classification, nameDict=nameDict)

        light = obj.data
        color = (light.color[0], light.color[1], light.color[2])
        asciiLines.append("  radius " + str(round(obj.nvb.radius, 1)))
        asciiLines.append("  multiplier " + str(round(obj.nvb.multiplier, 1)))
        asciiLines.append("  color " +  str(round(color[0], 2)) + " " +
                                        str(round(color[1], 2)) + " " +
                                        str(round(color[2], 2)))
        asciiLines.append("  ambientonly " + str(int(obj.nvb.ambientonly)))
        asciiLines.append("  nDynamicType " + str(obj.nvb.isdynamic))
        asciiLines.append("  affectDynamic " + str(int(obj.nvb.affectdynamic)))
        asciiLines.append("  shadow " + str(int(obj.nvb.shadow)))
        asciiLines.append("  lightpriority " + str(obj.nvb.lightpriority))
        asciiLines.append("  fadingLight " + str(int(obj.nvb.fadinglight)))
        self.add_flares_to_ascii(obj, asciiLines)


class Aabb(Trimesh):
    """
    No need to import Aaabb's. Aabb nodes in mdl files will be
    treated as trimeshes
    """
    def __init__(self, name = "UNNAMED"):
        Trimesh.__init__(self, name)
        self.nodetype = "aabb"

        self.meshtype = nvb_def.Meshtype.AABB

    def compute_layout_position(self, wkm):
        wkmv1 = wkm.verts[wkm.facelist.faces[0][0]]
        wkmv1 = (wkmv1[0] - wkm.position[0],
                 wkmv1[1] - wkm.position[1],
                 wkmv1[2] - wkm.position[2])
        for faceIdx, face in enumerate(self.facelist.faces):
            if self.facelist.matId[faceIdx] != 7:
                v1 = self.verts[face[0]]
                self.lytposition = (round(wkmv1[0] - v1[0], 6),
                                    round(wkmv1[1] - v1[1], 6),
                                    round(wkmv1[2] - v1[2], 6))
                break
        bpy.data.objects[self.objref].nvb.lytposition = self.lytposition

    def add_aabb_to_ascii(self, obj, asciiLines):
        if nvb_glob.applyModifiers:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            obj_eval = obj.evaluated_get(depsgraph)
            walkmesh = obj_eval.to_mesh()
        else:
            walkmesh = obj.to_mesh()

        faceList = []
        faceIdx  = 0
        for polygon in walkmesh.polygons:
            if len(polygon.vertices) == 3:
                # Tri
                v0 = polygon.vertices[0]
                v1 = polygon.vertices[1]
                v2 = polygon.vertices[2]

                centroid = Vector((walkmesh.vertices[v0].co + walkmesh.vertices[v1].co + walkmesh.vertices[v2].co)/3)
                faceList.append((faceIdx, [walkmesh.vertices[v0].co, walkmesh.vertices[v1].co, walkmesh.vertices[v2].co], centroid))
                faceIdx += 1

            elif len(polygon.vertices) == 4:
                # Quad
                v0 = polygon.vertices[0]
                v1 = polygon.vertices[1]
                v2 = polygon.vertices[2]
                v3 = polygon.vertices[3]

                centroid = Vector((walkmesh.vertices[v0].co + walkmesh.vertices[v1].co + walkmesh.vertices[v2].co)/3)
                faceList.append((faceIdx, [walkmesh.vertices[v0].co, walkmesh.vertices[v1].co, walkmesh.vertices[v2].co], centroid))
                faceIdx += 1

                centroid = Vector((walkmesh.vertices[v2].co + walkmesh.vertices[v3].co + walkmesh.vertices[v0].co)/3)
                faceList.append((faceIdx, [walkmesh.vertices[v2].co, walkmesh.vertices[v3].co, walkmesh.vertices[v0].co], centroid))
                faceIdx += 1
            else:
                # Ngon or no polygon at all (This should never be the case with tessfaces)
                print("KotorBlender: WARNING - ngon in walkmesh. Unable to generate aabb.")
                return

        aabbTree = []
        nvb_aabb.generate_tree(aabbTree, faceList)

        l_round = round
        if aabbTree:
            node = aabbTree.pop(0)
            asciiLines.append("  aabb  " +
                              " " +
                              str(l_round(node[0], 7)) +
                              " " +
                              str(l_round(node[1], 7)) +
                              " " +
                              str(l_round(node[2], 7)) +
                              " " +
                              str(l_round(node[3], 7)) +
                              " " +
                              str(l_round(node[4], 7)) +
                              " " +
                              str(l_round(node[5], 7)) +
                              " " +
                              str(node[6]))
            for node in aabbTree:
                asciiLines.append("    " +
                                  str(l_round(node[0], 7)) +
                                  " " +
                                  str(l_round(node[1], 7)) +
                                  " " +
                                  str(l_round(node[2], 7)) +
                                  " " +
                                  str(l_round(node[3], 7)) +
                                  " " +
                                  str(l_round(node[4], 7)) +
                                  " " +
                                  str(l_round(node[5], 7)) +
                                  " " +
                                  str(node[6]) )

    def add_data_to_ascii(self, obj, asciiLines, classification = nvb_def.Classification.UNKNOWN, simple = False, nameDict=None):
        if obj.parent and nameDict and obj.parent.name in nameDict:
            asciiLines.append("  parent " + nameDict[obj.parent.name])
        elif obj.parent:
            asciiLines.append("  parent " + obj.parent.name)
        else:
            asciiLines.append("  parent " + nvb_def.null)
        loc = obj.location
        asciiLines.append("  position " + str(round(loc[0], 7)) + " " +
                                          str(round(loc[1], 7)) + " " +
                                          str(round(loc[2], 7)) )
        rot = nvb_utils.get_aurora_rot_from_object(obj)
        asciiLines.append("  orientation " + str(round(rot[0], 7)) + " " +
                                             str(round(rot[1], 7)) + " " +
                                             str(round(rot[2], 7)) + " " +
                                             str(round(rot[3], 7)) )
        color = obj.nvb.wirecolor
        asciiLines.append("  wirecolor " + str(round(color[0], 2)) + " " +
                                           str(round(color[1], 2)) + " " +
                                           str(round(color[2], 2))  )
        asciiLines.append("  ambient 1.0 1.0 1.0")
        self.add_material_data_to_ascii(obj, asciiLines)
        Trimesh.add_mesh_data_to_ascii(self, obj, asciiLines, simple)
        if self.roottype != "wok":
            self.add_aabb_to_ascii(obj, asciiLines)

    def add_material_data_to_ascii(self, obj, asciiLines):
        asciiLines.append("  diffuse 1.0 1.0 1.0")

        imgName = obj.nvb.bitmap2 if obj.nvb.bitmap2 else nvb_def.null

        asciiLines.append("  bitmap " + nvb_def.null)
        asciiLines.append("  bitmap2 " + imgName)

        lightmapped = 1 if obj.nvb.lightmapped else 0
        asciiLines.append("  lightmapped " + str(lightmapped))

    def create_mesh(self, name):
        # Create the mesh itself
        mesh = bpy.data.meshes.new(name)
        mesh.vertices.add(len(self.verts))
        mesh.vertices.foreach_set("co", unpack_list(self.verts))
        num_faces = len(self.facelist.faces)
        mesh.loops.add(3 * num_faces)
        mesh.loops.foreach_set("vertex_index", unpack_list(self.facelist.faces))
        mesh.polygons.add(num_faces)
        mesh.polygons.foreach_set("loop_start", range(0, 3 * num_faces, 3))
        mesh.polygons.foreach_set("loop_total", (3,) * num_faces)

        # Create materials
        for wokMat in nvb_def.wok_materials:
            matName = wokMat[0]
            # Walkmesh materials will be shared across multiple walkmesh
            # objects
            if matName in bpy.data.materials:
                material = bpy.data.materials[matName]
            else:
                material = bpy.data.materials.new(matName)
                material.diffuse_color      = [*wokMat[1], 1.0]
                material.specular_color     = (0.0,0.0,0.0)
                material.specular_intensity = wokMat[2]
            mesh.materials.append(material)

        # Apply the walkmesh materials to each face
        for idx, polygon in enumerate(mesh.polygons):
            polygon.material_index = self.facelist.matId[idx]

        # Create UV map
        if len(self.tverts) > 0:
            uv = unpack_list([self.tverts[i] for indices in self.facelist.uvIdx for i in indices])
            uv_layer = mesh.uv_layers.new(name="UVMap", do_init=False)
            uv_layer.data.foreach_set("uv", uv)

        # Create lightmap UV map
        if len(self.tverts1) > 0:
            if len(self.texindices1) > 0:
                uv = unpack_list([self.tverts1[i] for indices in self.texindices1 for i in indices])
            else:
                uv = unpack_list([self.tverts1[i] for indices in self.facelist.uvIdx for i in indices])

            uv_layer = mesh.uv_layers.new(name="UVMap_lm", do_init=False)
            uv_layer.data.foreach_set("uv", uv)

        # If there are room links in MDL, then this model is from MDLedit, and we must NOT skip non-walkable faces
        if self.roottype == "mdl" and len(self.roomlinks):
            self.set_room_links(mesh, False)

        mesh.update()
        return mesh

    def add_to_collection(self, collection):
        if nvb_glob.minimapMode:
            # No walkmeshes in minimap mode and we don't need an empty as
            # replacement either as AABB nodes never have children
            return GeometryNode.add_to_collection(self, collection)
        mesh = self.create_mesh(self.name)
        obj = bpy.data.objects.new(self.name, mesh)
        self.set_object_data(obj)
        collection.objects.link(obj)
        return obj
