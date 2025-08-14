#!/bin/bash

# Wait for Redis to be ready
echo "Starting Redis..."
redis-server /etc/redis/redis.conf &
REDIS_PID=$!

# Wait for Redis to start
sleep 5

# Test Redis connection
echo "Testing Redis connection..."
redis-cli ping
if [ $? -ne 0 ]; then
    echo "Redis failed to start"
    exit 1
fi

echo "Redis is ready!"

# Initialize database if needed
echo "Initializing database..."
python -c "
import asyncio
from app.db.init_db import init_db

async def main():
    await init_db()
    print('Database initialized successfully')

if __name__ == '__main__':
    asyncio.run(main())
" || echo "Database initialization failed or already exists"

# Start supervisor to manage all services
echo "Starting all services with supervisor..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf