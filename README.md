# KotorBlender

This add-on is a fork of KotorBlender, upgraded to support Blender 2.8+. KotorBlender is in turn based on NeverBlender, forked from version 1.23a.

## Features

- Import & export MDL models, including walkmeshes
- Import & export LYT files
- Import & export PTH files

## Installation

1. Clone this repository or donwload a ZIP release
1. Copy or unpack the **kotorblender** folder into Blender addons directory, e.g. "C:/Users/USERNAME/AppData/Roaming/Blender Foundation/Blender/BLENDER_VERSION/scripts/addons"
1. Enable the add-on in Blender Preferences via Edit → Preferences → Add-ons

## Usage

### Modelling

1. Extract MDL, MDX, WOK, and, optionally, TPC and LYT files to a single directory (Kotor Tool, reone-tools, etc.)
1. Convert TPC files to TGA/TXI (reone-tools)
1. Import MDL into Blender via File → Import → KotOR Model (.mdl)
1. Create/modify models
1. Select an MDL root object to be exported 
1. Export MDL via File → Export → KotOR Model (.mdl)

### Baking Lightmaps

1. Select lightmapped objects and enter Edit mode
1. UV Unwrap Faces via UV → Lightmap Pack (increase Margin to avoid overlapping faces) 
1. For each lightmapped object:
    1. Select lightmap UV Map in Object Data Properties
    1. Select lightmap texture node in material node tree
    1. Remove a link between Multiply node and Base Color slot of Principled BSDF node
1. In Render Properties
    1. Set Render Engine to Cycles
    1. Set Device to GPU Compute, if available
    1. Set Margin to a lower number, e.g. 2
    1. Press the Bake button

Fine-tuning:

1. Disable rendering of walkmeshes in Outliner
1. Set Render samples to a higher number, e.g. 1024, to reduce noise
1. Enable Ambient Occlusion in World Properties and tweak Factor to improve contrast
1. Tweak light radii and color (try copying color from vanilla lightmaps)

### Editing Paths

1. Extract PTH file from the module's RIM file, e.g. "modules/danm13_s.rim" (Kotor Tool, reone-tools, etc.)
1. Import PTH into Blender via File → Import → KotOR Path (.pth)
1. Create/move path points, or modify path connections via Object Properties
1. Export PTH via File → Export → KotOR Path (.pth)

### Connecting Room Walkmeshes

1. Select a room walkmesh
1. Enter Edit mode and select two vertices adjacent to another room
1. Determine 0-based index of the other room into the LYT file
1. Enter Vertex Paint mode and set brush color to (0.0, G, 0.0), where G = (200 + room index) / 255
1. Ensure that brush blending mode is set to Mix, and brush strength is set to 1.0
1. Paint over the selected vertices

## Trivia

- Check "Image search" when importing to recursively search for textures in subdirectories

## Compatibility

- Blender 2.8+

## License

[GPL-3.0-or-later](LICENSE)
