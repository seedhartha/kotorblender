import bmesh
import bpy
import bpy_extras
from mathutils import Matrix, Quaternion, Vector

from . import nvb_def, nvb_io, nvb_material, nvb_txi, nvb_utils


class KB_OT_children_smoothgroup(bpy.types.Operator):
    bl_idname = "kb.children_smoothgroup"
    bl_label = "Smoothgroup settings on descendants"
    bl_options = {'UNDO'}

    action : bpy.props.StringProperty()

    def execute(self, context):
        descendants = nvb_utils.search_node_all(
            context.object, lambda o: o.type == 'MESH'
        )
        for d in descendants:
            d.nvb.smoothgroup = self.action
        return {'FINISHED'}


class KB_OT_toggle_smoothgroup(bpy.types.Operator):
    bl_idname = "kb.smoothgroup_toggle"
    bl_label = "Smoothgroup toggle"
    bl_options = {'UNDO'}

    sg_number : bpy.props.IntProperty()
    activity : bpy.props.IntProperty(default=0)

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.object.data)
        # the smoothgroup data layer
        sg_layer = bm.faces.layers.int.get(nvb_def.sg_layer_name)
        # convert sg_number to actual sg bitflag value
        sg_value = pow(2, self.sg_number)
        for face in bm.faces:
            if not face.select:
                continue
            if sg_value & face[sg_layer]:
                # turn off for face
                face[sg_layer] &= ~sg_value
            else:
                # turn on for face
                face[sg_layer] |= sg_value
        bmesh.update_edit_mesh(context.object.data)
        return {'FINISHED'}


class KB_OT_generate_smoothgroup(bpy.types.Operator):
    bl_idname = "kb.smoothgroup_generate"
    bl_label = "Smoothgroup generate"
    bl_options = {'UNDO'}

    action : bpy.props.EnumProperty(items=(
        ("ALL", "All Faces", "Generate smoothgroups for all faces, replacing current values"),
        ("EMPTY", "Empty Faces", "Generate smoothgroups for all faces without current assignments"),
        ("SEL", "Selected Faces", "Generate smoothgroups for all selected faces, replacing current values")
    ))

    def execute(self, context):
        ob = context.object

        # switch into object mode so that the mesh gets committed,
        # and sg layer is available and modifiable
        initial_mode = ob.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        # copy the mesh, applying modifiers w/ render settings
        mesh = ob.to_mesh(scene=context.scene, apply_modifiers=True, settings='RENDER')

        # get, or create, the smoothgroups data layer on the object mesh (not the copy)
        sg_list = ob.data.polygon_layers_int.get(nvb_def.sg_layer_name)
        if sg_list is None:
            sg_list = ob.data.polygon_layers_int.new(name=nvb_def.sg_layer_name)

        # make all the faces on mesh copy smooth,
        # allowing calc_smooth_groups to work
        for face in mesh.polygons:
            face.use_smooth = True
        (sg, _) = mesh.calc_smooth_groups(use_bitflags=True)

        # apply the calculated smoothgroups
        if self.action == "ALL":
            sg_list.data.foreach_set("value", sg)
        else:
            for face in mesh.polygons:
                if (self.action == "EMPTY" and \
                    sg_list.data[face.index].value == 0) or \
                   (self.action == "SEL" and face.select):
                    sg_list.data[face.index].value = sg[face.index]

        # return object to original mode
        bpy.ops.object.mode_set(mode=initial_mode)
        # remove the copied mesh
        bpy.data.meshes.remove(mesh)
        return {'FINISHED'}


