import bpy


class KB_UL_path_points(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop_search(item, "point", bpy.data, "objects")