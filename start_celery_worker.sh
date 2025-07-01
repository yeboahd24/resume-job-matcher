#!/bin/bash

# Start Celery worker with proper configuration and logging

echo "🔄 Starting Celery Worker"
echo "========================"

# Check if Redis is running
echo "🔍 Checking Redis..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running. Starting Redis..."
    redis-server --daemonize yes
    sleep 2
    
    if ! redis-cli ping > /dev/null 2>&1; then
        echo "❌ Failed to start Redis"
        exit 1
    fi
fi

echo "✅ Redis is running"

# Kill any existing Celery workers
echo "🛑 Stopping existing Celery workers..."
pkill -f "celery.*worker" 2>/dev/null || true
sleep 2

# Clear any existing tasks in queue (optional)
echo "🧹 Clearing task queue..."
redis-cli DEL celery 2>/dev/null || true

# Start Celery worker with verbose logging
echo "🚀 Starting Celery worker..."
echo "   Command: celery -A app.core.celery_app.celery_app worker --loglevel=debug --concurrency=1"
echo "   Press Ctrl+C to stop"
echo ""

# Set environment variables for better debugging
export PYTHONUNBUFFERED=1
export CELERY_TASK_ALWAYS_EAGER=False

# Start the worker
celery -A app.core.celery_app.celery_app worker \
    --loglevel=debug \
    --concurrency=1 \
    --pool=solo \
    --without-gossip \
    --without-mingle \
    --without-heartbeat