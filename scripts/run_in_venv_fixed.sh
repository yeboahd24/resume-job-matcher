#!/bin/bash

# Run Resume Job Matcher in virtual environment

echo "Starting Resume Job Matcher in Virtual Environment"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Setting it up..."
    ./scripts/setup_venv.sh
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if Redis is running
echo "Checking if Redis is running..."
if ! podman ps | grep -q "resume-matcher-redis"; then
    echo "Redis is not running. Starting Redis..."
    podman run -d --name resume-matcher-redis -p 127.0.0.1:6379:6379 redis:7-alpine
    
    # Wait for Redis to start
    echo "Waiting for Redis to start..."
    sleep 5
    
    # Test Redis connection
    if podman exec -it resume-matcher-redis redis-cli ping | grep -q "PONG"; then
        echo "Redis is responding"
    else
        echo "Redis is not responding"
        exit 1
    fi
else
    echo "Redis is already running"
fi

# Create a temporary .env file with the correct Redis settings
echo "Creating temporary .env file with correct Redis settings..."
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
    echo "Backing up original .env file to .env.backup..."
    cp .env .env.backup
fi

# Replace the .env file
echo "Replacing .env file with fixed configuration..."
mv .env.temp .env

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data/uploads data/samples logs

# Test Celery configuration and task discovery
echo "Testing Celery configuration..."
python3 -c "
from app.services.tasks import process_resume_and_match_jobs, health_check_task
from app.core.celery_app import celery_app
print('Tasks imported successfully')
task_count = len([t for t in celery_app.tasks.keys() if 'app.services.tasks' in t])
print(f'Found {task_count} custom tasks')
if task_count == 0:
    print('ERROR: No custom tasks found!')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "Task discovery failed. Exiting..."
    exit 1
fi

# Start Celery worker in background with debug logging
echo "Starting Celery worker..."
celery -A app.core.celery_app.celery_app worker --loglevel=debug --concurrency=1 &
WORKER_PID=$!

# Wait for worker to start
echo "Waiting for worker to start..."
sleep 8

# Test if worker can process tasks
echo "Testing worker task processing..."
python3 -c "
from app.services.tasks import health_check_task
import time
try:
    result = health_check_task.delay()
    print(f'Test task submitted: {result.id}')
    # Wait a bit and check status
    time.sleep(3)
    print(f'Task status: {result.state}')
    if result.state == 'SUCCESS':
        print('SUCCESS: Worker is processing tasks correctly!')
    elif result.state == 'PENDING':
        print('WARNING: Task is still pending - worker may not be connected')
    else:
        print(f'Task state: {result.state}')
except Exception as e:
    print(f'ERROR: Task test failed: {e}')
"

# Start API server
echo "Starting API server..."
echo "The API server will run in the foreground. Press Ctrl+C to stop."
echo "To test the API, open another terminal and run: ./scripts/test_api.sh"
echo ""

python main.py

# Cleanup when the script is interrupted
function cleanup {
    echo ""
    echo "Stopping services..."
    kill $WORKER_PID 2>/dev/null || true
    echo "Services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM