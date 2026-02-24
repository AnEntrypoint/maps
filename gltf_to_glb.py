#!/usr/bin/env python3
import json
import struct
import os
import sys
from pathlib import Path

def gltf_to_glb(gltf_path, output_path):
    """Convert glTF (separate .gltf + .bin) to GLB (binary bundle)"""
    
    gltf_path = Path(gltf_path)
    bin_path = gltf_path.parent / (gltf_path.stem + '.bin')
    
    # Read glTF JSON
    with open(gltf_path, 'r') as f:
        gltf_json = json.load(f)
    
    # Read binary data
    if bin_path.exists():
        with open(bin_path, 'rb') as f:
            bin_data = f.read()
    else:
        bin_data = b''
    
    # Serialize glTF JSON
    json_str = json.dumps(gltf_json, separators=(',', ':'))
    json_bytes = json_str.encode('utf-8')
    
    # Align JSON to 4-byte boundary
    json_padding = (4 - (len(json_bytes) % 4)) % 4
    json_bytes += b' ' * json_padding
    
    # Align BIN to 4-byte boundary
    bin_padding = (4 - (len(bin_data) % 4)) % 4
    bin_data += b'\x00' * bin_padding
    
    # Build GLB
    glb = bytearray()
    
    # GLB header
    glb += struct.pack('<I', 0x46546C67)  # magic
    glb += struct.pack('<I', 2)            # version
    glb += struct.pack('<I', 12 + 8 + len(json_bytes) + 8 + len(bin_data))  # total length
    
    # JSON chunk
    glb += struct.pack('<I', len(json_bytes))
    glb += struct.pack('<I', 0x4E4F534A)  # "JSON"
    glb += json_bytes
    
    # BIN chunk
    if bin_data:
        glb += struct.pack('<I', len(bin_data))
        glb += struct.pack('<I', 0x004E4942)  # "BIN\0"
        glb += bin_data
    
    # Write GLB
    with open(output_path, 'wb') as f:
        f.write(glb)
    
    return len(glb)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: gltf_to_glb.py <input.gltf> <output.glb>")
        sys.exit(1)
    
    gltf_path = sys.argv[1]
    output_path = sys.argv[2]
    
    size = gltf_to_glb(gltf_path, output_path)
    print(f"Converted: {output_path} ({size} bytes)")
