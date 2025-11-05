#!/usr/bin/env python3
import json
import os
from pathlib import Path

# Path to CC Libraries
base_path = Path.home() / "Library/Application Support/Adobe/Creative Cloud Libraries/LIBS/6D27744844570B5D992016E5_AdobeID"

def extract_elements():
    all_elements = []
    
    # Process private libraries
    private_path = base_path / "creative_cloud/dcx"
    if private_path.exists():
        for library_dir in private_path.iterdir():
            if library_dir.is_dir():
                manifest_file = library_dir / "manifest"
                if manifest_file.exists():
                    try:
                        with open(manifest_file, 'r') as f:
                            data = json.load(f)
                            library_id = data.get('id')
                            library_name = data.get('name')
                            
                            # Extract elements
                            children = data.get('children', [])
                            for child in children:
                                if child.get('name') == 'elements':
                                    for element in child.get('children', []):
                                        # Get file type from components
                                        file_type = 'unknown'
                                        file_name = ''
                                        file_size = 0
                                        
                                        components = element.get('components', [])
                                        if components:
                                            comp = components[0]
                                            file_type = comp.get('type', 'unknown')
                                            file_name = comp.get('name', '')
                                            file_size = comp.get('length', 0)
                                        
                                        all_elements.append({
                                            'library_id': library_id,
                                            'library_name': library_name,
                                            'library_type': 'private',
                                            'element_id': element.get('id'),
                                            'element_name': element.get('name', 'Untitled'),
                                            'element_type': element.get('type', ''),
                                            'file_type': file_type,
                                            'file_name': file_name,
                                            'file_size': file_size,
                                            'path': element.get('path', ''),
                                            'created': element.get('library#created'),
                                            'modified': element.get('library#modified')
                                        })
                    except (json.JSONDecodeError, IOError) as e:
                        print(f"// Error reading {manifest_file}: {e}", file=sys.stderr)
                        continue
    
    # Process shared libraries
    collab_path = base_path / "collaborated/dcx"
    if collab_path.exists():
        for library_dir in collab_path.iterdir():
            if library_dir.is_dir():
                manifest_file = library_dir / "manifest"
                if manifest_file.exists():
                    try:
                        with open(manifest_file, 'r') as f:
                            data = json.load(f)
                            library_id = data.get('id')
                            library_name = data.get('name')
                            
                            # Extract elements
                            children = data.get('children', [])
                            for child in children:
                                if child.get('name') == 'elements':
                                    for element in child.get('children', []):
                                        # Get file type from components
                                        file_type = 'unknown'
                                        file_name = ''
                                        file_size = 0
                                        
                                        components = element.get('components', [])
                                        if components:
                                            comp = components[0]
                                            file_type = comp.get('type', 'unknown')
                                            file_name = comp.get('name', '')
                                            file_size = comp.get('length', 0)
                                        
                                        all_elements.append({
                                            'library_id': library_id,
                                            'library_name': library_name,
                                            'library_type': 'shared',
                                            'element_id': element.get('id'),
                                            'element_name': element.get('name', 'Untitled'),
                                            'element_type': element.get('type', ''),
                                            'file_type': file_type,
                                            'file_name': file_name,
                                            'file_size': file_size,
                                            'path': element.get('path', ''),
                                            'created': element.get('library#created'),
                                            'modified': element.get('library#modified')
                                        })
                    except (json.JSONDecodeError, IOError) as e:
                        print(f"// Error reading {manifest_file}: {e}", file=sys.stderr)
                        continue
    
    # Output as JavaScript
    print("// Auto-generated library elements data")
    print(f"const libraryElements = {json.dumps(all_elements, indent=2)};")

if __name__ == '__main__':
    import sys
    extract_elements()

