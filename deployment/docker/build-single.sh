#!/bin/bash

# Build script for single-container deployment

echo "Building single-container Docker image..."

# Choose which Dockerfile to use
DOCKERFILE=${1:-"Dockerfile.dev.simple"}

echo "Using Dockerfile: $DOCKERFILE"

# Build the image
docker build -f deployment/docker/$DOCKERFILE -t resume-matcher-single:latest .

if [ $? -eq 0 ]; then
    echo "Build successful!"
    echo ""
    echo "To run the container:"
    echo "docker run -p 8000:8000 -p 5555:5555 -v \$(pwd)/data:/app/data resume-matcher-single:latest"
    echo ""
    echo "Services will be available at:"
    echo "- FastAPI: http://localhost:8000"
    echo "- Flower: http://localhost:5555"
else
    echo "Build failed!"
    exit 1
fi