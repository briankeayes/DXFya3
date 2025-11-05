#!/usr/bin/env python3
"""
Open a file from Creative Cloud Libraries directly in Illustrator.
Fast lookup using the indexed database.
"""

import sys
import subprocess
from pathlib import Path
from search_libraries import get_element_by_name

def open_in_illustrator(file_path):
    """Open a file in Illustrator using AppleScript."""
    applescript = f'''
    tell application "Adobe Illustrator"
        activate
        open POSIX file "{file_path}"
    end tell
    '''
    
    try:
        subprocess.run(['osascript', '-e', applescript], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error opening in Illustrator: {e}")
        return False

def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 open_from_library.py <element_name> [<library_name>]")
        print()
        print("Examples:")
        print("  python3 open_from_library.py RT007760-bkdxfya librarytest")
        print("  python3 open_from_library.py RT007760")
        print()
        print("This will:")
        print("  1. Search the indexed database (instant)")
        print("  2. Find the file path")
        print("  3. Open it in Illustrator")
        return
    
    element_name = sys.argv[1]
    library_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"🔍 Looking up: {element_name}...")
    
    # Search database
    result = get_element_by_name(element_name, library_name)
    
    if not result:
        print(f"❌ Element not found: {element_name}")
        if library_name:
            print(f"   in library: {library_name}")
        return
    
    print(f"✅ Found: {result['element_name']}")
    print(f"   Library: {result['library_name']}")
    
    # Check if we have a component path (actual file)
    if not result['component_path']:
        print(f"❌ No file available for this element")
        print(f"   This might be a color, text style, or other non-file asset")
        return
    
    file_path = Path(result['component_path'])
    
    if not file_path.exists():
        print(f"❌ File not found on disk: {file_path}")
        print(f"   The file may need to sync from Creative Cloud")
        return
    
    print(f"📁 File: {file_path.name}")
    print(f"📂 Opening in Illustrator...")
    
    # Open in Illustrator
    if open_in_illustrator(str(file_path)):
        print(f"✅ Opened successfully!")
    else:
        print(f"❌ Failed to open in Illustrator")
        print(f"   Manual path: {file_path}")

if __name__ == '__main__':
    main()

