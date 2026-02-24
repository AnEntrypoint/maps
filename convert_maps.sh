#!/bin/bash
# Counter-Strike BSP to GLB Batch Conversion
# Output: Textures + 3D Models (no lightmaps)

CONVERTER="/config/hlbsp-converter/build/bsp-converter"
INPUT_DIR="/tmp/cs_maps"
OUTPUT_DIR="/tmp/cs_maps/converted"

echo "=== Counter-Strike BSP to GLB Conversion ==="
echo "Output: Textures + 3D Models (no lightmaps)"
echo "Input directory: $INPUT_DIR"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Find all BSP files
bsp_files=("$INPUT_DIR"/*.bsp)
if [ ! -e "${bsp_files[0]}" ]; then
    echo "No BSP files found in $INPUT_DIR"
    echo "Please place Counter-Strike 1.6 map files (.bsp) in: $INPUT_DIR"
    exit 1
fi

success_count=0
fail_count=0

for bsp_file in "$INPUT_DIR"/*.bsp; do
    filename=$(basename "$bsp_file")
    mapname="${filename%.bsp}"
    
    echo "Converting: $filename"
    
    # Run converter with texture extraction and sky removal
    # No lightmap options = excludes lightmaps from output
    if "$CONVERTER" "$bsp_file" -tex -skip_sky 2>&1 | grep -q "Can't load map\|Error"; then
        echo "  ✗ FAILED"
        ((fail_count++))
    else
        # Check if output GLB was created
        if [ -f "$mapname.glb" ]; then
            mv "$mapname.glb" "$OUTPUT_DIR/"
            glb_size=$(stat -f%z "$OUTPUT_DIR/$mapname.glb" 2>/dev/null || stat -c%s "$OUTPUT_DIR/$mapname.glb" 2>/dev/null)
            echo "  ✓ SUCCESS - $mapname.glb ($glb_size bytes)"
            ((success_count++))
        else
            echo "  ✗ FAILED - No output generated"
            ((fail_count++))
        fi
    fi
done

echo ""
echo "=== SUMMARY ==="
echo "Successful conversions: $success_count"
echo "Failed conversions: $fail_count"
echo "Output location: $OUTPUT_DIR"
echo "Output format: GLB with textures and 3D models"
echo "Lightmaps: Excluded"
