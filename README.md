# KotorBlender

This add-on is a fork of KotorBlender, upgraded to support Blender 2.8+. KotorBlender is in turn based on NeverBlender, forked from version 1.23a.

## Features

- Import & export ASCII MDL models: geometry, materials, animations, walkmeshes and TXI files
- Import & export LYT files
- Import & export ASCII PTH files

## Installation

1. Clone this repository or donwload a ZIP release
2. Copy or unpack the **kotorblender** folder into Blender addons directory, e.g. "C:/Users/USERNAME/AppData/Roaming/Blender Foundation/Blender/BLENDER_VERSION/scripts/addons"
3. Enable the add-on in Blender Preferences via Edit → Preferences → Add-ons

## Usage

### Modelling

1. Extract MDL, MDX, WOK, and, optionally, TPC and LYT files to a single directory (Kotor Tool, reone-tools, etc.)
2. Convert TPC files to TGA/TXI (reone-tools)
3. Convert binary MDL to ASCII MDL using MDLops or MDLedit
4. Import ASCII MDL into Blender via File → Import → KotOR Model (.mdl)
5. Create/modify models
6. Export ASCII MDL via File → Export → KotOR Model (.mdl)
7. Convert ASCII MDL to binary MDL using MDLops or MDLedit

### Baking Lightmaps

1. Select lightmapped objects and enter Edit mode
2. UV Unwrap Faces via UV → Lightmap Pack
3. For each lightmapped object:
    1. Select lightmap UV Map in Object Data Properties
    2. Select lightmap texture node in material node tree
    3. Remove a link between lightmap texture node and Multiply node
4. In Render Properties
    1. Set Render Engine to Cycles
    2. Set Margin to a lower number, e.g. 1
    3. Press the Bake button

### Editing Paths

1. Extract PTH file from the module's RIM file, e.g. "modules/danm13_s.rim" (Kotor Tool, reone-tools, etc.)
2. Convert binary PTH to ASCII PTH using reone-tools: `reone-tools --to-ascii m13aa.pth`
3. Import ASCII PTH into Blender via File → Import → KotOR Path (.pth)
4. Create/move path points, or modify path connections via Object Properties
5. Export ASCII PTH via File → Export → KotOR Path (.pth)
6. Convert ASCII PTH to binary PTH using reone-tools: `reone-tools --to-pth m13aa-ascii.pth`

### Connecting Room Walkmeshes

1. Select a room walkmesh
2. Enter Edit mode and select two vertices adjacent to another room
3. Determine 0-based index of the other room into the LYT file
4. Enter Vertex Paint mode and set brush color to (0.0, G, 0.0), where G = (200 + room index) / 255
5. Ensure that brush blending mode is set to Mix, and brush strength is set to 1.0
6. Paint over the selected vertices

## Trivia

- Check "Image search" when importing to recursively search for textures in subdirectories
- Only selected objects are exported, unless none are selected, in which case all objects will be exported
- When baking lightmaps, disable rendering of unwanted objects, such as walkmeshes and path points

## Compatibility

- Blender 2.8+
- MDLops 1.0.2
- MDLedit 1.0.3

### Known Issues

- You cannot have neverblender and kotorblender *enabled* at the same time
- MDLedit has problems reading `color` and `selfillumcolor` controllers from ASCII MDL

## License

[GPL-3.0-or-later](LICENSE)
