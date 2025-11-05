#!/usr/bin/env python3
"""
Update a Creative Cloud Library file with a timestamped layer from a local AI file.
Integrates DXFya3 with DXFya3toCCLibrary database.
"""

import sys
import subprocess
from pathlib import Path

# Add parent directory to path to import search_libraries
sys.path.insert(0, str(Path(__file__).parent))
from search_libraries import get_element_by_name

def copy_layer_to_cc_file(local_ai_path, cc_file_path):
    """Copy timestamped layer from local AI file to CC Library file using ExtendScript."""
    
    # Create ExtendScript that will be executed in Illustrator
    extendscript_path = Path(__file__).parent / "copy_layer_to_cc.jsx"
    
    extendscript_content = f'''
try {{
    // Suppress dialogs
    app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
    
    // Open local file (source)
    var localFile = new File("{local_ai_path}");
    if (!localFile.exists) {{
        "ERROR: Local file not found: {local_ai_path}";
    }} else {{
        var localDoc = app.open(localFile);
        
        // Find the timestamped layer (should be first layer)
        var sourceLayerName = null;
        var sourceLayerIndex = -1;
        for (var i = 0; i < localDoc.layers.length; i++) {{
            if (localDoc.layers[i].name.match(/\\d{{4}}-\\d{{2}}-\\d{{2}}_\\d{{2}}-\\d{{2}}-\\d{{2}}/)) {{
                sourceLayerName = localDoc.layers[i].name;
                sourceLayerIndex = i;
                break;
            }}
        }}
        
        if (sourceLayerIndex === -1) {{
            localDoc.close(SaveOptions.DONOTSAVECHANGES);
            "ERROR: No timestamped layer found in local file";
        }} else {{
            // Open CC Library file (destination)
            var ccFile = new File("{cc_file_path}");
            if (!ccFile.exists) {{
                localDoc.close(SaveOptions.DONOTSAVECHANGES);
                "ERROR: CC file not found: {cc_file_path}";
            }} else {{
                var ccDoc;
                try {{
                    ccDoc = app.open(ccFile);
                }} catch (openError) {{
                    localDoc.close(SaveOptions.DONOTSAVECHANGES);
                    "ERROR opening CC file: " + openError.toString();
                    throw openError;
                }}
                
                // Unlock all layers in CC document
                try {{
                    for (var k = 0; k < ccDoc.layers.length; k++) {{
                        ccDoc.layers[k].locked = false;
                    }}
                }} catch (unlockError) {{
                    localDoc.close(SaveOptions.DONOTSAVECHANGES);
                    ccDoc.close(SaveOptions.DONOTSAVECHANGES);
                    "ERROR unlocking layers: " + unlockError.toString();
                    throw unlockError;
                }}
                
                // Find the correct position: above any layer starting with "DXF"
                var targetLayer = null;
                for (var i = 0; i < ccDoc.layers.length; i++) {{
                    if (ccDoc.layers[i].name.indexOf("DXF") === 0) {{
                        targetLayer = ccDoc.layers[i];
                        break;
                    }}
                }}
                
                // Make source layer active and select all its items
                try {{
                    app.activeDocument = localDoc;
                    var sourceLayer = localDoc.layers[sourceLayerIndex];
                    localDoc.activeLayer = sourceLayer;
                    localDoc.selection = null;
                    var itemCount = sourceLayer.pageItems.length;
                    
                    // Select all items in source layer
                    for (var j = 0; j < sourceLayer.pageItems.length; j++) {{
                        sourceLayer.pageItems[j].selected = true;
                    }}
                    
                    // Copy to clipboard
                    app.copy();
                    
                    // Switch to CC document and create new layer
                    app.activeDocument = ccDoc;
                    var newLayer = ccDoc.layers.add();
                    newLayer.name = sourceLayerName;
                    newLayer.locked = false;
                    ccDoc.activeLayer = newLayer;
                    ccDoc.selection = null;
                    
                    // Paste items into new layer
                    app.paste();
                }} catch (copyError) {{
                    localDoc.close(SaveOptions.DONOTSAVECHANGES);
                    ccDoc.close(SaveOptions.DONOTSAVECHANGES);
                    "ERROR during copy/paste: " + copyError.toString();
                    throw copyError;
                }}
                
                // Position the new layer correctly (after items are copied)
                var positionMsg = "";
                if (targetLayer) {{
                    // Place above the first DXF layer found
                    newLayer.move(targetLayer, ElementPlacement.PLACEBEFORE);
                    positionMsg = " (placed above '" + targetLayer.name + "')";
                }} else {{
                    // No DXF layers found, leave at top
                    positionMsg = " (placed at top - no DXF layers found)";
                }}
                
                // Save CC document without dialogs
                ccDoc.save();
                ccDoc.close(SaveOptions.DONOTSAVECHANGES);
                
                // Close local document without saving
                localDoc.close(SaveOptions.DONOTSAVECHANGES);
                
                "SUCCESS: Layer '" + sourceLayerName + "' with " + itemCount + " objects copied to CC Library file" + positionMsg;
            }}
        }}
    }}
}} catch (error) {{
    "ERROR: " + error.toString();
}}
'''
    
    # Write ExtendScript to temporary file
    with open(extendscript_path, 'w') as f:
        f.write(extendscript_content)
    
    # Execute via AppleScript
    applescript = f'''
    tell application "Adobe Illustrator"
        try
            set scriptResult to do javascript file POSIX file "{extendscript_path}"
            return scriptResult
        on error errMsg
            return "Error: " & errMsg
        end try
    end tell
    '''
    
    try:
        result = subprocess.run(['osascript', '-e', applescript], 
                              capture_output=True, text=True, timeout=120)
        
        # Clean up temporary ExtendScript file
        try:
            extendscript_path.unlink()
        except:
            pass
        
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "ERROR: Operation timed out"
    except Exception as e:
        return f"ERROR: {e}"

