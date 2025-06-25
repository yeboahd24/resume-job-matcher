#!/bin/bash

# Script to fix port conflicts for Resume Job Matcher

echo "🔍 Checking for port conflicts..."

# Function to check if port is in use
check_port() {
    local port=$1
    local service=$2
    
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        echo "⚠️  Port $port is in use (needed for $service)"
        
        # Try to identify what's using the port
        local process=$(netstat -tulpn 2>/dev/null | grep ":$port " | head -1)
        echo "   Used by: $process"
        
        return 1
    else
        echo "✅ Port $port is available for $service"
        return 0
    fi
}

# Function to stop conflicting services
stop_conflicting_service() {
    local port=$1
    local service_name=$2
    
    echo "🛑 Attempting to stop conflicting services on port $port..."
    
    # Try to stop common services that might use these ports
    case $port in
        6379)
            # Redis port
            if systemctl is-active --quiet redis-server 2>/dev/null; then
                echo "   Stopping system Redis service..."
                sudo systemctl stop redis-server
            fi
            if systemctl is-active --quiet redis 2>/dev/null; then
                echo "   Stopping system Redis service..."
                sudo systemctl stop redis
            fi
            # Kill any Redis processes
            pkill -f redis-server 2>/dev/null || true
            ;;
        8000)
            # Common web server port
            if systemctl is-active --quiet apache2 2>/dev/null; then
                echo "   Stopping Apache..."
                sudo systemctl stop apache2
            fi
            if systemctl is-active --quiet nginx 2>/dev/null; then
                echo "   Stopping Nginx..."
                sudo systemctl stop nginx
            fi
            # Kill any processes on port 8000
            sudo fuser -k 8000/tcp 2>/dev/null || true
            ;;
        5555)
            # Flower port
            sudo fuser -k 5555/tcp 2>/dev/null || true
            ;;
    esac
    
    sleep 2
}

# Function to stop existing Resume Job Matcher containers
stop_existing_containers() {
    echo "🐳 Stopping existing Resume Job Matcher containers..."
    
    # Stop containers using podman
    podman stop $(podman ps -q --filter "name=resume-matcher") 2>/dev/null || true
    
    # Remove containers
    podman rm $(podman ps -aq --filter "name=resume-matcher") 2>/dev/null || true
    
    echo "✅ Existing containers stopped and removed"
}

# Main execution
echo "🔧 Resume Job Matcher - Port Conflict Resolution"
echo "==============================================="

# Stop existing containers first
stop_existing_containers

# Check required ports
PORTS_OK=true

if ! check_port 6379 "Redis"; then
    stop_conflicting_service 6379 "Redis"
    if ! check_port 6379 "Redis"; then
        echo "❌ Could not free port 6379. Please manually stop the service using this port."
        PORTS_OK=false
    fi
fi

if ! check_port 8000 "API Server"; then
    stop_conflicting_service 8000 "API Server"
    if ! check_port 8000 "API Server"; then
        echo "❌ Could not free port 8000. Please manually stop the service using this port."
        PORTS_OK=false
    fi
fi

if ! check_port 5555 "Flower (optional)"; then
    stop_conflicting_service 5555 "Flower"
    # Don't fail if Flower port can't be freed (it's optional)
fi

if [ "$PORTS_OK" = true ]; then
    echo ""
    echo "✅ All required ports are now available!"
    echo "🚀 You can now start the Resume Job Matcher:"
    echo "   ./scripts/podman_start.sh"
else
    echo ""
    echo "❌ Some ports are still in use. Please resolve manually:"
    echo "   sudo netstat -tulpn | grep -E ':(6379|8000|5555) '"
    echo "   sudo fuser -k PORT/tcp  # Replace PORT with the conflicting port"
    exit 1
fi