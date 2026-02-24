import bpy
import sys
import os
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(script_dir, "input")
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)

glb_files = list(Path(input_dir).glob("*.glb"))
if not glb_files:
    print("No .glb files found in input/")
    sys.exit(1)

print(f"Found {len(glb_files)} GLB files")

# Process first file as test
glb_file = str(glb_files[0])
name = Path(glb_file).stem
output_path = os.path.join(output_dir, name + "_processed.glb")

print(f"Processing: {glb_file}")

# Use bpy.ops with context override (Blender 5.0 compatible)
bpy.ops.wm.read_factory_settings(use_empty=True)

# Import using bpy.ops.import_scene.gltf() - works in headless mode
try:
    bpy.ops.import_scene.gltf(filepath=glb_file)
    print(f"✓ Successfully imported {name}")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Export with compression
try:
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        export_image_format='WEBP',
        export_image_add_webp=False,
        export_image_quality=15,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
    )
    print(f"✓ DONE: {output_path}")
except Exception as e:
    print(f"✗ Export failed: {e}")
    sys.exit(1)
