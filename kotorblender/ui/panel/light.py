import bpy


class KB_PT_light(bpy.types.Panel):
    """
    Property panel for additional light properties. This
    holds all properties not supported by blender at the moment,
    but used by OpenGL and the aurora engine. This is only available
    for LIGHT objects.
    It is located under the object data panel in the properties window
    """
    bl_label = "Odyssey Light Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'LIGHT')

    def draw(self, context):
        obj    = context.object
        layout = self.layout

        row = layout.row()
        row.prop(obj.nvb, "lighttype", text="Type")

        layout.separator()

        row = layout.row()
        box = row.box()

        row = box.row()
        row.prop(obj.nvb, "wirecolor", text="Wirecolor")
        row = box.row()
        row.prop(obj.nvb, "lightpriority", text="Priority")
        row = box.row()
        row.prop(obj.nvb, "radius", text="Radius")
        row = box.row()
        row.prop(obj.nvb, "multiplier", text="Multiplier")

        split = box.split()
        col = split.column(align=True)
        col.prop(obj.nvb, "ambientonly", text="Ambient Only")
        col.prop(obj.nvb, "shadow", text="Shadows")
        col = split.column(align=True)
        col.prop(obj.nvb, "fadinglight", text="Fading")
        col.prop(obj.nvb, "isdynamic", text="Dynamic Type")
        col.prop(obj.nvb, "affectdynamic", text="Affect dynamic")

        layout.separator()

        # Lens flares
        row = layout.row()
        row.enabled = (obj.nvb.lighttype == "NONE")
        box = row.box()
        row = box.row()
        row.prop(obj.nvb, "lensflares")
        sub = row.row(align=True)
        sub.active = obj.nvb.lensflares
        sub.prop(obj.nvb, "flareradius", text="Radius")
        row = box.row()
        row.active = obj.nvb.lensflares
        row.template_list("KB_UL_lightflares", "The_List", obj.nvb, "flareList", obj.nvb, "flareListIdx")
        col = row.column(align = True)
        col.operator("kb.lightflare_new", icon='ADD', text = "")
        col.operator("kb.lightflare_delete", icon='REMOVE', text = "")
        col.separator()
        col.operator("kb.lightflare_move", icon='TRIA_UP', text = "").direction = "UP"
        col.operator("kb.lightflare_move", icon='TRIA_DOWN', text = "").direction = "DOWN"
        if obj.nvb.flareListIdx >= 0 and len(obj.nvb.flareList) > 0:
            item = obj.nvb.flareList[obj.nvb.flareListIdx]
            row = box.row()
            row.active = obj.nvb.lensflares
            row.prop(item, "texture")
            row = box.row()
            row.active = obj.nvb.lensflares
            row.prop(item, "colorshift")
            row = box.row()
            row.active = obj.nvb.lensflares
            row.prop(item, "size")
            row.prop(item, "position")