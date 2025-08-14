#!/bin/bash

# Fix dependencies for authentication system

echo "🔧 Fixing Dependencies for Authentication System"
echo "=============================================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Install specific dependencies first to resolve conflicts
echo "📦 Installing specific dependencies to resolve conflicts..."
pip install python-multipart==0.0.7
pip install aiosqlite==0.19.0
pip install fastapi-users[sqlalchemy]==12.1.3

# Then install the rest
echo "📦 Installing remaining dependencies..."
pip install -r requirements.txt --no-deps

echo "✅ Dependencies fixed!"
echo ""
echo "🚀 Next steps:"
echo "1. Initialize the database: python setup_auth.py"
echo "2. Create admin user: python create_admin_user.py"
echo "3. Start the server: python main.py"