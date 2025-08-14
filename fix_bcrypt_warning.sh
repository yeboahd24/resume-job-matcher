#!/bin/bash

# Fix bcrypt warning by updating passlib

echo "🔧 Fixing bcrypt warning"
echo "======================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Install specific versions that work well together
echo "📦 Installing compatible versions..."
pip install --upgrade passlib==1.7.4 bcrypt==4.0.1

echo "✅ Fixed bcrypt warning!"
echo ""
echo "🚀 The warning should no longer appear when creating users."