# DXFya3 - DXF to AI Converter with Monitor (Version 3.1)

A Python script that automatically detects DXF files in the `/DXF` folder, opens them in Adobe Illustrator, runs ExtendScript actions, and saves them as AI files in the `/AI` folder. Includes a file monitor for automatic processing.

**Version 3.1**: Fully automated workflow with no user interaction required - all alerts and prompts suppressed.

## Requirements

- macOS (uses AppleScript to control Adobe Illustrator)
- Adobe Illustrator installed
- Python 3.6 or higher

## Usage

### Option 1: File Monitor (Recommended)
1. Start the monitor:
   ```bash
   ./start_monitor.sh
   ```
   or
   ```bash
   python3 DXFya3
   ```
2. Place your DXF files in the `DXF` folder
3. The monitor will automatically detect new files and convert them
4. Converted AI files will be saved in the `AI` folder

### Option 2: Manual Conversion
1. Place your DXF files in the `DXF` folder
2. Run the converter:
   ```bash
   python3 dxf_to_ai_converter.py
   ```
3. The converted AI files will be saved in the `AI` folder

### Option 3: Single File Conversion
1. Convert a specific file:
   ```bash
   python3 dxf_to_ai_converter.py --file path/to/your/file.dxf
   ```

## How it works

1. Scans the `DXF` folder for `.dxf` files
2. Checks if Adobe Illustrator is running (launches it if not)
3. For each DXF file:
   - Opens it in Illustrator using AppleScript
   - Suppresses all Illustrator dialogs and alerts (Version 3.1)
   - Runs ExtendScript actions (canvas size check, layer duplication, path extraction)
   - Outputs canvas dimensions to terminal (no alerts)
   - Creates timestamped layers with all objects
   - Extracts and joins overlapping paths
   - Saves it as an AI file in the `AI` folder (no save prompts)
   - Closes the document without prompting
4. Provides a summary of successful and failed conversions

## Notes

- The script will automatically create the `AI` folder if it doesn't exist
- If Illustrator is not running, the script will attempt to launch it
- Each conversion includes appropriate delays to ensure proper processing
- The script handles timeouts gracefully and verifies file creation
- Uses AppleScript commands for better reliability
- Includes ExtendScript actions for canvas analysis before saving
- Large canvas threshold is set to 227.5 inches (standard large format)

## Files

- `DXFya3` - File monitor script (main startup script)
- `dxf_to_ai_converter.py` - Conversion script with ExtendScript support
- `start_monitor.sh` - Bash startup script for the monitor
- `requirements.txt` - Python dependencies (none required)
- `README.md` - This documentation

## Features

- **Fully Automated (Version 3.1)**: No user interaction required - all alerts and prompts suppressed
- **Creative Cloud Integration (NEW)**: Automatically updates matching CC Library files with timestamped layers
- **Automatic File Monitoring**: Detects new DXF files and converts them automatically
- **Terminal Output**: All information displayed in terminal (no Illustrator alerts)
- **ExtendScript Integration**: Canvas size checks, layer duplication, path extraction and joining
- **Timestamped Layers**: Creates organized layers with date/time stamps
- **Path Processing**: Automatically extracts paths from groups and joins overlapping endpoints
- **Multiple Usage Options**: Monitor mode, manual conversion, or single file processing
- **Real-time Feedback**: Shows conversion progress and status in terminal
- **Error Handling**: Graceful handling of timeouts and conversion errors
- **No External Dependencies**: Uses only built-in Python modules and AppleScript