class KB_OT_select_smoothgroup(bpy.types.Operator):
    bl_idname = "kb.smoothgroup_select"
    bl_label = "Smoothgroup select"
    bl_options = {'UNDO'}

    sg_number : bpy.props.IntProperty()
    action : bpy.props.EnumProperty(items=(
        ("SEL", "Select", "Select faces with this smoothgroup"),
        ("DESEL", "Deselect", "Deselect faces with this smoothgroup")
    ))

    @classmethod
    def description(self, context, properties):
        if self.action == "SEL":
            return "Select faces with this smoothgroup"
        else:
            return "Deselect faces with this smoothgroup"

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.object.data)
        bm.faces.ensure_lookup_table()
        # the smoothgroup data layer
        sg_layer = bm.faces.layers.int.get(nvb_def.sg_layer_name)
        # convert sg_number to actual sg bitflag value
        sg_value = pow(2, self.sg_number)

        for face in bm.faces:
            if sg_value & face[sg_layer]:
                # select/deselect face
                face.select_set(self.action == "SEL")
        # required to get the selection change to show in the 3D view
        bmesh.update_edit_mesh(context.object.data)
        return {'FINISHED'}


class KB_OT_texture_io(bpy.types.Operator):
    bl_idname = "kb.texture_info_io"
    bl_label = "Texture Info"
    bl_property = "action"
    bl_options = {'UNDO'}

    action : bpy.props.EnumProperty(items=(
        ("LOAD", "Load", "Import TXI file for this texture"),
        ("SAVE", "Save", "Export TXI file for this texture")
    ))

    def execute(self, context):
        if self.action == "SAVE":
            nvb_txi.save_txi(context.texture, self)
        else:
            nvb_txi.load_txi(context.texture, self)
        return {'FINISHED'}


class KB_OT_texture_box_ops(bpy.types.Operator):
    """ Hide/show Texture Info sub-groups"""
    bl_idname = "kb.texture_info_box_ops"
    bl_label = "Box Controls"
    bl_description = "Show/hide this property list"

    boxname : bpy.props.StringProperty(default="")

    def execute(self, context):
        if self.boxname == "":
            return {'FINISHED'}
        attrname = "box_visible_" + self.boxname
        texture = context.texture
        current_state = getattr(texture.nvb, attrname)
        setattr(texture.nvb, attrname, not current_state)
        return {'FINISHED'}


