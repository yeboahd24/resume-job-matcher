#!/bin/bash

# Script to enable real job scraping for the Resume Job Matcher

echo "🔄 Enabling Real Job Scraping for Resume Job Matcher"
echo "=================================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
else
    echo "📁 .env file already exists"
fi

# Update USE_MOCK_JOBS setting
echo "🔧 Configuring job scraping settings..."

# Use sed to update the USE_MOCK_JOBS setting
if grep -q "USE_MOCK_JOBS" .env; then
    sed -i 's/USE_MOCK_JOBS=true/USE_MOCK_JOBS=false/' .env
    echo "✅ Updated USE_MOCK_JOBS=false"
else
    echo "USE_MOCK_JOBS=false" >> .env
    echo "✅ Added USE_MOCK_JOBS=false"
fi

# Ensure other scraping settings are present
echo "📋 Checking scraping configuration..."

# Function to add setting if not present
add_setting_if_missing() {
    local setting=$1
    local value=$2
    
    if ! grep -q "^$setting=" .env; then
        echo "$setting=$value" >> .env
        echo "✅ Added $setting=$value"
    else
        echo "✓ $setting already configured"
    fi
}

# Add scraping settings
add_setting_if_missing "SCRAPING_MIN_DELAY" "1.0"
add_setting_if_missing "SCRAPING_MAX_DELAY" "3.0"
add_setting_if_missing "SCRAPING_MAX_RETRIES" "3"
add_setting_if_missing "ENABLE_REMOTEOK" "true"
add_setting_if_missing "ENABLE_WEWORKREMOTELY" "true"
add_setting_if_missing "ENABLE_ENHANCED_FALLBACK" "true"

echo ""
echo "🎯 Real Job Scraping Configuration Complete!"
echo ""
echo "📊 Current Settings:"
echo "   USE_MOCK_JOBS=false (real scraping enabled)"
echo "   SCRAPING_MIN_DELAY=1.0 (respectful rate limiting)"
echo "   ENABLE_REMOTEOK=true (RemoteOK scraping enabled)"
echo "   ENABLE_WEWORKREMOTELY=true (We Work Remotely enabled)"
echo ""
echo "🚀 Next Steps:"
echo "   1. Start Redis: redis-server"
echo "   2. Start Celery: celery -A app.core.celery_app.celery_app worker --loglevel=info"
echo "   3. Start API: python main.py"
echo "   4. Test with: curl -X POST 'http://localhost:8000/api/v1/jobs/match' -F 'file=@resume.pdf'"
echo ""
echo "📖 For more details, see: docs/JOB_SCRAPING_GUIDE.md"
echo "✅ Setup complete!"