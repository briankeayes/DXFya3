#!/usr/bin/env python3
"""
DXF to AI Converter - Working Version with Layer Duplication
Detects DXF files in the /DXF folder, opens them in Adobe Illustrator, runs ExtendScript actions, and saves them as AI files in the /AI folder.
Uses AppleScript to control Illustrator, run canvas size checks, and perform layer operations before saving.
"""

import os
import subprocess
import sys
from pathlib import Path
import time

def check_illustrator_running():
    """Check if Adobe Illustrator is running."""
    try:
        result = subprocess.run(['pgrep', '-f', 'Adobe Illustrator'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def launch_illustrator():
    """Launch Adobe Illustrator if not already running."""
    try:
        subprocess.run(['open', '-a', 'Adobe Illustrator'], check=True)
        print("Launching Adobe Illustrator...")
        time.sleep(5)  # Wait for Illustrator to start
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error launching Illustrator: {e}")
        return False

def convert_dxf_to_ai(dxf_path, ai_path):
    """Convert a DXF file to AI format using AppleScript."""
    
    # Ensure AI directory exists
    os.makedirs(os.path.dirname(ai_path), exist_ok=True)
    
    # Use a single-line AppleScript approach
    applescript = f'tell application "Adobe Illustrator" to set doc to open POSIX file "{dxf_path}"'
    
    try:
        # First, open the DXF file
        result1 = subprocess.run(['osascript', '-e', applescript], 
                               capture_output=True, text=True, timeout=30)
        
        if result1.returncode != 0:
            return False, f"Failed to open DXF file: {result1.stderr.strip()}"
        
        # Wait for file to load
        time.sleep(3)
        
        # Run ExtendScript actions before saving
        # First action: Check if large canvas and display canvas size
        canvas_check_script = '''
        tell application "Adobe Illustrator"
            try
                set doc to document 1
                tell doc
                    set docWidth to width
                    set docHeight to height
                    set isLargeCanvas to (docWidth > 227.5 or docHeight > 227.5)
                    set canvasInfo to "Canvas Size: " & docWidth & " x " & docHeight & " inches, Large Canvas: " & isLargeCanvas
                    return canvasInfo
                end tell
            on error errMsg
                return "Error: " & errMsg
            end try
        end tell
        '''
        
        print("Running canvas size check...")
        try:
            canvas_result = subprocess.run(['osascript', '-e', canvas_check_script], 
                                         capture_output=True, text=True, timeout=30)
            
            if canvas_result.returncode != 0:
                print(f"Warning: Canvas check failed: {canvas_result.stderr.strip()}")
            else:
                print("Canvas check completed successfully")
                # Display canvas information in terminal
                canvas_info = canvas_result.stdout.strip()
                if canvas_info and not canvas_info.startswith("Error:"):
                    print(f"📐 CANVAS INFO: {canvas_info}")
                elif canvas_info.startswith("Error:"):
                    print(f"❌ Canvas check error: {canvas_info}")
        except subprocess.TimeoutExpired:
            print("Canvas check timed out, but continuing with conversion")
        
        # Second action: Move objects directly to new timestamped layer
        script_dir = Path(__file__).parent
        test_script_path = script_dir / "test_move_objects.jsx"
        
        layer_duplication_script = f'''
        tell application "Adobe Illustrator"
            try
                set scriptResult to do javascript file POSIX file "{test_script_path}"
                return scriptResult
            on error errMsg
                return "Error running ExtendScript: " & errMsg
            end try
        end tell
        '''
        
        print("Running layer duplication...")
        layer_result = subprocess.run(['osascript', '-e', layer_duplication_script], 
                                    capture_output=True, text=True, timeout=30)
        
        print(f"Layer duplication result: {layer_result.stdout.strip()}")
        if layer_result.stderr.strip():
            print(f"Layer duplication stderr: {layer_result.stderr.strip()}")
        
        if layer_result.returncode != 0:
            print(f"Warning: Layer duplication failed: {layer_result.stderr.strip()}")
        else:
            print("Layer duplication completed successfully")
            
            # Parse and display object count information
            result_text = layer_result.stdout.strip()
            if "SUCCESS:" in result_text and "objects" in result_text:
                print("📊 OBJECT COUNT SUMMARY:")
                print(f"   {result_text}")
            elif "WARNING:" in result_text:
                print(f"⚠️  {result_text}")
        
        # Third action: Analyze object types
        analyze_script_path = script_dir / "analyze_object_types.jsx"
        
        if analyze_script_path.exists():
            analyze_script = f'''
            tell application "Adobe Illustrator"
                try
                    set scriptResult to do javascript file POSIX file "{analyze_script_path}"
                    return scriptResult
                on error errMsg
                    return "Error running object analysis script: " & errMsg
                end try
            end tell
            '''
            
            print("Running object type analysis...")
            analyze_result = subprocess.run(['osascript', '-e', analyze_script], 
                                          capture_output=True, text=True, timeout=30)
            
            print(f"Object analysis result: {analyze_result.stdout.strip()}")
            if analyze_result.stderr.strip():
                print(f"Object analysis stderr: {analyze_result.stderr.strip()}")
            
            if analyze_result.returncode != 0:
                print(f"Warning: Object analysis failed: {analyze_result.stderr.strip()}")
            else:
                print("Object analysis completed successfully")
                
                # Display analysis results
                analyze_text = analyze_result.stdout.strip()
                if "OBJECT TYPE ANALYSIS" in analyze_text:
                    print("🔍 OBJECT TYPE ANALYSIS:")
                    # Split by newlines and display each line with proper indentation
                    lines = analyze_text.split('\n')
                    for line in lines:
                        if line.strip() != "":
                            print(f"   {line}")
        else:
            print("⚠️  Object analysis script not found, skipping...")
        
        # Fourth action: Diagnose GroupItem contents
        diagnose_script_path = script_dir / "diagnose_groups.jsx"
        
        if diagnose_script_path.exists():
            diagnose_script = f'''
            tell application "Adobe Illustrator"
                try
                    set scriptResult to do javascript file POSIX file "{diagnose_script_path}"
                    return scriptResult
                on error errMsg
                    return "Error running group diagnosis script: " & errMsg
                end try
            end tell
            '''
            
            print("Running group diagnosis...")
            diagnose_result = subprocess.run(['osascript', '-e', diagnose_script], 
                                           capture_output=True, text=True, timeout=30)
            
            print(f"Group diagnosis result: {diagnose_result.stdout.strip()}")
            if diagnose_result.stderr.strip():
                print(f"Group diagnosis stderr: {diagnose_result.stderr.strip()}")
            
            if diagnose_result.returncode != 0:
                print(f"Warning: Group diagnosis failed: {diagnose_result.stderr.strip()}")
            else:
                print("Group diagnosis completed successfully")
                
                # Display diagnosis results
                diagnose_text = diagnose_result.stdout.strip()
                if "GROUP ANALYSIS" in diagnose_text:
                    print("🔍 GROUP DIAGNOSIS:")
                    lines = diagnose_text.split('\n')
                    for line in lines:
                        if line.strip() != "":
                            print(f"   {line}")
        else:
            print("⚠️  Group diagnosis script not found, skipping...")
        
        # Fifth action: Debug ungrouping process
        debug_script_path = script_dir / "debug_ungroup.jsx"
        
        if debug_script_path.exists():
            debug_script = f'''
            tell application "Adobe Illustrator"
                try
                    set scriptResult to do javascript file POSIX file "{debug_script_path}"
                    return scriptResult
                on error errMsg
                    return "Error running debug script: " & errMsg
                end try
            end tell
            '''
            
            print("Running ungroup debugging...")
            debug_result = subprocess.run(['osascript', '-e', debug_script], 
                                        capture_output=True, text=True, timeout=30)
            
            print(f"Debug result: {debug_result.stdout.strip()}")
            if debug_result.stderr.strip():
                print(f"Debug stderr: {debug_result.stderr.strip()}")
            
            if debug_result.returncode != 0:
                print(f"Warning: Debug failed: {debug_result.stderr.strip()}")
            else:
                print("Debug completed successfully")
                
                # Display debug results
                debug_text = debug_result.stdout.strip()
                if "DEBUG UNGROUPING" in debug_text:
                    print("🔍 DEBUG UNGROUPING:")
                    lines = debug_text.split('\n')
                    for line in lines:
                        if line.strip() != "":
                            print(f"   {line}")
        else:
            print("⚠️  Debug script not found, skipping...")
        
        # Sixth action: Ungroup all objects in timestamped layer
        ungroup_script_path = script_dir / "ungroup_objects.jsx"
        
        if ungroup_script_path.exists():
            ungroup_script = f'''
            tell application "Adobe Illustrator"
                try
                    set scriptResult to do javascript file POSIX file "{ungroup_script_path}"
                    return scriptResult
                on error errMsg
                    return "Error running ungroup script: " & errMsg
                end try
            end tell
            '''
            
            print("Running object ungrouping...")
            ungroup_result = subprocess.run(['osascript', '-e', ungroup_script], 
                                          capture_output=True, text=True, timeout=60)
            
            print(f"Ungroup result: {ungroup_result.stdout.strip()}")
            if ungroup_result.stderr.strip():
                print(f"Ungroup stderr: {ungroup_result.stderr.strip()}")
            
            if ungroup_result.returncode != 0:
                print(f"Warning: Ungrouping failed: {ungroup_result.stderr.strip()}")
            else:
                print("Object ungrouping completed successfully")
                
                # Display ungroup results
                ungroup_text = ungroup_result.stdout.strip()
                if "SUCCESS:" in ungroup_text:
                    print("📦 UNGROUP SUMMARY:")
                    print(f"   {ungroup_text}")
        else:
            print("⚠️  Ungroup script not found, skipping...")
        
        # Sixth action: Extract PathItems from GroupItems
        extract_script_path = script_dir / "extract_paths.jsx"
        
        if extract_script_path.exists():
            extract_script = f'''
            tell application "Adobe Illustrator"
                try
                    set scriptResult to do javascript file POSIX file "{extract_script_path}"
                    return scriptResult
                on error errMsg
                    return "Error running path extraction script: " & errMsg
                end try
            end tell
            '''
            
            print("Running path extraction...")
            extract_result = subprocess.run(['osascript', '-e', extract_script], 
                                          capture_output=True, text=True, timeout=60)
            
            print(f"Path extraction result: {extract_result.stdout.strip()}")
            if extract_result.stderr.strip():
                print(f"Path extraction stderr: {extract_result.stderr.strip()}")
            
            if extract_result.returncode != 0:
                print(f"Warning: Path extraction failed: {extract_result.stderr.strip()}")
            else:
                print("Path extraction completed successfully")
                
                # Display extraction results
                extract_text = extract_result.stdout.strip()
                if "SUCCESS:" in extract_text:
                    print("📤 PATH EXTRACTION SUMMARY:")
                    print(f"   {extract_text}")
        else:
            print("⚠️  Path extraction script not found, skipping...")
        
        # Seventh action: Debug PathItems and overlap detection
        debug_paths_script_path = script_dir / "debug_paths.jsx"
        
        if debug_paths_script_path.exists():
            debug_paths_script = f'''
            tell application "Adobe Illustrator"
                try
                    set scriptResult to do javascript file POSIX file "{debug_paths_script_path}"
                    return scriptResult
                on error errMsg
                    return "Error running path debug script: " & errMsg
                end try
            end tell
            '''
            
            print("Running path debugging...")
            debug_paths_result = subprocess.run(['osascript', '-e', debug_paths_script], 
                                              capture_output=True, text=True, timeout=30)
            
            print(f"Path debug result: {debug_paths_result.stdout.strip()}")
            if debug_paths_result.stderr.strip():
                print(f"Path debug stderr: {debug_paths_result.stderr.strip()}")
            
            if debug_paths_result.returncode != 0:
                print(f"Warning: Path debug failed: {debug_paths_result.stderr.strip()}")
            else:
                print("Path debug completed successfully")
                
                # Display debug results
                debug_paths_text = debug_paths_result.stdout.strip()
                if "PATH ANALYSIS" in debug_paths_text:
                    print("🔍 PATH DEBUG ANALYSIS:")
                    lines = debug_paths_text.split('\n')
                    for line in lines:
                        if line.strip() != "":
                            print(f"   {line}")
        else:
            print("⚠️  Path debug script not found, skipping...")
        
        # Eighth action: Simple path joining using Illustrator's join command
        simple_join_script_path = script_dir / "simple_join_paths.jsx"
        
        if simple_join_script_path.exists():
            simple_join_script = f'''
            tell application "Adobe Illustrator"
                try
                    set scriptResult to do javascript file POSIX file "{simple_join_script_path}"
                    return scriptResult
                on error errMsg
                    return "Error running simple join script: " & errMsg
                end try
            end tell
            '''
            
            print("Running simple path joining...")
            simple_join_result = subprocess.run(['osascript', '-e', simple_join_script], 
                                               capture_output=True, text=True, timeout=60)
            
            print(f"Simple join result: {simple_join_result.stdout.strip()}")
            if simple_join_result.stderr.strip():
                print(f"Simple join stderr: {simple_join_result.stderr.strip()}")
            
            if simple_join_result.returncode != 0:
                print(f"Warning: Simple path joining failed: {simple_join_result.stderr.strip()}")
            else:
                print("Simple path joining completed successfully")
                
                # Parse and display path joining information
                simple_join_text = simple_join_result.stdout.strip()
                if "SUCCESS:" in simple_join_text:
                    print("🔗 SIMPLE PATH JOINING SUMMARY:")
                    print(f"   {simple_join_text}")
                elif "INFO:" in simple_join_text:
                    print(f"ℹ️  {simple_join_text}")
        else:
            print("⚠️  Simple join script not found, skipping...")
        
        # Save as AI file
        save_script = f'tell application "Adobe Illustrator" to save document 1 in POSIX file "{ai_path}"'
        result2 = subprocess.run(['osascript', '-e', save_script], 
                               capture_output=True, text=True, timeout=60)
        
        if result2.returncode != 0:
            return False, f"Failed to save AI file: {result2.stderr.strip()}"
        
        # Close the document (don't fail if this times out)
        close_script = 'tell application "Adobe Illustrator" to close document 1'
        try:
            result3 = subprocess.run(['osascript', '-e', close_script], 
                                   capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            # Document close timed out, but conversion was successful
            pass
        
        # Check if the AI file was actually created
        if os.path.exists(ai_path):
            return True, "Success"
        else:
            return False, "AI file was not created"
        
    except subprocess.TimeoutExpired:
        return False, "Timeout: Illustrator operation took too long"
    except Exception as e:
        return False, f"Error running AppleScript: {e}"

def find_dxf_files(dxf_folder):
    """Find all DXF files in the specified folder."""
    dxf_files = []
    if os.path.exists(dxf_folder):
        for file in os.listdir(dxf_folder):
            if file.lower().endswith('.dxf'):
                dxf_files.append(os.path.join(dxf_folder, file))
    return dxf_files

def ensure_ai_folder(ai_folder):
    """Ensure the AI folder exists."""
    os.makedirs(ai_folder, exist_ok=True)

def process_single_file(dxf_file):
    """Process a single DXF file."""
    script_dir = Path(__file__).parent
    ai_folder = script_dir / "AI"
    
    # Ensure AI folder exists
    ensure_ai_folder(ai_folder)
    
    filename = os.path.basename(dxf_file)
    name_without_ext = os.path.splitext(filename)[0]
    ai_file = ai_folder / f"{name_without_ext}.ai"
    
    print(f"🔄 Processing: {filename}")
    print(f"💾 Output: {ai_file}")
    
    # Check if Illustrator is running
    if not check_illustrator_running():
        print("⚠️  Adobe Illustrator is not running. Launching...")
        if not launch_illustrator():
            print("❌ Failed to launch Adobe Illustrator.")
            sys.exit(1)
    
    success, message = convert_dxf_to_ai(str(dxf_file), str(ai_file))
    
    if success:
        print(f"✅ Successfully converted: {filename}")
    else:
        print(f"❌ Failed to convert {filename}: {message}")
        sys.exit(1)

def main():
    """Main function to process DXF files."""
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--file':
        if len(sys.argv) < 3:
            print("❌ Error: --file requires a file path")
            sys.exit(1)
        single_file = sys.argv[2]
        if not os.path.exists(single_file):
            print(f"❌ Error: File not found: {single_file}")
            sys.exit(1)
        if not single_file.lower().endswith('.dxf'):
            print(f"❌ Error: File is not a DXF file: {single_file}")
            sys.exit(1)
        process_single_file(single_file)
        return
    
    # Define paths
    script_dir = Path(__file__).parent
    dxf_folder = script_dir / "DXF"
    ai_folder = script_dir / "AI"
    
    print("DXF to AI Converter - Working Version")
    print("====================================")
    print("Features: Canvas size check, large canvas detection, layer duplication")
    
    # Ensure AI folder exists
    ensure_ai_folder(ai_folder)
    
    # Find DXF files
    dxf_files = find_dxf_files(dxf_folder)
    
    if not dxf_files:
        print(f"No DXF files found in {dxf_folder}")
        return
    
    print(f"Found {len(dxf_files)} DXF file(s):")
    for file in dxf_files:
        print(f"  - {os.path.basename(file)}")
    
    # Check if Illustrator is running
    if not check_illustrator_running():
        print("Adobe Illustrator is not running. Launching...")
        if not launch_illustrator():
            print("Failed to launch Adobe Illustrator. Please launch it manually and try again.")
            return
    
    # Process each DXF file
    successful_conversions = 0
    failed_conversions = 0
    
    for dxf_file in dxf_files:
        filename = os.path.basename(dxf_file)
        name_without_ext = os.path.splitext(filename)[0]
        ai_file = ai_folder / f"{name_without_ext}.ai"
        
        print(f"\nProcessing: {filename}")
        print(f"Output: {ai_file}")
        
        success, message = convert_dxf_to_ai(str(dxf_file), str(ai_file))
        
        if success:
            print(f"✓ Successfully converted: {filename}")
            successful_conversions += 1
        else:
            print(f"✗ Failed to convert {filename}: {message}")
            failed_conversions += 1
        
        # Small delay between conversions
        time.sleep(1)
    
    # Summary
    print(f"\nConversion Summary:")
    print(f"  Successful: {successful_conversions}")
    print(f"  Failed: {failed_conversions}")
    print(f"  Total: {len(dxf_files)}")

if __name__ == "__main__":
    main()