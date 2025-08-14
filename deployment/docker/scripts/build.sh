#!/bin/bash
# Build script for Resume Job Matcher Docker images

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
IMAGE_NAME="resume-job-matcher"
TAG="latest"
BUILD_TYPE="production"
PUSH=false
REGISTRY=""

# Function to show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -n, --name NAME       Image name (default: resume-job-matcher)"
    echo "  -t, --tag TAG         Image tag (default: latest)"
    echo "  -d, --dev             Build development image"
    echo "  -p, --push            Push to registry after build"
    echo "  -r, --registry REG    Registry URL (required if pushing)"
    echo "  -h, --help            Show this help message"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -d|--dev)
            BUILD_TYPE="development"
            shift
            ;;
        -p|--push)
            PUSH=true
            shift
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
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

# Set dockerfile based on build type
if [ "$BUILD_TYPE" = "development" ]; then
    DOCKERFILE="deployment/docker/Dockerfile.dev"
    FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}-dev"
else
    DOCKERFILE="deployment/docker/Dockerfile"
    FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"
fi

# Add registry prefix if provided
if [ -n "$REGISTRY" ]; then
    FULL_IMAGE_NAME="${REGISTRY}/${FULL_IMAGE_NAME}"
fi

echo -e "${GREEN}Building Resume Job Matcher Docker image...${NC}"
echo -e "Image name: ${YELLOW}${FULL_IMAGE_NAME}${NC}"
echo -e "Build type: ${YELLOW}${BUILD_TYPE}${NC}"
echo -e "Dockerfile: ${YELLOW}${DOCKERFILE}${NC}"

# Build the image
echo -e "\n${GREEN}Starting Docker build...${NC}"
docker build \
    -f "$DOCKERFILE" \
    -t "$FULL_IMAGE_NAME" \
    --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    --build-arg VCS_REF="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
    .

echo -e "\n${GREEN}Build completed successfully!${NC}"

# Push if requested
if [ "$PUSH" = true ]; then
    if [ -z "$REGISTRY" ]; then
        echo -e "${RED}Error: Registry URL required for pushing${NC}"
        exit 1
    fi
    
    echo -e "\n${GREEN}Pushing image to registry...${NC}"
    docker push "$FULL_IMAGE_NAME"
    echo -e "${GREEN}Push completed successfully!${NC}"
fi

echo -e "\n${GREEN}Docker image ready: ${YELLOW}${FULL_IMAGE_NAME}${NC}"
echo -e "\nTo run the image:"
echo -e "  ${YELLOW}docker run -p 8000:8000 ${FULL_IMAGE_NAME}${NC}"
echo -e "\nTo run with docker-compose:"
echo -e "  ${YELLOW}docker-compose -f deployment/docker/docker-compose.yml up${NC}"