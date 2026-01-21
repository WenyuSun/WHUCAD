#!/usr/bin/env python3
"""
Simple example of visualizing WHUCAD models

This example demonstrates how to:
1. Load a CAD model from an h5 file
2. Parse the vector representation
3. Build and visualize the 3D model using pyOCC

Note: Requires pythonocc-core to be installed
      conda install -c conda-forge pythonocc-core
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from visualize_cad import visualize_cad_model, PYOCC_AVAILABLE

def main():
    """Run a simple visualization example"""
    
    # Check if pyOCC is available
    if not PYOCC_AVAILABLE:
        print("=" * 60)
        print("ERROR: pyOCC (pythonocc-core) is not installed")
        print("=" * 60)
        print("\nTo install pyOCC:")
        print("  conda install -c conda-forge pythonocc-core")
        print("\nFor more information, see:")
        print("  docs/VISUALIZATION_GUIDE.md")
        print("=" * 60)
        return
    
    # Example h5 file path
    example_file = "data/vec/0097/00138437.h5"
    
    if not Path(example_file).exists():
        print(f"Example file not found: {example_file}")
        print("\nPlease provide a valid h5 file path:")
        print("  python example_visualize.py path/to/your/file.h5")
        return
    
    # Get file path from command line if provided
    if len(sys.argv) > 1:
        h5_file = sys.argv[1]
    else:
        h5_file = example_file
    
    print("=" * 60)
    print("WHUCAD CAD Model Visualization Example")
    print("=" * 60)
    print(f"\nVisualizing file: {h5_file}\n")
    
    # Visualize the model
    visualize_cad_model(h5_file)
    
    print("\nVisualization complete!")
    print("\nFor more options, use:")
    print("  python visualize_cad.py --help")


if __name__ == "__main__":
    main()