class KB_OT_skin_bone_ops(bpy.types.Operator):
    bl_idname = "kb.armature"
    bl_label = "Armature Operations"
    bl_options = {'UNDO'}

    def execute(self, context):
        mdl_root = nvb_utils.get_mdl_root_from_context()
        if mdl_root:
            # Begin creating bones from the rootdummy
            rootdummy = nvb_utils.search_node(mdl_root, lambda o: o.name.lower() == "rootdummy")
            if rootdummy:
                # (Re)create armature
                armature_name = "Armature_"+mdl_root.name
                if armature_name in bpy.data.armatures:
                    armature = bpy.data.armatures[armature_name]
                    bpy.data.armatures.remove(armature)
                armature = bpy.data.armatures.new(armature_name)
                armature_object = bpy.data.objects.new(armature_name, armature)
                armature_object.show_in_front = True
                bpy.context.collection.objects.link(armature_object)
                bpy.context.view_layer.objects.active = armature_object

                # Enter Edit Mode
                bpy.ops.object.mode_set(mode='EDIT')

                self._create_bones_recursive(armature, rootdummy)

                # Enter Pose Mode
                bpy.ops.object.mode_set(mode='POSE')

                self._create_armature_animation(armature_object, rootdummy)

                # Enter Object Mode
                bpy.ops.object.mode_set(mode='OBJECT')

                # Add Armature modifier to all skinmeshes
                skinmeshes = nvb_utils.search_node_all(mdl_root, lambda o: o.nvb.meshtype == nvb_def.Meshtype.SKIN)
                for mesh in skinmeshes:
                    modifier = mesh.modifiers.new(name="Armature", type="ARMATURE")
                    modifier.object = armature_object

        return {'FINISHED'}

    def _create_bones_recursive(self, armature, obj, parent_bone=None):
        # Skip Trimeshes whose Render flag is set to True
        if (obj.type == 'MESH') and obj.nvb.render:
            return

        bone = armature.edit_bones.new(obj.name)
        bone.parent = parent_bone
        bone.head = obj.matrix_world.to_translation()

        if obj.children:
            # If object has children, set bone tail to the average child location
            bone.tail = Vector([0.0] * 3)
            for child in obj.children:
                bone.tail += child.matrix_world.to_translation()
            bone.tail /= float(len(obj.children))

            # Recursively create bones from child objects
            for child in obj.children:
                self._create_bones_recursive(armature, child, bone)
        else:
            # If object has no children, place bone tail away from its parent
            parent_dir = (parent_bone.tail - parent_bone.head).normalized()
            bone.tail = bone.head + 0.1 * parent_dir

    def _create_armature_animation(self, armature_object, rootdummy):
        if not armature_object.animation_data:
            armature_object.animation_data_create()

        action = bpy.data.actions.new(armature_object.name)
        armature_object.animation_data.action = action

        self._copy_keyframes_to_bones_recursive(rootdummy, armature_object)

    def _copy_keyframes_to_bones_recursive(self, obj, armature_object):
        # Skip Trimeshes whose Render flag is set to True
        if (obj.type == 'MESH') and obj.nvb.render:
            return

        if obj.animation_data and obj.name in armature_object.pose.bones:
            bone = armature_object.pose.bones[obj.name]
            action = obj.animation_data.action
            frames = set()
            locations = dict()
            rotations = dict()
            for fcurve in action.fcurves:
                if fcurve.data_path == "location":
                    for kp in fcurve.keyframe_points:
                        frame = kp.co[0]
                        frames.add(frame)
                        if not kp.co[0] in locations:
                            locations[frame] = [0.0]*3
                        locations[frame][fcurve.array_index] = kp.co[1]
                elif fcurve.data_path == "rotation_quaternion":
                    for kp in fcurve.keyframe_points:
                        frame = kp.co[0]
                        frames.add(frame)
                        if not kp.co[0] in rotations:
                            rotations[frame] = [0.0]*4
                        rotations[frame][fcurve.array_index] = kp.co[1]
            for frame in sorted(frames):
                if frame in locations:
                    bone.location = Vector(locations[frame]) - obj.location
                    bone.keyframe_insert("location", frame=frame)
                if frame in rotations:
                    bone.rotation_quaternion = obj.rotation_quaternion.inverted() @ Quaternion(rotations[frame])
                    bone.keyframe_insert("rotation_quaternion", frame=frame)

        for child in obj.children:
            self._copy_keyframes_to_bones_recursive(child, armature_object)

class KB_OT_texture_ops(bpy.types.Operator):
    bl_idname = "kb.texture_info_ops"
    bl_label = "Texture Info Operations"
    bl_property = "action"
    bl_options = {'UNDO'}

    action : bpy.props.EnumProperty(items=(
        ("RESET", "Reset", "Reset the property to default value. This will prevent it from being written to TXI file output."),
        ("NYI", "Other", "")
    ))
    propname : bpy.props.StringProperty(default="")

    def execute(self, context):
        if self.propname == "":
            return {'FINISHED'}
        if self.action == "RESET":
            attr_def = getattr(bpy.types.ImageTexture.nvb[1]["type"], self.propname)[1]
            if "default" in attr_def:
                setattr(context.texture.nvb, self.propname, attr_def["default"])
        return {'FINISHED'}


class KB_OT_new_lightflare(bpy.types.Operator):
    """ Add a new item to the flare list """

    bl_idname = "kb.lightflare_new"
    bl_label  = "Add a new flare to a light"

    def execute(self, context):
        if (context.object.type == 'LIGHT'):
            context.object.nvb.flareList.add()

        return{'FINISHED'}


class KB_OT_delete_lightflare(bpy.types.Operator):
    """ Delete the selected item from the flare list """

    bl_idname = "kb.lightflare_delete"
    bl_label = "Deletes a flare from the light"

    @classmethod
    def poll(self, context):
        """ Enable only if the list isn't empty """
        return len(context.object.nvb.flareList) > 0

    def execute(self, context):
        flareList = context.object.nvb.flareList
        flareIdx  = context.object.nvb.flareListIdx

        flareList.remove(flareIdx)
        if flareIdx > 0:
            flareIdx =flareIdx - 1

        return{"FINISHED"}


class KB_OT_move_lightflare(bpy.types.Operator):
    """ Move an item in the flare list """

    bl_idname = "kb.lightflare_move"
    bl_label  = "Move an item in the flare list"

    direction : bpy.props.EnumProperty(items=(("UP", "Up", ""), ("DOWN", "Down", "")))

    @classmethod
    def poll(self, context):
        return len(context.object.nvb.flareList) > 0

    def move_index(self, context):
        flareList = context.object.nvb.flareList
        flareIdx  = context.object.nvb.flareListIdx

        listLength = len(flareList) - 1 # (index starts at 0)
        newIdx = 0
        if self.direction == "UP":
            newIdx = flareIdx - 1
        elif self.direction == "DOWN":
            newIdx = flareIdx + 1

        newIdx   = max(0, min(newIdx, listLength))
        context.object.nvb.flareListIdx = newIdx

    def execute(self, context):
        flareList = context.object.nvb.flareList
        flareIdx  = context.object.nvb.flareListIdx

        if self.direction == "DOWN":
            neighbour = flareIdx + 1
            flareList.move(flareIdx, neighbour)
            self.move_index(context)
        elif self.direction == "UP":
            neighbour = flareIdx - 1
            flareList.move(neighbour, flareIdx)
            self.move_index(context)
        else:
            return{'CANCELLED'}

        return{'FINISHED'}


class KB_OT_import_mdl(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Odyssey Engine model (.mdl)"""

    bl_idname = "kb.mdlimport"
    bl_label = "Import Odyssey MDL"
    bl_options = {'UNDO'}

    filename_ext = ".mdl"

    filter_glob : bpy.props.StringProperty(
            default = "*.mdl;*.mdl.ascii",
            options = {'HIDDEN'})

    importGeometry : bpy.props.BoolProperty(
            name = "Import Geometry",
            description = "Disable if only animations are needed",
            default = True)

    importWalkmesh : bpy.props.BoolProperty(
            name = "Import Walkmesh",
            description = "Attempt to load placeable and door walkmeshes",
            default = True)

    importSmoothGroups : bpy.props.BoolProperty(
            name = "Import Smooth Groups",
            description = "Import smooth groups as sharp edges",
            default = True)

    importMaterials : bpy.props.BoolProperty(
            name = "Import Materials",
            description = "Import materials",
            default = True)

    importAnim : bpy.props.BoolProperty(
            name = "Import Animations",
            description = "Import animations",
            default = True)

    textureSearch : bpy.props.BoolProperty(
            name = "Image search",
            description = "Search for images in subdirectories" \
                          " (Warning, may be slow)",
            default = False)

    createArmature : bpy.props.BoolProperty(
            name = "Create armature",
            description = "Create armature from bone nodes",
            default = False)

    # Hidden option, only used for batch minimap creation
    minimapMode : bpy.props.BoolProperty(
            name = "Minimap Mode",
            description = "Ignore lights and walkmeshes",
            default = False,
            options = {'HIDDEN'})

    minimapSkipFade : bpy.props.BoolProperty(
            name = "Minimap Mode: Import Fading Objects",
            description = "Ignore fading objects",
            default = False,
            options = {'HIDDEN'})

    def execute(self, context):
        return nvb_io.load_mdl(self, context, **self.as_keywords(ignore=("filter_glob",)))


class KB_OT_import_lyt(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Odyssey Engine layout (.lyt)"""

    bl_idname = "kb.lytimport"
    bl_label = "Import Odyssey LYT"
    bl_options = {'UNDO'}

    filename_ext = ".lyt"

    filter_glob : bpy.props.StringProperty(
        default="*.lyt",
        options={'HIDDEN'})

    importGeometry : bpy.props.BoolProperty(
            name = "Import Geometry",
            description = "Disable if only animations are needed",
            default = True)

    importWalkmesh : bpy.props.BoolProperty(
            name = "Import Walkmesh",
            description = "Attempt to load placeable and door walkmeshes",
            default = True)

    importSmoothGroups : bpy.props.BoolProperty(
            name = "Import Smooth Groups",
            description = "Import smooth groups as sharp edges",
            default = True)

    importMaterials : bpy.props.BoolProperty(
            name = "Import Materials",
            description = "Import materials",
            default = True)

    importAnim : bpy.props.BoolProperty(
            name = "Import Animations",
            description = "Import animations",
            default = True)

    textureSearch : bpy.props.BoolProperty(
            name="Image search",
            description="Search for images in subdirectories" \
                        " (Warning, may be slow)",
            default=False)

    def execute(self, context):
        return nvb_io.load_lyt(self, context, **self.as_keywords(ignore=("filter_glob",)))


class KB_OT_export_mdl(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export Odyssey Engine model (.mdl)"""

    bl_idname = "kb.mdlexport"
    bl_label  = "Export Odyssey MDL"

    filename_ext = ".mdl"

    filter_glob : bpy.props.StringProperty(
            default = "*.mdl;*.mdl.ascii",
            options = {'HIDDEN'})

    exports : bpy.props.EnumProperty(
            name = "Export",
            options = {'ENUM_FLAG'},
            items = (("ANIMATION", "Animations", "Export animations"),
                     ("WALKMESH", "Walkmesh", "Attempt to create walkmesh file (.pwk, .dwk or .wok depending on classification)"),
                     ),
            default = {"ANIMATION", "WALKMESH"})

    exportSmoothGroups : bpy.props.BoolProperty(
            name="Export Smooth Groups",
            description="Generate smooth groups from sharp edges" \
                        "(When disabled every face belongs to the same group)",
            default=True)

    applyModifiers : bpy.props.BoolProperty(
            name="Apply Modifiers",
            description="Apply Modifiers before exporting",
            default=True)

    def execute(self, context):
        return nvb_io.save_mdl(self, context, **self.as_keywords(ignore=("filter_glob","check_existing")))


class KB_OT_load_wok_materials(bpy.types.Operator):
    """
    Load all materials for aabb walkmeshes for the selected object. Current
    material slots will be deleted.
    """
    bl_idname = "kb.load_wok_mats"
    bl_label  = "Load walkmesh materials"

    def execute(self, context):
        """
        - Deletes all current materials
        - adds walkmesh materials
        """
        selected_object = context.object
        if (selected_object) and (selected_object.type == 'MESH'):
            object_mesh = selected_object.data

            # Remove all current material slots
            for _ in range(len(selected_object.material_slots)):
                bpy.ops.object.material_slot_remove()

            # Create materials
            for matDef in nvb_def.wok_materials:
                matName = matDef[0]

                # Walkmesh materials should be shared across multiple
                # walkmeshes, as they always identical
                if matName in bpy.data.materials.keys():
                    mat = bpy.data.materials[matName]
                else:
                    mat = bpy.data.materials.new(matName)

                    mat.diffuse_color      = [*matDef[1], 1.0]
                    mat.specular_color     = (0.0,0.0,0.0)
                    mat.specular_intensity = matDef[2]

                object_mesh.materials.append(mat)
        else:
            self.report({'INFO'}, "A mesh must be selected")
            return {'CANCELLED'}

        return {'FINISHED'}


class KB_OT_render_minimap(bpy.types.Operator):
    bl_idname = "kb.render_minimap"
    bl_label  = "Render Minimap"

    def execute(self, context):
        """
        - Creates an camera and a light
        - Renders Minimap
        """
        obj   = context.object
        scene = bpy.context.scene
        if obj and (obj.type == 'EMPTY'):
            if (obj.nvb.dummytype == nvb_def.Dummytype.MDLROOT):
                nvb_utils.setup_minimap_render(obj, scene)
                bpy.ops.render.render(use_viewport = True)

                self.report({'INFO'}, "Ready to render")
            else:
                self.report({'INFO'}, "A MDLROOT must be selected")
                return {'CANCELLED'}
        else:
            self.report({'INFO'}, "An Empty must be selected")
            return {'CANCELLED'}

        return {'FINISHED'}


class KB_OT_add_skingroup(bpy.types.Operator):
    bl_idname = "kb.skingroup_add"
    bl_label  = "Add new Skingroup"

    def execute(self, context):
        obj        = context.object
        skingrName = obj.nvb.skingroup_obj
        # Check if there is already a vertex group with this name
        if skingrName:
            if (skingrName not in obj.vertex_groups.keys()):
                # Create the vertex group
                obj.vertex_groups.new(name=skingrName)
                obj.nvb.skingroup_obj = ""

                self.report({'INFO'}, "Created vertex group " + skingrName)
                return{'FINISHED'}
            else:
                self.report({'INFO'}, "Duplicate Name")
                return {'CANCELLED'}
        else:
            self.report({'INFO'}, "Empty Name")
            return {'CANCELLED'}


class KB_OT_export_lyt(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export Odyssey Engine layout (.lyt)"""

    bl_idname = "kb.lytexport"
    bl_label  = "Export Odyssey LYT"

    filename_ext = ".lyt"

    filter_glob : bpy.props.StringProperty(
            default = "*.lyt",
            options = {'HIDDEN'})

    def _describe_object(self, obj):
        parent = nvb_utils.get_mdl_root(obj)
        orientation = obj.rotation_euler.to_quaternion()
        return "{} {} {:.7g} {:.7g} {:.7g} {:.7g} {:.7g} {:.7g} {:.7g}".format(parent.name if parent else "NULL", obj.name, *obj.matrix_world.translation, *orientation)

    def execute(self, context):
        with open(self.filepath, "w") as f:
            rooms = []
            doors = []
            others = []

            objects = bpy.context.selected_objects if len(bpy.context.selected_objects) > 0 else bpy.context.collection.objects
            for obj in objects:
                if obj.type == 'EMPTY':
                    if obj.nvb.dummytype == nvb_def.Dummytype.MDLROOT:
                        rooms.append(obj)
                    elif obj.name.lower().startswith("door"):
                        doors.append(obj)
                    else:
                        others.append(obj)

            f.write("beginlayout\n")
            f.write("  roomcount {}\n".format(len(rooms)))
            for room in rooms:
                f.write("    {} {:.7g} {:.7g} {:.7g}\n".format(room.name, *room.location))
            f.write("  trackcount 0\n")
            f.write("  obstaclecount 0\n")
            f.write("  doorhookcount {}\n".format(len(doors)))
            for door in doors:
                f.write("    {}\n".format(self._describe_object(door)))
            f.write("  othercount {}\n".format(len(others)))
            for other in others:
                f.write("    {}\n".format(self._describe_object(other)))
            f.write("donelayout\n")

        return {'FINISHED'}


class KB_OT_rebuild_material_nodes(bpy.types.Operator):
    """Rebuild material node tree of this object."""

    bl_idname = "kb.rebuild_material_nodes"
    bl_label = "Rebuild Material Nodes"

    def execute(self, context):
        if context.object and (context.object.type == 'MESH') and (context.object.nvb.meshtype != nvb_def.Meshtype.EMITTER):
            nvb_material.rebuild_material(context.object)

        return {'FINISHED'}
