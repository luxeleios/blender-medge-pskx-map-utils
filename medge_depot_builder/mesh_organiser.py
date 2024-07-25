import bpy
import re
from bpy.types import Operator
from bpy.utils import register_class, unregister_class

def get_modular_set_name(name):
    match = re.match(r"S_[A-Z]_\d{2}_\d{2}_(R|F|S|R\d+)", name)
    return match.group(0) if match else None

def get_all_objects(collection):
    objects = set(collection.objects)
    for child in collection.children:
        objects.update(get_all_objects(child))
    return objects

class OrganiseMeshes(Operator):
    bl_idname = "object.organise_meshes"
    bl_label = "Organise Meshes"
    bl_description = "Organise meshes in the GenericBrowser collection"

    def execute(self, context):
        props = context.scene.mass_import_props
        generic_browser = bpy.data.collections.get('GenericBrowser')

        if not generic_browser:
            self.report({'ERROR'}, "GenericBrowser collection not found")
            return {'CANCELLED'}

        if props.lock_compound:
            self.lock_compounds(generic_browser)
        else:
            self.unlock_compounds(generic_browser)

        self.report({'INFO'}, "Compound locking/unlocking completed")
        return {'FINISHED'}

    def lock_compounds(self, collection):
        all_objects = get_all_objects(collection)
        modular_sets = {}

        for obj in all_objects:
            modular_set_name = get_modular_set_name(obj.name)
            if modular_set_name:
                if modular_set_name not in modular_sets:
                    modular_sets[modular_set_name] = []
                modular_sets[modular_set_name].append(obj)

        for modular_set_name, objects in modular_sets.items():
            parent_obj = next((obj for obj in objects if obj.name.endswith('_F')), None)
            if parent_obj:
                for obj in objects:
                    if obj != parent_obj:
                        obj.parent = parent_obj
                        print(f"Parented {obj.name} to {parent_obj.name}")

    def unlock_compounds(self, collection):
        all_objects = get_all_objects(collection)
        for obj in all_objects:
            if obj.parent:
                # Select the object to clear parent with keep transform
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                print(f"Cleared parent for {obj.name}")

def register():
    register_class(OrganiseMeshes)

def unregister():
    unregister_class(OrganiseMeshes)

if __name__ == "__main__":
    register()
