"""
CAD Model Visualization Tool
This script loads CAD models from h5 files and visualizes them using pyOCC.

Usage:
    python visualize_cad.py --input data/vec/0097/00138437.h5
    python visualize_cad.py --input data/vec/0097/00138437.h5 --export model.step
"""

import argparse
import h5py
import numpy as np
import sys
from pathlib import Path

# Add cadlib to path
sys.path.insert(0, str(Path(__file__).parent))

from cadlib.macro import *
from cadlib.CAD_Class import Profile, Extrude, Revolve, Pocket, Groove, Sketch

# pyOCC imports
try:
    from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Dir, gp_Ax2, gp_Ax1, gp_Pln
    from OCC.Core.BRepBuilderAPI import (
        BRepBuilderAPI_MakeEdge, 
        BRepBuilderAPI_MakeWire,
        BRepBuilderAPI_MakeFace,
        BRepBuilderAPI_Transform
    )
    from OCC.Core.BRepPrimAPI import (
        BRepPrimAPI_MakePrism,
        BRepPrimAPI_MakeRevol
    )
    from OCC.Core.BRepAlgoAPI import (
        BRepAlgoAPI_Cut,
        BRepAlgoAPI_Fuse,
        BRepAlgoAPI_Common
    )
    from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakeOffset
    from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet, BRepFilletAPI_MakeChamfer
    from OCC.Core.GC import GC_MakeArcOfCircle, GC_MakeCircle, GC_MakeSegment
    from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Compound, TopoDS_Wire
    from OCC.Core.TopExp import TopExp_Explorer
    from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_VERTEX
    from OCC.Core.BRep import BRep_Builder, BRep_Tool
    from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
    from OCC.Core.TColgp import TColgp_Array1OfPnt
    from OCC.Core.Geom import Geom_BSplineCurve
    from OCC.Display.SimpleGui import init_display
    from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
    from OCC.Core.IFSelect import IFSelect_RetDone
    
    PYOCC_AVAILABLE = True
except ImportError as e:
    print(f"Warning: pyOCC not available: {e}")
    print("Install with: conda install -c conda-forge pythonocc-core")
    PYOCC_AVAILABLE = False


