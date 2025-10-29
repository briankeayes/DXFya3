#!/usr/bin/env python3
"""
DXF to AI Converter - Working Version
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
                    set alertMessage to "Canvas Size: " & docWidth & " x " & docHeight & " inches" & return & "Large Canvas: " & isLargeCanvas
                    display alert alertMessage
                end tell
            on error errMsg
                return "Error: " & errMsg
            end try
        end tell
        '''
        
        print("Running canvas size check...")
        try:
            canvas_result = subprocess.run(['osascript', '-e', canvas_check_script], 
                                         capture_output=True, text=True, timeout=60)
            
            if canvas_result.returncode != 0:
                print(f"Warning: Canvas check failed: {canvas_result.stderr.strip()}")
            else:
                print("Canvas check completed successfully")
        except subprocess.TimeoutExpired:
            print("Canvas check timed out, but continuing with conversion")
        
        # Second action: Create a new layer with datestamp and copy ALL objects
        # Use ExtendScript for more reliable layer operations
        script_dir = Path(__file__).parent
        extendscript_path = script_dir / "layer_duplication_extendscript.jsx"
        
        print(f"🔍 Looking for ExtendScript at: {extendscript_path}")
        if not extendscript_path.exists():
            print(f"❌ ExtendScript file not found: {extendscript_path}")
            return False, f"ExtendScript file not found: {extendscript_path}"
        else:
            print(f"✅ ExtendScript file found: {extendscript_path}")
        
        # Use AppleScript to run the ExtendScript with better error handling
        layer_duplication_script = f'''
    tell application "Adobe Illustrator"
        try
            set scriptResult to do javascript file POSIX file "{extendscript_path}"
            return scriptResult
        on error errMsg
            return "Error running ExtendScript: " & errMsg
        end try
    end tell
    '''
        
        print("Running layer duplication...")
        try:
            layer_result = subprocess.run(['osascript', '-e', layer_duplication_script], 
                                        capture_output=True, text=True, timeout=60)
            
            print(f"Layer duplication result: {layer_result.stdout.strip()}")
            if layer_result.stderr.strip():
                print(f"Layer duplication stderr: {layer_result.stderr.strip()}")
            
            if layer_result.returncode != 0:
                print(f"Warning: Layer duplication failed: {layer_result.stderr.strip()}")
                print("Trying fallback AppleScript method...")
                # Fallback to direct AppleScript
                fallback_script = '''
    tell application "Adobe Illustrator"
        try
            set currentDate to current date
            set dateString to "Layer_" & (year of currentDate) & "-" & (month of currentDate as integer) & "-" & (day of currentDate) & "_" & (hours of currentDate) & "-" & (minutes of currentDate) & "-" & (seconds of currentDate)
            
            tell document 1
                set newLayer to make new layer
                set name of newLayer to dateString
                move newLayer to beginning of layers
                
                select every page item
                copy
                select layer 1
                tell application "Adobe Illustrator" to paste
                
                set layerCount to count of layers
                repeat with i from layerCount to 2 by -1
                    delete layer i
                end repeat
            end tell
            
            return "Fallback: Layer created successfully"
        on error errMsg
            return "Fallback Error: " & errMsg
        end try
    end tell
    '''
                fallback_result = subprocess.run(['osascript', '-e', fallback_script], 
                                               capture_output=True, text=True, timeout=60)
                print(f"Fallback result: {fallback_result.stdout.strip()}")
            else:
                print("Layer duplication completed successfully")
        except subprocess.TimeoutExpired:
            print("Layer duplication timed out, but continuing with conversion")
        
        # Wait a moment for layer operations to complete
        time.sleep(2)
        
        # Save as AI file using the working method
        save_script = f'tell application "Adobe Illustrator" to save document 1 in POSIX file "{ai_path}"'
        try:
            result2 = subprocess.run(['osascript', '-e', save_script], 
                                   capture_output=True, text=True, timeout=60)
            
            if result2.returncode != 0:
                return False, f"Failed to save AI file: {result2.stderr.strip()}"
        except subprocess.TimeoutExpired:
            # Save operation timed out, but check if file was created
            if os.path.exists(ai_path):
                print("Save operation timed out, but file was created successfully")
            else:
                return False, "Save operation timed out and file was not created"
        
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
    print(f"🔧 Using converter script: {script_dir / 'dxf_to_ai_converter.py'}")
    
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
    print("Features: Canvas size check, large canvas detection, layer duplication with datestamp")
    
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
