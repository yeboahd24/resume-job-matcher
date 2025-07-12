#!/bin/bash

# Render.sh - Script to run FastAPI + Celery for Render deployment
# This script creates a virtual environment and runs both services

set -e  # Exit on any error

echo "🚀 Starting Resume Job Matcher on Render..."

# Function to handle shutdown
cleanup() {
    echo "🛑 Shutting down services..."
    if [ -n "$CELERY_PID" ]; then
        kill $CELERY_PID 2>/dev/null || true
    fi
    if [ -n "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
    fi
    wait
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Download spacy model if not already present
echo "🧠 Setting up NLP model..."
python -m spacy download en_core_web_sm || echo "Spacy model already installed"

# Set default environment variables if not set
export REDIS_URL=${REDIS_URL:-"redis://red-d1kqjmndiees73esmufg:6379"}
export CELERY_BROKER_URL=${CELERY_BROKER_URL:-"$REDIS_URL"}
export CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND:-"$REDIS_URL"}
export DEBUG=${DEBUG:-"false"}
export ENVIRONMENT=${ENVIRONMENT:-"production"}
export HOST=${HOST:-"0.0.0.0"}
export PORT=${PORT:-"8000"}

echo "🔗 Testing Redis connection..."
python -c "
import redis
import sys
try:
    r = redis.Redis.from_url('$REDIS_URL')
    result = r.ping()
    if result:
        print('✅ Redis connection successful!')
    else:
        print('❌ Redis ping failed')
        sys.exit(1)
except Exception as e:
    print(f'❌ Redis connection error: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Redis connection failed - exiting"
    exit 1
fi

# Initialize database
echo "🗄️ Initializing database..."
python -c "
import asyncio
import sys
sys.path.append('.')
from app.db.init_db import init_db

async def main():
    try:
        await init_db()
        print('✅ Database initialized successfully')
    except Exception as e:
        print(f'Database initialization: {e}')

if __name__ == '__main__':
    asyncio.run(main())
" || echo "Database initialization completed"

# Create necessary directories
mkdir -p data/uploads data/samples logs

echo "🔄 Starting Celery worker..."
celery -A app.core.celery_app.celery_app worker --loglevel=info --concurrency=2 &
CELERY_PID=$!

# Give Celery a moment to start
sleep 3

echo "🌐 Starting FastAPI application..."
python main.py &
API_PID=$!

echo "✅ All services started!"
echo "📍 FastAPI running on: http://$HOST:$PORT"
echo "🔗 Redis: $REDIS_URL"
echo "⚡ Celery worker running with PID: $CELERY_PID"

# Wait for any process to exit
wait -n

# If we get here, one of the processes exited
echo "⚠️ One of the services exited, shutting down..."
cleanup