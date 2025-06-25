#!/bin/bash

# Run API directly on the host (without Podman)

echo "🚀 Running API Directly on Host"
echo "============================"

# Check if Redis is running
echo "🔍 Checking if Redis is running..."
if ! podman ps | grep -q "resume-matcher-redis"; then
    echo "❌ Redis is not running. Starting Redis..."
    podman run -d --name resume-matcher-redis -p 127.0.0.1:6379:6379 redis:7-alpine
    
    # Wait for Redis to start
    echo "⏳ Waiting for Redis to start..."
    sleep 5
    
    # Test Redis connection
    if podman exec -it resume-matcher-redis redis-cli ping | grep -q "PONG"; then
        echo "✅ Redis is responding"
    else
        echo "❌ Redis is not responding"
        exit 1
    fi
else
    echo "✅ Redis is already running"
fi

# Create a temporary .env file with the correct Redis settings
echo "📝 Creating temporary .env file with correct Redis settings..."
cat > .env.temp << EOL
# Environment Configuration
PROJECT_NAME="Resume Job Matcher API"
VERSION="1.0.0"
DEBUG=true
ENVIRONMENT=development

# Server Settings
HOST=0.0.0.0
PORT=8000
WORKERS=1

# Redis Settings - FIXED CONFIGURATION
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_URL=redis://localhost:6379/0

# Celery Settings - FIXED CONFIGURATION
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_TASK_TIME_LIMIT=1800
CELERY_TASK_SOFT_TIME_LIMIT=1500

# File Upload Settings
MAX_FILE_SIZE_MB=10
UPLOAD_DIR=data/uploads

# ML/NLP Settings
SPACY_MODEL=en_core_web_sm
SIMILARITY_THRESHOLD=0.1
MAX_SKILLS_EXTRACT=20
MAX_JOB_TITLES_EXTRACT=10
MAX_JOBS_PER_SKILL=2
MAX_MATCHED_JOBS=5

# Job Scraping Settings
JOB_SCRAPING_ENABLED=true
JOB_SCRAPING_TIMEOUT=30
USE_MOCK_JOBS=true

# Rate limiting for web scraping
SCRAPING_MIN_DELAY=1.0
SCRAPING_MAX_DELAY=3.0
SCRAPING_MAX_RETRIES=3

# Free job board settings
ENABLE_REMOTEOK=true
ENABLE_WEWORKREMOTELY=true
ENABLE_ENHANCED_FALLBACK=true

# Logging Settings
LOG_LEVEL=DEBUG
EOL

# Backup the original .env file if it exists
if [ -f ".env" ]; then
    echo "📦 Backing up original .env file to .env.backup..."
    cp .env .env.backup
fi

# Replace the .env file
echo "🔄 Replacing .env file with fixed configuration..."
mv .env.temp .env

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/uploads data/samples logs

# Check if pydantic-settings is installed
echo "🔍 Checking if pydantic-settings is installed..."
if ! pip3 list | grep -q "pydantic-settings"; then
    echo "📦 Installing pydantic-settings..."
    pip3 install pydantic-settings
else
    echo "✅ pydantic-settings is already installed"
fi

# Check if spaCy model is installed
echo "🔍 Checking if spaCy model is installed..."
if ! python3 -c "import spacy; spacy.load('en_core_web_sm')" &> /dev/null; then
    echo "📦 Installing spaCy model..."
    python3 -m spacy download en_core_web_sm
else
    echo "✅ spaCy model is already installed"
fi

# Start Celery worker in background
echo "🚀 Starting Celery worker..."
celery -A app.core.celery_app.celery_app worker --loglevel=info --concurrency=1 &
WORKER_PID=$!

# Wait for worker to start
echo "⏳ Waiting for worker to start..."
sleep 5

# Start API server
echo "🚀 Starting API server..."
echo "📋 The API server will run in the foreground. Press Ctrl+C to stop."
echo "📊 To test the API, open another terminal and run: ./scripts/test_api.sh"
echo ""

python3 main.py

# Cleanup when the script is interrupted
function cleanup {
    echo ""
    echo "🛑 Stopping services..."
    kill $WORKER_PID 2>/dev/null || true
    echo "✅ Services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM