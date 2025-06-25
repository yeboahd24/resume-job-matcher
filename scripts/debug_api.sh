#!/bin/bash

# Debug API container issues

echo "🔍 Debugging API Container Issues"
echo "=============================="

# Check if API container exists
if ! podman ps -a | grep -q "resume-matcher-api"; then
    echo "❌ API container doesn't exist"
else
    # Check API container status
    if podman ps | grep -q "resume-matcher-api"; then
        echo "✅ API container is running"
    else
        echo "❌ API container is not running"
        
        # Get container logs
        echo ""
        echo "📋 API Container Logs:"
        podman logs resume-matcher-api
        
        # Try to start the container
        echo ""
        echo "🔄 Attempting to start API container..."
        podman start resume-matcher-api
        
        # Check if it started
        sleep 5
        if podman ps | grep -q "resume-matcher-api"; then
            echo "✅ API container started successfully"
        else
            echo "❌ Failed to start API container"
        fi
    fi
fi

# Check if the API image exists
echo ""
echo "🔍 Checking API image..."
if podman images | grep -q "podman_api"; then
    echo "✅ API image exists"
else
    echo "❌ API image doesn't exist"
    echo "🔄 Attempting to build API image..."
    
    # Try to build the image
    podman build -t podman_api:latest -f deployment/docker/Dockerfile .
    
    if [ $? -eq 0 ]; then
        echo "✅ API image built successfully"
    else
        echo "❌ Failed to build API image"
    fi
fi

# Try running API container directly
echo ""
echo "🚀 Attempting to run API container directly..."
podman run --rm -it --name resume-matcher-api-test -p 8000:8000 \
  -e REDIS_URL=redis://host.containers.internal:6379/0 \
  -e CELERY_BROKER_URL=redis://host.containers.internal:6379/0 \
  -e CELERY_RESULT_BACKEND=redis://host.containers.internal:6379/0 \
  -e DEBUG=true \
  -e ENVIRONMENT=development \
  -e USE_MOCK_JOBS=true \
  -e LOG_LEVEL=DEBUG \
  -e PYTHONUNBUFFERED=1 \
  --add-host=host.containers.internal:host-gateway \
  localhost/podman_api:latest python -c "
import sys
print('Python version:', sys.version)
print('Checking imports...')
try:
    from app.core.config import settings
    print('Config settings imported successfully')
    print('Redis URL:', settings.REDIS_URL)
    print('Broker URL:', settings.CELERY_BROKER_URL)
    
    import redis
    r = redis.Redis.from_url(settings.REDIS_URL)
    print('Redis connection test:', r.ping())
    
    from app.core.celery_app import celery_app
    print('Celery app imported successfully')
    
    print('All imports successful!')
except Exception as e:
    print('Error:', str(e))
"