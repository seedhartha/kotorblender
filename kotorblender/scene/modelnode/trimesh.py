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

from math import cos, radians, sqrt

import bpy

from bpy_extras.io_utils import unpack_list
from mathutils import Vector

from ...defines import NormalsAlgorithm

from ... import defines, glob, utils

from .. import material

from .geometry import GeometryNode

MERGE_DISTANCE = 1e-4
MERGE_DISTANCE_UV = 1e-4

UV_MAP_DIFFUSE = "UVMap"
UV_MAP_LIGHTMAP = "UVMap_lm"


class FaceList:
    def __init__(self):
        self.vertices = []  # vertex indices
        self.uv = []  # UV indices
        self.materials = []
        self.normals = []


class TrimeshNode(GeometryNode):

    def __init__(self, name="UNNAMED"):
        GeometryNode.__init__(self, name)
        self.nodetype = "trimesh"

        # Properties
        self.meshtype = defines.Meshtype.TRIMESH
        self.center = (0.0, 0.0, 0.0)  # Unused ?
        self.lightmapped = 0
        self.render = 1
        self.shadow = 1
        self.beaming = 0
        self.inheritcolor = 0  # Unused ?
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
        self.bitmap = defines.NULL
        self.bitmap2 = defines.NULL
        self.tangentspace = 0
        self.rotatetexture = 0

        # Vertices
        self.verts = []
        self.normals = []
        self.uv1 = []
        self.uv2 = []
        self.tangents = []
        self.bitangents = []
        self.tangentspacenormals = []

        # Faces
        self.facelist = FaceList()

        # Internal
        self.sharp_edges = set()
        self.eval_mesh = None

    def add_to_collection(self, collection):
        mesh = self.create_mesh(self.name)
        obj = bpy.data.objects.new(self.name, mesh)
        self.set_object_data(obj)

        if glob.build_materials and self.roottype == "mdl":
            material.rebuild_object_material(obj)

        collection.objects.link(obj)
        return obj

    def create_mesh(self, name):
        if glob.normals_algorithm == NormalsAlgorithm.SHARP_EDGES:
            self.merge_similar_vertices()

        # Create the mesh itself
        mesh = bpy.data.meshes.new(name)
        mesh.vertices.add(len(self.verts))
        mesh.vertices.foreach_set("co", unpack_list(self.verts))
        num_faces = len(self.facelist.vertices)
        mesh.loops.add(3 * num_faces)
        mesh.loops.foreach_set("vertex_index", unpack_list(self.facelist.vertices))
        mesh.polygons.add(num_faces)
        mesh.polygons.foreach_set("loop_start", range(0, 3 * num_faces, 3))
        mesh.polygons.foreach_set("loop_total", (3,) * num_faces)
        mesh.polygons.foreach_set("use_smooth", [True] * num_faces)

        # Create UV map
        if len(self.uv1) > 0:
            uv = unpack_list([self.uv1[i] for indices in self.facelist.uv for i in indices])
            uv_layer = mesh.uv_layers.new(name=UV_MAP_DIFFUSE, do_init=False)
            uv_layer.data.foreach_set("uv", uv)

        # Create lightmap UV map
        if len(self.uv2) > 0:
            uv = unpack_list([self.uv2[i] for indices in self.facelist.uv for i in indices])
            uv_layer = mesh.uv_layers.new(name=UV_MAP_LIGHTMAP, do_init=False)
            uv_layer.data.foreach_set("uv", uv)

        mesh.update()

        self.post_process_mesh(mesh)

        return mesh

    def merge_similar_vertices(self):
        def cos_angle_between(a, b):
            len2_a = sum([a[i] * a[i] for i in range(3)])
            if len2_a == 0.0:
                return -1.0
            len2_b = sum([b[i] * b[i] for i in range(3)])
            if len2_b == 0.0:
                return -1.0
            dot = sum([a[i] * b[i] for i in range(3)])
            return dot / sqrt(len2_a * len2_b)

        # Sort vertices into unique and duplicate

        new_idx_by_old_idx = dict()
        unique_indices = []
        split_normals = []
        for vert_idx, vert in enumerate(self.verts):
            if vert_idx in new_idx_by_old_idx:
                continue
            num_unique = len(unique_indices)
            normal = self.normals[vert_idx]
            normals = [normal]
            if self.uv1:
                uv1 = self.uv1[vert_idx]
            if self.uv2:
                uv2 = self.uv2[vert_idx]
            for other_vert_idx in range(vert_idx+1, len(self.verts)):
                if other_vert_idx in new_idx_by_old_idx:
                    continue
                other_vert = self.verts[other_vert_idx]
                other_normal = self.normals[other_vert_idx]
                if self.uv1:
                    other_uv1 = self.uv1[other_vert_idx]
                if self.uv2:
                    other_uv2 = self.uv2[other_vert_idx]
                # Vertices are similar if their coords and UV are very close, and angle between their normals is acute
                if (utils.is_close_3(vert, other_vert, MERGE_DISTANCE) and
                        ((not self.uv1) or utils.is_close_2(uv1, other_uv1, MERGE_DISTANCE_UV)) and
                        ((not self.uv2) or utils.is_close_2(uv2, other_uv2, MERGE_DISTANCE_UV)) and
                        cos_angle_between(normal, other_normal) > 0.5):
                    new_idx_by_old_idx[other_vert_idx] = num_unique
                    normals.append(other_normal)
            new_idx_by_old_idx[vert_idx] = num_unique
            unique_indices.append(vert_idx)
            split_normals.append(normals)

        # Compact vertices

        self.compact_vertices(unique_indices, split_normals)

        # Determine sharp vertices

        sharp_verts = [False] * len(self.verts)
        cos_angle_sharp = cos(radians(glob.sharp_edge_angle))
        for vert_idx, normals in enumerate(split_normals):
            # Vertex is sharp if an angle between at least two of its split normals exceeds threshold
            for normal_idx, normal in enumerate(normals):
                if sharp_verts[vert_idx]:
                    break
                for other_normal_idx in range(normal_idx+1, len(normals)):
                    other_normal = normals[other_normal_idx]
                    if cos_angle_between(normal, other_normal) < cos_angle_sharp:
                        sharp_verts[vert_idx] = True
                        break

        # Fix face vertex indices, determine sharp edges

        for face_idx, old_face in enumerate(self.facelist.vertices):
            new_face = [new_idx_by_old_idx[old_face[i]] for i in range(3)]
            self.facelist.vertices[face_idx] = new_face
            self.facelist.uv[face_idx] = new_face

            # Edge is sharp if both of its vertices are sharp

            edges = [tuple(sorted(pair)) for pair in [(new_face[0], new_face[1]), (new_face[1], new_face[2]), (new_face[2], new_face[0])]]
            for edge in edges:
                if sharp_verts[edge[0]] and sharp_verts[edge[1]]:
                    self.sharp_edges.add(edge)

    def compact_vertices(self, unique_indices, split_normals):
        for new_idx, old_idx in enumerate(unique_indices):
            normal = Vector()
            for n in split_normals[new_idx]:
                for i in range(3):
                    normal[i] += n[i]
            normal.normalize()

            self.verts[new_idx] = self.verts[old_idx]
            self.normals[new_idx] = tuple(normal[:3])
            if self.uv1:
                self.uv1[new_idx] = self.uv1[old_idx]
            if self.uv2:
                self.uv2[new_idx] = self.uv2[old_idx]

        num_unique = len(unique_indices)
        self.verts = self.verts[:num_unique]
        self.normals = self.normals[:num_unique]
        if self.uv1:
            self.uv1 = self.uv1[:num_unique]
        if self.uv2:
            self.uv2 = self.uv2[:num_unique]

    def post_process_mesh(self, mesh):
        if glob.normals_algorithm == NormalsAlgorithm.SHARP_EDGES:
            # Mark sharp edges
            for edge in mesh.edges:
                if tuple(sorted(edge.vertices)) in self.sharp_edges:
                    edge.use_edge_sharp = True
        elif glob.normals_algorithm == NormalsAlgorithm.CUSTOM:
            # Set custom normals
            mesh.normals_split_custom_set_from_vertices(self.normals)
            mesh.use_auto_smooth = True

    def set_object_data(self, obj):
        GeometryNode.set_object_data(self, obj)

        obj.kb.meshtype = self.meshtype
        obj.kb.bitmap = self.bitmap if not utils.is_null(self.bitmap) else ""
        obj.kb.bitmap2 = self.bitmap2 if not utils.is_null(self.bitmap2) else ""
        obj.kb.alpha = self.alpha
        obj.kb.lightmapped = (self.lightmapped == 1)
        obj.kb.render = (self.render == 1)
        obj.kb.shadow = (self.shadow == 1)
        obj.kb.beaming = (self.beaming == 1)
        obj.kb.tangentspace = (self.tangentspace == 1)
        obj.kb.inheritcolor = (self.inheritcolor == 1)
        obj.kb.rotatetexture = (self.rotatetexture == 1)
        obj.kb.background_geometry = (self.background_geometry == 1)
        obj.kb.dirt_enabled = (self.dirt_enabled == 1)
        obj.kb.dirt_texture = self.dirt_texture
        obj.kb.dirt_worldspace = self.dirt_worldspace
        obj.kb.hologram_donotdraw = (self.hologram_donotdraw == 1)
        obj.kb.animateuv = (self.animateuv == 1)
        obj.kb.uvdirectionx = self.uvdirectionx
        obj.kb.uvdirectiony = self.uvdirectiony
        obj.kb.uvjitter = self.uvjitter
        obj.kb.uvjitterspeed = self.uvjitterspeed
        obj.kb.transparencyhint = self.transparencyhint
        obj.kb.selfillumcolor = self.selfillumcolor
        obj.kb.diffuse = self.diffuse
        obj.kb.ambient = self.ambient

        if glob.normals_algorithm == NormalsAlgorithm.SHARP_EDGES:
            modifier = obj.modifiers.new(name="EdgeSplit", type='EDGE_SPLIT')
            modifier.use_edge_angle = False

    def load_object_data(self, obj):
        GeometryNode.load_object_data(self, obj)

        self.meshtype = obj.kb.meshtype
        self.bitmap = obj.kb.bitmap if obj.kb.bitmap else defines.NULL
        self.bitmap2 = obj.kb.bitmap2 if obj.kb.bitmap2 else ""
        self.alpha = obj.kb.alpha
        self.lightmapped = 1 if obj.kb.lightmapped else 0
        self.render = 1 if obj.kb.render else 0
        self.shadow = 1 if obj.kb.shadow else 0
        self.beaming = 1 if obj.kb.beaming else 0
        self.tangentspace = 1 if obj.kb.tangentspace else 0
        self.inheritcolor = 1 if obj.kb.inheritcolor else 0
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

        depsgraph = bpy.context.evaluated_depsgraph_get()
        mesh = self.eval_mesh = obj.evaluated_get(depsgraph).data
        mesh.calc_loop_triangles()

        for vert in mesh.vertices:
            self.verts.append(vert.co[:3])

        if glob.export_custom_normals and mesh.has_custom_normals:
            mesh.calc_normals_split()
            normals = dict()
            for loop in mesh.loops:
                vert_idx = loop.vertex_index
                if loop.vertex_index not in normals:
                    normals[vert_idx] = loop.normal
                else:
                    normals[vert_idx] += loop.normal
            for vert_idx in range(len(mesh.vertices)):
                normal = normals[vert_idx].normalized()
                self.normals.append(normal)
        else:
            for vert in mesh.vertices:
                self.normals.append(vert.normal[:3])

        self.uv1 = self.get_uv_from_uv_layer(mesh, UV_MAP_DIFFUSE)
        self.uv2 = self.get_uv_from_uv_layer(mesh, UV_MAP_LIGHTMAP)

        if self.tangentspace:
            num_verts = len(mesh.vertices)
            self.tangents = [Vector() for _ in range(num_verts)]
            self.bitangents = [Vector() for _ in range(num_verts)]
            self.tangentspacenormals = [Vector() for _ in range(num_verts)]
            if self.uv1:
                mesh.calc_tangents(uvmap=UV_MAP_DIFFUSE)

        for tri in mesh.loop_triangles:
            self.facelist.vertices.append(tri.vertices[:3])
            self.facelist.uv.append(tri.vertices[:3])
            self.facelist.materials.append(tri.material_index)
            self.facelist.normals.append(tri.normal)

            if self.tangentspace and self.uv1:
                for loop in [mesh.loops[i] for i in tri.loops]:
                    vert_idx = loop.vertex_index
                    self.tangents[vert_idx] += loop.tangent
                    self.bitangents[vert_idx] += loop.bitangent
                    self.tangentspacenormals[vert_idx] += loop.normal

        if self.tangentspace:
            if self.uv1:
                for vert_idx in range(num_verts):
                    self.tangents[vert_idx].normalize()
                    self.bitangents[vert_idx].normalize()
                    self.tangentspacenormals[vert_idx].normalize()
            else:
                for vert_idx in range(num_verts):
                    self.tangents[vert_idx] = Vector((1.0, 0.0, 0.0))
                    self.bitangents[vert_idx] = Vector((0.0, 1.0, 0.0))
                    self.tangentspacenormals[vert_idx] = Vector((0.0, 0.0, 1.0))

    def get_uv_from_uv_layer(self, mesh, layer_name):
        if not layer_name in mesh.uv_layers:
            return []
        layer_data = mesh.uv_layers[layer_name].data
        tverts = dict()
        for tri in mesh.loop_triangles:
            for vert_idx, loop_idx in zip(tri.vertices, tri.loops):
                tverts[vert_idx] = layer_data[loop_idx].uv[:2]
        return [v for _, v in sorted(tverts.items())]
