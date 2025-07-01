#!/bin/bash

# Development startup script for Resume Job Matcher

set -e

echo "🚀 Starting Resume Job Matcher in Development Mode"
echo "=================================================="

# Function to cleanup background processes
cleanup() {
  echo ""
  echo "🛑 Shutting down services..."
  if [ ! -z "$CELERY_PID" ]; then
    echo "   Stopping Celery worker (PID: $CELERY_PID)..."
    kill $CELERY_PID 2>/dev/null || true
  fi
  if [ ! -z "$REDIS_PID" ]; then
    echo "   Stopping Redis server (PID: $REDIS_PID)..."
    kill $REDIS_PID 2>/dev/null || true
  fi
  echo "✅ Cleanup completed"
  exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check Python version
echo "🐍 Checking Python version..."
if ! command -v python3 &>/dev/null; then
  echo "❌ Python 3 is not installed. Please install Python 3.8+"
  exit 1
fi

python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
  echo "❌ Python 3.8+ is required. Current version: $python_version"
  exit 1
fi

echo "✅ Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download spacy model
# echo "🧠 Downloading spacy model..."
# python -m spacy download en_core_web_sm

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/uploads data/samples logs

# Check if .env file exists
if [ ! -f ".env" ]; then
  echo "📝 Creating .env file from example..."
  cp .env.example .env
  echo "⚠️  Please update .env file with your configuration if needed"
fi

# Check if Redis is installed
if ! command -v redis-server &>/dev/null; then
  echo "❌ Redis is not installed. Installing Redis..."

  # Try to install Redis based on the OS
  if command -v apt-get &>/dev/null; then
    echo "   Installing Redis on Ubuntu/Debian..."
    sudo apt-get update && sudo apt-get install -y redis-server
  elif command -v dnf &>/dev/null; then
    echo "   Installing Redis on Fedora/RHEL..."
    sudo dnf install -y redis
  elif command -v brew &>/dev/null; then
    echo "   Installing Redis on macOS..."
    brew install redis
  else
    echo "❌ Cannot auto-install Redis. Please install Redis manually:"
    echo "   Ubuntu/Debian: sudo apt-get install redis-server"
    echo "   Fedora/RHEL: sudo dnf install redis"
    echo "   macOS: brew install redis"
    echo "   Or use Docker: docker run -d -p 6379:6379 redis:alpine"
    exit 1
  fi
fi

# Check if Redis is running
echo "🔍 Checking Redis connection..."
if ! redis-cli ping >/dev/null 2>&1; then
  echo "🚀 Starting Redis server..."

  # Try to start Redis as a daemon
  if redis-server --daemonize yes; then
    echo "✅ Redis started successfully"
    REDIS_PID=$(pgrep redis-server)
    echo "   Redis PID: $REDIS_PID"
  else
    echo "❌ Failed to start Redis. Please start Redis manually:"
    echo "   macOS: brew services start redis"
    echo "   Ubuntu: sudo systemctl start redis-server"
    echo "   Docker: docker run -d -p 6379:6379 redis:alpine"
    exit 1
  fi

  # Wait for Redis to start
  echo "⏳ Waiting for Redis to start..."
  sleep 3
fi

# Test Redis connection
echo "🧪 Testing Redis connection..."
if redis-cli ping | grep -q "PONG"; then
  echo "✅ Redis is responding"
else
  echo "❌ Redis is not responding"
  exit 1
fi

# Start Celery worker in background
echo "🔄 Starting Celery worker..."
celery -A app.core.celery_app.celery_app worker --loglevel=info --concurrency=1 &
CELERY_PID=$!

if [ ! -z "$CELERY_PID" ]; then
  echo "✅ Celery worker started (PID: $CELERY_PID)"
else
  echo "❌ Failed to start Celery worker"
  exit 1
fi

# Wait for Celery to start
echo "⏳ Waiting for Celery worker to start..."
sleep 5

# Verify Celery is running
if ps -p $CELERY_PID >/dev/null; then
  echo "✅ Celery worker is running"
else
  echo "❌ Celery worker failed to start"
  exit 1
fi

# Start FastAPI server
echo ""
echo "🌐 Starting FastAPI server..."
echo "=================================================="
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🔍 Health check: http://localhost:8000/api/v1/health"
echo "🧪 Test upload: open test_upload.html in your browser"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Start the FastAPI server (this will run in foreground)
python main.py
