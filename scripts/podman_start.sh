#!/bin/bash

# Start Resume Job Matcher with Podman

echo "🚀 Starting Resume Job Matcher with Podman"
echo "=========================================="

# Set DOCKER_HOST for docker-compose compatibility
export DOCKER_HOST="unix:///run/user/$UID/podman/podman.sock"

# Determine which compose command to use
if command -v podman-compose &> /dev/null; then
    COMPOSE_CMD="podman-compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "❌ Neither podman-compose nor docker-compose found."
    echo "   Please run: ./scripts/podman_setup.sh first"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 .env file not found. Creating from .env.example..."
    cp .env.example .env
    sed -i 's/USE_MOCK_JOBS=true/USE_MOCK_JOBS=false/' .env
fi

# Parse command line arguments
BUILD_FLAG=""
DETACH_FLAG=""
MONITORING=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            BUILD_FLAG="--build"
            shift
            ;;
        --detach|-d)
            DETACH_FLAG="-d"
            shift
            ;;
        --monitoring)
            MONITORING="--profile monitoring"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --build        Force rebuild of containers"
            echo "  --detach, -d   Run in background (detached mode)"
            echo "  --monitoring   Include monitoring services (Flower)"
            echo "  --help, -h     Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "🔧 Using compose command: $COMPOSE_CMD"
echo "📁 Using compose file: deployment/podman/podman-compose.yml"

# Start services
echo "🐳 Starting containers..."
$COMPOSE_CMD -f deployment/podman/podman-compose.yml up $BUILD_FLAG $DETACH_FLAG $MONITORING

if [ "$DETACH_FLAG" = "-d" ]; then
    echo ""
    echo "✅ Services started in background!"
    echo ""
    echo "📊 Service URLs:"
    echo "   API:          http://localhost:8000"
    echo "   API Docs:     http://localhost:8000/docs"
    echo "   Health Check: http://localhost:8000/api/v1/health/"
    
    if [ "$MONITORING" != "" ]; then
        echo "   Flower:       http://localhost:5555"
    fi
    
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs:    ./scripts/podman_logs.sh"
    echo "   Stop services: ./scripts/podman_stop.sh"
    echo "   Test API:     curl http://localhost:8000/api/v1/health/"
fi