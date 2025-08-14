#!/bin/bash
# Run script for Resume Job Matcher Docker containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="development"
DETACH=false
BUILD=false
LOGS=false
MONITORING=false

# Function to show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -e, --env ENV         Environment (development|production) (default: development)"
    echo "  -d, --detach          Run in detached mode"
    echo "  -b, --build           Build images before starting"
    echo "  -l, --logs            Show logs after starting"
    echo "  -m, --monitoring      Include monitoring services (Flower)"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --env development --build    # Build and run development environment"
    echo "  $0 --env production --detach    # Run production environment in background"
    echo "  $0 --logs                       # Run and show logs"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -d|--detach)
            DETACH=true
            shift
            ;;
        -b|--build)
            BUILD=true
            shift
            ;;
        -l|--logs)
            LOGS=true
            shift
            ;;
        -m|--monitoring)
            MONITORING=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option $1"
            usage
            ;;
    esac
done

# Validate environment
if [[ "$ENVIRONMENT" != "development" && "$ENVIRONMENT" != "production" ]]; then
    echo -e "${RED}Error: Environment must be 'development' or 'production'${NC}"
    exit 1
fi

# Set compose files based on environment
COMPOSE_FILES="-f deployment/docker/docker-compose.yml"

if [ "$ENVIRONMENT" = "development" ]; then
    COMPOSE_FILES="$COMPOSE_FILES -f deployment/docker/docker-compose.dev.yml"
elif [ "$ENVIRONMENT" = "production" ]; then
    COMPOSE_FILES="$COMPOSE_FILES -f deployment/docker/docker-compose.prod.yml"
fi

# Build docker-compose command
COMPOSE_CMD="docker-compose $COMPOSE_FILES"

# Add build flag if requested
if [ "$BUILD" = true ]; then
    BUILD_FLAG="--build"
else
    BUILD_FLAG=""
fi

# Add detach flag if requested
if [ "$DETACH" = true ]; then
    DETACH_FLAG="-d"
else
    DETACH_FLAG=""
fi

# Add monitoring profile if requested
if [ "$MONITORING" = true ]; then
    MONITORING_FLAG="--profile monitoring"
else
    MONITORING_FLAG=""
fi

echo -e "${GREEN}Starting Resume Job Matcher...${NC}"
echo -e "Environment: ${YELLOW}${ENVIRONMENT}${NC}"
echo -e "Compose files: ${YELLOW}${COMPOSE_FILES}${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}.env file created. Please review and update the values.${NC}"
    else
        echo -e "${RED}Error: .env.example file not found${NC}"
        exit 1
    fi
fi

# Start services
echo -e "\n${GREEN}Starting services...${NC}"
$COMPOSE_CMD up $BUILD_FLAG $DETACH_FLAG $MONITORING_FLAG

# Show logs if requested and running in detached mode
if [ "$LOGS" = true ] && [ "$DETACH" = true ]; then
    echo -e "\n${GREEN}Showing logs...${NC}"
    $COMPOSE_CMD logs -f
fi

if [ "$DETACH" = true ]; then
    echo -e "\n${GREEN}Services started successfully!${NC}"
    echo -e "\nAPI available at: ${YELLOW}http://localhost:8000${NC}"
    echo -e "API docs at: ${YELLOW}http://localhost:8000/docs${NC}"
    if [ "$MONITORING" = true ]; then
        echo -e "Flower monitoring at: ${YELLOW}http://localhost:5555${NC}"
    fi
    echo -e "\nTo view logs: ${YELLOW}docker-compose $COMPOSE_FILES logs -f${NC}"
    echo -e "To stop services: ${YELLOW}docker-compose $COMPOSE_FILES down${NC}"
fi