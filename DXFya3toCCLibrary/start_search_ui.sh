#!/bin/bash
# Start the Creative Cloud Library Search Web Interface

cd "$(dirname "$0")"

echo "🎨 Creative Cloud Library Search"
echo "=================================="
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Setting up Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing Flask..."
    pip install flask
    echo ""
else
    source venv/bin/activate
fi

# Check if database exists
if [ ! -f "cc_libraries_enhanced.db" ]; then
    echo "⚠️  Enhanced database not found!"
    echo "Building database now..."
    python3 build_library_index_enhanced.py
    echo ""
fi

echo "🚀 Starting web server..."
echo "   Open your browser to: http://localhost:5001"
echo ""
echo "   Press Ctrl+C to stop"
echo "=================================="
echo ""

python3 library_search_server.py

