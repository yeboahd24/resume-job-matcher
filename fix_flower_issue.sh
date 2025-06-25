#!/bin/bash

# Quick fix for the flower container issue

echo "🔧 Fixing Resume Job Matcher Flower container issue"
echo "=================================================="

# Stop and remove the flower container
echo "🛑 Stopping and removing flower container..."
podman stop resume-matcher-flower 2>/dev/null || true
podman rm resume-matcher-flower 2>/dev/null || true

# Stop and remove the redis container
echo "🛑 Stopping and removing redis container..."
podman stop resume-matcher-redis 2>/dev/null || true
podman rm resume-matcher-redis 2>/dev/null || true

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

# Install pydantic-settings if needed
echo "📦 Installing pydantic-settings..."
pip install pydantic-settings

# Update the config file
echo "🔧 Updating config.py..."
if ! grep -q "from pydantic_settings import BaseSettings" app/core/config.py; then
    sed -i 's/from pydantic import BaseSettings, validator/try:\n    from pydantic_settings import BaseSettings\n    from pydantic import validator\nexcept ImportError:\n    # Fallback for older pydantic versions\n    from pydantic import BaseSettings, validator/' app/core/config.py
fi

# Start the services with build flag
echo "🚀 Starting services with build flag..."
./scripts/podman_start.sh --build

echo ""
echo "✅ Fix applied! If you still have issues, try:"
echo "   ./scripts/fix_podman_issues.sh"