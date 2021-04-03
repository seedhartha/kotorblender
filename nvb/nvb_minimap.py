"""
Functions related to minimap rendering.
"""

import bpy


def setup_minimap_render(mdlroot, scene, light_color = (1.0, 1.0, 1.0), alpha_mode = 'TRANSPARENT'):
    # Create the light if not already present in scene
    lightName = 'MinimapLight'
    camName  = 'MinimapCamera'

    if lightName in scene.objects:
        minimapLight = scene.objects[lightName]
    else:
        # Check if present in db
        if lightName in bpy.data.objects:
            minimapLight = bpy.data.objects[lightName]
        else:
            if lightName in bpy.data.lights:
                lightData = bpy.data.lights[lightName]
            else:
                lightData = bpy.data.lights.new(lightName, 'POINT')
            minimapLight = bpy.data.objects.new(lightName , lightData)
        bpy.context.collection.objects.link(minimapLight)
    # Adjust light properties
    # TODO: rewrite for Blender 2.8
    #minimapLight.data.use_specular = False
    minimapLight.data.color        = light_color
    #minimapLight.data.falloff_type = 'CONSTANT'
    minimapLight.data.distance     = (mdlroot.nvb.minimapzoffset+20.0)*2.0
    minimapLight.location.z        = mdlroot.nvb.minimapzoffset+20.0

    # Create the cam if not already present in scene
    if camName in scene.objects:
        minimapCam = scene.objects[camName]
    else:
        # Check if present in db
        if camName in bpy.data.objects:
            minimapCam = bpy.data.objects[camName]
        else:
            if camName in bpy.data.cameras:
                camData = bpy.data.cameras[camName]
            else:
                camData = bpy.data.cameras.new(camName)
            minimapCam = bpy.data.objects.new(camName, camData)
        bpy.context.collection.objects.link(minimapCam)
    # Adjust cam properties
    minimapCam.data.type        = 'ORTHO'
    minimapCam.data.ortho_scale = 10.0
    minimapCam.location.z       = mdlroot.nvb.minimapzoffset+20.0

    scene.camera = minimapCam
    # Adjust render settings
    # TODO: rewrite for Blender 2.8
    #scene.render.alpha_mode                 = alpha_mode
    #scene.render.use_antialiasing           = True
    #scene.render.pixel_filter_type          = 'BOX'
    #scene.render.antialiasing_samples       = '16'
    #scene.render.use_shadows                = False
    #scene.render.use_envmaps                = False
    scene.render.resolution_x               = mdlroot.nvb.minimapsize
    scene.render.resolution_y               = mdlroot.nvb.minimapsize / 2
    scene.render.resolution_percentage      = 100
    scene.render.image_settings.color_mode  = 'RGB'
    scene.render.image_settings.file_format = 'TARGA_RAW'
