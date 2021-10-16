import bpy

from ... import kb_def


class KB_PT_empty(bpy.types.Panel):
    """
    Property panel for additional properties needed for the mdl file
    format. This is only available for EMPTY objects.
    It is located under the object data panel in the properties window
    """
    bl_label = "Odyssey Dummy Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'EMPTY')

    def draw(self, context):
        obj    = context.object
        layout = self.layout

        row = layout.row()
        row.prop(obj.nvb, "dummytype", text="Type")
        layout.separator()

        # Display properties depending on type of the empty
        if (obj.nvb.dummytype == kb_def.Dummytype.MDLROOT):
            row = layout.row()
            box = row.box()
            split = box.split()
            col = split.column()
            col.label(text = "Classification:")
            col.label(text = "Supermodel:")
            col.label(text = "Ignore Fog:")
            col.label(text = "Animation Scale:")
            if obj.nvb.classification == kb_def.Classification.CHARACTER:
                col.label(text = "Head Model:")
            col = split.column()
            col.prop(obj.nvb, "classification", text = "")
            col.prop(obj.nvb, "supermodel", text = "")
            col.prop(obj.nvb, "ignorefog", text = "")
            col.prop(obj.nvb, "animscale", text = "")
            if obj.nvb.classification == kb_def.Classification.CHARACTER:
                col.prop(obj.nvb, "headlink", text = "")
            box.operator("kb.recreate_armature")
            layout.separator()

            # Minimap Helper.
            # TODO: uncomment when compatible with Blender 2.8
            '''
            row = layout.row()
            box = row.box()
            box.label(text = 'Minimap Helper')
            row = box.row()
            row.prop(obj.nvb, 'minimapzoffset', text = 'z Offset')
            row = box.row()
            row.prop(obj.nvb, 'minimapsize', text = 'Minimap size')
            row = box.row()
            row.operator('kb.render_minimap', text = 'Render Minimap', icon='NONE')
            '''

            # All Children Settings Helper
            row = layout.row()
            box = row.box()
            box.label(text="Child Node Settings")
            row = box.row()
            row.label(text="Smoothgroups")
            row = box.row()
            op = row.operator("kb.children_smoothgroup", text="Direct")
            op.action = "DRCT"
            op = row.operator("kb.children_smoothgroup", text="Auto")
            op.action = "AUTO"
            op = row.operator("kb.children_smoothgroup", text="Single")
            op.action = "SING"
            op = row.operator("kb.children_smoothgroup", text="Separate")
            op.action = "SEPR"

        elif (obj.nvb.dummytype == kb_def.Dummytype.PWKROOT):
            pass

        elif (obj.nvb.dummytype == kb_def.Dummytype.DWKROOT):
            pass

        elif (obj.nvb.dummytype == kb_def.Dummytype.REFERENCE):
            row = layout.row()
            box = row.box()

            row = box.row()
            row.prop(obj.nvb, "refmodel")
            row = box.row()
            row.prop(obj.nvb, "reattachable")

        else:
            row = layout.row()
            box = row.box()

            row = box.row()
            row.prop(obj.nvb, "wirecolor")
            row = box.row()
            row.prop(obj.nvb, "dummysubtype")