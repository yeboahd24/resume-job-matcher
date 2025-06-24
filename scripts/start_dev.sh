#!/bin/bash

# Development startup script for Resume Job Matcher

set -e

echo "🚀 Starting Resume Job Matcher in Development Mode"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Download spacy model
echo "🧠 Downloading spacy model..."
python -m spacy download en_core_web_sm

# Check if Redis is running
echo "🔍 Checking Redis connection..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running. Please start Redis server:"
    echo "   macOS: brew services start redis"
    echo "   Ubuntu: sudo systemctl start redis-server"
    echo "   Docker: docker run -d -p 6379:6379 redis:alpine"
    exit 1
fi

echo "✅ Redis is running"

# Start Celery worker in background
echo "🔄 Starting Celery worker..."
celery -A app.core.celery_app.celery_app worker --loglevel=info --detach

# Start FastAPI server
echo "🌐 Starting FastAPI server..."
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "🔍 Health check: http://localhost:8000/api/v1/health/"
echo ""
echo "Press Ctrl+C to stop the server"

python main.py