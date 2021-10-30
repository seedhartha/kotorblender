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

from ... import defines

from .trimesh import TrimeshNode


class AabbNode(TrimeshNode):

    def __init__(self, name = "UNNAMED"):
        TrimeshNode.__init__(self, name)
        self.nodetype = "aabb"

        self.meshtype = defines.Meshtype.AABB

    def add_to_collection(self, collection):
        mesh = self.create_mesh(self.name)
        obj = bpy.data.objects.new(self.name, mesh)
        self.set_object_data(obj)
        collection.objects.link(obj)
        return obj

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
        for wokMat in defines.wok_materials:
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
        bpy.data.objects[self.objref].kb.lytposition = self.lytposition
