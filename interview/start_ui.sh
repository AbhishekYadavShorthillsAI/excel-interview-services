#!/bin/bash

# AI Interview Service Streamlit UI Launcher
# Simple script to start the Streamlit interface

echo "🚀 AI Interview Service - Streamlit UI"
echo "======================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "interview/streamlit_app.py" ]; then
    echo "❌ Please run this script from the project root directory"
    echo "💡 Expected: /project-root/interview/streamlit_app.py"
    exit 1
fi

# Check for virtual environment
VENV_PATH="/Users/shtlpmac090/Desktop/environments/genai"
if [ -d "$VENV_PATH" ]; then
    echo "🐍 Using virtual environment: $VENV_PATH"
    source "$VENV_PATH/bin/activate"
    PYTHON_CMD="python"
else
    echo "🐍 Using system Python"
    PYTHON_CMD="python3"
fi

# Install dependencies if needed
echo "📦 Checking Streamlit installation..."
if ! $PYTHON_CMD -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing Streamlit dependencies..."
    pip install -r interview/streamlit_requirements.txt
fi

# Launch the Python startup script
echo "🎯 Starting Streamlit UI..."
$PYTHON_CMD interview/run_streamlit.py 