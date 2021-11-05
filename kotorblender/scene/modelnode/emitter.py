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

from .geometry import GeometryNode


class EmitterNode(GeometryNode):

    emitter_attrs = [
        "deadspace",
        "blastradius",
        "blastlength",
        "num_branches",
        "controlptsmoothing",
        "xgrid",
        "ygrid",
        "spawntype",
        "update",
        "render_emitter",
        "blend",
        "texture",
        "chunk_name",
        "twosidedtex",
        "loop",
        "renderorder",
        "frame_blending",
        "depth_texture_name",
        "p2p",
        "p2p_sel",
        "affected_by_wind",
        "tinted",
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
        "random_birth_rate",
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

    def __init__(self, name="UNNAMED"):
        GeometryNode.__init__(self, name)
        self.nodetype = "emitter"

        self.meshtype = defines.Meshtype.EMITTER
        # object data
        self.deadspace = 0.0
        self.blastradius = 0.0
        self.blastlength = 0.0
        self.num_branches = 0
        self.controlptsmoothing = 0
        self.xgrid = 0
        self.ygrid = 0
        self.spawntype = 0
        self.update = ""
        self.render_emitter = ""
        self.blend = ""
        self.texture = ""
        self.chunk_name = ""
        self.twosidedtex = False
        self.loop = False
        self.renderorder = 0
        self.frame_blending = False
        self.depth_texture_name = defines.NULL
        # flags
        self.p2p = False
        self.p2p_sel = False
        self.affected_by_wind = False
        self.tinted = False
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
        self.random_birth_rate = 0.0
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

    def add_to_collection(self, collection):
        mesh = self.create_mesh(self.name)
        obj = bpy.data.objects.new(self.name, mesh)

        self.set_object_data(obj)
        collection.objects.link(obj)
        return obj

    def create_mesh(self, name):
        verts = [
            ((self.xsize/2) / 100.0, (self.ysize/2) / 100.0, 0.0),
            ((self.xsize/2) / 100.0, (-self.ysize/2) / 100.0, 0.0),
            ((-self.xsize/2) / 100.0, (-self.ysize/2) / 100.0, 0.0),
            ((-self.xsize/2) / 100.0, (self.ysize/2) / 100.0, 0.0)
        ]
        indices = [
            (0, 1, 2),
            (0, 2, 3)
        ]
        # Create the mesh itself
        mesh = bpy.data.meshes.new(name)
        mesh.vertices.add(len(verts))
        mesh.vertices.foreach_set("co", unpack_list(verts))
        num_faces = len(indices)
        mesh.loops.add(3 * num_faces)
        mesh.loops.foreach_set("vertex_index", unpack_list(indices))
        mesh.polygons.add(num_faces)
        mesh.polygons.foreach_set("loop_start", range(0, 3 * num_faces, 3))
        mesh.polygons.foreach_set("loop_total", (3,) * num_faces)
        mesh.update()
        return mesh

    def set_object_data(self, obj):
        GeometryNode.set_object_data(self, obj)

        obj.kb.meshtype = self.meshtype

        for attrname in self.emitter_attrs:
            value = getattr(self, attrname)
            # Enum translation is not pretty...
            if attrname == "spawntype":
                if value == 0:
                    value = "Normal"
                elif value == 1:
                    value = "Trail"
                else:
                    value = "NONE"
            elif attrname == "update":
                if value.title() not in ["Fountain", "Single", "Explosion", "Lightning"]:
                    value = "NONE"
                else:
                    value = value.title()
            elif attrname == "render_emitter":
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
                    obj.kb.p2p_type = "Bezier"
                else:
                    obj.kb.p2p_type = "Gravity"
                # p2p_type has update method, sets p2p_sel
                # except it doesn't seem to initially
                obj.kb.p2p_sel = self.p2p_sel
                continue
            setattr(obj.kb, attrname, value)

    def load_object_data(self, obj):
        GeometryNode.load_object_data(self, obj)

        for attrname in self.emitter_attrs:
            value = getattr(obj.kb, attrname)

            if attrname == "spawntype":
                if value == "Normal":
                    value = 0
                elif value == "Trail":
                    value = 1
                else:
                    continue
            elif attrname == "update":
                if value not in ["Fountain", "Single", "Explosion", "Lightning"]:
                    continue
            elif attrname == "render_emitter":
                if value not in ["Normal", "Billboard_to_Local_Z", "Billboard_to_World_Z", "Aligned_to_World_Z", "Aligned_to_Particle_Dir", "Motion_Blur"]:
                    continue
            elif attrname == "blend":
                if value == "Punch-Through":
                    value = "PunchThrough"
                elif value not in ["Lighten", "Normal"]:
                    continue
            elif attrname == "p2p_sel":
                self.p2p_sel = obj.kb.p2p_type == "Bezier"
                continue

            setattr(self, attrname, value)
