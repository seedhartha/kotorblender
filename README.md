# KotORBlender

This add-on is a fork of KotORBlender, upgraded to support Blender 2.8+. KotORBlender is in turn based on NeverBlender, forked from version 1.23a.

## Features

- Import & export ASCII MDL models: geometry, materials, animations, walkmeshes and TXI files
- Import LYT files

## Installation

- Clone this repository or donwload a ZIP release
- Copy or unpack the *kotorblender* folder into Blender addons directory, e.g. "C:/Users/USERNAME/AppData/Roaming/Blender Foundation/Blender/BLENDER_VERSION/scripts/addons"
- Enable the add-on in Blender Preferences via Edit → Preferences → Add-ons

## Usage

- Extract MDL, MDX, WOK, and, optionally, TPC and LYT files to a single directory (Kotor Tool, reone-tools, etc.)
- Convert TPC files to TGA/TXI (reone-tools)
- Convert binary MDL to ASCII MDL using MDLops (preferably) or MDLedit
- Import ASCII MDL or LYT into Blender via File → Import → Odyssey (KotOR) (.mdl)
- Create/modify models
- Export ASCII MDL via File → Export → Odyssey (KotOR) (.mdl)
- Convert ASCII MDL to binary MDL using MDLedit (preferably) or MDLops

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
