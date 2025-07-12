#!/bin/bash

# Function to handle shutdown
cleanup() {
    echo "Shutting down services..."
    kill $CELERY_PID $API_PID 2>/dev/null
    wait
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

echo "Testing external Redis connection..."
# Test external Redis connection using Python
python -c "
import redis
import sys
try:
    r = redis.Redis.from_url('$REDIS_URL')
    result = r.ping()
    if result:
        print('✅ External Redis connection successful!')
    else:
        print('❌ Redis ping failed')
        sys.exit(1)
except Exception as e:
    print(f'❌ Redis connection error: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "External Redis connection failed"
    exit 1
fi

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

# Flower removed for simplicity
FLOWER_PID=""

echo "Starting FastAPI application..."
python main.py &
API_PID=$!

echo "All services started!"
echo "FastAPI: http://localhost:8000"
echo "External Redis: red-d1kqjmndiees73esmufg:6379"

# Wait for any process to exit
wait -n

# If we get here, one of the processes exited
echo "One of the services exited, shutting down..."
cleanup