import bpy
import os
from bpy.types import Operator
from bpy.utils import register_class, unregister_class
from .config import MassImportProperties

def create_materials_from_mat_files(directory_path, search_path):
    print(f"Checking directory path: {directory_path}")
    print(f"Checking search path: {search_path}")
    
    if not os.path.exists(directory_path):
        print(f"Directory does not exist: {directory_path}")
        return

    material_files = []

    stack = [directory_path]
    while stack:
        dir_name = stack.pop()
        for filename in os.listdir(dir_name):
            filename = os.path.join(dir_name, filename)
            if filename.endswith('.mat'):
                material_files.append(filename)
            elif os.path.isdir(filename):
                stack.append(filename)
    for mat_file in material_files:
        create_or_update_material_from_mat_file(mat_file, search_path)
        
    remove_duplicate_images()

def create_or_update_material_from_mat_file(mat_file_path, search_path):
    directory, mat_filename = os.path.split(mat_file_path)
    material_name = os.path.splitext(mat_filename)[0]

    texture_paths = {}
    with open(mat_file_path, 'r') as file:
        for line in file:
            if '=' in line:
                key, value = line.strip().split('=')
                texture_paths[key.strip()] = value.strip()

    if material_name in bpy.data.materials:
        material = bpy.data.materials[material_name]
        material.use_nodes = True
        nodes = material.node_tree.nodes
    else:
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True
        nodes = material.node_tree.nodes

    bsdf_node = None
    output_node = None

    for node in nodes:
        if node.type == 'BSDF_PRINCIPLED':
            bsdf_node = node
        elif node.type == 'OUTPUT_MATERIAL':
            output_node = node

    if not bsdf_node:
        bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf_node.location = (300, 300)

    if not output_node:
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (500, 300)

    def load_and_link_texture(texture_key, node_location, input_socket, color_space='sRGB'):
        if texture_key in texture_paths:
            texture_image_path = os.path.join(directory, texture_paths[texture_key] + '.png')
            image_name = os.path.basename(texture_image_path)
            image = bpy.data.images.get(image_name)
            if not image:
                if os.path.isfile(texture_image_path):
                    image = bpy.data.images.load(texture_image_path)
                else:
                    matches = []
                    for root, dirnames, filenames in os.walk(search_path):
                        for f in filenames:
                            if f == texture_paths[texture_key] + '.png':
                                matches.append(os.path.join(root, f))
                    if matches:
                        image = bpy.data.images.load(matches[0])
                    else:
                        print(f"Texture file not found for key: {texture_key}")
                        return None
            image.colorspace_settings.name = color_space

            texture_image_node = nodes.new('ShaderNodeTexImage')
            texture_image_node.image = image
            texture_image_node.location = node_location

            if input_socket:
                material.node_tree.links.new(input_socket, texture_image_node.outputs['Color'])
            return texture_image_node

    load_and_link_texture('Diffuse', (100, 400), bsdf_node.inputs['Base Color'])

    specular_node = load_and_link_texture('Specular', (100, 200), None, 'Non-Color')
    if specular_node:
        invert_node = nodes.new('ShaderNodeInvert')
        invert_node.location = (300, 200)
        material.node_tree.links.new(invert_node.inputs['Color'], specular_node.outputs['Color'])
        material.node_tree.links.new(bsdf_node.inputs['Roughness'], invert_node.outputs['Color'])

    normal_map_node = load_and_link_texture('Normal', (100, 0), None, 'Non-Color')
    if normal_map_node:
        separate_rgb_node = nodes.new('ShaderNodeSeparateRGB')
        separate_rgb_node.location = (200, 0)
        material.node_tree.links.new(separate_rgb_node.inputs['Image'], normal_map_node.outputs['Color'])

        invert_green_node = nodes.new('ShaderNodeInvert')
        invert_green_node.location = (400, 0)
        material.node_tree.links.new(invert_green_node.inputs['Color'], separate_rgb_node.outputs['G'])

        combine_rgb_node = nodes.new('ShaderNodeCombineRGB')
        combine_rgb_node.location = (600, 0)
        material.node_tree.links.new(combine_rgb_node.inputs['R'], separate_rgb_node.outputs['R'])
        material.node_tree.links.new(combine_rgb_node.inputs['G'], invert_green_node.outputs['Color'])
        material.node_tree.links.new(combine_rgb_node.inputs['B'], separate_rgb_node.outputs['B'])

        normal_map_convert_node = nodes.new('ShaderNodeNormalMap')
        normal_map_convert_node.location = (800, 0)
        material.node_tree.links.new(normal_map_convert_node.inputs['Color'], combine_rgb_node.outputs['Image'])
        material.node_tree.links.new(bsdf_node.inputs['Normal'], normal_map_convert_node.outputs['Normal'])

    material.node_tree.links.new(output_node.inputs['Surface'], bsdf_node.outputs['BSDF'])
    organize_nodes(material.node_tree)
    return material

def organize_nodes(node_tree):
    def get_node_depth(node, visited=None):
        if visited is None:
            visited = set()
        if node in visited:
            return 0
        visited.add(node)
        if not node.inputs or all(not link.is_linked for link in node.inputs):
            return 0
        return 1 + max(get_node_depth(link.from_node, visited) for input in node.inputs if input.is_linked for link in input.links)

    nodes_by_depth = {}
    for node in node_tree.nodes:
        depth = get_node_depth(node)
        if depth not in nodes_by_depth:
            nodes_by_depth[depth] = []
        nodes_by_depth[depth].append(node)

    for depth, nodes in nodes_by_depth.items():
        y = 0
        for node in nodes:
            node.location.x = depth * 300
            node.location.y = y
            y -= 300

    for depth, nodes in nodes_by_depth.items():
        for node in nodes:
            connected_y_positions = [link.from_node.location.y for input in node.inputs if input.is_linked for link in input.links]
            if connected_y_positions:
                node.location.y = sum(connected_y_positions) / len(connected_y_positions)

def remove_duplicate_images():
    image_names = {img.name for img in bpy.data.images}
    for img in bpy.data.images:
        if any(img.name.startswith(name) and img.name != name for name in image_names):
            bpy.data.images.remove(img)

class MATERIAL_OT_Import(Operator):
    bl_idname = "material.import_mat_files"
    bl_label = "Import Materials"
    bl_description = "Import materials from .mat files"

    def execute(self, context):
        props = context.scene.mass_import_props
        directory = props.material_folder_path
        search_path = props.depot_path
        create_materials_from_mat_files(directory, search_path)
        remove_duplicate_images()
        return {'FINISHED'}

def register():
    register_class(MATERIAL_OT_Import)

def unregister():
    unregister_class(MATERIAL_OT_Import)

if __name__ == "__main__":
    register()
