# CAD Model Visualization

This tool allows you to visualize CAD models from WHUCAD h5 files using pyOCC (pythonOCC-core).

## Installation

### Install pyOCC

```bash
# Using conda (recommended)
conda install -c conda-forge pythonocc-core

# Or using pip (may require additional dependencies)
pip install pythonocc-core
```

### Install other dependencies

```bash
pip install h5py numpy
```

## Usage

### Basic Visualization

Visualize a CAD model from an h5 file:

```bash
python visualize_cad.py --input data/vec/0097/00138437.h5
```

### Export to STEP Format

Visualize and export to STEP file for use in other CAD software:

```bash
python visualize_cad.py --input data/vec/0097/00138437.h5 --export output.step
```

### Batch Processing

Process multiple files:

```bash
# Visualize all files in a directory
for file in data/vec/0097/*.h5; do
    python visualize_cad.py --input "$file" --export "output/$(basename $file .h5).step"
done
```

## Understanding the Visualization

The script performs the following steps:

1. **Load h5 file**: Reads the CAD vector representation
2. **Parse commands**: Analyzes the sequence of CAD operations (Line, Arc, Circle, Extrude, etc.)
3. **Build geometry**: Uses pyOCC to construct 3D geometry from the commands
4. **Visualize**: Opens an interactive 3D viewer

## Supported Features

Currently supports:
- ✓ Line, Arc, Circle curves
- ✓ Extrusion (Ext) operations
- ✓ Revolution (Rev) operations
- ✓ Pocket operations
- ✓ Groove operations
- ✓ STEP file export

Advanced features (in development):
- Shell, Chamfer, Fillet
- Mirror operations
- Boolean operations
- Selection mechanisms

## Troubleshooting

### pyOCC installation issues

If you encounter issues installing pyOCC:

1. Try using conda instead of pip:
   ```bash
   conda install -c conda-forge pythonocc-core
   ```

2. Ensure you have a compatible Python version (3.7-3.11)

3. For detailed installation instructions, see:
   https://github.com/tpaviot/pythonocc-core

### Visualization window doesn't open

Some systems may require additional display libraries. Try:

```bash
# On Linux
sudo apt-get install libgl1-mesa-glx

# On macOS
brew install mesa
```

## Examples

### Example 1: Simple Extrusion

```bash
python visualize_cad.py --input data/vec/0097/00138437.h5
```

This will open an interactive window where you can:
- Rotate: Left mouse button
- Pan: Middle mouse button
- Zoom: Scroll wheel

### Example 2: Export for CAD Software

```bash
python visualize_cad.py --input data/vec/0097/00138437.h5 --export model.step
```

The exported STEP file can be opened in:
- FreeCAD
- SolidWorks
- CATIA
- Fusion 360
- And other CAD software

## Reference

This implementation is based on:
- [DeepCAD](https://github.com/rundiwu/DeepCAD) - Original CAD generation framework
- [pythonOCC](https://github.com/tpaviot/pythonocc-core) - Python bindings for OpenCASCADE

## Vector Format

For detailed information about the WHUCAD vector format, see:
[docs/VECTOR_FORMAT_EXPLANATION.md](docs/VECTOR_FORMAT_EXPLANATION.md)
