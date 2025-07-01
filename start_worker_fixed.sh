#!/bin/bash

# Start Celery worker with correct queue configuration

echo "🔧 Starting Celery Worker with Fixed Queue Configuration"
echo "======================================================="

# Kill any existing workers
echo "🛑 Stopping existing workers..."
pkill -f "celery.*worker" 2>/dev/null || true
sleep 2

# Clear Redis to start fresh
echo "🧹 Clearing Redis queues..."
redis-cli FLUSHALL

# Activate virtual environment
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Test configuration
echo "🧪 Testing Celery configuration..."
python3 -c "
from app.core.celery_app import celery_app
print(f'✅ Default queue: {celery_app.conf.task_default_queue}')
print(f'✅ Task routes: {celery_app.conf.task_routes}')
print(f'✅ Broker URL: {celery_app.conf.broker_url}')
"

echo ""
echo "🚀 Starting Celery worker listening to 'default' queue..."
echo "   Watch for 'celery@hostname ready.' message"
echo "   Press Ctrl+C to stop"
echo ""

# Start worker with explicit queue specification
PYTHONUNBUFFERED=1 celery -A app.core.celery_app.celery_app worker \
    --loglevel=info \
    --concurrency=1 \
    --queues=default \
    --pool=solo \
    --without-gossip \
    --without-mingle