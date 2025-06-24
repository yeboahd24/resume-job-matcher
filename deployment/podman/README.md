# Resume Job Matcher - Podman Deployment

This directory contains Podman-specific deployment configurations for the Resume Job Matcher application.

## 🐳 Prerequisites

### Install Podman

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install podman podman-compose
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install podman
pip install podman-compose
```

**macOS:**
```bash
brew install podman
pip install podman-compose
```

**Windows:**
```bash
# Install via Windows Subsystem for Linux (WSL)
# Or use Podman Desktop: https://podman-desktop.io/
```

### Verify Installation
```bash
podman --version
podman-compose --version  # or docker-compose --version
```

## 🚀 Quick Start

### 1. Initial Setup
```bash
# Run the setup script
./scripts/podman_setup.sh
```

### 2. Start Services
```bash
# Start all services
./scripts/podman_start.sh

# Start with monitoring (includes Flower)
./scripts/podman_start.sh --monitoring

# Start in background
./scripts/podman_start.sh --detach

# Force rebuild and start
./scripts/podman_start.sh --build
```

### 3. Test the Application
```bash
# Check health
curl http://localhost:8000/api/v1/health/

# View API documentation
open http://localhost:8000/docs

# Test job matching
curl -X POST "http://localhost:8000/api/v1/jobs/match" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@data/samples/sample_resume.txt"
```

## 📋 Available Scripts

| Script | Description |
|--------|-------------|
| `./scripts/podman_setup.sh` | Initial setup and configuration |
| `./scripts/podman_start.sh` | Start all services |
| `./scripts/podman_stop.sh` | Stop all services |
| `./scripts/podman_logs.sh` | View service logs |
| `./scripts/podman_cleanup.sh` | Clean up all resources |

## 🔧 Manual Commands

### Basic Operations
```bash
# Set environment for docker-compose compatibility
export DOCKER_HOST="unix:///run/user/$UID/podman/podman.sock"

# Start services
podman-compose -f deployment/podman/podman-compose.yml up

# Start in background
podman-compose -f deployment/podman/podman-compose.yml up -d

# Stop services
podman-compose -f deployment/podman/podman-compose.yml down

# View logs
podman-compose -f deployment/podman/podman-compose.yml logs -f
```

### Advanced Operations
```bash
# Build and start
podman-compose -f deployment/podman/podman-compose.yml up --build

# Start with monitoring
podman-compose -f deployment/podman/podman-compose.yml --profile monitoring up

# Scale workers
podman-compose -f deployment/podman/podman-compose.yml up --scale worker=3

# Remove everything including volumes
podman-compose -f deployment/podman/podman-compose.yml down --volumes --rmi all
```

## 🏗️ Architecture

### Services

| Service | Port | Description |
|---------|------|-------------|
| **api** | 8000 | FastAPI application server |
| **worker** | - | Celery worker for background tasks |
| **redis** | 6379 | Redis broker and result backend |
| **flower** | 5555 | Celery monitoring (optional) |

### Volumes

| Volume | Purpose |
|--------|---------|
| `redis_data` | Redis persistence |
| `app_data` | Application data and uploads |
| `app_logs` | Application logs |

### Networks

- **resume-matcher-network**: Internal communication between services

## ⚙️ Configuration

### Environment Variables

The application uses environment variables from `.env` file:

```bash
# Job Scraping (enabled by default in Podman)
USE_MOCK_JOBS=false
ENABLE_REMOTEOK=true
ENABLE_WEWORKREMOTELY=true

# Redis Configuration
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Application Settings
DEBUG=false
ENVIRONMENT=production
```

### Podman-Specific Settings

The Podman compose file includes:

- **User namespace mapping**: `userns_mode: "keep-id"`
- **Unbuffered Python output**: `PYTHONUNBUFFERED=1`
- **Proper volume permissions**: Handled by Podman user mapping

## 🔍 Monitoring and Debugging

### View Logs
```bash
# All services
./scripts/podman_logs.sh

# Specific service
./scripts/podman_logs.sh --service api

# Follow logs
./scripts/podman_logs.sh --follow

# API logs only
./scripts/podman_logs.sh -s api -f
```

### Check Service Status
```bash
# List containers
podman ps

# Check specific containers
podman ps --filter "name=resume-matcher"

# Inspect container
podman inspect resume-matcher-api
```

### Access Container Shell
```bash
# API container
podman exec -it resume-matcher-api /bin/bash

# Worker container
podman exec -it resume-matcher-worker /bin/bash

# Redis container
podman exec -it resume-matcher-redis redis-cli
```

## 🐛 Troubleshooting

### Common Issues

1. **Permission Denied Errors**
   ```bash
   # Ensure Podman socket is enabled
   systemctl --user enable --now podman.socket
   
   # Set DOCKER_HOST
   export DOCKER_HOST="unix:///run/user/$UID/podman/podman.sock"
   ```

2. **Port Already in Use**
   ```bash
   # Check what's using the port
   sudo netstat -tulpn | grep :8000
   
   # Stop conflicting services
   sudo systemctl stop apache2  # or nginx, etc.
   ```

3. **Build Failures**
   ```bash
   # Clean build cache
   podman system prune -f
   
   # Rebuild from scratch
   ./scripts/podman_start.sh --build
   ```

4. **Network Issues**
   ```bash
   # Recreate network
   podman network rm resume-matcher-network
   ./scripts/podman_start.sh
   ```

### Debug Mode

Enable debug logging:

```bash
# Add to .env file
DEBUG=true
LOG_LEVEL=DEBUG

# Restart services
./scripts/podman_stop.sh
./scripts/podman_start.sh
```

## 🔒 Security Considerations

### Podman Security Benefits

- **Rootless containers**: Runs without root privileges
- **User namespace mapping**: Better isolation
- **SELinux integration**: Enhanced security on supported systems
- **No daemon**: Reduced attack surface

### Best Practices

1. **Keep images updated**:
   ```bash
   podman pull python:3.11-slim
   podman pull redis:7-alpine
   ```

2. **Regular cleanup**:
   ```bash
   ./scripts/podman_cleanup.sh --all
   ```

3. **Monitor logs**:
   ```bash
   ./scripts/podman_logs.sh --follow
   ```

## 📈 Performance Tuning

### Resource Limits

Add to compose file:
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
```

### Scaling Workers

```bash
# Scale to 3 workers
podman-compose -f deployment/podman/podman-compose.yml up --scale worker=3
```

### Redis Optimization

```bash
# Connect to Redis
podman exec -it resume-matcher-redis redis-cli

# Check memory usage
INFO memory

# Monitor commands
MONITOR
```

## 🔄 Updates and Maintenance

### Update Application
```bash
# Pull latest code
git pull

# Rebuild and restart
./scripts/podman_stop.sh
./scripts/podman_start.sh --build
```

### Backup Data
```bash
# Backup Redis data
podman exec resume-matcher-redis redis-cli BGSAVE

# Copy volume data
podman volume export redis_data > redis_backup.tar
```

### Restore Data
```bash
# Restore volume
podman volume import redis_data < redis_backup.tar
```

## 🆘 Support

For issues specific to Podman deployment:

1. Check the logs: `./scripts/podman_logs.sh`
2. Verify Podman setup: `./scripts/podman_setup.sh`
3. Clean and restart: `./scripts/podman_cleanup.sh && ./scripts/podman_start.sh --build`
4. Check Podman documentation: https://docs.podman.io/

---

**Happy containerizing with Podman! 🐳**