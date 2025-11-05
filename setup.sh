#!/bin/bash

# DXFya3 Setup Script
# This script automates the installation process on a new Mac

echo "🎯 DXFya3 Installation Script"
echo "=============================="

# Check if we're in the right directory
if [ ! -f "DXFya3" ]; then
    echo "❌ Error: Please run this script from the DXFya3 directory"
    echo "   Make sure you've cloned the repository first:"
    echo "   git clone https://github.com/briankeayes/DXFya3.git"
    exit 1
fi

echo "✅ Found DXFya3 directory"

# Check Python 3
echo "🔍 Checking Python 3..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Found: $PYTHON_VERSION"
else
    echo "❌ Python 3 not found"
    echo "   Please install Python 3 first:"
    echo "   brew install python3"
    exit 1
fi

# Check Adobe Illustrator
echo "🔍 Checking Adobe Illustrator..."
if [ -d "/Applications/Adobe Illustrator 2024" ] || [ -d "/Applications/Adobe Illustrator 2023" ] || [ -d "/Applications/Adobe Illustrator 2022" ] || [ -d "/Applications/Adobe Illustrator 2021" ]; then
    echo "✅ Adobe Illustrator found"
else
    echo "⚠️  Adobe Illustrator not found in Applications"
    echo "   Please ensure Adobe Illustrator is installed"
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x DXFya3
chmod +x dxf_to_ai_converter_working.py
echo "✅ Scripts made executable"

# Create directories
echo "📁 Creating directories..."
mkdir -p DXF
mkdir -p AI
echo "✅ Directories created"

# Test Illustrator access
echo "🎨 Testing Adobe Illustrator access..."
if open -a "Adobe Illustrator" 2>/dev/null; then
    echo "✅ Adobe Illustrator can be launched"
    sleep 2
    # Close Illustrator
    osascript -e 'tell application "Adobe Illustrator" to quit' 2>/dev/null
else
    echo "⚠️  Could not launch Adobe Illustrator"
    echo "   Please ensure it's installed and accessible"
fi

# Test Python script execution
echo "🐍 Testing Python script execution..."
if python3 -c "import subprocess, sys; print('Python imports working')" 2>/dev/null; then
    echo "✅ Python script execution working"
else
    echo "❌ Python script execution failed"
    exit 1
fi

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "📋 Next Steps:"
echo "1. Place DXF files in the DXF/ folder"
echo "2. Run the monitor: ./DXFya3"
echo "3. Check AI/ folder for converted files"
echo ""
echo "📖 For detailed usage instructions, see:"
echo "   - INSTALLATION_GUIDE.md"
echo "   - README.md"
echo ""
echo "🚀 Ready to process DXF files!"

