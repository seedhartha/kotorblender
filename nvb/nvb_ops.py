import bmesh
import bpy
import bpy_extras
from mathutils import Matrix, Quaternion, Vector

from . import nvb_def, nvb_io, nvb_material, nvb_txi, nvb_utils


class NVB_OT_children_smoothgroup(bpy.types.Operator):
    bl_idname = "nvb.children_smoothgroup"
    bl_label = "Smoothgroup settings on descendants"
    #bl_property = 'action'
    bl_options = {'UNDO'}

    action : bpy.props.StringProperty()

    def execute(self, context):
        descendants = nvb_utils.search_node_all(
            context.object, lambda o: o.type == 'MESH'
        )
        for d in descendants:
            d.nvb.smoothgroup = self.action
        return {'FINISHED'}


class NVB_OT_toggle_smoothgroup(bpy.types.Operator):
    bl_idname = "nvb.smoothgroup_toggle"
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
            #print("face sg before: {}".format(face[sg_layer]))
            if sg_value & face[sg_layer]:
                # turn off for face
                face[sg_layer] &= ~sg_value
            else:
                # turn on for face
                face[sg_layer] |= sg_value
            #print("face sg after: {}".format(face[sg_layer]))
        bmesh.update_edit_mesh(context.object.data)
        return {'FINISHED'}


class NVB_OT_generate_smoothgroup(bpy.types.Operator):
    bl_idname = "nvb.smoothgroup_generate"
    bl_label = "Smoothgroup generate"
    bl_options = {'UNDO'}

    action : bpy.props.EnumProperty(items=(
        ('ALL', 'All Faces', 'Generate smoothgroups for all faces, replacing current values'),
        ('EMPTY', 'Empty Faces', 'Generate smoothgroups for all faces without current assignments'),
        ('SEL', 'Selected Faces', 'Generate smoothgroups for all selected faces, replacing current values')
    ))

    def execute(self, context):
        ob = context.object

        # switch into object mode so that the mesh gets committed,
        # and sg layer is available and modifiable
        initial_mode = ob.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        #ob.data.update(True, True)
        # copy the mesh, applying modifiers w/ render settings
        mesh = ob.to_mesh(scene=context.scene, apply_modifiers=True, settings='RENDER')
        #mesh.update(True, True)

        # get, or create, the smoothgroups data layer on the object mesh (not the copy)
        sg_list = ob.data.polygon_layers_int.get(nvb_def.sg_layer_name)
        if sg_list is None:
            sg_list = ob.data.polygon_layers_int.new(name=nvb_def.sg_layer_name)
        #ob.data.update()
        #mesh.calc_tessface()

        # make all the faces on mesh copy smooth,
        # allowing calc_smooth_groups to work
        for face in mesh.polygons:
            face.use_smooth = True
        (sg, sg_number) = mesh.calc_smooth_groups(use_bitflags=True)
        #print(sg)

        # apply the calculated smoothgroups
        if self.action == 'ALL':
            sg_list.data.foreach_set('value', sg)
        else:
            for face in mesh.polygons:
                if (self.action == 'EMPTY' and \
                    sg_list.data[face.index].value == 0) or \
                   (self.action == 'SEL' and face.select):
                    sg_list.data[face.index].value = sg[face.index]

        # return object to original mode
        bpy.ops.object.mode_set(mode=initial_mode)
        # remove the copied mesh
        bpy.data.meshes.remove(mesh)
        return {'FINISHED'}


