# MEDGE Depot Builder - Mass Import PSKX Files + Utils
This is a Blender addon made to conveniently mass import *.pskx and *.mat assets extracted by UModel from Mirror's Edge (2008), aided by multiple utility functions. Intended as a supplement to [MEdge Map Editor](https://github.com/medge-tools/medge-map-editor/tree/main). Tested on Blender 3.6. 

## Prerequisites
1. Install [PSK import script from Befzz](https://github.com/Befzz/blender3d_import_psk_psa/releases) for Blender
2. Install [MEdge Map Editor](https://github.com/medge-tools/medge-map-editor/tree/main) for Blender
3. Install [UModel](https://www.gildor.org/en/projects/umodel) to be able to extract assets (mesh, textures, materials) found in UE3 *.upk packages and processed by this addon

## Features
- __Mass import *.pskx meshes extracted by UModel from the specifed folder and its subfolders__
- __Mass import *.mat files created by UModel as blender materials__ - *.mat files are primitve reconstructions of the materials found inside the unreal *.upk packages. They are created by UModel to be used with 3ds Max material system. They usually contain references to Diffuse, Specular and Normal map textures, nothing complex.
- __Reconstruct *.upk folder/group structure as Blender collections and place imported meshes inside__
- __Automatically convert duplicate objects found in the scene into StaticMeshActors used by MEdge Map Editor addon__
- __Automatically convert multiple selected objects into a non-destructive group__ - Groups behave like a singular object when transformed. When ungrouped, they maintain their group transforms.

## UI Overview and Addon Usage
The addon UI is located inside the `Tool` category.

![UI](https://github.com/luxeleios/blender-medge-pskx-map-utils/blob/main/addon_ui_sample.png)

### UI Overview
- `Folder Path` - Path to the folder containing *.pskx files to import. Folders found within will be recreated as Blender Collections.
- `Depot Path` - Path to the folder where umodel extracted the UPK contents.
- `Skip LOD Files` - Skips *.pskx files that contain LOD in their filenames during import. Default is set to True.
- `Material Folder Path` - Path to the folder from which the materials exported by UModel as *.mat files will be imported. Can be used without setting the `Folder Path`
- `Duplicates to Prefabs` - Identifies duplicates of objects located either inside the GenericBrowser collection or anywhere in the scene by their name and converts them into StaticMeshActors for export via medge-map-editor.
- `Process All Collections` - Defines whether `Duplicates to Prefabs` will look for duplicates everywhere in the scene or only inside the Level collection. Default is set to True.
- `Move Duplicates to Level` - If `Process All Collections` is checked, duplicate objects will be moved inside the `Level` collection during conversion.
- `Group` - Create a non-destructive group from selected objects. While grouped, they are transformed as one.
- `Ungroup` - Ungroup selected objects. Once ungrouped, they maintain their transformations.

### Usage
- Use UModel to extract StaticMesh, material and texture assets to a folder, make sure you use the following settings, especially the ones highlighted in red:

![UModel](https://github.com/luxeleios/blender-medge-pskx-map-utils/blob/main/umodel_settings.png)
- The folder UModel extracted the assets to will also have to be set in the `Depot Path` field. It is necessary to have both `Depot Path` and `Folder Path` set, they can have the same path.
- You can import materials on their own, without importing the meshes. Most imported materials will have a basecolor, roughness and OGL normal map already set.

## TODO
- Remove unused mesh_organiser.py
- Clean up unused code
