#!/bin/bash

# Test script for Podman setup

echo "🧪 Testing Podman Setup for Resume Job Matcher"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
test_command() {
    local cmd="$1"
    local desc="$2"
    
    if command -v "$cmd" &> /dev/null; then
        echo -e "✅ ${GREEN}$desc${NC}: $(command -v "$cmd")"
        return 0
    else
        echo -e "❌ ${RED}$desc${NC}: Not found"
        return 1
    fi
}

test_service() {
    local service="$1"
    local desc="$2"
    
    if systemctl --user is-active --quiet "$service" 2>/dev/null; then
        echo -e "✅ ${GREEN}$desc${NC}: Active"
        return 0
    else
        echo -e "⚠️  ${YELLOW}$desc${NC}: Not active"
        return 1
    fi
}

# Test 1: Check if Podman is installed
echo "1. Checking Podman installation..."
if test_command "podman" "Podman"; then
    echo "   Version: $(podman --version)"
else
    echo -e "   ${RED}Please install Podman first${NC}"
    echo "   Visit: https://podman.io/getting-started/installation"
    exit 1
fi

# Test 2: Check compose tools
echo ""
echo "2. Checking compose tools..."
COMPOSE_FOUND=false

if test_command "podman-compose" "Podman Compose"; then
    COMPOSE_CMD="podman-compose"
    COMPOSE_FOUND=true
    echo "   Version: $(podman-compose --version)"
fi

if test_command "docker-compose" "Docker Compose"; then
    if [ "$COMPOSE_FOUND" = false ]; then
        COMPOSE_CMD="docker-compose"
        COMPOSE_FOUND=true
    fi
    echo "   Version: $(docker-compose --version)"
fi

if [ "$COMPOSE_FOUND" = false ]; then
    echo -e "   ${RED}No compose tool found. Install one of:${NC}"
    echo "   - pip install podman-compose"
    echo "   - Install docker-compose"
    exit 1
fi

echo -e "   ${GREEN}Will use: $COMPOSE_CMD${NC}"

# Test 3: Check Podman socket
echo ""
echo "3. Checking Podman socket..."
if test_service "podman.socket" "Podman Socket"; then
    echo "   Socket path: /run/user/$UID/podman/podman.sock"
else
    echo "   Attempting to enable Podman socket..."
    if systemctl --user enable --now podman.socket 2>/dev/null; then
        echo -e "   ✅ ${GREEN}Podman socket enabled${NC}"
    else
        echo -e "   ⚠️  ${YELLOW}Could not enable Podman socket automatically${NC}"
        echo "   Run: systemctl --user enable --now podman.socket"
    fi
fi

# Test 4: Check DOCKER_HOST
echo ""
echo "4. Checking DOCKER_HOST environment..."
EXPECTED_DOCKER_HOST="unix:///run/user/$UID/podman/podman.sock"

if [ "$DOCKER_HOST" = "$EXPECTED_DOCKER_HOST" ]; then
    echo -e "   ✅ ${GREEN}DOCKER_HOST correctly set${NC}"
else
    echo -e "   ⚠️  ${YELLOW}DOCKER_HOST not set or incorrect${NC}"
    echo "   Current: ${DOCKER_HOST:-"(not set)"}"
    echo "   Expected: $EXPECTED_DOCKER_HOST"
    echo "   Run: export DOCKER_HOST=\"$EXPECTED_DOCKER_HOST\""
fi

# Test 5: Check project files
echo ""
echo "5. Checking project files..."
FILES=(
    ".env.example"
    "deployment/podman/podman-compose.yml"
    "deployment/podman/Containerfile"
    "requirements.txt"
    "main.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "   ✅ ${GREEN}$file${NC}"
    else
        echo -e "   ❌ ${RED}$file${NC}: Missing"
    fi
done

# Test 6: Check directories
echo ""
echo "6. Checking directories..."
DIRS=(
    "data/uploads"
    "data/samples"
    "logs"
    "scripts"
)

for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "   ✅ ${GREEN}$dir/${NC}"
    else
        echo -e "   ⚠️  ${YELLOW}$dir/${NC}: Missing (will be created)"
        mkdir -p "$dir"
        echo -e "   ✅ ${GREEN}Created $dir/${NC}"
    fi
done

# Test 7: Test Podman basic functionality
echo ""
echo "7. Testing Podman functionality..."

# Test podman info
if podman info &>/dev/null; then
    echo -e "   ✅ ${GREEN}Podman info${NC}: Working"
else
    echo -e "   ❌ ${RED}Podman info${NC}: Failed"
fi

# Test podman pull
echo "   Testing image pull..."
if podman pull hello-world &>/dev/null; then
    echo -e "   ✅ ${GREEN}Image pull${NC}: Working"
    podman rmi hello-world &>/dev/null
else
    echo -e "   ❌ ${RED}Image pull${NC}: Failed"
fi

# Test 8: Check .env file
echo ""
echo "8. Checking .env configuration..."
if [ -f ".env" ]; then
    echo -e "   ✅ ${GREEN}.env file exists${NC}"
    
    # Check important settings
    if grep -q "USE_MOCK_JOBS=false" .env; then
        echo -e "   ✅ ${GREEN}Real scraping enabled${NC}"
    else
        echo -e "   ⚠️  ${YELLOW}Mock jobs enabled${NC} (change USE_MOCK_JOBS=false for real scraping)"
    fi
else
    echo -e "   ⚠️  ${YELLOW}.env file missing${NC}"
    echo "   Run: cp .env.example .env"
fi

# Summary
echo ""
echo "📋 Test Summary"
echo "==============="

# Set DOCKER_HOST for the test
export DOCKER_HOST="$EXPECTED_DOCKER_HOST"

# Test compose file syntax
if $COMPOSE_CMD -f deployment/podman/podman-compose.yml config &>/dev/null; then
    echo -e "✅ ${GREEN}Compose file syntax: Valid${NC}"
else
    echo -e "❌ ${RED}Compose file syntax: Invalid${NC}"
fi

echo ""
echo "🚀 Ready to start!"
echo ""
echo "Next steps:"
echo "1. Run: ./scripts/podman_setup.sh (if not done already)"
echo "2. Run: ./scripts/podman_start.sh"
echo "3. Test: curl http://localhost:8000/api/v1/health/"
echo ""
echo "For help: ./scripts/podman_start.sh --help"