#!/bin/bash

# Quick fix script for Celery issues

echo "🔧 Quick Fix for Celery Issues"
echo "=============================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
if ! command_exists python3; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✅ Python 3 is available"

# Check pip
if ! command_exists pip3; then
    echo "❌ pip3 is not installed"
    exit 1
fi

echo "✅ pip3 is available"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Check if Redis is installed
if ! command_exists redis-server; then
    echo "❌ Redis is not installed. Installing..."
    
    if command_exists apt-get; then
        sudo apt-get update && sudo apt-get install -y redis-server
    elif command_exists dnf; then
        sudo dnf install -y redis
    elif command_exists brew; then
        brew install redis
    else
        echo "❌ Cannot install Redis automatically. Please install manually."
        exit 1
    fi
fi

echo "✅ Redis is available"

# Stop any existing Redis processes
echo "🛑 Stopping existing Redis processes..."
sudo pkill -f redis-server 2>/dev/null || true

# Start Redis
echo "🚀 Starting Redis..."
redis-server --daemonize yes

# Wait for Redis to start
sleep 2

# Test Redis
if redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis is running"
else
    echo "❌ Redis failed to start"
    exit 1
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
fi

# Test imports
echo "🧪 Testing Python imports..."
python3 -c "
try:
    from app.core.celery_app import celery_app
    from app.services.tasks import process_resume_and_match_jobs
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import failed: {e}')
    exit(1)
"

# Start Celery worker in background
echo "🔄 Starting Celery worker..."
celery -A app.core.celery_app.celery_app worker --loglevel=info --concurrency=1 --detach

# Wait for worker to start
sleep 5

# Test Celery worker
echo "🧪 Testing Celery worker..."
python3 -c "
from app.core.celery_app import celery_app
from app.services.tasks import health_check_task

try:
    result = health_check_task.delay()
    print(f'✅ Task created: {result.id}')
    task_result = result.get(timeout=10)
    print(f'✅ Task completed: {task_result}')
except Exception as e:
    print(f'❌ Task failed: {e}')
    exit(1)
"

echo ""
echo "🎉 Celery setup completed successfully!"
echo ""
echo "Now you can:"
echo "1. Start the FastAPI server: python3 main.py"
echo "2. Test the API: python3 debug_upload.py"
echo "3. Use the web interface: open test_upload.html"
echo ""
echo "To stop services:"
echo "- Stop FastAPI: Ctrl+C"
echo "- Stop Celery: pkill -f celery"
echo "- Stop Redis: redis-cli shutdown"