import bpy
from bpy.types import Panel
from bpy.utils import register_class, unregister_class
from .config import MassImportProperties

class MassImportPanel(Panel):
    bl_label = "MEDGE Depot Builder - Mass Import PSKX Files"
    bl_idname = "OBJECT_PT_mass_import"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        props = context.scene.mass_import_props

        layout.prop(props, "folder_path")
        layout.prop(props, "depot_path")

        layout.prop(props, "skip_lod_files")

        layout.operator("object.mass_import_operator")

        layout.separator()

        # Material import section
        layout.prop(props, "material_folder_path")
        layout.operator("material.import_mat_files")

        layout.separator()

        # Prefab conversion section
        row = layout.row()
        row.prop(props, "process_all_collections", text="Process All Collections")
        row.prop(props, "move_duplicates_to_level")
        layout.operator("object.convert_duplicates_to_prefabs")

        layout.separator()

        # Lock compound section (hidden for now)
        # layout.prop(props, "lock_compound")

        layout.separator()

        # Group and Ungroup buttons
        row = layout.row(align=True)
        row.operator("object.group_objects", text="Group")
        row.operator("object.ungroup_objects", text="Ungroup")

def register():
    register_class(MassImportPanel)

def unregister():
    unregister_class(MassImportPanel)

if __name__ == "__main__":
    register()
