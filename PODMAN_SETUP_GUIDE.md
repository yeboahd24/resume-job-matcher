# Resume Job Matcher - Podman Setup Guide

## 🐳 Complete Podman Setup for Resume Job Matcher

This guide will help you set up and run the Resume Job Matcher using Podman instead of Docker. Podman is a daemonless, rootless container engine that's fully compatible with Docker commands and compose files.

## 🎯 Why Podman?

- **Rootless**: Runs without root privileges for better security
- **Daemonless**: No background daemon required
- **Docker Compatible**: Works with existing Docker Compose files
- **Secure**: Better isolation and security features
- **Lightweight**: Lower resource usage

## 📋 Prerequisites

### 1. Install Podman

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install podman
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install podman
```

**macOS:**
```bash
brew install podman
```

**Arch Linux:**
```bash
sudo pacman -S podman
```

### 2. Install Compose Tool

**Option A: Podman Compose (Recommended)**
```bash
pip install podman-compose
```

**Option B: Docker Compose (Alternative)**
```bash
# If you already have docker-compose installed, it works with Podman too
sudo apt-get install docker-compose  # Ubuntu/Debian
sudo dnf install docker-compose      # Fedora
brew install docker-compose          # macOS
```

### 3. Verify Installation
```bash
podman --version
podman-compose --version  # or docker-compose --version
```

## 🚀 Quick Start

### 1. Test Your Podman Setup
```bash
# Run the test script to verify everything is working
./scripts/test_podman_setup.sh
```

### 2. Initial Setup
```bash
# Run the setup script (this handles everything automatically)
./scripts/podman_setup.sh
```

### 3. Start the Application
```bash
# Start all services
./scripts/podman_start.sh

# Or start with monitoring (includes Flower for Celery monitoring)
./scripts/podman_start.sh --monitoring

# Or start in background
./scripts/podman_start.sh --detach
```

### 4. Test the Application
```bash
# Check if services are running
curl http://localhost:8000/api/v1/health/

# View API documentation
open http://localhost:8000/docs

# Test job matching with a resume
curl -X POST "http://localhost:8000/api/v1/jobs/match" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@data/samples/sample_resume.txt"
```

## 📊 Service URLs

Once running, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| **API** | http://localhost:8000 | Main application API |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/api/v1/health/ | Service health status |
| **Flower** | http://localhost:5555 | Celery monitoring (with --monitoring) |

## 🔧 Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Enable Podman Socket
```bash
# Enable Podman socket for docker-compose compatibility
systemctl --user enable --now podman.socket
```

### 2. Set Environment Variable
```bash
# Set DOCKER_HOST for docker-compose compatibility
export DOCKER_HOST="unix:///run/user/$UID/podman/podman.sock"

# Add to your shell profile for persistence
echo 'export DOCKER_HOST="unix:///run/user/$UID/podman/podman.sock"' >> ~/.bashrc
```

### 3. Create .env File
```bash
# Copy example environment file
cp .env.example .env

# Enable real job scraping (optional)
sed -i 's/USE_MOCK_JOBS=true/USE_MOCK_JOBS=false/' .env
```

### 4. Start Services
```bash
# Using podman-compose
podman-compose -f deployment/podman/podman-compose.yml up

# Or using docker-compose with Podman
docker-compose -f deployment/podman/podman-compose.yml up
```

## 📋 Available Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `test_podman_setup.sh` | Test Podman installation and setup | `./scripts/test_podman_setup.sh` |
| `podman_setup.sh` | Initial setup and configuration | `./scripts/podman_setup.sh` |
| `podman_start.sh` | Start all services | `./scripts/podman_start.sh [--build] [--detach] [--monitoring]` |
| `podman_stop.sh` | Stop all services | `./scripts/podman_stop.sh [--volumes] [--rmi]` |
| `podman_logs.sh` | View service logs | `./scripts/podman_logs.sh [--service SERVICE] [--follow]` |
| `podman_cleanup.sh` | Clean up all resources | `./scripts/podman_cleanup.sh [--force] [--all]` |

## 🔍 Monitoring and Debugging

### View Logs
```bash
# View all service logs
./scripts/podman_logs.sh

# View specific service logs
./scripts/podman_logs.sh --service api
./scripts/podman_logs.sh --service worker
./scripts/podman_logs.sh --service redis

# Follow logs in real-time
./scripts/podman_logs.sh --follow
```

### Check Service Status
```bash
# List all containers
podman ps

# List only Resume Job Matcher containers
podman ps --filter "name=resume-matcher"

