#!/bin/bash

# Comprehensive script to fix Podman issues for Resume Job Matcher

echo "🔧 Resume Job Matcher - Podman Issue Fixer"
echo "=========================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if podman is installed
if ! command_exists podman; then
    echo "❌ Podman is not installed. Please install Podman first."
    echo "   Visit: https://podman.io/getting-started/installation"
    exit 1
fi

echo "✅ Podman found: $(podman --version)"

# Step 1: Stop all existing containers
echo ""
echo "🛑 Stopping all existing Resume Job Matcher containers..."
podman stop $(podman ps -q --filter "name=resume-matcher") 2>/dev/null || true
podman rm $(podman ps -aq --filter "name=resume-matcher") 2>/dev/null || true
echo "✅ Existing containers stopped and removed"

# Step 2: Check for port conflicts
echo ""
echo "🔍 Checking for port conflicts..."
./scripts/fix_port_conflicts.sh
if [ $? -ne 0 ]; then
    echo "⚠️  Port conflicts detected. Please resolve them manually."
    exit 1
fi

# Step 3: Fix pydantic-settings dependency
echo ""
echo "📦 Ensuring pydantic-settings is installed..."
if ! grep -q "pydantic-settings" requirements.txt; then
    echo "pydantic-settings==2.1.0  # Required for BaseSettings" >> requirements.txt
    echo "✅ Added pydantic-settings to requirements.txt"
else
    echo "✅ pydantic-settings already in requirements.txt"
fi

# Step 4: Update config.py to use pydantic-settings
echo ""
echo "🔧 Updating config.py to use pydantic-settings..."
if ! grep -q "from pydantic_settings import BaseSettings" app/core/config.py; then
    sed -i 's/from pydantic import BaseSettings, validator/try:\n    from pydantic_settings import BaseSettings\n    from pydantic import validator\nexcept ImportError:\n    # Fallback for older pydantic versions\n    from pydantic import BaseSettings, validator/' app/core/config.py
    echo "✅ Updated app/core/config.py to use pydantic-settings"
else
    echo "✅ app/core/config.py already updated"
fi

# Step 5: Update Containerfile and Dockerfile
echo ""
echo "🐳 Updating container build files..."
for file in deployment/podman/Containerfile deployment/docker/Dockerfile; do
    if [ -f "$file" ]; then
        if ! grep -q "pip install --no-cache-dir --user pydantic-settings" "$file"; then
            sed -i '/pip install --no-cache-dir --user -r requirements.txt/a RUN pip install --no-cache-dir --user pydantic-settings' "$file"
            echo "✅ Updated $file to install pydantic-settings"
        else
            echo "✅ $file already updated"
        fi
    fi
done

# Step 6: Update podman-compose.yml to avoid port conflicts
echo ""
echo "📄 Updating podman-compose.yml to avoid port conflicts..."
if grep -q '"6379:6379"' deployment/podman/podman-compose.yml; then
    sed -i 's/"6379:6379"/"127.0.0.1:6379:6379"  # Bind to localhost only for security/' deployment/podman/podman-compose.yml
    echo "✅ Updated Redis port binding in podman-compose.yml"
else
    echo "✅ Redis port binding already updated"
fi

# Step 7: Clean up Podman resources
echo ""
echo "🧹 Cleaning up Podman resources..."
podman system prune -f >/dev/null 2>&1
echo "✅ Podman resources cleaned up"

# Step 8: Rebuild images
echo ""
echo "🏗️  Rebuilding container images..."
if command_exists podman-compose; then
    COMPOSE_CMD="podman-compose"
elif command_exists docker-compose; then
    COMPOSE_CMD="docker-compose"
    # Set DOCKER_HOST for docker-compose compatibility
    export DOCKER_HOST="unix:///run/user/$UID/podman/podman.sock"
else
    echo "❌ Neither podman-compose nor docker-compose found."
    echo "   Please install one of them:"
    echo "   - pip install podman-compose"
    echo "   - or install docker-compose"
    exit 1
fi

$COMPOSE_CMD -f deployment/podman/podman-compose.yml build

# Step 9: Final instructions
echo ""
echo "✅ All issues fixed!"
echo ""
echo "🚀 Next steps:"
echo "1. Start the application: ./scripts/podman_start.sh --build"
echo "2. Test the API: curl http://localhost:8000/api/v1/health/"
echo ""
echo "📋 If you still encounter issues:"
echo "   - Check logs: ./scripts/podman_logs.sh"
echo "   - Verify ports: netstat -tulpn | grep -E ':(6379|8000|5555)'"
echo "   - Restart your system and try again"