class NVB_OT_select_smoothgroup(bpy.types.Operator):
    bl_idname = "nvb.smoothgroup_select"
    bl_label = "Smoothgroup select"
    #bl_property = 'action'
    bl_options = {'UNDO'}

    sg_number : bpy.props.IntProperty()
    action : bpy.props.EnumProperty(items=(
        ('SEL', 'Select', 'Select faces with this smoothgroup'),
        ('DESEL', 'Deselect', 'Deselect faces with this smoothgroup')
    ))

    @classmethod
    def description(self, context, properties):
        if self.action == 'SEL':
            return "Select faces with this smoothgroup"
        else:
            return "Deselect faces with this smoothgroup"

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.object.data)
        bm.faces.ensure_lookup_table()
        # the smoothgroup data layer
        sg_layer = bm.faces.layers.int.get(nvb_def.sg_layer_name)
        #print("test with #{} and sel/desel: {}".format(self.sg_number, str(sel)))
        # convert sg_number to actual sg bitflag value
        sg_value = pow(2, self.sg_number)

        for face in bm.faces:
            if sg_value & face[sg_layer]:
                # select/deselect face
                #print("select set: {}".format(str(sel)))
                face.select_set(self.action == 'SEL')
        # using this causes ALL connected geometry to be selected,
        # including additional faces, undesirable
        #bm.select_flush(sel)
        # required to get the selection change to show in the 3D view
        bmesh.update_edit_mesh(context.object.data)
        return {'FINISHED'}


class NVB_OT_texture_io(bpy.types.Operator):
    bl_idname = "nvb.texture_info_io"
    bl_label = "Texture Info"
    bl_property = 'action'
    bl_options = {'UNDO'}

    action : bpy.props.EnumProperty(items=(
        ('LOAD', 'Load', 'Import TXI file for this texture'),
        ('SAVE', 'Save', 'Export TXI file for this texture')
    ))

    def execute(self, context):
        if self.action == 'SAVE':
            nvb_txi.save_txi(context.texture, self)
            #if nvb_txi.save_txi(context.texture):
            #    self.report({'INFO'}, 'Successfully saved TXI file')
        else:
            nvb_txi.load_txi(context.texture, self)
            #if nvb_txi.load_txi(context.texture):
            #    self.report({'INFO'}, 'Successfully loaded TXI file')
        return {'FINISHED'}

class NVB_OT_texture_box_ops(bpy.types.Operator):
    """ Hide/show Texture Info sub-groups"""
    bl_idname = "nvb.texture_info_box_ops"
    bl_label = "Box Controls"
    bl_description = "Show/hide this property list"

    boxname : bpy.props.StringProperty(default='')

    def execute(self, context):
        if self.boxname == '':
            return {'FINISHED'}
        attrname = 'box_visible_' + self.boxname
        texture = context.texture
        current_state = getattr(texture.nvb, attrname)
        setattr(texture.nvb, attrname, not current_state)
        return {'FINISHED'}

class NVB_OT_skin_bone_ops(bpy.types.Operator):
    bl_idname = "nvb.armature"
    bl_label = "Armature Operations"
    #bl_property = 'action'
    bl_options = {'UNDO'}

    def boner(self, amt, obj, parent=None, pbone=None):
        bone = None
        if obj.nvb.meshtype == nvb_def.Meshtype.TRIMESH and \
           not obj.nvb.render:
            bone = amt.edit_bones.new(obj.name + 'Bone')
            bone.parent = pbone
            bone.head = pbone.tail
            bone.tail = obj.matrix_world.to_translation()
            #+ parent.matrix_world.to_translation()
            '''
            if pbone is not None:
                #bone.parent = amt.edit_bones[parent.name + 'Bone']
                bone.parent = pbone
                bone.head = bone.parent.tail
                bone.use_connect = False
                (trans, rot, scale) = bone.parent.matrix.decompose()
                vector = trans
                if not isinstance(rot, Quaternion):
                    rot = rot.to_quaternion()
                bone.tail = rot * obj.rotation_quaternion * bone.head
            else:
                #bone.head = obj.location
                bone.tail = obj.location
                rot = obj.rotation_euler
                if not isinstance(rot, Quaternion):
                    rot = rot.to_quaternion()
                #rot = Matrix.Translation((0, 0, 0))
                #vector = (1, 0, 0)
                bone.head = rot * obj.rotation_quaternion * bone.tail
            #bone.tail = rot * Vector(vector) + bone.head
            '''
        if bone is None:
            bone = pbone
        for c in obj.children:
            #print(obj.nvb.meshtype)
            #print(obj.nvb.render)
            self.boner(amt, c, obj, bone)

    def execute(self, context):
        #bpy.ops.object.add(type='ARMATURE', enter_editmode=True, location=context.scene.objects['cutscenedummy'].location)
        bpy.ops.object.armature_add()
        ob = bpy.context.scene.objects.active
        ob.show_x_ray = True
        ob.name = 'Armature'
        ob.show_axis = True
        ob.location = context.scene.objects['cutscenedummy'].location
        #context.scene.objects.active = ob
        print(dir(ob))
        amt = ob.data
        print(dir(amt))
        amt.name = 'ArmatureAmt'
        #amt.show_axes = True
        bpy.ops.object.mode_set(mode='EDIT')
        amt.edit_bones[0].tail = context.scene.objects['rootdummy'].location
        self.boner(amt, context.scene.objects['rootdummy'], pbone=amt.edit_bones[0])
        bpy.ops.object.mode_set(mode='OBJECT')
        #for name, obj in context.scene.objects.items():
        '''
        while len(obj.children):
            print(name)
            print(dir(obj))
            if obj.nvb.meshtype == nvb_def.Meshtype.TRIMESH and \
               not obj.nvb.render:
                pass
        '''
        return {'FINISHED'}

