import bpy, sys, os, glob

script_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(script_dir, "input")
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)

glb_files = glob.glob(os.path.join(input_dir, "*.glb"))
if not glb_files:
    print("No .glb files found in input/")
    sys.exit(1)

for glb_path in glb_files:
    name = os.path.splitext(os.path.basename(glb_path))[0]
    glb_path = os.path.join(output_dir, name + ".glb")

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(
        filepath=glb_path,
        directory=os.path.dirname(glb_path),
        files=[{"name": os.path.basename(glb_path)}],
        loglevel=20
    )

    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format='GLB',
        export_image_format='WEBP',
        export_image_add_webp=False,
        export_image_quality=15,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
    )
    print(f"DONE: {glb_path}")
