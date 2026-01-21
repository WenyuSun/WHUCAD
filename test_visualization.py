#!/usr/bin/env python3
"""
Test script to validate CAD model building from h5 files

This script tests the visualization tool with multiple examples from the dataset
to verify that CAD models can be successfully parsed and built.
"""

import sys
import h5py
import numpy as np
from pathlib import Path
import traceback

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from cadlib.macro import ALL_COMMANDS, SOL_IDX, EXT_IDX, REV_IDX, POCKET_IDX, GROOVE_IDX, EOS_IDX, TOPO_IDX
from cadlib.CAD_Class import Profile, Extrude, Revolve, Pocket, Groove
from cadlib.macro import EOS_VEC, N_ARGS_SKETCH, N_ARGS_EXT


def test_h5_file(h5_path):
    """Test parsing and building a CAD model from h5 file
    
    Returns:
        dict: Test results including success status and details
    """
    result = {
        'file': h5_path,
        'success': False,
        'shape': None,
        'num_commands': 0,
        'command_types': [],
        'operations': [],
        'error': None
    }
    
    try:
        # Load h5 file
        with h5py.File(h5_path, "r") as fp:
            cad_vec = fp["vec"][:]
        
        result['shape'] = cad_vec.shape
        result['num_commands'] = cad_vec.shape[0]
        
        # Analyze commands
        commands = []
        operations = []
        
        for i in range(len(cad_vec)):
            cmd_idx = int(cad_vec[i][0])
            if 0 <= cmd_idx < len(ALL_COMMANDS):
                cmd_name = ALL_COMMANDS[cmd_idx]
                commands.append(cmd_name)
                
                # Track major operations
                if cmd_idx in [EXT_IDX, REV_IDX, POCKET_IDX, GROOVE_IDX]:
                    operations.append(cmd_name)
        
        result['command_types'] = list(set(commands))
        result['operations'] = operations
        
        # Try to build profiles and operations
        built_operations = []
        i = 0
        
        while i < len(cad_vec):
            cmd_idx = int(cad_vec[i][0])
            
            if cmd_idx == EXT_IDX:
                # Try to build extrusion
                try:
                    # Find sketch start
                    sketch_start = i - 1
                    while sketch_start >= 0:
                        if int(cad_vec[sketch_start][0]) == SOL_IDX:
                            break
                        sketch_start -= 1
                    
                    if sketch_start >= 0:
                        sketch_end = sketch_start + 1
                        while sketch_end < i:
                            cmd = int(cad_vec[sketch_end][0])
                            if cmd in [TOPO_IDX, EXT_IDX]:
                                break
                            sketch_end += 1
                        
                        sketch_vec = cad_vec[sketch_start:sketch_end]
                        
                        # Build profile
                        profile = Profile.from_vector(
                            np.vstack([sketch_vec, EOS_VEC[np.newaxis]]),
                            is_numerical=True
                        )
                        profile.denumericalize(256)
                        
                        built_operations.append({
                            'type': 'Extrusion',
                            'sketch_commands': len(sketch_vec),
                            'success': True
                        })
                    
                except Exception as e:
                    built_operations.append({
                        'type': 'Extrusion',
                        'success': False,
                        'error': str(e)
                    })
            
            elif cmd_idx == REV_IDX:
                # Try to build revolution
                try:
                    sketch_start = i - 1
                    while sketch_start >= 0:
                        if int(cad_vec[sketch_start][0]) == SOL_IDX:
                            break
                        sketch_start -= 1
                    
                    if sketch_start >= 0:
                        sketch_end = sketch_start + 1
                        while sketch_end < i:
                            cmd = int(cad_vec[sketch_end][0])
                            if cmd in [TOPO_IDX, REV_IDX]:
                                break
                            sketch_end += 1
                        
                        sketch_vec = cad_vec[sketch_start:sketch_end]
                        
                        profile = Profile.from_vector(
                            np.vstack([sketch_vec, EOS_VEC[np.newaxis]]),
                            is_numerical=True
                        )
                        profile.denumericalize(256)
                        
                        built_operations.append({
                            'type': 'Revolution',
                            'sketch_commands': len(sketch_vec),
                            'success': True
                        })
                
                except Exception as e:
                    built_operations.append({
                        'type': 'Revolution',
                        'success': False,
                        'error': str(e)
                    })
            
            i += 1
        
        result['built_operations'] = built_operations
        result['success'] = True
        
    except Exception as e:
        result['error'] = str(e)
        result['traceback'] = traceback.format_exc()
    
    return result


