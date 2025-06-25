# Resume Job Matcher - Podman Troubleshooting Guide

## 🔧 Common Issues and Solutions

### 1. Port Conflicts

**Issue:** Error messages like:
```
Error: unable to start container: rootlessport listen tcp 0.0.0.0:6379: bind: address already in use
```

**Solutions:**

#### Option A: Automatic Fix
```bash
# Run the port conflict resolution script
./scripts/fix_port_conflicts.sh
```

#### Option B: Manual Fix
```bash
# Check what's using the ports
sudo netstat -tulpn | grep -E ':(6379|8000|5555)'

# Stop Redis if it's running
sudo systemctl stop redis-server

# Kill processes on specific ports
sudo fuser -k 6379/tcp  # For Redis
sudo fuser -k 8000/tcp  # For API
sudo fuser -k 5555/tcp  # For Flower
```

### 2. Pydantic Import Error

**Issue:** Error messages like:
```
pydantic.errors.PydanticImportError: `BaseSettings` has been moved to the `pydantic-settings` package.
```

**Solutions:**

#### Option A: Automatic Fix
```bash
# Run the comprehensive fix script
./scripts/fix_podman_issues.sh
```

#### Option B: Manual Fix
```bash
# Install pydantic-settings
pip install pydantic-settings

# Update the container image
./scripts/podman_start.sh --build
```

### 3. Container Startup Issues

**Issue:** Containers fail to start or crash immediately

**Solutions:**

```bash
# Check container logs
./scripts/podman_logs.sh

# Clean up and rebuild
./scripts/podman_stop.sh
./scripts/podman_cleanup.sh
./scripts/podman_start.sh --build
```

### 4. Redis Connection Issues

**Issue:** Services can't connect to Redis

**Solutions:**

```bash
# Check if Redis is running
podman ps | grep redis

# Check Redis logs
./scripts/podman_logs.sh -s redis

# Test Redis connection
podman exec -it resume-matcher-redis redis-cli ping
```

### 5. Permission Issues

**Issue:** Permission denied errors

**Solutions:**

```bash
# Fix file permissions
chmod -R 755 scripts/
chmod -R 644 deployment/podman/*

# Run with proper user namespace
podman run --userns=keep-id ...
```

## 🚀 Complete Reset Procedure

If you're still having issues, try this complete reset procedure:

```bash
# 1. Stop all containers
./scripts/podman_stop.sh

# 2. Clean up all resources
./scripts/podman_cleanup.sh --force --all

# 3. Fix any issues
./scripts/fix_podman_issues.sh

# 4. Start fresh
./scripts/podman_start.sh --build
```

## 🔍 Diagnostic Commands

### Check Podman Status
```bash
# Check Podman version
podman --version

# Check running containers
podman ps

# Check all containers (including stopped)
podman ps -a
```

### Check Network Status
```bash
# List networks
podman network ls

# Inspect network
podman network inspect resume-matcher-network
```

### Check Volume Status
```bash
# List volumes
podman volume ls

# Inspect volume
podman volume inspect redis_data
```

### Check System Resources
```bash
# Check system resources
podman system df

# Check container resource usage
podman stats
```

## 📋 Log Collection for Support

If you need to share logs for support:

```bash
# Collect all logs
./scripts/podman_logs.sh > resume-matcher-logs.txt

# Collect system information
(podman info; podman ps -a; podman volume ls; podman network ls) > podman-info.txt

# Collect configuration
cat deployment/podman/podman-compose.yml > podman-compose-config.txt
```

## 🆘 Still Having Issues?

1. **Check for system updates**: Ensure Podman is up to date
2. **Verify system requirements**: Ensure you have enough disk space and memory
3. **Try rootful mode**: If rootless mode has issues, try with sudo
4. **Check SELinux**: If using SELinux, try `sudo setenforce 0` temporarily
5. **Restart system**: Sometimes a simple restart fixes permission issues

---

If you've tried all these solutions and still have issues, please file a detailed bug report including:
- Error messages
- Output of `podman info`
- Steps to reproduce
- Logs from `./scripts/podman_logs.sh`