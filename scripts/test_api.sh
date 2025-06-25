#!/bin/bash

# Test script for Resume Job Matcher API

echo "🧪 Testing Resume Job Matcher API"
echo "================================="

# Check if curl is installed
if ! command -v curl &> /dev/null; then
    echo "❌ curl is not installed. Please install curl first."
    exit 1
fi

# Check if the API is running
echo "🔍 Checking if API is running..."
if ! curl -s "http://localhost:8000/api/v1/health/" | grep -q "status"; then
    echo "❌ API is not running. Please start the API first."
    echo "   Run: ./scripts/podman_start.sh"
    exit 1
fi

echo "✅ API is running!"

# Check if sample resume exists
SAMPLE_RESUME="data/samples/sample_resume.txt"
if [ ! -f "$SAMPLE_RESUME" ]; then
    echo "❌ Sample resume not found: $SAMPLE_RESUME"
    exit 1
fi

echo "✅ Sample resume found: $SAMPLE_RESUME"

# Test the job matching endpoint
echo ""
echo "🚀 Testing job matching endpoint..."
echo "   POST http://localhost:8000/api/v1/jobs/match"
echo "   Uploading file: $SAMPLE_RESUME"
echo ""
echo "⏳ This may take a moment..."

RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/jobs/match" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@$SAMPLE_RESUME")

# Check if the response contains task_id
if echo "$RESPONSE" | grep -q "task_id"; then
    TASK_ID=$(echo "$RESPONSE" | grep -o '"task_id":"[^"]*' | cut -d'"' -f4)
    echo "✅ Request successful! Task ID: $TASK_ID"
    
    # Wait for task to complete
    echo ""
    echo "⏳ Waiting for task to complete..."
    
    STATUS="PENDING"
    MAX_ATTEMPTS=30
    ATTEMPT=0
    
    while [ "$STATUS" == "PENDING" ] || [ "$STATUS" == "STARTED" ]; do
        ATTEMPT=$((ATTEMPT+1))
        if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
            echo "⚠️  Task is taking too long. You can check the status manually:"
            echo "   curl http://localhost:8000/api/v1/tasks/$TASK_ID/status"
            break
        fi
        
        echo -n "."
        sleep 2
        
        STATUS_RESPONSE=$(curl -s "http://localhost:8000/api/v1/tasks/$TASK_ID/status")
        STATUS=$(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*' | cut -d'"' -f4)
    done
    
    echo ""
    echo "✅ Task completed with status: $STATUS"
    
    if [ "$STATUS" == "SUCCESS" ]; then
        echo ""
        echo "🎉 Job matching successful! Results:"
        echo ""
        curl -s "http://localhost:8000/api/v1/tasks/$TASK_ID/result" | python -m json.tool
    else
        echo ""
        echo "❌ Task failed. Details:"
        echo "$STATUS_RESPONSE" | python -m json.tool
    fi
else
    echo "❌ Request failed. Response:"
    echo "$RESPONSE" | python -m json.tool
fi