#!/bin/bash
set -e

# Docker entrypoint script for Resume Job Matcher

# Function to wait for a service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    
    echo "Waiting for $service_name at $host:$port..."
    while ! nc -z "$host" "$port"; do
        sleep 1
    done
    echo "$service_name is ready!"
}

# Function to run database migrations
run_migrations() {
    echo "Running database migrations..."
    python -c "
from app.db.init_db import init_db
import asyncio
asyncio.run(init_db())
"
}

# Wait for Redis if REDIS_HOST is set
if [ -n "$REDIS_HOST" ]; then
    wait_for_service "$REDIS_HOST" "${REDIS_PORT:-6379}" "Redis"
fi

# Wait for PostgreSQL if DATABASE_URL contains postgres
if [[ "$DATABASE_URL" == *"postgresql"* ]]; then
    # Extract host and port from DATABASE_URL
    DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
        wait_for_service "$DB_HOST" "$DB_PORT" "PostgreSQL"
    fi
fi

# Run migrations for API service
if [ "$1" = "api" ] || [ "$1" = "python" ]; then
    run_migrations
fi

# Execute the main command
exec "$@"