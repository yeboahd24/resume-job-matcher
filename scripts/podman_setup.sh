#!/bin/bash

# Podman setup script for Resume Job Matcher

echo "🐳 Setting up Resume Job Matcher with Podman"
echo "============================================="

# Check if podman is installed
if ! command -v podman &> /dev/null; then
    echo "❌ Podman is not installed. Please install Podman first."
    echo "   Visit: https://podman.io/getting-started/installation"
    exit 1
fi

echo "✅ Podman found: $(podman --version)"

# Check if podman-compose is available
if command -v podman-compose &> /dev/null; then
    COMPOSE_CMD="podman-compose"
    echo "✅ Using podman-compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    echo "✅ Using docker-compose with Podman"
else
    echo "❌ Neither podman-compose nor docker-compose found."
    echo "   Please install one of them:"
    echo "   - pip install podman-compose"
    echo "   - or install docker-compose"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    
    # Enable real scraping for production
    sed -i 's/USE_MOCK_JOBS=true/USE_MOCK_JOBS=false/' .env
    echo "✅ .env file created with real scraping enabled"
else
    echo "📁 .env file already exists"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/uploads data/samples logs
echo "✅ Directories created"

# Set up Podman-specific configurations
echo "🔧 Setting up Podman configurations..."

# Enable Podman socket if not already enabled (for docker-compose compatibility)
if ! systemctl --user is-active --quiet podman.socket; then
    echo "🔌 Enabling Podman socket for docker-compose compatibility..."
    systemctl --user enable --now podman.socket
    echo "✅ Podman socket enabled"
fi

# Set DOCKER_HOST for docker-compose compatibility
export DOCKER_HOST="unix:///run/user/$UID/podman/podman.sock"
echo "🔗 DOCKER_HOST set to: $DOCKER_HOST"

# Add to shell profile for persistence
if ! grep -q "DOCKER_HOST.*podman" ~/.bashrc 2>/dev/null; then
    echo "export DOCKER_HOST=unix:///run/user/\$UID/podman/podman.sock" >> ~/.bashrc
    echo "✅ Added DOCKER_HOST to ~/.bashrc"
fi

echo ""
echo "🚀 Podman setup complete!"
echo ""
echo "📋 Available commands:"
echo "   Start services:     ./scripts/podman_start.sh"
echo "   Stop services:      ./scripts/podman_stop.sh"
echo "   View logs:          ./scripts/podman_logs.sh"
echo "   Clean up:           ./scripts/podman_cleanup.sh"
echo ""
echo "🔧 Manual commands:"
echo "   Build and start:    $COMPOSE_CMD -f deployment/podman/podman-compose.yml up --build"
echo "   Start in background: $COMPOSE_CMD -f deployment/podman/podman-compose.yml up -d"
echo "   Stop services:      $COMPOSE_CMD -f deployment/podman/podman-compose.yml down"
echo ""
echo "📖 For more details, see: deployment/podman/README.md"