class CADBuilder:
    """Build 3D CAD models from vector representations using pyOCC"""
    
    def __init__(self, n=256):
        self.n = n
        self.shapes = []
        self.current_shape = None
        
    def build_from_vector(self, cad_vec):
        """Build CAD model from vector representation
        
        Args:
            cad_vec: numpy array of shape (seq_len, 33)
        
        Returns:
            TopoDS_Shape: The built CAD model
        """
        if not PYOCC_AVAILABLE:
            raise RuntimeError("pyOCC is not available. Please install pythonocc-core.")
        
        # Parse the vector sequence
        i = 0
        shapes = []
        
        while i < len(cad_vec):
            cmd_idx = int(cad_vec[i][0])
            
            if cmd_idx == SOL_IDX:
                # Start of a new sketch/feature
                i += 1
                continue
                
            elif cmd_idx == EXT_IDX:
                # Extrusion operation
                shape = self._build_extrusion(cad_vec, i)
                if shape is not None:
                    shapes.append(shape)
                i += 1
                
            elif cmd_idx == REV_IDX:
                # Revolution operation
                shape = self._build_revolution(cad_vec, i)
                if shape is not None:
                    shapes.append(shape)
                i += 1
                
            elif cmd_idx == POCKET_IDX:
                # Pocket operation
                shape = self._build_pocket(cad_vec, i)
                if shape is not None:
                    shapes.append(shape)
                i += 1
                
            elif cmd_idx == GROOVE_IDX:
                # Groove operation
                shape = self._build_groove(cad_vec, i)
                if shape is not None:
                    shapes.append(shape)
                i += 1
                
            elif cmd_idx == EOS_IDX:
                # End of sequence
                i += 1
                
            else:
                # Skip other commands for now
                i += 1
        
        # Combine all shapes using boolean operations
        if not shapes:
            return None
            
        result_shape = shapes[0]
        for shape in shapes[1:]:
            # Try to fuse shapes
            try:
                fuse = BRepAlgoAPI_Fuse(result_shape, shape)
                if fuse.IsDone():
                    result_shape = fuse.Shape()
            except:
                pass
        
        return result_shape
    
    def _build_extrusion(self, cad_vec, ext_idx):
        """Build extrusion from vector"""
        # Find the sketch before this extrusion
        sketch_start = ext_idx - 1
        while sketch_start >= 0:
            if int(cad_vec[sketch_start][0]) == SOL_IDX:
                break
            sketch_start -= 1
        
        if sketch_start < 0:
            return None
        
        # Find where sketch ends (TOPO or EXT)
        sketch_end = sketch_start + 1
        while sketch_end < ext_idx:
            cmd = int(cad_vec[sketch_end][0])
            if cmd in [TOPO_IDX, EXT_IDX]:
                break
            sketch_end += 1
        
        # Extract sketch vectors
        sketch_vec = cad_vec[sketch_start + 1:sketch_end]
        
        # Build sketch profile
        try:
            profile = Profile.from_vector(
                np.vstack([sketch_vec, EOS_VEC[np.newaxis]]),
                is_numerical=True
            )
            profile.denumericalize(self.n)
        except Exception as e:
            print(f"Failed to build profile: {e}")
            return None
        
        # Get extrusion parameters
        ext_vec = cad_vec[ext_idx][1 + N_ARGS_SKETCH:1 + N_ARGS_SKETCH + N_ARGS_EXT]
        
        # Extract plane and position
        theta = ext_vec[0] / self.n * 2 - 1.0
        phi = ext_vec[1] / self.n * 2 - 1.0
        gamma = ext_vec[2] / self.n * 2 - 1.0
        
        theta *= np.pi
        phi *= np.pi
        gamma *= np.pi
        
        pos_x = ext_vec[3] / self.n * 2 - 1.0
        pos_y = ext_vec[4] / self.n * 2 - 1.0
        pos_z = ext_vec[5] / self.n * 2 - 1.0
        size = ext_vec[6] / self.n * 2
        
        length1 = ext_vec[7] / self.n * 2 - 1.0
        
        # Build the wire from profile
        wire = self._build_wire_from_profile(profile)
        if wire is None:
            return None
        
        # Create sketch plane
        origin = gp_Pnt(pos_x, pos_y, pos_z)
        
        # Calculate normal from theta and phi
        normal = gp_Dir(
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta)
        )
        
        # Create face from wire
        plane = gp_Pln(origin, normal)
        face = BRepBuilderAPI_MakeFace(plane, wire).Face()
        
        # Extrude the face
        extrusion_vec = gp_Vec(normal.X() * length1, normal.Y() * length1, normal.Z() * length1)
        prism = BRepPrimAPI_MakePrism(face, extrusion_vec)
        
        if prism.IsDone():
            return prism.Shape()
        
        return None
    
    def _build_revolution(self, cad_vec, rev_idx):
        """Build revolution from vector"""
        # Similar to extrusion but with revolution
        sketch_start = rev_idx - 1
        while sketch_start >= 0:
            if int(cad_vec[sketch_start][0]) == SOL_IDX:
                break
            sketch_start -= 1
        
        if sketch_start < 0:
            return None
        
        sketch_end = sketch_start + 1
        while sketch_end < rev_idx:
            cmd = int(cad_vec[sketch_end][0])
            if cmd in [TOPO_IDX, REV_IDX]:
                break
            sketch_end += 1
        
        sketch_vec = cad_vec[sketch_start + 1:sketch_end]
        
        try:
            profile = Profile.from_vector(
                np.vstack([sketch_vec, EOS_VEC[np.newaxis]]),
                is_numerical=True
            )
            profile.denumericalize(self.n)
        except:
            return None
        
        wire = self._build_wire_from_profile(profile)
        if wire is None:
            return None
        
        # Get revolution parameters
        rev_vec = cad_vec[rev_idx][1 + N_ARGS_SKETCH:1 + N_ARGS_SKETCH + N_ARGS_EXT]
        
        theta = (rev_vec[0] / self.n * 2 - 1.0) * np.pi
        phi = (rev_vec[1] / self.n * 2 - 1.0) * np.pi
        
        pos_x = rev_vec[3] / self.n * 2 - 1.0
        pos_y = rev_vec[4] / self.n * 2 - 1.0
        pos_z = rev_vec[5] / self.n * 2 - 1.0
        
        angle1 = (rev_vec[11] / self.n * 2 - 1.0) * 2 * np.pi
        
        origin = gp_Pnt(pos_x, pos_y, pos_z)
        normal = gp_Dir(
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta)
        )
        
        plane = gp_Pln(origin, normal)
        face = BRepBuilderAPI_MakeFace(plane, wire).Face()
        
        # Create revolution axis
        axis = gp_Ax1(origin, normal)
        revol = BRepPrimAPI_MakeRevol(face, axis, angle1)
        
        if revol.IsDone():
            return revol.Shape()
        
        return None
    
    def _build_pocket(self, cad_vec, pocket_idx):
        """Build pocket (negative extrusion)"""
        # Similar to extrusion but subtracts
        return self._build_extrusion(cad_vec, pocket_idx)
    
    def _build_groove(self, cad_vec, groove_idx):
        """Build groove (negative revolution)"""
        return self._build_revolution(cad_vec, groove_idx)
    
    def _build_wire_from_profile(self, profile):
        """Build a wire from a Profile object
        
        Args:
            profile: Profile object from CAD_Class
            
        Returns:
            TopoDS_Wire: The built wire
        """
        try:
            wire_builder = BRepBuilderAPI_MakeWire()
            
            for loop in profile.children:
                for curve in loop.children:
                    edge = self._build_edge_from_curve(curve)
                    if edge is not None:
                        wire_builder.Add(edge)
            
            if wire_builder.IsDone():
                return wire_builder.Wire()
            
        except Exception as e:
            print(f"Failed to build wire: {e}")
        
        return None
    
    def _build_edge_from_curve(self, curve):
        """Build an edge from a curve object"""
        try:
            start_pt = gp_Pnt(curve.start_point[0], curve.start_point[1], 0)
            end_pt = gp_Pnt(curve.end_point[0], curve.end_point[1], 0)
            
            # Handle different curve types
            curve_type = type(curve).__name__
            
            if curve_type == 'Line':
                edge = BRepBuilderAPI_MakeEdge(start_pt, end_pt).Edge()
                return edge
                
            elif curve_type == 'Arc':
                # For arc, we need a middle point
                # Calculate middle point from arc parameters
                if hasattr(curve, 'xAxis_angle') and hasattr(curve, 'angle'):
                    mid_angle = curve.xAxis_angle + curve.angle / 2
                    mid_x = curve.center[0] + curve.radius * np.cos(mid_angle)
                    mid_y = curve.center[1] + curve.radius * np.sin(mid_angle)
                    mid_pt = gp_Pnt(mid_x, mid_y, 0)
                    
                    arc = GC_MakeArcOfCircle(start_pt, mid_pt, end_pt).Value()
                    edge = BRepBuilderAPI_MakeEdge(arc).Edge()
                    return edge
                else:
                    # Fallback to line
                    edge = BRepBuilderAPI_MakeEdge(start_pt, end_pt).Edge()
                    return edge
                    
            elif curve_type == 'Circle':
                if hasattr(curve, 'center') and hasattr(curve, 'radius'):
                    center = gp_Pnt(curve.center[0], curve.center[1], 0)
                    normal = gp_Dir(0, 0, 1)
                    circle = GC_MakeCircle(center, normal, curve.radius).Value()
                    edge = BRepBuilderAPI_MakeEdge(circle).Edge()
                    return edge
                    
            else:
                # For other types, use a line as fallback
                edge = BRepBuilderAPI_MakeEdge(start_pt, end_pt).Edge()
                return edge
                
        except Exception as e:
            print(f"Failed to build edge from {type(curve).__name__}: {e}")
            
        return None