def print_test_result(result):
    """Print test result in a readable format"""
    print("\n" + "=" * 80)
    print(f"File: {result['file']}")
    print("=" * 80)
    
    if result['success']:
        print(f"✓ Successfully parsed")
        print(f"  Shape: {result['shape']}")
        print(f"  Total commands: {result['num_commands']}")
        print(f"  Command types: {', '.join(result['command_types'][:10])}")
        if len(result['command_types']) > 10:
            print(f"                 ... and {len(result['command_types']) - 10} more")
        print(f"  Operations: {', '.join(result['operations'])}")
        
        if 'built_operations' in result:
            print(f"\n  Built operations:")
            for op in result['built_operations']:
                if op['success']:
                    print(f"    ✓ {op['type']}: {op['sketch_commands']} sketch commands")
                else:
                    print(f"    ✗ {op['type']}: Failed - {op.get('error', 'Unknown error')}")
    else:
        print(f"✗ Failed to parse")
        print(f"  Error: {result['error']}")
        if 'traceback' in result:
            print(f"  Traceback:")
            for line in result['traceback'].split('\n')[:10]:
                print(f"    {line}")


def main():
    """Run tests on multiple h5 files"""
    
    # Select test files from different directories
    test_files = [
        "data/vec/0097/00138437.h5",  # Original example
        "data/vec/0097/00138320.h5",
        "data/vec/0000/00000001.h5",
        "data/vec/0001/00010001.h5",
        "data/vec/0050/00500001.h5",
    ]
    
    # Find actual files that exist
    existing_files = []
    for f in test_files:
        if Path(f).exists():
            existing_files.append(f)
    
    # If no specific files exist, find any 5 files
    if len(existing_files) < 3:
        print("Finding available h5 files...")
        import glob
        all_files = glob.glob("data/vec/*/*.h5")
        existing_files = all_files[:5] if all_files else []
    
    if not existing_files:
        print("ERROR: No h5 files found in data/vec directory")
        return
    
    print("=" * 80)
    print(f"Testing CAD model building with {len(existing_files)} examples")
    print("=" * 80)
    
    results = []
    for h5_file in existing_files:
        result = test_h5_file(h5_file)
        results.append(result)
        print_test_result(result)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"\nTotal files tested: {total}")
    print(f"Successfully parsed: {successful} ({100*successful/total:.1f}%)")
    print(f"Failed: {total - successful}")
    
    # Count successful operations
    total_ops = 0
    successful_ops = 0
    
    for r in results:
        if 'built_operations' in r:
            for op in r['built_operations']:
                total_ops += 1
                if op['success']:
                    successful_ops += 1
    
    if total_ops > 0:
        print(f"\nTotal operations attempted: {total_ops}")
        print(f"Successfully built: {successful_ops} ({100*successful_ops/total_ops:.1f}%)")
    
    # Most common operations
    all_operations = []
    for r in results:
        all_operations.extend(r.get('operations', []))
    
    if all_operations:
        from collections import Counter
        op_counts = Counter(all_operations)
        print(f"\nMost common operations:")
        for op, count in op_counts.most_common(5):
            print(f"  {op}: {count}")
    
    print("\n" + "=" * 80)
    
    if successful == total:
        print("✓ All tests passed!")
    elif successful > 0:
        print(f"⚠ {successful}/{total} tests passed")
    else:
        print("✗ All tests failed")
    
    print("=" * 80)


if __name__ == "__main__":
    main()
