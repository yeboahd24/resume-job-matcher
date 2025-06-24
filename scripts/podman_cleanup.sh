#!/bin/bash

# Cleanup Resume Job Matcher Podman resources

echo "🧹 Cleaning up Resume Job Matcher Podman resources"
echo "=================================================="

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
FORCE=""
CLEAN_ALL=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --force|-f)
            FORCE="yes"
            shift
            ;;
        --all)
            CLEAN_ALL="yes"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --force, -f    Don't ask for confirmation"
            echo "  --all          Clean everything including system resources"
            echo "  --help, -h     Show this help message"
            echo ""
            echo "This script will:"
            echo "  1. Stop all Resume Job Matcher containers"
            echo "  2. Remove containers and networks"
            echo "  3. Remove volumes (data will be lost!)"
            echo "  4. Remove built images"
            echo "  5. Optionally clean system resources"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Confirmation
if [ "$FORCE" != "yes" ]; then
    echo "⚠️  WARNING: This will remove all Resume Job Matcher containers, volumes, and data!"
    echo "   This action cannot be undone."
    echo ""
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cleanup cancelled"
        exit 1
    fi
fi

echo "🛑 Stopping services..."
$COMPOSE_CMD -f deployment/podman/podman-compose.yml down --volumes --rmi all

echo "🗑️  Removing Resume Job Matcher containers..."
podman rm -f $(podman ps -a --filter "name=resume-matcher" -q) 2>/dev/null || true

echo "🗑️  Removing Resume Job Matcher images..."
podman rmi $(podman images --filter "reference=*resume-matcher*" -q) 2>/dev/null || true

echo "🗑️  Removing Resume Job Matcher volumes..."
podman volume rm $(podman volume ls --filter "name=*resume-matcher*" -q) 2>/dev/null || true

echo "🗑️  Removing Resume Job Matcher networks..."
podman network rm resume-matcher-network 2>/dev/null || true

if [ "$CLEAN_ALL" = "yes" ]; then
    echo "🧹 Cleaning system resources..."
    
    echo "   Removing unused containers..."
    podman container prune -f
    
    echo "   Removing unused images..."
    podman image prune -f
    
    echo "   Removing unused volumes..."
    podman volume prune -f
    
    echo "   Removing unused networks..."
    podman network prune -f
    
    echo "   Cleaning build cache..."
    podman system prune -f
fi

echo ""
echo "✅ Cleanup completed!"
echo ""
echo "📊 Current Podman status:"
echo "   Containers: $(podman ps -a --filter 'name=resume-matcher' --format '{{.Names}}' | wc -l) Resume Job Matcher containers"
echo "   Images:     $(podman images --filter 'reference=*resume-matcher*' --format '{{.Repository}}' | wc -l) Resume Job Matcher images"
echo "   Volumes:    $(podman volume ls --filter 'name=*resume-matcher*' --format '{{.Name}}' | wc -l) Resume Job Matcher volumes"
echo ""
echo "💡 To start fresh, run: ./scripts/podman_start.sh --build"