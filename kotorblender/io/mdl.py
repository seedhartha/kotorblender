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

import os

import bpy

from ..format.bwm.loader import BwmLoader
from ..format.bwm.saver import BwmSaver
from ..format.mdl.loader import MdlLoader
from ..format.mdl.saver import MdlSaver
from ..scene.modelnode.aabb import AabbNode
from ..scene.model import Model
from ..scene.walkmesh import Walkmesh

from .. import utils


def load_mdl(operator, filepath, options, position=(0.0, 0.0, 0.0)):
    operator.report({'INFO'}, "Loading model from '{}'".format(filepath))
    mdl = MdlLoader(filepath)
    model = mdl.load()

    pwk_walkmesh = None
    dwk_walkmesh1 = None
    dwk_walkmesh2 = None
    dwk_walkmesh3 = None

    if options.import_geometry and options.import_walkmeshes:
        wok_path = filepath[:-4] + ".wok"
        if os.path.exists(wok_path):
            wok = BwmLoader(wok_path, model.name)
            walkmesh = wok.load()
            aabb = model.find_node(lambda n: isinstance(n, AabbNode))
            aabb_wok = walkmesh.find_node(lambda n: isinstance(n, AabbNode))
            if aabb and aabb_wok:
                aabb.bwmposition = aabb_wok.bwmposition
                aabb.roomlinks = aabb_wok.roomlinks
                aabb.compute_lyt_position(aabb_wok)

        pwk_path = filepath[:-4] + ".pwk"
        if os.path.exists(pwk_path):
            operator.report({'INFO'}, "Loading walkmesh from '{}'".format(pwk_path))
            pwk = BwmLoader(pwk_path, model.name)
            pwk_walkmesh = pwk.load()

        dwk0_path = filepath[:-4] + "0.dwk"
        dwk1_path = filepath[:-4] + "1.dwk"
        dwk2_path = filepath[:-4] + "2.dwk"
        if os.path.exists(dwk0_path) and os.path.exists(dwk1_path) and os.path.exists(dwk2_path):
            operator.report({'INFO'}, "Loading walkmesh from '{}'".format(dwk0_path))
            dwk1 = BwmLoader(dwk0_path, model.name)
            operator.report({'INFO'}, "Loading walkmesh from '{}'".format(dwk1_path))
            dwk2 = BwmLoader(dwk1_path, model.name)
            operator.report({'INFO'}, "Loading walkmesh from '{}'".format(dwk2_path))
            dwk3 = BwmLoader(dwk2_path, model.name)
            dwk_walkmesh1 = dwk1.load()
            dwk_walkmesh2 = dwk2.load()
            dwk_walkmesh3 = dwk3.load()

    collection = bpy.context.collection
    model_root = model.import_to_collection(collection, options, position)

    if pwk_walkmesh:
        pwk_walkmesh.import_to_collection(model_root, collection, options)
    if dwk_walkmesh1 and dwk_walkmesh2 and dwk_walkmesh3:
        dwk_walkmesh1.import_to_collection(model_root, collection, options)
        dwk_walkmesh2.import_to_collection(model_root, collection, options)
        dwk_walkmesh3.import_to_collection(model_root, collection, options)

    # Reset Pose
    bpy.context.scene.frame_set(0)


def save_mdl(operator, filepath, options):
    # Reset Pose
    bpy.context.scene.frame_set(0)

    mdl_root = next(iter(obj for obj in bpy.context.selected_objects if utils.is_mdl_root(obj)), None)
    if not mdl_root:
        mdl_root = next(iter(obj for obj in bpy.context.collection.objects if utils.is_mdl_root(obj)), None)
    if not mdl_root:
        return

    # Export MDL
    model = Model.from_mdl_root(mdl_root, options)
    operator.report({'INFO'}, "Saving model to '{}'".format(filepath))
    mdl = MdlSaver(filepath, model, options.export_for_tsl)
    mdl.save()

    if options.export_walkmeshes:
        # Export WOK
        aabb_node = model.find_node(lambda node: isinstance(node, AabbNode))
        if aabb_node:
            base_path, _ = os.path.splitext(filepath)
            wok_path = base_path + ".wok"
            walkmesh = Walkmesh.from_aabb_node(aabb_node)
            operator.report({'INFO'}, "Saving walkmesh to '{}'".format(wok_path))
            bwm = BwmSaver(wok_path, walkmesh)
            bwm.save()

        # Export PWK, DWK
        xwk_roots = utils.find_objects(mdl_root, lambda obj: utils.is_pwk_root(obj) or utils.is_dwk_root(obj))
        for xwk_root in xwk_roots:
            base_path, _ = os.path.splitext(filepath)
            if utils.is_pwk_root(xwk_root):
                xwk_path = base_path + ".pwk"
            else:
                if xwk_root.name.endswith("open1"):
                    dwk_state = 1
                elif xwk_root.name.endswith("open2"):
                    dwk_state = 2
                elif xwk_root.name.endswith("closed"):
                    dwk_state = 0
                xwk_path = "{}{}.dwk".format(base_path, dwk_state)
            walkmesh = Walkmesh.from_root_object(xwk_root, options)
            operator.report({'INFO'}, "Saving walkmesh to '{}'".format(xwk_path))
            bwm = BwmSaver(xwk_path, walkmesh)
            bwm.save()
