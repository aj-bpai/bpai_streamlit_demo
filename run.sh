#!/bin/bash

# Video Processing Pipeline Demo - Quick Start Script

echo "🎥 Video Processing Pipeline Demo"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✓ Dependencies installed"

# Run Streamlit app
echo ""
echo "🚀 Starting Streamlit app..."
echo "   The app will open in your default browser."
echo "   Press Ctrl+C to stop the server."
echo ""
streamlit run app.py

