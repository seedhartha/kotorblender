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

import bpy

from bpy_extras.io_utils import unpack_list
from mathutils import Vector

from ...constants import NodeType, RootType, MeshType, NULL
from ...utils import is_not_null
from .. import material
from .base import BaseNode

UV_MAP_DIFFUSE = "UVMap"
UV_MAP_LIGHTMAP = "UVMap_lm"


class FaceList:
    def __init__(self):
        self.vertices = []  # vertex indices
        self.uv = []  # UV indices
        self.materials = []
        self.normals = []


class EdgeLoopMesh:
    def __init__(self):
        self.verts = []  # vertex coordinates
        self.weights = []  # vertex bone weights
        self.constraints = []  # vertex constraints (danglymesh)

        self.loop_verts = []  # vertex indices
        self.loop_normals = []
        self.loop_uv1 = []  # diffuse texture coordinates
        self.loop_uv2 = []  # lightmap texture coordinates
        self.loop_tangents = []
        self.loop_bitangents = []

        self.face_materials = []
        self.face_normals = []

    def num_faces(self):
        return self.num_loops() // 3

    def num_loops(self):
        return len(self.loop_verts)

    def num_verts(self):
        return len(self.verts)


class TrimeshNode(BaseNode):
    def __init__(self, name="UNNAMED"):
        BaseNode.__init__(self, name)
        self.nodetype = NodeType.TRIMESH
        self.compress = True

        # Properties
        self.meshtype = MeshType.TRIMESH
        self.center = (0.0, 0.0, 0.0)  # Unused ?
        self.lightmapped = 0
        self.render = 1
        self.shadow = 1
        self.beaming = 0
        self.background_geometry = 0
        self.dirt_enabled = 0
        self.dirt_texture = 1
        self.dirt_worldspace = 1
        self.hologram_donotdraw = 0
        self.animateuv = 0
        self.uvdirectionx = 1.0
        self.uvdirectiony = 1.0
        self.uvjitter = 0.0
        self.uvjitterspeed = 0.0
        self.alpha = 1.0
        self.transparencyhint = 0
        self.selfillumcolor = (0.0, 0.0, 0.0)
        self.ambient = (0.2, 0.2, 0.2)
        self.diffuse = (0.8, 0.8, 0.8)
        self.bitmap = NULL
        self.bitmap2 = NULL
        self.tangentspace = 0
        self.rotatetexture = 0

        # Mesh
        self.verts = []
        self.normals = []
        self.uv1 = []
        self.uv2 = []
        self.tangents = []
        self.bitangents = []
        self.tangentspacenormals = []
        self.weights = []
        self.constraints = []
        self.facelist = FaceList()

    def add_to_collection(self, collection, options):
        mesh = self.mdl_to_edge_loop_mesh()
        bl_mesh = self.create_blender_mesh(self.name, mesh)
        obj = bpy.data.objects.new(self.name, bl_mesh)
        self.apply_edge_loop_mesh(mesh, obj)
        self.set_object_data(obj, options)
        if options.build_materials and self.roottype == RootType.MODEL:
            material.rebuild_object_material(
                obj, options.texture_search_paths, options.lightmap_search_paths
            )
        collection.objects.link(obj)
        return obj

    def mdl_to_edge_loop_mesh(self):
        num_faces = len(self.facelist.vertices)
        num_loops = 3 * num_faces
        mesh = EdgeLoopMesh()
        mesh.loop_verts = [-1] * num_loops
        mesh.loop_normals = [(0, 0, 1)] * num_loops
        mesh.loop_uv1 = [(0, 0)] * num_loops if self.uv1 else []
        mesh.loop_uv2 = [(0, 0)] * num_loops if self.uv2 else []
        if self.compress:
            attrs_to_vert_idx = dict()
            for face_idx in range(num_faces):
                face_verts = self.facelist.vertices[face_idx]
                for i in range(3):
                    loop_idx = 3 * face_idx + i
                    vert_idx = face_verts[i]
                    vert = tuple(self.verts[vert_idx])
                    # TODO: hash also by weights and constraint?
                    attrs = (vert,)
                    if attrs in attrs_to_vert_idx:
                        mesh.loop_verts[loop_idx] = attrs_to_vert_idx[attrs]
                    else:
                        num_verts = len(mesh.verts)
                        mesh.verts.append(vert)
                        if self.weights:
                            mesh.weights.append(self.weights[vert_idx])
                        if self.constraints:
                            mesh.constraints.append(self.constraints[vert_idx])
                        attrs_to_vert_idx[attrs] = num_verts
                        mesh.loop_verts[loop_idx] = num_verts
                    mesh.loop_normals[loop_idx] = self.normals[vert_idx]
                    if self.uv1:
                        mesh.loop_uv1[loop_idx] = self.uv1[vert_idx]
                    if self.uv2:
                        mesh.loop_uv2[loop_idx] = self.uv2[vert_idx]
                    if self.tangents and self.bitangents:
                        mesh.loop_tangents[loop_idx] = self.tangents[vert_idx]
                        mesh.loop_bitangents[loop_idx] = self.bitangents[vert_idx]
        else:
            mesh.verts = self.verts
            mesh.weights = self.weights
            mesh.constraints = self.constraints
            for face_idx in range(num_faces):
                face_verts = self.facelist.vertices[face_idx]
                for i in range(3):
                    loop_idx = 3 * face_idx + i
                    vert_idx = face_verts[i]
                    mesh.loop_verts[loop_idx] = vert_idx
                    mesh.loop_normals[loop_idx] = self.normals[vert_idx]
                    if self.uv1:
                        mesh.loop_uv1[loop_idx] = self.uv1[vert_idx]
                    if self.uv2:
                        mesh.loop_uv2[loop_idx] = self.uv2[vert_idx]
                    if self.tangents and self.bitangents:
                        mesh.loop_tangents[loop_idx] = self.tangents[vert_idx]
                        mesh.loop_bitangents[loop_idx] = self.bitangents[vert_idx]
        mesh.face_materials = self.facelist.materials
        mesh.face_normals = self.facelist.normals
        return mesh

    def create_blender_mesh(self, name, mesh):
        bl_mesh = bpy.data.meshes.new(name)
        bl_mesh.vertices.add(mesh.num_verts())
        bl_mesh.vertices.foreach_set("co", unpack_list(mesh.verts))
        bl_mesh.loops.add(mesh.num_loops())
        bl_mesh.loops.foreach_set("vertex_index", mesh.loop_verts)
        bl_mesh.polygons.add(mesh.num_faces())
        bl_mesh.polygons.foreach_set("loop_start", range(0, mesh.num_loops(), 3))
        bl_mesh.polygons.foreach_set("loop_total", [3] * mesh.num_faces())
        bl_mesh.polygons.foreach_set("use_smooth", [True] * mesh.num_faces())
        bl_mesh.update()
        if mesh.loop_normals:
            bl_mesh.normals_split_custom_set(mesh.loop_normals)
            bl_mesh.use_auto_smooth = True
        if mesh.loop_uv1:
            uv_layer = bl_mesh.uv_layers.new(name=UV_MAP_DIFFUSE, do_init=False)
            uv_layer.data.foreach_set("uv", unpack_list(mesh.loop_uv1))
        if mesh.loop_uv2:
            uv_layer = bl_mesh.uv_layers.new(name=UV_MAP_LIGHTMAP, do_init=False)
            uv_layer.data.foreach_set("uv", unpack_list(mesh.loop_uv2))
        return bl_mesh

    def apply_edge_loop_mesh(self, mesh, obj):
        pass

    def set_object_data(self, obj, options):
        BaseNode.set_object_data(self, obj, options)

        obj.kb.meshtype = self.meshtype
        obj.kb.bitmap = self.bitmap if is_not_null(self.bitmap) else ""
        obj.kb.bitmap2 = self.bitmap2 if is_not_null(self.bitmap2) else ""
        obj.kb.alpha = self.alpha
        obj.kb.lightmapped = self.lightmapped == 1
        obj.kb.render = self.render == 1
        obj.kb.shadow = self.shadow == 1
        obj.kb.beaming = self.beaming == 1
        obj.kb.tangentspace = self.tangentspace == 1
        obj.kb.rotatetexture = self.rotatetexture == 1
        obj.kb.background_geometry = self.background_geometry == 1
        obj.kb.dirt_enabled = self.dirt_enabled == 1
        obj.kb.dirt_texture = self.dirt_texture
        obj.kb.dirt_worldspace = self.dirt_worldspace
        obj.kb.hologram_donotdraw = self.hologram_donotdraw == 1
        obj.kb.animateuv = self.animateuv == 1
        obj.kb.uvdirectionx = self.uvdirectionx
        obj.kb.uvdirectiony = self.uvdirectiony
        obj.kb.uvjitter = self.uvjitter
        obj.kb.uvjitterspeed = self.uvjitterspeed
        obj.kb.transparencyhint = self.transparencyhint
        obj.kb.selfillumcolor = self.selfillumcolor
        obj.kb.diffuse = self.diffuse
        obj.kb.ambient = self.ambient

    def load_object_data(self, obj, options):
        BaseNode.load_object_data(self, obj, options)

        self.meshtype = obj.kb.meshtype
        self.bitmap = obj.kb.bitmap if obj.kb.bitmap else NULL
        self.bitmap2 = obj.kb.bitmap2 if obj.kb.bitmap2 else ""
        self.alpha = obj.kb.alpha
        self.lightmapped = 1 if obj.kb.lightmapped else 0
        self.render = 1 if obj.kb.render else 0
        self.shadow = 1 if obj.kb.shadow else 0
        self.beaming = 1 if obj.kb.beaming else 0
        self.tangentspace = 1 if obj.kb.tangentspace else 0
        self.rotatetexture = 1 if obj.kb.rotatetexture else 0
        self.background_geometry = 1 if obj.kb.background_geometry else 0
        self.dirt_enabled = 1 if obj.kb.dirt_enabled else 0
        self.dirt_texture = obj.kb.dirt_texture
        self.dirt_worldspace = obj.kb.dirt_worldspace
        self.hologram_donotdraw = 1 if obj.kb.hologram_donotdraw else 0
        self.animateuv = 1 if obj.kb.animateuv else 0
        self.uvdirectionx = obj.kb.uvdirectionx
        self.uvdirectiony = obj.kb.uvdirectiony
        self.uvjitter = obj.kb.uvjitter
        self.uvjitterspeed = obj.kb.uvjitterspeed
        self.transparencyhint = obj.kb.transparencyhint
        self.selfillumcolor = obj.kb.selfillumcolor
        self.diffuse = obj.kb.diffuse
        self.ambient = obj.kb.ambient

        mesh = self.unapply_edge_loop_mesh(obj)
        self.edge_loop_to_mdl_mesh(mesh)

    def unapply_edge_loop_mesh(self, obj):
        bl_mesh = obj.data
        bl_mesh.calc_loop_triangles()
        bl_mesh.calc_normals_split()
        if self.tangentspace and UV_MAP_DIFFUSE in bl_mesh.uv_layers:
            bl_mesh.calc_tangents(uvmap=UV_MAP_DIFFUSE)
        mesh = EdgeLoopMesh()
        for vert in bl_mesh.vertices:
            mesh.verts.append(vert.co[:3])
        for face in bl_mesh.loop_triangles:
            for i in range(3):
                mesh.loop_verts.append(face.vertices[i])
                mesh.loop_normals.append(face.split_normals[i])
                loop_idx = face.loops[i]
                if UV_MAP_DIFFUSE in bl_mesh.uv_layers:
                    mesh.loop_uv1.append(
                        bl_mesh.uv_layers[UV_MAP_DIFFUSE].data[loop_idx].uv[:2]
                    )
                if UV_MAP_LIGHTMAP in bl_mesh.uv_layers:
                    mesh.loop_uv2.append(
                        bl_mesh.uv_layers[UV_MAP_LIGHTMAP].data[loop_idx].uv[:2]
                    )
                if self.tangentspace:
                    loop = bl_mesh.loops[loop_idx]
                    mesh.loop_tangents.append(loop.tangent)
                    mesh.loop_bitangents.append(loop.bitangent)
            mesh.face_materials.append(face.material_index)
            mesh.face_normals.append(face.normal)
        return mesh

    def edge_loop_to_mdl_mesh(self, mesh):
        self.verts = []
        self.normals = []
        self.uv1 = []
        self.uv2 = []
        self.tangents = []
        self.bitangents = []
        self.tangentspacenormals = []
        self.weights = []
        self.constraints = []
        self.facelist = FaceList()

        if self.compress:
            attrs_to_vert_idx = dict()
            for face_idx in range(mesh.num_faces()):
                vert_indices = [0] * 3
                for i in range(3):
                    loop_idx = 3 * face_idx + i
                    vert_idx = mesh.loop_verts[loop_idx]
                    vert = mesh.verts[vert_idx]
                    normal = mesh.loop_normals[loop_idx]
                    uv1 = mesh.loop_uv1[loop_idx] if mesh.loop_uv1 else (0, 0)
                    uv2 = mesh.loop_uv2[loop_idx] if mesh.loop_uv2 else (0, 0)
                    attrs = (vert, normal, uv1, uv2)
                    if attrs in attrs_to_vert_idx:
                        vert_indices[i] = attrs_to_vert_idx[attrs]
                    else:
                        num_verts = len(self.verts)
                        attrs_to_vert_idx[attrs] = num_verts
                        vert_indices[i] = num_verts
                        self.verts.append(vert)
                        self.normals.append(normal)
                        if mesh.loop_uv1:
                            self.uv1.append(uv1)
                        if mesh.loop_uv2:
                            self.uv2.append(uv2)
                        if mesh.loop_tangents and mesh.loop_bitangents:
                            self.tangents.append(mesh.loop_tangents[loop_idx])
                            self.bitangents.append(mesh.loop_bitangents[loop_idx])
                            # TODO: is this correct?
                            self.tangentspacenormals.append(mesh.loop_normals[loop_idx])
                        if mesh.weights:
                            self.weights.append(mesh.weights[vert_idx])
                        if mesh.constraints:
                            self.constraints.append(mesh.constraints[vert_idx])
                self.facelist.vertices.append(vert_indices)
                self.facelist.uv.append(vert_indices)
        else:
            num_verts = len(mesh.verts)
            self.verts = mesh.verts
            self.weights = mesh.weights
            self.constraints = mesh.constraints
            normals = [Vector((0, 0, 0))] * num_verts
            if mesh.loop_tangents and mesh.loop_bitangents:
                tangents = [Vector((0, 0, 0))] * num_verts
                bitangents = [Vector((0, 0, 0))] * num_verts
                tanspacenormals = [Vector((0, 0, 0))] * num_verts
            if mesh.loop_uv1:
                self.uv1 = [(0, 0)] * num_verts
            if mesh.loop_uv2:
                self.uv2 = [(0, 0)] * num_verts
            for face_idx in range(mesh.num_faces()):
                start_loop_idx = 3 * face_idx
                face_verts = mesh.loop_verts[start_loop_idx : (start_loop_idx + 3)]
                for i in range(3):
                    loop_idx = start_loop_idx + i
                    vert_idx = face_verts[i]
                    normals[vert_idx] += Vector(mesh.loop_normals[loop_idx])
                    if mesh.loop_uv1:
                        self.uv1[vert_idx] = mesh.loop_uv1[loop_idx]
                    if mesh.loop_uv2:
                        self.uv2[vert_idx] = mesh.loop_uv2[loop_idx]
                    if mesh.loop_tangents and mesh.loop_bitangents:
                        tangents[vert_idx] += Vector(mesh.loop_tangents[loop_idx])
                        bitangents[vert_idx] += Vector(mesh.loop_bitangents[loop_idx])
                        # TODO: is this correct?
                        tanspacenormals[vert_idx] += Vector(mesh.loop_normals[loop_idx])
                self.facelist.vertices.append(face_verts)
                self.facelist.uv.append(face_verts)
            normals = [normal.normalized() for normal in normals]
            self.normals = [normal[:3] for normal in normals]
            if mesh.loop_tangents and mesh.loop_bitangents:
                tangents = [tangent.normalized() for tangent in tangents]
                bitangents = [bitangent.normalized() for bitangent in bitangents]
                tanspacenormals = [normal.normalized() for normal in tanspacenormals]
                self.tangents = [tangent[:3] for tangent in tangents]
                self.bitangents = [bitangent[:3] for bitangent in bitangents]
                self.tangentspacenormals = [normal[:3] for normal in tanspacenormals]

        self.facelist.materials = mesh.face_materials
        self.facelist.normals = mesh.face_normals
