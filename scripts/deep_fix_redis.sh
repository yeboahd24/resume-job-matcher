#!/bin/bash

# Deep fix for Redis connection issues in Resume Job Matcher

echo "🔧 Deep Fix for Redis Connection Issues"
echo "======================================"

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
REDIS_HOST=resume-matcher-redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_URL=redis://resume-matcher-redis:6379/0

# Celery Settings - FIXED CONFIGURATION
CELERY_BROKER_URL=redis://resume-matcher-redis:6379/0
CELERY_RESULT_BACKEND=redis://resume-matcher-redis:6379/0
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

# Create a custom docker-compose file with host networking
echo "📝 Creating custom docker-compose file with host networking..."
cat > deployment/podman/host-network-compose.yml << EOL
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: resume-matcher-redis
    network_mode: "host"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --bind 127.0.0.1
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    # Podman-specific: ensure proper user mapping
    userns_mode: "keep-id"

  api:
    build:
      context: ../..
      dockerfile: deployment/docker/Dockerfile
    container_name: resume-matcher-api
    network_mode: "host"
    environment:
      - REDIS_URL=redis://127.0.0.1:6379/0
      - CELERY_BROKER_URL=redis://127.0.0.1:6379/0
      - CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
      - DEBUG=true
      - ENVIRONMENT=development
      - USE_MOCK_JOBS=true
      - LOG_LEVEL=DEBUG
      # Podman-specific environment variables
      - PYTHONUNBUFFERED=1
    volumes:
      - app_data:/app/data
      - app_logs:/app/logs
    depends_on:
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    # Podman-specific: ensure proper user mapping
    userns_mode: "keep-id"
    command: sh -c "sleep 5 && python main.py"

  worker:
    build:
      context: ../..
      dockerfile: deployment/docker/Dockerfile
    container_name: resume-matcher-worker
    network_mode: "host"
    command: sh -c "sleep 10 && celery -A app.core.celery_app.celery_app worker --loglevel=debug --concurrency=1"
    environment:
      - REDIS_URL=redis://127.0.0.1:6379/0
      - CELERY_BROKER_URL=redis://127.0.0.1:6379/0
      - CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
      - DEBUG=true
      - ENVIRONMENT=development
      - USE_MOCK_JOBS=true
      - LOG_LEVEL=DEBUG
      # Podman-specific environment variables
      - PYTHONUNBUFFERED=1
    volumes:
      - app_data:/app/data
      - app_logs:/app/logs
    depends_on:
      - redis
      - api
    # Podman-specific: ensure proper user mapping
    userns_mode: "keep-id"

volumes:
  redis_data:
  app_data:
  app_logs:
EOL

# Set DOCKER_HOST for docker-compose compatibility
export DOCKER_HOST="unix:///run/user/$UID/podman/podman.sock"

# Determine which compose command to use
if command -v podman-compose &> /dev/null; then
    COMPOSE_CMD="podman-compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "❌ Neither podman-compose nor docker-compose found."
    echo "   Please install one of them:"
    echo "   - pip install podman-compose"
    echo "   - or install docker-compose"
    exit 1
fi

# Start services with the host networking compose file
echo "🚀 Starting services with host networking..."
$COMPOSE_CMD -f deployment/podman/host-network-compose.yml up -d --build

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 15

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

# Test Redis connection
echo ""
echo "🧪 Testing Redis connection..."
if podman exec -it resume-matcher-redis redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis is responding"
else
    echo "❌ Redis is not responding"
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
echo "✅ Deep fix applied! Try testing the API now:"
echo "   ./scripts/test_api.sh"
echo ""
echo "📊 To monitor logs:"
echo "   podman logs -f resume-matcher-worker"