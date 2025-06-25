#!/bin/bash

# Simple Redis connection fix for Resume Job Matcher

echo "🔧 Simple Redis Connection Fix"
echo "============================"

# Stop all containers
echo "🛑 Stopping all containers..."
podman stop $(podman ps -q --filter "name=resume-matcher") 2>/dev/null || true
podman rm $(podman ps -aq --filter "name=resume-matcher") 2>/dev/null || true

# Check if Redis is running on the host
echo "🔍 Checking if Redis is running on the host..."
if pgrep -x "redis-server" > /dev/null; then
    echo "⚠️  Redis server is running on the host. Stopping it..."
    sudo systemctl stop redis-server 2>/dev/null || true
    sudo systemctl stop redis 2>/dev/null || true
    sudo pkill -f redis-server 2>/dev/null || true
    
    echo "⏳ Waiting for Redis to stop..."
    sleep 2
fi

# Check if port 6379 is still in use
if netstat -tuln 2>/dev/null | grep -q ":6379 "; then
    echo "⚠️  Port 6379 is still in use. Attempting to kill process..."
    sudo fuser -k 6379/tcp 2>/dev/null || true
    sleep 2
fi

# Start Redis standalone
echo "🚀 Starting Redis standalone..."
podman run -d --name resume-matcher-redis -p 127.0.0.1:6379:6379 redis:7-alpine

# Wait for Redis to start
echo "⏳ Waiting for Redis to start..."
sleep 5

# Test Redis connection
echo "🧪 Testing Redis connection..."
if podman exec -it resume-matcher-redis redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis is responding"
else
    echo "❌ Redis is not responding"
    exit 1
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

# Start API container
echo "🚀 Starting API container..."
podman run -d --name resume-matcher-api -p 8000:8000 \
  -e REDIS_URL=redis://host.containers.internal:6379/0 \
  -e CELERY_BROKER_URL=redis://host.containers.internal:6379/0 \
  -e CELERY_RESULT_BACKEND=redis://host.containers.internal:6379/0 \
  -e DEBUG=true \
  -e ENVIRONMENT=development \
  -e USE_MOCK_JOBS=true \
  -e LOG_LEVEL=DEBUG \
  -e PYTHONUNBUFFERED=1 \
  -v podman_app_data:/app/data \
  -v podman_app_logs:/app/logs \
  --add-host=host.containers.internal:host-gateway \
  localhost/podman_api:latest

# Wait for API to start
echo "⏳ Waiting for API to start..."
sleep 10

# Start worker container
echo "🚀 Starting worker container..."
podman run -d --name resume-matcher-worker \
  -e REDIS_URL=redis://host.containers.internal:6379/0 \
  -e CELERY_BROKER_URL=redis://host.containers.internal:6379/0 \
  -e CELERY_RESULT_BACKEND=redis://host.containers.internal:6379/0 \
  -e DEBUG=true \
  -e ENVIRONMENT=development \
  -e USE_MOCK_JOBS=true \
  -e LOG_LEVEL=DEBUG \
  -e PYTHONUNBUFFERED=1 \
  -v podman_app_data:/app/data \
  -v podman_app_logs:/app/logs \
  --add-host=host.containers.internal:host-gateway \
  localhost/podman_worker:latest \
  celery -A app.core.celery_app.celery_app worker --loglevel=debug --concurrency=1

# Check if services are running
echo "🔍 Checking if services are running..."

if podman ps | grep -q "resume-matcher-redis"; then
    echo "✅ Redis is running"
else
    echo "❌ Redis failed to start"
fi

if podman ps | grep -q "resume-matcher-api"; then
    echo "✅ API is running"
else
    echo "❌ API failed to start"
fi

if podman ps | grep -q "resume-matcher-worker"; then
    echo "✅ Worker is running"
else
    echo "❌ Worker failed to start"
fi

# Check API health
echo ""
echo "🧪 Testing API health..."
if curl -s http://localhost:8000/api/v1/health/ | grep -q "status"; then
    echo "✅ API is healthy"
else
    echo "❌ API is not responding"
fi

echo ""
echo "📋 Container Status:"
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "resume-matcher"

echo ""
echo "✅ Simple fix applied! Try testing the API now:"
echo "   ./scripts/test_api.sh"
echo ""
echo "📊 To monitor logs:"
echo "   podman logs -f resume-matcher-worker"