#!/bin/bash

# Function to handle shutdown
cleanup() {
    echo "Shutting down services..."
    if [ -n "$FLOWER_PID" ]; then
        kill $REDIS_PID $CELERY_PID $FLOWER_PID $API_PID 2>/dev/null
    else
        kill $REDIS_PID $CELERY_PID $API_PID 2>/dev/null
    fi
    wait
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

echo "Starting Redis server..."
redis-server --daemonize no --bind 127.0.0.1 --port 6379 &
REDIS_PID=$!

# Wait for Redis to be ready
echo "Waiting for Redis to start..."
sleep 5

# Test Redis connection
redis-cli ping
if [ $? -ne 0 ]; then
    echo "Redis failed to start"
    exit 1
fi

echo "Redis is ready!"

# Initialize database if needed
echo "Initializing database..."
cd /app
python -c "
import asyncio
import sys
sys.path.append('/app')
from app.db.init_db import init_db

async def main():
    try:
        await init_db()
        print('Database initialized successfully')
    except Exception as e:
        print(f'Database initialization: {e}')

if __name__ == '__main__':
    asyncio.run(main())
" 2>/dev/null || echo "Database initialization completed"

echo "Starting Celery worker..."
celery -A app.core.celery_app.celery_app worker --loglevel=info --concurrency=2 &
CELERY_PID=$!

echo "Starting Flower monitoring..."
if command -v flower >/dev/null 2>&1; then
    celery -A app.core.celery_app.celery_app flower --port=5555 &
    FLOWER_PID=$!
    echo "Flower started successfully"
else
    echo "Flower not available, skipping..."
    FLOWER_PID=""
fi

echo "Starting FastAPI application..."
python main.py &
API_PID=$!

echo "All services started!"
echo "FastAPI: http://localhost:8000"
echo "Flower: http://localhost:5555"
echo "Redis: localhost:6379"

# Wait for any process to exit
wait -n

# If we get here, one of the processes exited
echo "One of the services exited, shutting down..."
cleanup