class NVB_OT_texture_ops(bpy.types.Operator):
    bl_idname = "nvb.texture_info_ops"
    bl_label = "Texture Info Operations"
    bl_property = 'action'
    bl_options = {'UNDO'}

    action : bpy.props.EnumProperty(items=(
        ('RESET', 'Reset', 'Reset the property to default value. This will prevent it from being written to TXI file output.'),
        ('NYI', 'Other', '')
    ))
    propname : bpy.props.StringProperty(default='')

    def execute(self, context):
        if self.propname == '':
            return {'FINISHED'}
        if self.action == 'RESET':
            #print(bpy.types.ImageTexture.nvb)
            #print(bpy.types.ImageTexture.nvb[1])
            #print(bpy.types.ImageTexture.nvb[1]['type'])
            #print(bpy.types.ImageTexture.nvb[1]['type'][self.propname])
            #print(getattr(bpy.types.ImageTexture.nvb[1]['type'], self.propname))
            #print(getattr(bpy.types.ImageTexture.nvb[1]['type'], self.propname)[1])
            #print(getattr(bpy.types.ImageTexture.nvb[1]['type'], self.propname)[1]['default'])
            #print(getattr(bpy.types.ImageTexture.nvb[1], self.propname)[1]['default'])
            #attr_def = getattr(bpy.types.ImageTexture.nvb[1], self.propname)[1]['default']
            attr_def = getattr(bpy.types.ImageTexture.nvb[1]['type'], self.propname)[1]
            if 'default' in attr_def:
                setattr(context.texture.nvb, self.propname, attr_def['default'])
        return {'FINISHED'}

class NVB_OT_new_lightflare(bpy.types.Operator):
    """ Add a new item to the flare list """

    bl_idname = 'nvb.lightflare_new'
    bl_label  = 'Add a new flare to a light'

    def execute(self, context):
        if (context.object.type == 'LIGHT'):
            context.object.nvb.flareList.add()

        return{'FINISHED'}


class NVB_OT_delete_lightflare(bpy.types.Operator):
    """ Delete the selected item from the flare list """

    bl_idname = 'nvb.lightflare_delete'
    bl_label = 'Deletes a flare from the light'

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

        return{'FINISHED'}


