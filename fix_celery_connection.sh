#!/bin/bash

# Fix Celery connection issues

echo "🔧 Fixing Celery Connection Issues"
echo "=================================="

# Step 1: Kill ALL Celery processes
echo "🛑 Killing all Celery processes..."
pkill -f "celery" 2>/dev/null || true
pkill -9 -f "celery" 2>/dev/null || true
sleep 3

# Verify no Celery processes remain
remaining=$(ps aux | grep -v grep | grep -c "celery" || echo "0")
if [ "$remaining" -gt 0 ]; then
    echo "⚠️  Still found $remaining Celery processes, force killing..."
    ps aux | grep -v grep | grep "celery" | awk '{print $2}' | xargs kill -9 2>/dev/null || true
    sleep 2
fi

echo "✅ All Celery processes stopped"

# Step 2: Reset Redis
echo "🧹 Resetting Redis..."
redis-cli FLUSHALL
redis-cli CONFIG SET save ""  # Disable persistence for testing

# Step 3: Check Redis connection
echo "🔍 Testing Redis connection..."
if redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis is responding"
else
    echo "❌ Redis is not responding"
    exit 1
fi

# Step 4: Verify environment
echo "🔍 Checking environment..."
if [ -d "venv" ]; then
    echo "✅ Virtual environment found"
    source venv/bin/activate
else
    echo "⚠️  No virtual environment found"
fi

# Step 5: Test imports
echo "🧪 Testing imports..."
python3 -c "
import sys
try:
    from app.core.celery_app import celery_app
    from app.services.tasks import health_check_task
    print('✅ All imports successful')
    
    # Test Celery configuration
    print(f'📊 Broker URL: {celery_app.conf.broker_url}')
    print(f'📊 Result Backend: {celery_app.conf.result_backend}')
    print(f'📊 Include: {celery_app.conf.include}')
    
except Exception as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Import test failed"
    exit 1
fi

echo ""
echo "🚀 Starting Celery worker with debug logging..."
echo "   Watch for 'celery@hostname ready.' message"
echo "   Press Ctrl+C to stop"
echo ""

# Step 6: Start worker with maximum debugging
PYTHONUNBUFFERED=1 celery -A app.core.celery_app.celery_app worker \
    --loglevel=debug \
    --concurrency=1 \
    --pool=solo \
    --without-gossip \
    --without-mingle \
    --without-heartbeat