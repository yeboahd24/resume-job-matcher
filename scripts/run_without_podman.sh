#!/bin/bash

# Run Resume Job Matcher without Podman
# This script runs the application directly on the host

echo "🚀 Running Resume Job Matcher without Podman"
echo "=========================================="

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis is not installed. Please install Redis first."
    echo "   Ubuntu/Debian: sudo apt-get install redis-server"
    echo "   Fedora/RHEL: sudo dnf install redis"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Stop all Podman containers
echo "🛑 Stopping all Podman containers..."
podman stop $(podman ps -q --filter "name=resume-matcher") 2>/dev/null || true
podman rm $(podman ps -aq --filter "name=resume-matcher") 2>/dev/null || true

# Stop Redis if it's running
echo "🛑 Stopping Redis if it's running..."
sudo systemctl stop redis-server 2>/dev/null || true
sudo systemctl stop redis 2>/dev/null || true
sudo pkill -f redis-server 2>/dev/null || true

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

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt
pip3 install pydantic-settings

# Install spaCy model
echo "📦 Installing spaCy model..."
python3 -m spacy download en_core_web_sm

# Start Redis
echo "🚀 Starting Redis..."
redis-server --daemonize yes

# Wait for Redis to start
echo "⏳ Waiting for Redis to start..."
sleep 2

# Test Redis connection
echo "🧪 Testing Redis connection..."
if redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis is responding"
else
    echo "❌ Redis is not responding"
    exit 1
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
    redis-cli shutdown 2>/dev/null || true
    echo "✅ Services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM