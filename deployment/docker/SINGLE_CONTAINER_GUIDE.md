# Single Container Deployment Guide

This guide explains how to run your Resume Job Matcher application in a single Docker container with all services (Redis, Celery, FastAPI) included.

## Quick Start

### Option 1: Simple Approach (Recommended)

1. **Build the image:**
   ```bash
   cd /path/to/your/project
   ./deployment/docker/build-single.sh
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name resume-matcher \
     -p 8000:8000 \
     -p 5555:5555 \
     -v $(pwd)/data:/app/data \
     resume-matcher-single:latest
   ```

3. **Check logs:**
   ```bash
   docker logs -f resume-matcher
   ```

### Option 2: Supervisor Approach (More Robust)

1. **Build with supervisor:**
   ```bash
   ./deployment/docker/build-single.sh Dockerfile.dev.single
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name resume-matcher \
     -p 8000:8000 \
     -p 5555:5555 \
     -v $(pwd)/data:/app/data \
     resume-matcher-single:latest
   ```

## What's Included

The single container includes:
- **Redis Server** (port 6379) - Message broker and cache
- **FastAPI Application** (port 8000) - Main API server
- **Celery Worker** - Background task processor
- **Flower** (port 5555) - Celery monitoring dashboard

## Environment Variables

The container sets these automatically:
- `REDIS_URL=redis://localhost:6379/0`
- `CELERY_BROKER_URL=redis://localhost:6379/0`
- `CELERY_RESULT_BACKEND=redis://localhost:6379/0`
- `DEBUG=true`
- `ENVIRONMENT=development`

## Accessing Services

Once running, you can access:
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/api/v1/health/
- **Celery Monitoring**: http://localhost:5555

## Production Considerations

For production deployment:

1. **Set production environment variables:**
   ```bash
   docker run -d \
     --name resume-matcher \
     -p 8000:8000 \
     -e DEBUG=false \
     -e ENVIRONMENT=production \
     -e SECRET_KEY=your-secure-secret-key \
     -v $(pwd)/data:/app/data \
     resume-matcher-single:latest
   ```

2. **Use a reverse proxy** (nginx) in front of the container

3. **Set up proper logging** and monitoring

4. **Use Docker volumes** for persistent data

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs resume-matcher

# Run interactively for debugging
docker run -it --rm resume-matcher-single:latest /bin/bash
```

### Redis connection issues
```bash
# Test Redis inside container
docker exec -it resume-matcher redis-cli ping
```

### Celery not processing tasks
```bash
# Check Celery worker status
docker exec -it resume-matcher celery -A app.core.celery_app.celery_app inspect active
```

### Port conflicts
If ports 8000 or 5555 are already in use:
```bash
# Use different ports
docker run -d \
  --name resume-matcher \
  -p 8080:8000 \
  -p 5556:5555 \
  resume-matcher-single:latest
```

## File Structure

The single container setup adds these files:
```
deployment/docker/
├── Dockerfile.dev.simple      # Simple single-container Dockerfile
├── Dockerfile.dev.single      # Supervisor-based Dockerfile
├── start-all.sh              # Simple startup script
├── start-services.sh         # Supervisor startup script
├── supervisord.conf          # Supervisor configuration
├── build-single.sh           # Build script
└── SINGLE_CONTAINER_GUIDE.md # This guide
```

## Differences from Compose Setup

| Aspect | Compose Setup | Single Container |
|--------|---------------|------------------|
| Services | Separate containers | All in one container |
| Networking | Docker network | localhost |
| Scaling | Can scale services independently | Scale entire stack |
| Resource Usage | More overhead | Less overhead |
| Debugging | Easier to debug individual services | All logs in one place |
| Production | Better for production | Good for development/simple deployments |

## Next Steps

After successful deployment:
1. Test the API endpoints
2. Upload a resume and test job matching
3. Monitor Celery tasks in Flower
4. Set up proper environment variables for production