def update_cc_library_file(local_ai_path, base_filename):
    """
    Find matching CC Library file and update it with timestamped layer.
    
    Args:
        local_ai_path: Path to the locally created AI file
        base_filename: Base name to search for (e.g., "RT004127_cut")
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    print(f"🔍 Searching CC Libraries for: {base_filename}")
    
    # Search database for matching element
    result = get_element_by_name(base_filename)
    
    if not result:
        print(f"ℹ️  No matching file found in CC Libraries")
        print(f"   Searched for: {base_filename}")
        return False
    
    print(f"✅ Found in CC Library: {result['library_name']}")
    print(f"   Element: {result['element_name']}")
    
    # Check if component path exists
    if not result['component_path']:
        print(f"❌ No file component available for this element")
        return False
    
    cc_file_path = Path(result['component_path'])
    
    if not cc_file_path.exists():
        print(f"❌ CC file not synced locally yet")
        print(f"   Path: {cc_file_path}")
        return False
    
    print(f"📂 CC File: {cc_file_path.name}")
    print(f"🔄 Copying timestamped layer to CC Library file...")
    
    # Copy the layer
    result_msg = copy_layer_to_cc_file(str(local_ai_path), str(cc_file_path))
    
    if "SUCCESS:" in result_msg:
        print(f"✅ {result_msg}")
        print(f"☁️  Changes will sync to Creative Cloud automatically")
        return True
    else:
        print(f"❌ {result_msg}")
        return False

def main():
    """Command-line interface."""
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 update_cc_library_file.py <local_ai_file> <base_filename>")
        print()
        print("Example:")
        print("  python3 update_cc_library_file.py ../AI/RT004127_cut.ai RT004127_cut")
        print()
        print("This will:")
        print("  1. Search CC Libraries database for matching file")
        print("  2. Find the local cached CC Library file")
        print("  3. Copy the timestamped layer to the CC file")
        print("  4. Save (Creative Cloud auto-syncs to cloud)")
        return
    
    local_ai_path = sys.argv[1]
    base_filename = sys.argv[2]
    
    if not Path(local_ai_path).exists():
        print(f"❌ Local AI file not found: {local_ai_path}")
        return
    
    success = update_cc_library_file(local_ai_path, base_filename)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

