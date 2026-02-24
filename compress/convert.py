import bpy, sys, os, glob
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(script_dir, "input")
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)

blender_addons = Path(bpy.utils.script_path_python()) / "addons"
gltf_importer_path = blender_addons / "io_scene_gltf2"

if not gltf_importer_path.exists():
    print(f"ERROR: glTF importer not found at {gltf_importer_path}")
    sys.exit(1)

if str(gltf_importer_path.parent) not in sys.path:
    sys.path.insert(0, str(gltf_importer_path.parent))

from io_scene_gltf2.importer import Glb

glb_files = glob.glob(os.path.join(input_dir, "*.glb"))
if not glb_files:
    print("No .glb files found in input/")
    sys.exit(1)

for glb_file in glb_files:
    name = os.path.splitext(os.path.basename(glb_file))[0]
    output_path = os.path.join(output_dir, name + ".glb")

    print(f"Processing: {glb_file}")
    bpy.ops.wm.read_factory_settings(use_empty=True)

    importer = Glb(glb_file)
    importer.read()
    importer.import_scene()

    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        export_image_format='WEBP',
        export_image_add_webp=False,
        export_image_quality=15,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
    )
    print(f"DONE: {output_path}")
