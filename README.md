# KotorBlender

This add-on is a fork of KotorBlender, upgraded to support newer versions of Blender. KotorBlender is in turn based on NeverBlender, forked from version 1.23a.

## Features

- Import & export MDL models, including walkmeshes
- Import & export LYT files
- Import & export PTH files

## Installation

1. Clone GitHub repository or download the latest release
1. Copy **kotorblender** folder into Blender addons directory, e.g. "C:/Users/USERNAME/AppData/Roaming/Blender Foundation/Blender/BLENDER_VERSION/scripts/addons"
1. Enable add-on "Import-Export: KotorBlender" in Blender Preferences via Edit → Preferences → Add-ons

## Usage

### Modelling

1. Extract MDL, MDX and, optionally, TPC, WOK, PWK, DWK, and LYT files (Kotor Tool, reone-tools, etc.)
1. Convert TPC files to TGA/TXI (reone-tools)
1. Import MDL into Blender via File → Import → KotOR Model (.mdl)
1. Edit model
1. Select a MDL root object to be exported
1. Export MDL via File → Export → KotOR Model (.mdl)

### Lightmapping

Most of the time, it will not be possible to use vanilla lighting and UV maps to recreate lightmaps. Depending on the scene, it might be necessary to tweak or replace both.

UV mapping:

1. Select objects having the same lightmap texture and enter Edit mode
1. Unwrap faces via UV → Lightmap Pack (increase Margin to avoid overlapping faces)

Baking lightmaps:

1. Select objects to bake lightmaps for
    1. If no object is selected, all objects from selected collection will be used
1. In Render Properties
    1. Set Render Engine to Cycles
    1. Set Device to GPU Compute, if available
1. In Render Properties → KotOR Lightmaps
    1. Tweak number of Samples (higher numbers increase quality, but also increase render time)
    1. Tweak Margin
    1. Press the Bake button

Fine-tuning:

1. In Outliner disable rendering of obstructing geometry, e.g. skyboxes
1. Enable Ambient Occlusion in World Properties and tweak Factor to increase contrast 

### Connecting Room Walkmeshes

1. Select a room walkmesh
1. Enter Edit mode and select two vertices adjacent to another room
1. Determine 0-based index of the other room into the LYT file
1. Enter Vertex Paint mode and set brush color to (0.0, G, 0.0), where G = (200 + room index) / 255
1. Ensure that brush blending mode is set to Mix, and brush strength is set to 1.0
1. Paint over the selected vertices

### Editing Paths

1. Extract PTH file from the module's RIM file, e.g. "modules/danm13_s.rim" (Kotor Tool, reone-tools, etc.)
1. Import PTH into Blender via File → Import → KotOR Path (.pth)
1. Create/move path points, or modify path connections via Object Properties
1. Export PTH via File → Export → KotOR Path (.pth)

## Compatibility

Known to work with Blender 2.93 and 3.2.

## License

[GPL-3.0-or-later](LICENSE)
