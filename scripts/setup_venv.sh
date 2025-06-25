#!/bin/bash

# Setup a Python virtual environment for Resume Job Matcher

echo "🔧 Setting up Python Virtual Environment"
echo "===================================="

# Check if python3-venv is installed
if ! dpkg -l | grep -q python3-venv; then
    echo "📦 Installing python3-venv..."
    sudo apt-get update
    sudo apt-get install -y python3-venv python3-full
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
pip install pydantic-settings

# Install spaCy model
echo "📦 Installing spaCy model..."
python -m spacy download en_core_web_sm

echo ""
echo "✅ Virtual environment setup complete!"
echo ""
echo "📋 To activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "📋 To run the application:"
echo "   ./scripts/run_in_venv.sh"
echo ""