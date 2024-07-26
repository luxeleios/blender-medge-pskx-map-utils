import bpy
from bpy.types import Operator
from bpy.utils import register_class, unregister_class

class GroupObjects(Operator):
    bl_idname = "object.group_objects"
    bl_label = "Group Objects"
    bl_description = "Group selected objects with an empty axis object"

    def execute(self, context):
        selected_objects = context.selected_objects
        active_object = context.active_object

        if not selected_objects or not active_object:
            self.report({'ERROR'}, "No objects selected or no active object")
            return {'CANCELLED'}

        # Create the empty axis object
        empty_name = f"TGROUP_{active_object.name}_001"
        empty = bpy.data.objects.new(empty_name, None)
        context.collection.objects.link(empty)
        empty.location = active_object.location
        empty.rotation_euler = active_object.rotation_euler
        empty.scale = active_object.scale

        # Add constraints to selected objects
        for obj in selected_objects:
            if obj != empty:
                loc_constraint = obj.constraints.new(type='COPY_LOCATION')
                loc_constraint.target = empty

                rot_constraint = obj.constraints.new(type='COPY_ROTATION')
                rot_constraint.target = empty

                scale_constraint = obj.constraints.new(type='COPY_SCALE')
                scale_constraint.target = empty

        # Set the selection to the new empty object
        bpy.ops.object.select_all(action='DESELECT')
        empty.select_set(True)
        context.view_layer.objects.active = empty

        # Re-attach the handler
        ensure_handler()

        self.report({'INFO'}, f"Grouped {len(selected_objects)} objects with {empty.name}")
        return {'FINISHED'}

class UngroupObjects(Operator):
    bl_idname = "object.ungroup_objects"
    bl_label = "Ungroup Objects"
    bl_description = "Ungroup selected objects and remove the empty axis object"

    def execute(self, context):
        selected_objects = context.selected_objects
        empties_to_remove = set()
        objects_to_apply = set()

        for obj in selected_objects:
            if obj.name.startswith("TGROUP_"):
                empties_to_remove.add(obj)
                for constrained_obj in self.get_constrained_objects(obj):
                    objects_to_apply.add(constrained_obj)
            else:
                objects_to_apply.add(obj)
                if obj.constraints:
                    for constraint in obj.constraints:
                        if constraint.target and constraint.target.name.startswith("TGROUP_"):
                            empties_to_remove.add(constraint.target)
                            for constrained_obj in self.get_constrained_objects(constraint.target):
                                objects_to_apply.add(constrained_obj)

        for obj in objects_to_apply:
            self.apply_constraints(obj)

        for empty in empties_to_remove:
            bpy.data.objects.remove(empty)

        # Re-attach the handler
        ensure_handler()

        self.report({'INFO'}, "Ungrouped selected objects")
        return {'FINISHED'}

    def get_constrained_objects(self, empty):
        constrained_objects = []
        for obj in bpy.data.objects:
            for constraint in obj.constraints:
                if constraint.target == empty:
                    constrained_objects.append(obj)
                    break
        return constrained_objects

    def apply_constraints(self, obj):
        if obj.constraints:
            for constraint in obj.constraints:
                if constraint.type == 'COPY_LOCATION':
                    obj.location = constraint.target.location
                elif constraint.type == 'COPY_ROTATION':
                    obj.rotation_euler = constraint.target.rotation_euler
                elif constraint.type == 'COPY_SCALE':
                    obj.scale = constraint.target.scale
            self.remove_constraints(obj)

    def remove_constraints(self, obj):
        for constraint in obj.constraints:
            obj.constraints.remove(constraint)

def redirect_selection_handler(scene):
    selected_objects = bpy.context.selected_objects
    if len(selected_objects) == 1:
        selected_obj = selected_objects[0]
        for constraint in selected_obj.constraints:
            if constraint.target and constraint.target.name.startswith("TGROUP_"):
                bpy.context.view_layer.objects.active = constraint.target
                bpy.ops.object.select_all(action='DESELECT')
                constraint.target.select_set(True)
                constrained_objects = get_constrained_objects(constraint.target)
                for obj in constrained_objects:
                    obj.select_set(True)
                return

def get_constrained_objects(empty):
    constrained_objects = []
    for obj in bpy.data.objects:
        for constraint in obj.constraints:
            if constraint.target == empty:
                constrained_objects.append(obj)
                break
    return constrained_objects

def ensure_handler():
    if redirect_selection_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(redirect_selection_handler)

def register():
    register_class(GroupObjects)
    register_class(UngroupObjects)
    ensure_handler()

def unregister():
    unregister_class(GroupObjects)
    unregister_class(UngroupObjects)
    if redirect_selection_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(redirect_selection_handler)

if __name__ == "__main__":
    register()
