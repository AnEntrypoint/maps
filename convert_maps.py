#!/usr/bin/env python3
import os
import subprocess
import json
import sys
from pathlib import Path

class BSPConverter:
    def __init__(self, converter_path, input_dir, output_dir):
        self.converter = converter_path
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.results = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "conversions": []
        }
    
    def convert_all(self):
        """Convert all BSP files in input directory"""
        bsp_files = list(Path(self.input_dir).glob("*.bsp"))
        
        if not bsp_files:
            print(f"No BSP files found in {self.input_dir}")
            return False
        
        print("=== Counter-Strike BSP to GLB Batch Conversion ===")
        print("(Textures + Models only, no lightmaps)\n")
        os.makedirs(self.output_dir, exist_ok=True)
        
        for bsp_file in bsp_files:
            self.convert_single(bsp_file)
        
        self.print_summary()
        return self.results["failed"] == 0
    
    def convert_single(self, bsp_file):
        """Convert a single BSP file"""
        self.results["total"] += 1
        map_name = bsp_file.stem
        output_glb = Path(self.output_dir) / f"{map_name}.glb"
        
        print(f"Converting: {bsp_file.name}...", end=" ")
        
        try:
            # Run converter with texture extraction, skip sky, no lightmaps
            # -tex: extract all textures
            # -skip_sky: remove sky polygons
            # (no -lm or -lstyle options = no lightmap data)
            result = subprocess.run(
                [self.converter, str(bsp_file), "-tex", "-skip_sky"],
                capture_output=True,
                timeout=60
            )
            
            # Check for errors
            if result.returncode != 0 or b"Error" in result.stderr or b"Can't load" in result.stderr:
                print("✗ FAILED")
                self.results["failed"] += 1
                self.results["conversions"].append({
                    "map": map_name,
                    "status": "failed",
                    "error": result.stderr.decode()[:100]
                })
                return
            
            # Check output
            if Path(map_name + ".glb").exists():
                output_path = Path(self.output_dir) / f"{map_name}.glb"
                Path(map_name + ".glb").rename(output_path)
                size = output_path.stat().st_size
                print(f"✓ SUCCESS ({size} bytes)")
                
                self.results["success"] += 1
                self.results["conversions"].append({
                    "map": map_name,
                    "status": "success",
                    "output_size": size,
                    "includes": ["textures", "models", "geometry"],
                    "excludes": ["lightmaps"]
                })
            else:
                print("✗ FAILED (no output)")
                self.results["failed"] += 1
                self.results["conversions"].append({
                    "map": map_name,
                    "status": "failed",
                    "error": "No output file generated"
                })
        
        except subprocess.TimeoutExpired:
            print("✗ TIMEOUT")
            self.results["failed"] += 1
            self.results["conversions"].append({
                "map": map_name,
                "status": "failed",
                "error": "Conversion timeout"
            })
        except Exception as e:
            print(f"✗ ERROR: {e}")
            self.results["failed"] += 1
    
    def print_summary(self):
        """Print conversion summary"""
        print(f"\n=== SUMMARY ===")
        print(f"Total processed: {self.results['total']}")
        print(f"Successful: {self.results['success']}")
        print(f"Failed: {self.results['failed']}")
        print(f"Output directory: {self.output_dir}")
        print(f"\nOutput format: GLB with textures and 3D models")
        print(f"Lightmaps: Excluded")
        print(f"Sky polygons: Removed")
        
        # Save results to JSON
        results_file = Path(self.output_dir) / "conversion_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"Results saved to: {results_file}")

if __name__ == "__main__":
    converter = "/config/hlbsp-converter/build/bsp-converter"
    input_dir = "/tmp/cs_maps"
    output_dir = "/tmp/cs_maps/converted"
    
    converter_tool = BSPConverter(converter, input_dir, output_dir)
    success = converter_tool.convert_all()
    sys.exit(0 if success else 1)
