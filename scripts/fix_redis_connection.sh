#!/bin/bash

# Script to fix Redis connection issues in Resume Job Matcher

echo "🔧 Fixing Redis Connection Issues"
echo "================================="

# Stop all containers
echo "🛑 Stopping all containers..."
podman stop $(podman ps -q --filter "name=resume-matcher") 2>/dev/null || true
podman rm $(podman ps -aq --filter "name=resume-matcher") 2>/dev/null || true

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

# Create the network if it doesn't exist
echo "🔄 Creating network..."
podman network create resume-matcher-network 2>/dev/null || true

# Start services with the fixed compose file
echo "🚀 Starting services with fixed configuration..."
$COMPOSE_CMD -f deployment/podman/fixed-compose.yml up -d --build

# Check if services are running
echo "🔍 Checking if services are running..."
sleep 5

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
echo "✅ Fix applied! Try testing the API now:"
echo "   ./scripts/test_api.sh"