#!/bin/bash

# Stop Resume Job Matcher Podman services

echo "🛑 Stopping Resume Job Matcher services"
echo "======================================="

# Set DOCKER_HOST for docker-compose compatibility
export DOCKER_HOST="unix:///run/user/$UID/podman/podman.sock"

# Determine which compose command to use
if command -v podman-compose &> /dev/null; then
    COMPOSE_CMD="podman-compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "❌ Neither podman-compose nor docker-compose found."
    exit 1
fi

# Parse command line arguments
REMOVE_VOLUMES=""
REMOVE_IMAGES=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --volumes|-v)
            REMOVE_VOLUMES="--volumes"
            shift
            ;;
        --rmi)
            REMOVE_IMAGES="--rmi all"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --volumes, -v  Remove named volumes"
            echo "  --rmi          Remove images"
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

# Stop and remove containers
echo "🐳 Stopping containers..."
$COMPOSE_CMD -f deployment/podman/podman-compose.yml down $REMOVE_VOLUMES $REMOVE_IMAGES

echo "✅ Services stopped successfully!"

# Show status
echo ""
echo "📊 Container status:"
podman ps -a --filter "name=resume-matcher" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

if [ "$REMOVE_VOLUMES" = "" ]; then
    echo ""
    echo "💡 Tip: Use --volumes to also remove data volumes"
    echo "   Example: $0 --volumes"
fi