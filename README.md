# KotorBlender

This add-on is a fork of KotorBlender, upgraded to support newer versions of Blender. KotorBlender is in turn based on NeverBlender, forked from version 1.23a.

## Features

- Import & export MDL models, including walkmeshes
- Import & export LYT files
- Import & export PTH files

## Installation

1. Clone this repository or download the latest release of KotorBlender from [Deadly Stream](https://deadlystream.com/files/file/1853-kotorblender-for-blender-293/)
1. If you have cloned the repository, create a ZIP archive containing the **io_scene_kotor** directory
1. From Edit → Preferences → Add-ons in Blender, install the add-on from the ZIP archive and enable it by ticking a box next to "Import-Export: KotorBlender"
1. Alternatively, if you want to contribute to KotorBlender, you may want to create a symbolic link to the local repository in the Blender add-ons directory, typically located at `C:/Users/{user}/AppData/Roaming/Blender Foundation/Blender/{version}/scripts/addons`:
  1. `mklink /D io_scene_kotor {repo}/io_scene_kotor`

## Usage

### Data Preparation

Extract models, textures, walkmeshes, LYT and PTH files into a working directory, using a tool of your choice, e.g. [reone toolkit](https://deadlystream.com/files/file/1862-reone-toolkit/). Recommended directory structure:

- *data* — extract all BIF archives here without subdirectories
- *texturepacks*
  - *swpc_tex_tpa* — extract swpc_tex_tpa ERF archive here

If you plan to edit textures, batch-convert TPC to TGA / TXI files using **reone toolkit**, although TPC textures are also supported by KotorBlender.

### Model Import and Export

1. Import via File → Import → KotOR Model (.mdl)
1. Select top-level MDL root object to be exported
1. Export via File → Export → KotOR Model (.mdl)

### Editing Animations

To edit list of model animations and corresponding events, select MDL root object and navigate to Object → KotOR Animations. KotorBlender supports both object and armature-based edits. To create an armature from objects, navigate to KotOR Animations → Armature and press Rebuild Armature and Apply Object Keyframes. Before exporting a model, make sure to copy armature keyframes back to objects by pressing Unapply Object Keyframes.

### Lightmapping

1. Select objects for which you want lightmaps to be recreated, or unselect all objects to recreate all lightmaps
1. Press KotOR → Lightmaps → Bake (auto)

UV mapping:

1. Select objects having the same lightmap texture and enter Edit mode
1. For every object, ensure that `UVMap_lm` UV layer is active
1. Select all faces and unwrap UVs via UV → Lightmap Pack, increase Margin to avoid face overlapping

Fine-tuning:

1. Increase lightmap image size via UV Editing → Image → Resize
1. Tweak ambient color via Scene → World → Surface → Color
1. Manually toggle rendering of objects in Outliner and press KotOR → Lightmaps → Bake (manual)
1. In Scene → Render, set Device to GPU Compute to improve performance, set Render Engine to Cycles if not already
1. In Scene → Render → Sampling → Render increase Max Samples to improve quality

### Connecting Rooms

1. Select a room walkmesh
1. Enter Edit mode and select two vertices adjacent to another room
1. Determine 0-based index of the other room into the LYT file
1. Enter Vertex Paint mode and set brush color to (0.0, G, 0.0), where G = (200 + room index) / 255
1. Ensure that brush blending mode is set to Mix, and brush strength is set to 1.0
1. Paint over the selected vertices

### Editing Paths

1. Extract PTH file from the module's RIM file, e.g. "modules/danm13_s.rim" (Kotor Tool, reone toolkit, etc.)
1. Import PTH into Blender via File → Import → KotOR Path (.pth)
1. Create/move path points, or modify path connections via Object Properties
1. Export PTH via File → Export → KotOR Path (.pth)

## Compatibility

Known to work with Blender versions ranging from 3.3 to 4.0.

## License

[GPL 3.0 or later](LICENSE)
