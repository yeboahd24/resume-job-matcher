#!/bin/bash

# Test script to verify the build works correctly

echo "Testing single-container build..."

# Build the image
echo "Building image..."
docker build -f deployment/docker/Dockerfile.dev.simple -t resume-matcher-test:latest .

if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

echo "Build successful!"

# Test that all required packages are installed
echo "Testing package installation..."
docker run --rm resume-matcher-test:latest python -c "
import celery
import flower
import redis
import fastapi
print('✅ All required packages are installed')
print(f'Celery version: {celery.__version__}')
print(f'Redis version: {redis.__version__}')
print(f'FastAPI version: {fastapi.__version__}')
"

if [ $? -eq 0 ]; then
    echo "✅ Package test passed!"
else
    echo "❌ Package test failed!"
    exit 1
fi

# Test that flower command is available
echo "Testing Flower command..."
docker run --rm resume-matcher-test:latest which flower

if [ $? -eq 0 ]; then
    echo "✅ Flower command is available!"
else
    echo "❌ Flower command not found!"
    exit 1
fi

echo "All tests passed! 🎉"
echo ""
echo "To run the container:"
echo "docker run -p 8000:8000 -p 5555:5555 -v \$(pwd)/data:/app/data resume-matcher-test:latest"