class NVB_OT_move_lightflare(bpy.types.Operator):
    """ Move an item in the flare list """

    bl_idname = 'nvb.lightflare_move'
    bl_label  = 'Move an item in the flare list'

    direction : bpy.props.EnumProperty(items=(('UP', 'Up', ''), ('DOWN', 'Down', '')))

    @classmethod
    def poll(self, context):
        return len(context.object.nvb.flareList) > 0

    def move_index(self, context):
        flareList = context.object.nvb.flareList
        flareIdx  = context.object.nvb.flareListIdx

        listLength = len(flareList) - 1 # (index starts at 0)
        newIdx = 0
        if self.direction == 'UP':
            newIdx = flareIdx - 1
        elif self.direction == 'DOWN':
            newIdx = flareIdx + 1

        newIdx   = max(0, min(newIdx, listLength))
        context.object.nvb.flareListIdx = newIdx

    def execute(self, context):
        flareList = context.object.nvb.flareList
        flareIdx  = context.object.nvb.flareListIdx

        if self.direction == 'DOWN':
            neighbour = flareIdx + 1
            flareList.move(flareIdx, neighbour)
            self.move_index(context)
        elif self.direction == 'UP':
            neighbour = flareIdx - 1
            flareList.move(neighbour, flareIdx)
            self.move_index(context)
        else:
            return{'CANCELLED'}

        return{'FINISHED'}


class NVB_OT_new_animevent(bpy.types.Operator):
    """ Add a new item to the event list """

    bl_idname = 'nvb.animevent_new'
    bl_label  = 'Add a new event to an animation'

    def execute(self, context):
        context.object.nvb.eventList.add()

        return{'FINISHED'}


class NVB_OT_delete_animevent(bpy.types.Operator):
    """ Delete the selected item from the event list """

    bl_idname = 'nvb.animevent_delete'
    bl_label = 'Deletes an event from an animation'

    @classmethod
    def poll(self, context):
        """ Enable only if the list isn't empty """
        return len(context.object.nvb.eventList) > 0

    def execute(self, context):
        eventList = context.object.nvb.eventList
        eventIdx  = context.object.nvb.eventListIdx

        eventList.remove(eventIdx)
        if eventIdx > 0:
            eventIdx = eventIdx - 1

        return{'FINISHED'}


class NVB_OT_move_animevent(bpy.types.Operator):
    """ Move an item in the event list """

    bl_idname = 'nvb.animevent_move'
    bl_label  = 'Move an item in the event  list'

    direction : bpy.props.EnumProperty(items=(('UP', 'Up', ''), ('DOWN', 'Down', '')))

    @classmethod
    def poll(self, context):
        return len(context.object.nvb.eventList) > 0

    def move_index(self, context):
        eventList = context.object.nvb.eventList
        eventIdx  = context.object.nvb.eventListIdx

        listLength = len(eventList) - 1 # (index starts at 0)
        newIdx = 0
        if self.direction == 'UP':
            newIdx = eventIdx - 1
        elif self.direction == 'DOWN':
            newIdx = eventIdx + 1

        newIdx   = max(0, min(newIdx, listLength))
        context.object.nvb.eventListIdx = newIdx

    def execute(self, context):
        eventList = context.object.nvb.eventList
        eventIdx  = context.object.nvb.eventListIdx

        if self.direction == 'DOWN':
            neighbour = eventIdx + 1
            eventList.move(eventIdx, neighbour)
            self.move_index(context)
        elif self.direction == 'UP':
            neighbour = eventIdx - 1
            eventList.move(neighbour, eventIdx)
            self.move_index(context)
        else:
            return{'CANCELLED'}

        return{'FINISHED'}


