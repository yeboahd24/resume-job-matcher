#!/bin/bash

# Setup script for Resume Job Matcher

set -e

echo "🔧 Setting up Resume Job Matcher"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Download spacy model
echo "🧠 Downloading spacy model..."
python -m spacy download en_core_web_sm

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/uploads data/samples logs

# Copy environment file
if [ ! -f ".env" ]; then
    echo "📝 Creating environment file..."
    cp .env.example .env
    echo "⚠️ Please update .env file with your configuration"
fi

# Run setup verification
echo "🧪 Running setup verification..."
python tests/test_setup.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your configuration"
echo "2. Start Redis server"
echo "3. Run: ./scripts/start_dev.sh"
echo ""
echo "For production deployment:"
echo "- Docker: docker-compose -f deployment/docker/docker-compose.yml up"
echo "- Kubernetes: kubectl apply -f deployment/kubernetes/"