# Check container details
podman inspect resume-matcher-api
```

### Access Container Shell
```bash
# Access API container
podman exec -it resume-matcher-api /bin/bash

# Access worker container
podman exec -it resume-matcher-worker /bin/bash

# Access Redis CLI
podman exec -it resume-matcher-redis redis-cli
```

## ⚙️ Configuration

### Environment Variables

Key settings in `.env` file:

```bash
# Job Scraping Settings
USE_MOCK_JOBS=false              # Set to false for real job scraping
ENABLE_REMOTEOK=true             # Enable RemoteOK scraping
ENABLE_WEWORKREMOTELY=true       # Enable We Work Remotely scraping
SCRAPING_MIN_DELAY=1.0           # Rate limiting

# Redis Settings
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Application Settings
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Scaling Services

```bash
# Scale Celery workers
podman-compose -f deployment/podman/podman-compose.yml up --scale worker=3

# Or with docker-compose
docker-compose -f deployment/podman/podman-compose.yml up --scale worker=3
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. Permission Denied
```bash
# Error: permission denied
# Solution: Enable Podman socket
systemctl --user enable --now podman.socket
export DOCKER_HOST="unix:///run/user/$UID/podman/podman.sock"
```

#### 2. Port Already in Use
```bash
# Error: port 8000 already in use
# Solution: Check what's using the port
sudo netstat -tulpn | grep :8000

# Stop conflicting service
sudo systemctl stop apache2  # or nginx, etc.
```

#### 3. Build Failures
```bash
# Error: build failed
# Solution: Clean and rebuild
./scripts/podman_cleanup.sh
./scripts/podman_start.sh --build
```

#### 4. Network Issues
```bash
# Error: network issues between containers
# Solution: Recreate network
podman network rm resume-matcher-network
./scripts/podman_start.sh
```

#### 5. Volume Permission Issues
```bash
# Error: volume permission denied
# Solution: Podman handles this automatically with userns_mode: "keep-id"
# If issues persist, check SELinux settings:
sudo setsebool -P container_manage_cgroup on
```

### Debug Mode

Enable debug logging:

```bash
# Edit .env file
DEBUG=true
LOG_LEVEL=DEBUG

# Restart services
./scripts/podman_stop.sh
./scripts/podman_start.sh
```

### Reset Everything

If you need to start completely fresh:

```bash
# Clean up everything
./scripts/podman_cleanup.sh --force --all

# Start fresh
./scripts/podman_setup.sh
./scripts/podman_start.sh --build
```

## 🔒 Security Benefits

Podman provides several security advantages:

- **Rootless**: Containers run as your user, not root
- **No daemon**: No privileged background process
- **User namespaces**: Better process isolation
- **SELinux integration**: Enhanced security on supported systems
- **Audit logging**: Better security monitoring

## 📈 Performance Tips

### Resource Optimization

```bash
# Limit container resources (add to compose file)
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
```

### Monitoring Performance

```bash
# Check container resource usage
podman stats

# Check specific container
podman stats resume-matcher-api

# Monitor Redis performance
podman exec -it resume-matcher-redis redis-cli INFO memory
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

# Export volume
podman volume export redis_data > redis_backup.tar
```

### Restore Data
```bash
# Import volume
podman volume import redis_data < redis_backup.tar
```

## 🆘 Getting Help

### Check Status
```bash
# Run comprehensive test
./scripts/test_podman_setup.sh

# Check logs for errors
./scripts/podman_logs.sh --service api
```

### Common Commands Reference

```bash
# Start services
./scripts/podman_start.sh

# Stop services
./scripts/podman_stop.sh

# View logs
./scripts/podman_logs.sh

# Clean up
./scripts/podman_cleanup.sh

# Test setup
./scripts/test_podman_setup.sh
```

### Resources

- **Podman Documentation**: https://docs.podman.io/
- **Podman Compose**: https://github.com/containers/podman-compose
- **Resume Job Matcher Docs**: `docs/`

---

## ✅ You're Ready!

Your Resume Job Matcher is now set up with Podman! The application includes:

- ✅ **Real job scraping** from RemoteOK and We Work Remotely
- ✅ **Enhanced fallback** job generation
- ✅ **Celery workers** for background processing
- ✅ **Redis** for task queuing and caching
- ✅ **Monitoring** with optional Flower interface
- ✅ **Health checks** and proper logging

**What would you like to do next?**

1. **Test the application** with a real resume
2. **Customize the configuration** for your needs
3. **Add more job sources** to the scraper
4. **Set up monitoring and alerts**
5. **Deploy to production** environment

Happy job matching with Podman! 🚀