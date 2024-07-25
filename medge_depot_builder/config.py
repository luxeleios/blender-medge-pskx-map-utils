import bpy
from bpy.props import StringProperty, BoolProperty

DEFAULT_DEPOT_PATH = r"D:\gamedev\medge_raw_depot"

class MassImportProperties(bpy.types.PropertyGroup):
    folder_path: StringProperty(
        name="Folder Path",
        description="Path to the folder containing PSKX files",
        default="",
        subtype='DIR_PATH'
    )
    depot_path: StringProperty(
        name="Depot Path",
        description="Path to the depot folder",
        default=DEFAULT_DEPOT_PATH,
        subtype='DIR_PATH'
    )
    material_folder_path: StringProperty(
        name="Material Folder Path",
        description="Path to the folder containing .mat files",
        default="",
        subtype='DIR_PATH'
    )
    skip_lod_files: BoolProperty(
        name="Skip LOD Files",
        description="Skip PSKX files with _lod postfix",
        default=True
    )
    process_all_collections: BoolProperty(
        name="Process All Collections",
        description="Process all collections including GenericBrowser",
        default=False
    )
    move_duplicates_to_level: BoolProperty(
        name="Move Duplicates to Level",
        description="Move duplicates of objects to the Level collection",
        default=False
    )
    lock_compound: BoolProperty(
        name="Lock Compound",
        description="Parent objects in the same modular set to the _F object",
        default=False,
        update=lambda self, context: bpy.ops.object.organise_meshes()
    )

def register():
    bpy.utils.register_class(MassImportProperties)
    bpy.types.Scene.mass_import_props = bpy.props.PointerProperty(type=MassImportProperties)

def unregister():
    bpy.utils.unregister_class(MassImportProperties)
    del bpy.types.Scene.mass_import_props
