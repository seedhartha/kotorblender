# KotORBlender

This add-on is a fork of KotORBlender, upgraded to support Blender 2.8+. KotORBlender is in turn based on NeverBlender, forked from version 1.23a.

## Features

- Import & export ASCII MDL models: geometry, materials, animations, walkmeshes and TXI files
- Import & export LYT files

## Installation

1. Clone this repository or donwload a ZIP release
2. Copy or unpack the *kotorblender* folder into Blender addons directory, e.g. "C:/Users/USERNAME/AppData/Roaming/Blender Foundation/Blender/BLENDER_VERSION/scripts/addons"
3. Enable the add-on in Blender Preferences via Edit → Preferences → Add-ons

## Usage

1. Extract MDL, MDX, WOK, and, optionally, TPC and LYT files to a single directory (Kotor Tool, reone-tools, etc.)
2. Convert TPC files to TGA/TXI (reone-tools)
3. Convert binary MDL to ASCII MDL using MDLops (preferably) or MDLedit
4. Import ASCII MDL into Blender via File → Import → KotOR Model (.mdl)
5. Create/modify models
6. Export ASCII MDL via File → Export → KotOR Model (.mdl)
7. Convert ASCII MDL to binary MDL using MDLedit (preferably) or MDLops

## Trivia

- Check "Image search" when importing to recursively search for textures in subdirectories
- Only selected objects are exported, unless none are selected, in which case all objects will be exported
- It is possible to bake lightmaps using the Cycles rendering engine

## Compatibility

- Blender 2.8+
- MDLops 1.0.2
- MDLedit 1.0.3

### Known Issues

- You cannot have neverblender and kotorblender *enabled* at the same time
- Armature management for animating is not working yet

## License

[GPL-3.0-or-later](LICENSE)
