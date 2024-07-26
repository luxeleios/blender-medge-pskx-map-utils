bl_info = {
    "name": "MEDGE Depot Builder - Mass Import PSKX Files",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
from . import config, import_pskx, import_materials, convert_prefabs, grouping, ui_panel

def register():
    config.register()
    import_pskx.register()
    import_materials.register()
    convert_prefabs.register()
    grouping.register()
    ui_panel.register()

def unregister():
    ui_panel.unregister()
    grouping.unregister()
    convert_prefabs.unregister()
    import_materials.unregister()
    import_pskx.unregister()
    config.unregister()

if __name__ == "__main__":
    register()
