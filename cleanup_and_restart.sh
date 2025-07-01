#!/bin/bash

# Clean up all Celery workers and restart properly

echo "🧹 Cleaning up Celery workers and restarting"
echo "============================================"

# Kill all existing Celery workers
echo "🛑 Stopping all Celery workers..."
pkill -f "celery.*worker" 2>/dev/null || true
sleep 3

# Double check - force kill if needed
echo "🔍 Checking for remaining Celery processes..."
remaining=$(ps aux | grep -c "celery.*worker" | grep -v grep || echo "0")
if [ "$remaining" -gt 0 ]; then
    echo "   Found $remaining remaining processes, force killing..."
    pkill -9 -f "celery.*worker" 2>/dev/null || true
    sleep 2
fi

# Check Redis
echo "🔍 Checking Redis..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "🚀 Starting Redis..."
    redis-server --daemonize yes
    sleep 2
fi

if redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis is running"
else
    echo "❌ Redis failed to start"
    exit 1
fi

# Clear Redis queues
echo "🧹 Clearing Redis queues..."
redis-cli FLUSHDB

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies to make sure they're available
echo "📦 Installing/updating dependencies..."
pip install -r requirements.txt

# Test imports
echo "🧪 Testing imports..."
python3 -c "
try:
    from app.core.celery_app import celery_app
    from app.services.tasks import process_resume_and_match_jobs
    print('✅ Imports successful')
except Exception as e:
    print(f'❌ Import failed: {e}')
    exit(1)
"

# Start single Celery worker
echo "🚀 Starting single Celery worker..."
echo "   This will run in the foreground. Press Ctrl+C to stop."
echo ""

# Start with detailed logging
celery -A app.core.celery_app.celery_app worker \
    --loglevel=info \
    --concurrency=1 \
    --pool=solo \
    --without-gossip \
    --without-mingle