def visualize_cad_model(h5_path, export_path=None):
    """Load and visualize CAD model from h5 file
    
    Args:
        h5_path: Path to h5 file
        export_path: Optional path to export STEP file
    """
    if not PYOCC_AVAILABLE:
        print("ERROR: pyOCC is not installed.")
        print("Install with: conda install -c conda-forge pythonocc-core")
        return
    
    # Load h5 file
    print(f"Loading CAD model from: {h5_path}")
    with h5py.File(h5_path, "r") as fp:
        cad_vec = fp["vec"][:]
    
    print(f"Vector shape: {cad_vec.shape}")
    
    # Analyze the sequence
    print("\nCAD Sequence:")
    for i in range(min(20, len(cad_vec))):
        cmd_idx = int(cad_vec[i][0])
        if 0 <= cmd_idx < len(ALL_COMMANDS):
            print(f"  {i:2d}. {ALL_COMMANDS[cmd_idx]}")
    
    # Build the CAD model
    print("\nBuilding 3D model...")
    builder = CADBuilder()
    
    try:
        shape = builder.build_from_vector(cad_vec)
        
        if shape is None:
            print("Failed to build CAD model")
            return
        
        print("✓ Model built successfully!")
        
        # Export to STEP if requested
        if export_path:
            print(f"\nExporting to: {export_path}")
            step_writer = STEPControl_Writer()
            step_writer.Transfer(shape, STEPControl_AsIs)
            status = step_writer.Write(export_path)
            
            if status == IFSelect_RetDone:
                print(f"✓ Exported successfully to {export_path}")
            else:
                print(f"✗ Export failed")
        
        # Visualize
        print("\nLaunching visualization...")
        display, start_display, add_menu, add_function_to_menu = init_display()
        display.DisplayShape(shape, update=True)
        display.FitAll()
        start_display()
        
    except Exception as e:
        print(f"Error building model: {e}")
        import traceback
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(
        description="Visualize CAD models from h5 files using pyOCC"
    )
    parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help='Path to input h5 file'
    )
    parser.add_argument(
        '--export', '-e',
        type=str,
        default=None,
        help='Optional: Export to STEP file'
    )
    
    args = parser.parse_args()
    
    if not Path(args.input).exists():
        print(f"Error: File not found: {args.input}")
        return
    
    visualize_cad_model(args.input, args.export)


if __name__ == "__main__":
    main()
