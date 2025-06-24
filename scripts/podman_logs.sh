#!/bin/bash

# View logs for Resume Job Matcher Podman services

echo "📋 Resume Job Matcher - Service Logs"
echo "===================================="

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
SERVICE=""
FOLLOW_FLAG=""
TAIL_LINES="50"

while [[ $# -gt 0 ]]; do
    case $1 in
        --service|-s)
            SERVICE="$2"
            shift 2
            ;;
        --follow|-f)
            FOLLOW_FLAG="-f"
            shift
            ;;
        --tail|-t)
            TAIL_LINES="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --service, -s SERVICE  Show logs for specific service (api, worker, redis, flower)"
            echo "  --follow, -f           Follow log output"
            echo "  --tail, -t LINES       Number of lines to show (default: 50)"
            echo "  --help, -h             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                     Show logs for all services"
            echo "  $0 -s api -f           Follow API logs"
            echo "  $0 -s worker -t 100    Show last 100 lines of worker logs"
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

if [ -n "$SERVICE" ]; then
    echo "📊 Showing logs for service: $SERVICE"
    $COMPOSE_CMD -f deployment/podman/podman-compose.yml logs $FOLLOW_FLAG --tail=$TAIL_LINES $SERVICE
else
    echo "📊 Showing logs for all services"
    $COMPOSE_CMD -f deployment/podman/podman-compose.yml logs $FOLLOW_FLAG --tail=$TAIL_LINES
fi