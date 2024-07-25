import bpy
import re
from bpy.types import Operator
from bpy.utils import register_class, unregister_class

def get_base_name(name):
    match = re.match(r"(.*)\.\d{3}", name)
    return match.group(1) if match else name

def get_all_objects(collection):
    objects = set(collection.objects)
    for child in collection.children:
        objects.update(get_all_objects(child))
    return objects

def set_static_mesh_with_prefab(obj, prefab_name):
    # Check if the object has the medge_actor property
    if not hasattr(obj, 'medge_actor'):
        print(f"Object '{obj.name}' does not have a medge_actor property")
        return
    
    # Set the medge_actor type to STATIC_MESH
    obj.medge_actor.type = 'STATIC_MESH'
    
    # Access the static_mesh property group
    static_mesh = obj.medge_actor.static_mesh
    
    # Set the use_prefab property to True
    static_mesh.use_prefab = True
    
    # Set the prefab property to the specified object
    prefab_obj = bpy.data.objects.get(prefab_name)
    if prefab_obj is None:
        print(f"Prefab object '{prefab_name}' not found")
        return
    
    static_mesh.prefab = prefab_obj
    
    # Initialize the actor if needed
    static_mesh.init()
    
    print(f"Object '{obj.name}' has been set to STATIC_MESH with prefab '{prefab_name}'")

class ConvertDuplicatesToPrefabs(Operator):
    bl_idname = "object.convert_duplicates_to_prefabs"
    bl_label = "Duplicates to Prefabs"
    bl_description = "Converts duplicates of meshes from the collections into prefab instances"

    def execute(self, context):
        props = context.scene.mass_import_props
        process_all_collections = props.process_all_collections

        generic_browser = bpy.data.collections.get('GenericBrowser')

        if not generic_browser:
            self.report({'ERROR'}, "GenericBrowser collection not found")
            return {'CANCELLED'}

        level_collection = bpy.data.collections.get("Level")

        if process_all_collections:
            collections_to_process = [col for col in bpy.data.collections]
        else:
            if level_collection:
                collections_to_process = [level_collection]
            else:
                self.report({'ERROR'}, "Level collection not found")
                return {'CANCELLED'}

        print(f"Collections to process: {[col.name for col in collections_to_process]}")

        generic_objects = get_all_objects(generic_browser)
        generic_object_dict = {obj.name: obj for obj in generic_objects}

        for collection in collections_to_process:
            level_objects = get_all_objects(collection)
            for obj in level_objects:
                base_name = get_base_name(obj.name)
                if base_name in generic_object_dict and obj.name != base_name:
                    original_obj = generic_object_dict[base_name]

                    # Set the static_mesh actor type and prefab properties
                    set_static_mesh_with_prefab(obj, original_obj.name)

        self.report({'INFO'}, "Duplicate conversion to prefabs completed")
        bpy.ops.object.move_prefabs_to_level()
        return {'FINISHED'}

class MovePrefabsToLevel(Operator):
    bl_idname = "object.move_prefabs_to_level"
    bl_label = "Move Prefabs to Level"
    bl_description = "Moves objects with names starting with 'PREFAB_' to the Level collection"

    def execute(self, context):
        props = context.scene.mass_import_props
        move_duplicates_to_level = props.move_duplicates_to_level

        # Ensure the Level collection exists
        level_collection = bpy.data.collections.get("Level")
        if not level_collection:
            level_collection = bpy.data.collections.new("Level")
            bpy.context.scene.collection.children.link(level_collection)

        def is_in_level_collection(obj):
            return any(col == level_collection or col.name.startswith("Level") for col in obj.users_collection)

        if move_duplicates_to_level:
            for obj in bpy.data.objects:
                if obj.name.startswith("PREFAB_") and not is_in_level_collection(obj):
                    # Unlink the object from its current collections, except the Level collection
                    for col in obj.users_collection:
                        if col != level_collection:
                            col.objects.unlink(obj)
                    # Link the object to the Level collection if it's not already there
                    if obj.name not in level_collection.objects:
                        level_collection.objects.link(obj)
                    print(f"Moved {obj.name} to Level collection")

        self.report({'INFO'}, "Moved prefabs to Level collection")
        return {'FINISHED'}

def register():
    register_class(ConvertDuplicatesToPrefabs)
    register_class(MovePrefabsToLevel)

def unregister():
    unregister_class(ConvertDuplicatesToPrefabs)
    unregister_class(MovePrefabsToLevel)

if __name__ == "__main__":
    register()