class NVB_OT_import_mdl(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Odyssey Engine model (.mdl)"""

    bl_idname = 'kb.mdlimport'
    bl_label = 'Import Odyssey MDL'
    bl_options = {'UNDO'}

    filename_ext = '.mdl'

    filter_glob : bpy.props.StringProperty(
            default = '*.mdl;*.mdl.ascii',
            options = {'HIDDEN'})

    importGeometry : bpy.props.BoolProperty(
            name = 'Import Geometry',
            description = 'Disable if only animations are needed',
            default = True)

    importWalkmesh : bpy.props.BoolProperty(
            name = 'Import Walkmesh',
            description = 'Attempt to load placeable and door walkmeshes',
            default = True)

    importSmoothGroups : bpy.props.BoolProperty(
            name = 'Import Smooth Groups',
            description = 'Import smooth groups as sharp edges',
            default = True)

    importAnim : bpy.props.BoolProperty(
            name = 'Import Animations',
            description = 'Import animations',
            default = True)

    materialMode : bpy.props.EnumProperty(
            name = 'Materials',
            items = (('NON', 'None', 'Don\'t create materials or import textures'),
                     ('SIN', 'Single', 'Create only one material per texture, shared between objects'),
                     ('MUL', 'Multiple', 'Create a seperate material for each object')),
            default = 'SIN')

    textureSearch : bpy.props.BoolProperty(
            name='Image search',
            description='Search for images in subdirectories' \
                        ' (Warning, may be slow)',
            default=False)

    # Hidden option, only used for batch minimap creation
    minimapMode : bpy.props.BoolProperty(
            name = 'Minimap Mode',
            description = 'Ignore lights and walkmeshes',
            default = False,
            options = {'HIDDEN'},
            )

    minimapSkipFade : bpy.props.BoolProperty(
            name = 'Minimap Mode: Import Fading Objects',
            description = 'Ignore fading objects',
            default = False,
            options = {'HIDDEN'},
            )

    def execute(self, context):
        return nvb_io.load_mdl(self, context, **self.as_keywords(ignore=('filter_glob',)))


class NVB_OT_import_lyt(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Odyssey Engine layout (.lyt)"""

    bl_idname = 'kb.lytimport'
    bl_label = 'Import Odyssey LYT'
    bl_options = {'UNDO'}

    filename_ext = '.lyt'

    filter_glob : bpy.props.StringProperty(
        default='*.lyt',
        options={'HIDDEN'})

    importGeometry : bpy.props.BoolProperty(
            name = 'Import Geometry',
            description = 'Disable if only animations are needed',
            default = True)

    importWalkmesh : bpy.props.BoolProperty(
            name = 'Import Walkmesh',
            description = 'Attempt to load placeable and door walkmeshes',
            default = True)

    importSmoothGroups : bpy.props.BoolProperty(
            name = 'Import Smooth Groups',
            description = 'Import smooth groups as sharp edges',
            default = True)

    importAnim : bpy.props.BoolProperty(
            name = 'Import Animations',
            description = 'Import animations',
            default = True)

    materialMode : bpy.props.EnumProperty(
            name = 'Materials',
            items = (('NON', 'None', 'Don\'t create materials or import textures'),
                     ('SIN', 'Single', 'Create only one material per texture, shared between objects'),
                     ('MUL', 'Multiple', 'Create a seperate material for each object')),
            default = 'SIN')

    textureSearch : bpy.props.BoolProperty(
            name='Image search',
            description='Search for images in subdirectories' \
                        ' (Warning, may be slow)',
            default=False)

    def execute(self, context):
        return nvb_io.load_lyt(self, context, **self.as_keywords(ignore=('filter_glob',)))


class NVB_OT_export_mdl(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export Odyssey Engine model (.mdl)"""

    bl_idname = 'kb.mdlexport'
    bl_label  = 'Export Odyssey MDL'

    filename_ext = '.mdl'

    filter_glob : bpy.props.StringProperty(
            default = '*.mdl;*.mdl.ascii',
            options = {'HIDDEN'})

    exports : bpy.props.EnumProperty(
            name = 'Export',
            options = {'ENUM_FLAG'},
            items = (('ANIMATION', 'Animations', 'Export animations'),
                     ('WALKMESH', 'Walkmesh', 'Attempt to create walkmesh file (.pwk, .dwk or .wok depending on classification)'),
                     ),
            default = {'ANIMATION', 'WALKMESH'})

    exportSmoothGroups : bpy.props.BoolProperty(
            name='Export Smooth Groups',
            description='Generate smooth groups from sharp edges' \
                        '(When disabled every face belongs to the same group)',
            default=True)

    applyModifiers : bpy.props.BoolProperty(
            name='Apply Modifiers',
            description='Apply Modifiers before exporting',
            default=True)

    def execute(self, context):
        return nvb_io.save_mdl(self, context, **self.as_keywords(ignore=('filter_glob','check_existing')))


class KB_OT_load_wok_materials(bpy.types.Operator):
    """
    Load all materials for aabb walkmeshes for the selected object. Current
    material slots will be deleted.
    """
    bl_idname = "nvb.load_wok_mats"
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
            for i in range(len(selected_object.material_slots)):
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
            self.report({'INFO'}, 'A mesh must be selected')
            return {'CANCELLED'}

        return {'FINISHED'}


class NVB_OT_render_minimap(bpy.types.Operator):
    bl_idname = "nvb.render_minimap"
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
                #bpy.ops.render.view_show()

                self.report({'INFO'}, 'Ready to render')
            else:
                self.report({'INFO'}, 'A MDLROOT must be selected')
                return {'CANCELLED'}
        else:
            self.report({'INFO'}, 'An Empty must be selected')
            return {'CANCELLED'}

        return {'FINISHED'}


class NVB_OT_add_skingroup(bpy.types.Operator):
    bl_idname = "nvb.skingroup_add"
    bl_label  = "Add new Skingroup"

    def execute(self, context):
        obj        = context.object
        skingrName = obj.nvb.skingroup_obj
        # Check if there is already a vertex group with this name
        if skingrName:
            if (skingrName not in obj.vertex_groups.keys()):
                # Create the vertex group
                vertGroup = obj.vertex_groups.new(name=skingrName)
                obj.nvb.skingroup_obj = ''

                self.report({'INFO'}, 'Created vertex group ' + skingrName)
                return{'FINISHED'}
            else:
                self.report({'INFO'}, 'Duplicate Name')
                return {'CANCELLED'}
        else:
            self.report({'INFO'}, 'Empty Name')
            return {'CANCELLED'}


class NVB_OT_rename_animscene(bpy.types.Operator):
    bl_idname = "nvb.animscene_rename"
    bl_label  = "Rename animation scene"

    @classmethod
    def poll(self, context):
        obj = context.object
        return (obj.type == 'EMPTY') and (obj.nvb.dummytype == nvb_def.Dummytype.MDLROOT) and obj.nvb.isanimation

    def execute(self, context):
        obj         = context.object
        newAnimName = obj.nvb.newanimname
        oldAnimName = obj.nvb.animname
        sourceScene = context.scene
        # Check if there is already a scene with this animation name
        if (newAnimName  != ''):
            if (newAnimName not in bpy.data.scenes):
                if nvb_utils.copy_anim_scene_check(obj, newAnimName, oldAnimName):
                    sourceScene.name = newAnimName

                    animRootDummy = nvb_utils.rename_anim_scene(obj, newAnimName, oldAnimName)
                    animRootDummy.nvb.animname    = newAnimName
                    animRootDummy.nvb.newanimname = ''

                    sourceScene.update()
                else:
                    self.report({'INFO'}, 'Duplicate Object')
                    return {'CANCELLED'}
            else:
                self.report({'INFO'}, 'Scene already present')
                return {'CANCELLED'}
        else:
            self.report({'INFO'}, 'Empty Name')
            return {'CANCELLED'}

        self.report({'INFO'}, 'Renamed animation ' + oldAnimName + ' to ' + newAnimName)
        return{'FINISHED'}


class NVB_OT_add_animscene(bpy.types.Operator):
    bl_idname = "nvb.animscene_add"
    bl_label  = "Add animation scene"

    @classmethod
    def poll(self, context):
        obj = context.object
        return (obj.type == 'EMPTY') and (obj.nvb.dummytype == nvb_def.Dummytype.MDLROOT)

    def execute(self, context):
        obj         = context.object
        newAnimName = obj.nvb.newanimname
        oldAnimName = obj.nvb.animname
        sourceScene = context.scene
        # Check if there is already a scene with this animation name
        if (newAnimName  != ''):
            if (newAnimName not in bpy.data.scenes):
                if nvb_utils.copy_anim_scene_check(obj, newAnimName, oldAnimName):
                    # Create the scene
                    newScene = bpy.data.scenes.new(newAnimName)
                    # Set fps
                    newScene.render.fps   = nvb_def.fps
                    newScene.frame_start = sourceScene.frame_start
                    newScene.frame_end   = sourceScene.frame_end

                    animRootDummy = nvb_utils.copy_anim_scene(newScene, obj, newAnimName, oldAnimName)
                    animRootDummy.nvb.isanimation = True
                    animRootDummy.nvb.animname    = newAnimName
                    animRootDummy.nvb.newanimname = ''

                    newScene.update()
                else:
                    self.report({'INFO'}, 'Duplicate Objects')
                    return {'CANCELLED'}
            else:
                self.report({'INFO'}, 'Scene already present')
                return {'CANCELLED'}
        else:
            self.report({'INFO'}, 'Empty Name')
            return {'CANCELLED'}

        self.report({'INFO'}, 'New animation ' + newAnimName)
        return{'FINISHED'}


class NVB_OT_export_lyt(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export Odyssey Engine layout (.lyt)"""

    bl_idname = 'kb.lytexport'
    bl_label  = 'Export Odyssey LYT'

    filename_ext = '.lyt'

    filter_glob : bpy.props.StringProperty(
            default = '*.lyt',
            options = {'HIDDEN'})

    def execute(self, context):
        with open(self.filepath, 'w') as f:
            rooms = []
            doors = []
            others = []

            objects = bpy.context.selected_objects if len(bpy.context.selected_objects) > 0 else bpy.context.collection.objects
            for obj in objects:
                if obj.type == 'EMPTY':
                    if obj.nvb.dummytype == nvb_def.Dummytype.MDLROOT:
                        rooms.append(obj)
                    elif obj.name.lower().startswith('door'):
                        doors.append(obj)
                    else:
                        others.append(obj)

            f.write('beginlayout\n')
            f.write('  roomcount {}\n'.format(len(rooms)))
            for room in rooms:
                f.write('    {} {:.7g} {:.7g} {:.7g}\n'.format(room.name, *room.location))
            f.write('  trackcount 0\n')
            f.write('  obstaclecount 0\n')
            f.write('  doorhookcount {}\n'.format(len(doors)))
            for door in doors:
                parent = nvb_utils.get_mdl_root(door)
                orientation = door.rotation_euler.to_quaternion()
                f.write('    {} {} {:.7g} {:.7g} {:.7g} {:.7g} {:.7g} {:.7g} {:.7g}\n'.format(parent.name if parent else 'NULL', door.name, *door.matrix_world.translation, *orientation))
            f.write('  othercount {}\n'.format(len(others)))
            for other in others:
                parent = nvb_utils.get_mdl_root(other)
                orientation = other.rotation_euler.to_quaternion()
                f.write('    {} {} {:.7g} {:.7g} {:.7g} {:.7g} {:.7g} {:.7g} {:.7g}\n'.format(parent.name if parent else 'NULL', other.name, *other.matrix_world.translation, *orientation))
            f.write('donelayout\n')

        return {'FINISHED'}


class KB_OT_rebuild_material_nodes(bpy.types.Operator):
    """Rebuild material node tree of this object."""

    bl_idname = 'kb.rebuild_material_nodes'
    bl_label = "Rebuild Material Nodes"

    def execute(self, context):
        if context.object and (context.object.type == 'MESH') and (context.object.nvb.meshtype != nvb_def.Meshtype.EMITTER):
            # Create a material if it does not exist
            mesh = context.object.data
            if len(mesh.materials) == 0:
                if context.object.name in bpy.data.materials:
                    material = bpy.data.materials[context.object.name]
                else:
                    material = bpy.data.materials.new(context.object.name)
                mesh.materials.append(material)
            else:
                material = context.object.active_material

            nvb_material.rebuild_material(material, context.object.nvb)

        return {'FINISHED'}
