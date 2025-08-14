# Docker Deployment Guide

This directory contains Docker configuration files for the Resume Job Matcher application.

## Quick Start

### Development Environment

```bash
# Clone the repository and navigate to the project root
cd /path/to/resume-job-matcher

# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings

# Build and run development environment
./deployment/docker/scripts/run.sh --env development --build

# Or using docker-compose directly
docker-compose -f deployment/docker/docker-compose.yml -f deployment/docker/docker-compose.dev.yml up --build
```

### Production Environment

```bash
# Set production environment variables
cp .env.example .env
# Configure production values in .env

# Run production environment
./deployment/docker/scripts/run.sh --env production --detach --build

# Or using docker-compose directly
docker-compose -f deployment/docker/docker-compose.yml -f deployment/docker/docker-compose.prod.yml up -d --build
```

## Files Overview

### Core Files
- `Dockerfile` - Multi-stage production Dockerfile
- `Dockerfile.dev` - Development Dockerfile with debugging tools
- `docker-compose.yml` - Base compose configuration
- `docker-compose.dev.yml` - Development overrides
- `docker-compose.prod.yml` - Production overrides
- `docker-entrypoint.sh` - Entrypoint script with service waiting

### Scripts
- `scripts/build.sh` - Build Docker images
- `scripts/run.sh` - Run Docker containers with various options

## Services

### API Service (`api`)
- **Port**: 8000
- **Health Check**: `/api/v1/health/`
- **Environment**: Configurable via environment variables

### Worker Service (`worker`)
- **Purpose**: Celery worker for background tasks
- **Concurrency**: Configurable (dev: 1, prod: 4)
- **Health Check**: Celery inspect ping

### Redis Service (`redis`)
- **Port**: 6379
- **Persistence**: Enabled with appendonly
- **Health Check**: Redis ping

### Flower Service (`flower`) - Optional
- **Port**: 5555
- **Purpose**: Celery monitoring
- **Profile**: `monitoring` (use `--profile monitoring` to enable)

### PostgreSQL Service (`postgres`) - Development Only
- **Port**: 5432
- **Database**: `resume_matcher_dev`
- **Credentials**: `dev_user` / `dev_password`

## Environment Variables

### Required
```bash
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
```

### Optional
```bash
# Redis
REDIS_PASSWORD=optional-redis-password

# Flower (production)
FLOWER_USER=admin
FLOWER_PASSWORD=secure-password

# Database (if using PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

## Usage Examples

### Development with Hot Reload
```bash
# Start development environment with code mounting
./deployment/docker/scripts/run.sh --env development --build --logs
```

### Production with Monitoring
```bash
# Start production with Flower monitoring
./deployment/docker/scripts/run.sh --env production --detach --monitoring
```

### Building Images
```bash
# Build production image
./deployment/docker/scripts/build.sh --name my-app --tag v1.0.0

# Build development image
./deployment/docker/scripts/build.sh --dev --name my-app --tag v1.0.0-dev

# Build and push to registry
./deployment/docker/scripts/build.sh --push --registry my-registry.com --name my-app
```

## Docker Compose Commands

### Basic Operations
```bash
# Start services
docker-compose -f deployment/docker/docker-compose.yml up

# Start in background
docker-compose -f deployment/docker/docker-compose.yml up -d

# Stop services
docker-compose -f deployment/docker/docker-compose.yml down

# View logs
docker-compose -f deployment/docker/docker-compose.yml logs -f

# Rebuild and start
docker-compose -f deployment/docker/docker-compose.yml up --build
```

### Environment-Specific
```bash
# Development
docker-compose -f deployment/docker/docker-compose.yml -f deployment/docker/docker-compose.dev.yml up

# Production
docker-compose -f deployment/docker/docker-compose.yml -f deployment/docker/docker-compose.prod.yml up -d

# With monitoring
docker-compose -f deployment/docker/docker-compose.yml --profile monitoring up
```

## Volumes

### Persistent Data
- `redis_data` - Redis persistence
- `app_data` - Application data (uploads, database)
- `app_logs` - Application logs
- `postgres_data` - PostgreSQL data (development only)

### Development Mounts
- Source code is mounted read-only for hot reload
- Data directories are mounted for persistence

## Health Checks

All services include health checks:
- **API**: HTTP check on `/api/v1/health/`
- **Worker**: Celery inspect ping
- **Redis**: Redis ping command
- **PostgreSQL**: pg_isready check

## Networking

- Default network: `resume-matcher-network`
- Services communicate using service names
- External ports: 8000 (API), 5555 (Flower), 5432 (PostgreSQL dev)

## Security Considerations

### Production
- Non-root user in containers
- Minimal base images
- Multi-stage builds to reduce attack surface
- Health checks for service monitoring
- Resource limits configured

### Secrets Management
- Use environment variables for secrets
- Consider Docker secrets for production
- Never commit secrets to version control

## Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Check what's using the port
   lsof -i :8000
   
   # Use different ports
   docker-compose -f deployment/docker/docker-compose.yml up -p 8001:8000
   ```

2. **Permission issues**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER data/
   ```

3. **Redis connection issues**
   ```bash
   # Check Redis logs
   docker-compose -f deployment/docker/docker-compose.yml logs redis
   
   # Test Redis connection
   docker-compose -f deployment/docker/docker-compose.yml exec redis redis-cli ping
   ```

4. **Build failures**
   ```bash
   # Clean build
   docker-compose -f deployment/docker/docker-compose.yml build --no-cache
   
   # Check disk space
   docker system df
   
   # Clean up
   docker system prune
   ```

### Logs and Debugging

```bash
# View all logs
docker-compose -f deployment/docker/docker-compose.yml logs

# Follow logs for specific service
docker-compose -f deployment/docker/docker-compose.yml logs -f api

# Execute commands in running container
docker-compose -f deployment/docker/docker-compose.yml exec api bash

# Check service status
docker-compose -f deployment/docker/docker-compose.yml ps
```

## Performance Tuning

### Production Optimizations
- Worker concurrency based on CPU cores
- Resource limits to prevent resource exhaustion
- Redis persistence configuration
- Log level optimization

### Development Optimizations
- Single worker for easier debugging
- Code mounting for hot reload
- Debug logging enabled
- Additional development tools installed

## Monitoring

### Built-in Monitoring
- Health checks on all services
- Flower for Celery monitoring (optional)
- Docker Compose service status

### External Monitoring
Consider adding:
- Prometheus metrics
- Grafana dashboards
- Log aggregation (ELK stack)
- APM tools (New Relic, DataDog)

## Backup and Recovery

### Data Backup
```bash
# Backup Redis data
docker-compose -f deployment/docker/docker-compose.yml exec redis redis-cli BGSAVE

# Backup application data
docker run --rm -v resume-matcher_app_data:/data -v $(pwd):/backup alpine tar czf /backup/app_data_backup.tar.gz -C /data .

# Backup PostgreSQL (development)
docker-compose -f deployment/docker/docker-compose.yml exec postgres pg_dump -U dev_user resume_matcher_dev > backup.sql
```

### Data Recovery
```bash
# Restore application data
docker run --rm -v resume-matcher_app_data:/data -v $(pwd):/backup alpine tar xzf /backup/app_data_backup.tar.gz -C /data

# Restore PostgreSQL
docker-compose -f deployment/docker/docker-compose.yml exec -T postgres psql -U dev_user resume_matcher_dev < backup.sql
```