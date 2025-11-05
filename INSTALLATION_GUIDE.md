# DXFya3 Installation Guide

## Prerequisites

### Required Software
1. **Python 3** - macOS usually comes with Python 3, but verify with `python3 --version`
2. **Adobe Illustrator** - Must be installed and accessible
3. **Git** - For cloning the repository (usually pre-installed on macOS)

### System Requirements
- macOS 10.14 (Mojave) or later
- Adobe Illustrator CC 2018 or later
- At least 4GB RAM
- Sufficient disk space for DXF/AI files

## Installation Steps

### Step 1: Clone the Repository
```bash
# Navigate to your desired directory
cd ~/Desktop  # or wherever you want to install it

# Clone the repository
git clone https://github.com/briankeayes/DXFya3.git

# Navigate to the project directory
cd DXFya3
```

### Step 2: Verify Python Installation
```bash
# Check Python version (should be 3.6 or later)
python3 --version

# If Python 3 is not installed, install via Homebrew:
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# brew install python3
```

### Step 3: Make Scripts Executable
```bash
# Make the main script executable
chmod +x DXFya3

# Make the converter script executable
chmod +x dxf_to_ai_converter_working.py
```

### Step 4: Test Adobe Illustrator Access
```bash
# Test if Illustrator can be launched
open -a "Adobe Illustrator"

# Close Illustrator after confirming it opens
```

### Step 5: Create Required Directories
```bash
# The script will create these automatically, but you can pre-create them:
mkdir -p DXF
mkdir -p AI
```

### Step 6: Test Installation
```bash
# Run the monitor to test installation
./DXFya3
```

## Configuration

### Directory Structure
After installation, your directory should look like:
```
DXFya3/
├── DXF/                    # Place DXF files here
├── AI/                     # Converted AI files appear here
├── DXFya3                  # Main monitor script
├── dxf_to_ai_converter_working.py
├── test_move_objects.jsx
├── analyze_object_types.jsx
├── extract_paths.jsx
├── simple_join_paths.jsx
└── README.md
```

### Usage Instructions
1. **Place DXF files** in the `DXF/` folder
2. **Run the monitor**: `./DXFya3`
3. **Monitor will automatically**:
   - Detect new DXF files
   - Convert them to AI format
   - Create timestamped layers
   - Extract and join paths
   - Save results in `AI/` folder

## Troubleshooting

### Common Issues

#### 1. Permission Denied Error
```bash
# Fix script permissions
chmod +x DXFya3
chmod +x dxf_to_ai_converter_working.py
```

#### 2. Illustrator Not Found
- Ensure Adobe Illustrator is installed
- Check if it's in Applications folder
- Try launching manually: `open -a "Adobe Illustrator"`

#### 3. Python Not Found
```bash
# Install Python via Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python3
```

#### 4. ExtendScript Errors
- Ensure Illustrator is running
- Check that ExtendScript files are in the same directory
- Verify Illustrator has permission to run scripts

### Testing the Installation

#### Test 1: Basic Functionality
```bash
# Create a test DXF file (or use an existing one)
# Place it in the DXF/ folder
# Run the monitor
./DXFya3
```

#### Test 2: Check Output
- Verify AI files are created in `AI/` folder
- Open AI files in Illustrator to check layer structure
- Confirm timestamped layers are created

## Advanced Configuration

### Customizing Settings
You can modify these settings in `dxf_to_ai_converter_working.py`:

- **Canvas size threshold**: Line 63 (currently 227.5 inches)
- **Path joining tolerance**: Line 15 in `simple_join_paths.jsx` (currently 1.0 points)
- **Polling interval**: Line 87 in `DXFya3` (currently 2 seconds)

### Running as Background Service
```bash
# Run in background
nohup ./DXFya3 > dxfya3.log 2>&1 &

# Check if running
ps aux | grep DXFya3

# Stop background process
pkill -f DXFya3
```

## Support

### Getting Help
- Check the terminal output for error messages
- Review the log files for detailed information
- Ensure all prerequisites are installed correctly

### File Locations
- **Logs**: Check terminal output or `dxfya3.log` if running in background
- **DXF Files**: Place in `DXF/` directory
- **AI Files**: Generated in `AI/` directory
- **Scripts**: All ExtendScript files must be in the main directory

## Updates

### Updating DXFya3
```bash
# Navigate to the project directory
cd DXFya3

# Pull latest changes
git pull origin main

# Restart the monitor
./DXFya3
```

---

*This installation guide ensures DXFya3 works correctly on any Mac system with the proper prerequisites.*


