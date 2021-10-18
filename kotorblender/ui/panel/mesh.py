import bpy

from ... import defines


class KB_PT_mesh(bpy.types.Panel):
    """
    Property panel for additional mesh properties. This
    holds all properties not supported by blender at the moment,
    but used by OpenGL and the aurora engine. This is only available
    for MESH objects.
    It is located under the object data panel in the properties window
    """
    bl_label = "Odyssey Mesh Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return (context.object and \
                context.object.type == 'MESH' and \
                context.object.nvb.meshtype != defines.Meshtype.EMITTER)

    def draw(self, context):
        obj      = context.object
        layout   = self.layout

        row = layout.row()
        row.prop(obj.nvb, "meshtype", text="Type")

        layout.separator()

        if (obj.nvb.meshtype == defines.Meshtype.EMITTER):
            row = layout.row()
            box = row.box()

            row = box.row()
            row.prop(obj.nvb, "wirecolor", text="Wirecolor")
            row = box.row()
            row.prop_search(obj.nvb, "rawascii", bpy.data, "texts", text="Data")

        else: # Trimesh, danglymesh, skin
            row = layout.row()
            box = row.box()
            row = box.row()
            row.prop_search(obj.nvb, "bitmap", bpy.data, "images")
            row = box.row()
            row.prop_search(obj.nvb, "bitmap2", bpy.data, "images")
            row = box.row()
            row.prop(obj.nvb, "diffuse")
            row = box.row()
            row.prop(obj.nvb, "ambient")
            row = box.row()
            row.prop(obj.nvb, "selfillumcolor")
            row = box.row()
            row.prop(obj.nvb, "wirecolor")
            row = box.row()
            row.prop(obj.nvb, "alpha")
            row = box.row()
            row.operator("kb.rebuild_material_nodes")

            row = layout.row()
            box = row.box()
            split = box.split()
            col = split.column()
            col.prop(obj.nvb, "render", text="Render")
            col.prop(obj.nvb, "shadow", text="Shadow")
            col.prop(obj.nvb, "lightmapped", text="Lightmapped")
            col.prop(obj.nvb, "tangentspace", text="Tangentspace")
            col.prop(obj.nvb, "m_bIsBackgroundGeometry", text="Background Geometry")
            col = split.column()
            col.prop(obj.nvb, "beaming", text="Beaming")
            col.prop(obj.nvb, "inheritcolor", text="Inherit Color")
            col.prop(obj.nvb, "rotatetexture", text="Rotate Texture")
            col.prop(obj.nvb, "hologram_donotdraw")
            row = box.row()
            row.prop(obj.nvb, "transparencyhint", text="Transparency Hint")
            row = box.row()
            row.prop(obj.nvb, "animateuv")
            if obj.nvb.animateuv:
                row = box.row()
                split = box.split()
                col = split.column()
                col.prop(obj.nvb, "uvdirectionx")
                col.prop(obj.nvb, "uvjitter")
                col = split.column()
                col.prop(obj.nvb, "uvdirectiony")
                col.prop(obj.nvb, "uvjitterspeed")
            row = box.row()
            row.prop(obj.nvb, "dirt_enabled")
            if obj.nvb.dirt_enabled:
                row = box.row()
                row.prop(obj.nvb, "dirt_texture")
                row = box.row()
                row.prop(obj.nvb, "dirt_worldspace")
            row = box.row()
            row.label(text = "Smoothgroups")
            row.prop(obj.nvb, "smoothgroup", text="Smooth Group", expand = True)

            # Additional props for danglymeshes
            if (obj.nvb.meshtype == defines.Meshtype.DANGLYMESH):
                layout.separator()

                row = layout.row()
                box = row.box()
                row = box.row()
                row.label(text = "Danglymesh Properties")
                row = box.row()
                row.prop_search(obj.nvb, "constraints", obj, "vertex_groups", text="Constraints")
                row = box.row()
                row.prop(obj.nvb, "period", text="Period")
                row = box.row()
                row.prop(obj.nvb, "tightness", text="Tightness")
                row = box.row()
                row.prop(obj.nvb, "displacement", text="Displacement")

            # Additional props for skins
            elif (obj.nvb.meshtype == defines.Meshtype.SKIN):
                layout.separator()

                row = layout.row()
                box = row.box()
                row = box.row()
                row.label(text = "Create vertex group: ")
                row = box.row(align = True)
                row.prop_search(obj.nvb, "skingroup_obj", context.scene, "objects")
                row.operator("kb.skingroup_add", text = "", icon='ADD')

            # Additional props for aabb walkmeshes
            elif (obj.nvb.meshtype == defines.Meshtype.AABB):
                layout.separator()

                row = layout.row()
                box = row.box()
                row = box.row()
                row.prop(obj.nvb, "lytposition", text="LYT Position")
                row = box.row()
                row.operator("kb.load_wok_mats", text = "Load walkmesh materials", icon='NONE')