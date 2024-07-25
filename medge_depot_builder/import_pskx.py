import bpy
import os
from pathlib import Path
from bpy.types import Operator
from bpy.utils import register_class, unregister_class
from io_import_scene_unreal_psa_psk_280 import pskimport
from .config import MassImportProperties

class MassImportOperator(Operator):
    bl_idname = "object.mass_import_operator"
    bl_label = "Import PSKX Files"

    def ensure_collection_exists(self, collection_name, parent_collection):
        collection = bpy.data.collections.get(collection_name)
        if not collection:
            collection = bpy.data.collections.new(collection_name)
            parent_collection.children.link(collection)
        return collection

    def object_exists_in_collection(self, object_name, collection):
        for obj in collection.objects:
            if obj.name == object_name:
                return True
        for sub_collection in collection.children:
            if self.object_exists_in_collection(object_name, sub_collection):
                return True
        return False

    def process_folder(self, current_path, current_collection, depot_path, skip_lod_files):
        for item in os.listdir(current_path):
            item_path = os.path.join(current_path, item)
            if os.path.isdir(item_path):
                relative_path = os.path.relpath(item_path, depot_path)
                sub_collection = self.ensure_nested_collections(relative_path, "GenericBrowser")
                self.process_folder(item_path, sub_collection, depot_path, skip_lod_files)
            elif item.endswith('.pskx'):
                if skip_lod_files and '_lod' in item.lower():
                    continue
                relative_path = os.path.relpath(item_path, depot_path)
                collection_path = Path("GenericBrowser") / Path(relative_path).parent
                object_name = Path(item).stem
                if not self.object_exists_in_collection(object_name, bpy.data.collections.get("GenericBrowser")):
                    self.import_pskx(item_path, collection_path)
                else:
                    print(f"Skipping {item} as it already exists in GenericBrowser collection")

    def ensure_nested_collections(self, relative_path, root_collection_name):
        parent_collection = bpy.data.collections.get(root_collection_name)
        if not parent_collection:
            parent_collection = bpy.data.collections.new(root_collection_name)
            bpy.context.scene.collection.children.link(parent_collection)
        
        for part in Path(relative_path).parts:
            parent_collection = self.ensure_collection_exists(part, parent_collection)
        
        return parent_collection

    def import_pskx(self, file_path, collection_path):
        print(f"Importing: {file_path} into collection {collection_path}")
        try:
            pskimport(file_path, bReorientBones=False)
            for obj in bpy.context.selected_objects:
                self.create_nested_collections_and_link(obj, collection_path)
                self.set_second_uv_channel(obj)
                self.set_auto_smooth(obj)
        except Exception as e:
            print(f"Error importing {file_path}: {e}")

    def create_nested_collections_and_link(self, obj, collection_path):
        parent_collection = bpy.context.scene.collection
        for part in collection_path.parts:
            parent_collection = self.ensure_collection_exists(part, parent_collection)
        if obj.name not in parent_collection.objects:
            while obj.users_collection:
                obj.users_collection[0].objects.unlink(obj)
            parent_collection.objects.link(obj)

    def cleanup_object_names(self, collection):
        for obj in collection.objects:
            obj.name = obj.name[:-3] if obj.name[-3:] == '.mo' else obj.name
            self.report({'INFO'}, obj.name)
        for sub_collection in collection.children:
            self.cleanup_object_names(sub_collection)

    def set_second_uv_channel(self, obj):
        if obj.type == 'MESH':
            mesh = obj.data
            if len(mesh.uv_layers) > 1:
                mesh.uv_layers.active_index = 1
                mesh.uv_layers[1].active_render = True

    def set_auto_smooth(self, obj):
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.shade_smooth(use_auto_smooth=True)
            obj.data.auto_smooth_angle = 3.14159 / 4  # 45 degrees in radians

    def execute(self, context):
        props = context.scene.mass_import_props
        folder_path = Path(props.folder_path)
        depot_path = Path(props.depot_path)
        skip_lod_files = props.skip_lod_files

        if not folder_path.exists():
            self.report({'ERROR'}, f"Folder path does not exist: {folder_path}")
            return {'CANCELLED'}

        generic_browser = self.ensure_collection_exists("GenericBrowser", bpy.context.scene.collection)
        self.process_folder(folder_path, generic_browser, depot_path, skip_lod_files)

        # Clean up object names to remove .mo postfix
        self.cleanup_object_names(generic_browser)

        bpy.context.view_layer.update()
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        self.report({'INFO'}, "Import completed successfully.")

        return {'FINISHED'}

def register():
    register_class(MassImportOperator)

def unregister():
    unregister_class(MassImportOperator)

if __name__ == "__main__":
    register()
