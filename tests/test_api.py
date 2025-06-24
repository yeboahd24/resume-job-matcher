#!/usr/bin/env python3
"""
Simple script to test the Resume Job Matcher API endpoints.
Make sure the FastAPI server and Celery worker are running before executing this script.
"""

import requests
import time
import json
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
SAMPLE_RESUME_PATH = "sample_resume.txt"

def test_health_endpoint():
    """Test the health check endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed: {data}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False

def test_upload_resume():
    """Test uploading a resume file."""
    print("\nTesting resume upload...")
    
    # Check if sample resume exists
    if not Path(SAMPLE_RESUME_PATH).exists():
        print(f"✗ Sample resume file not found: {SAMPLE_RESUME_PATH}")
        return None
    
    try:
        with open(SAMPLE_RESUME_PATH, 'rb') as file:
            files = {'file': (SAMPLE_RESUME_PATH, file, 'text/plain')}
            response = requests.post(f"{API_BASE_URL}/api/match-jobs", files=files)
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('task_id')
            print(f"✓ Resume uploaded successfully")
            print(f"  Task ID: {task_id}")
            print(f"  Status: {data.get('status')}")
            print(f"  Message: {data.get('message')}")
            return task_id
        else:
            print(f"✗ Resume upload failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Resume upload error: {e}")
        return None

def test_task_status(task_id, max_wait_time=60):
    """Test checking task status and wait for completion."""
    print(f"\nTesting task status for task: {task_id}")
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(f"{API_BASE_URL}/api/task-status/{task_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                
                print(f"  Status: {status}")
                
                if 'progress' in data:
                    print(f"  Progress: {data['progress']}")
                
                if status == 'SUCCESS':
                    print("✓ Task completed successfully!")
                    result = data.get('result', [])
                    print(f"  Found {len(result)} matching jobs:")
                    
                    for i, job in enumerate(result[:3], 1):  # Show first 3 jobs
                        print(f"    {i}. {job['title']} at {job['company']}")
                        print(f"       Location: {job['location']}")
                        print(f"       Similarity: {job['similarity_score']:.3f}")
                        print(f"       URL: {job['url']}")
                        print()
                    
                    return True
                
                elif status == 'FAILURE':
                    print(f"✗ Task failed: {data.get('error', 'Unknown error')}")
                    return False
                
                elif status in ['PENDING', 'STARTED']:
                    print("  Task is still processing...")
                    time.sleep(5)  # Wait 5 seconds before checking again
                    continue
                
                else:
                    print(f"  Unknown status: {status}")
                    time.sleep(2)
                    continue
                    
            else:
                print(f"✗ Status check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Status check error: {e}")
            return False
    
    print(f"✗ Task did not complete within {max_wait_time} seconds")
    return False

def test_invalid_file():
    """Test uploading an invalid file type."""
    print("\nTesting invalid file upload...")
    
    try:
        # Create a temporary invalid file
        invalid_content = b"This is not a valid resume file"
        files = {'file': ('invalid.xyz', invalid_content, 'application/octet-stream')}
        response = requests.post(f"{API_BASE_URL}/api/match-jobs", files=files)
        
        if response.status_code == 400:
            print("✓ Invalid file correctly rejected")
            return True
        else:
            print(f"✗ Expected 400 status code, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Invalid file test error: {e}")
        return False

def main():
    """Run all API tests."""
    print("=" * 60)
    print("Resume Job Matcher API - Integration Test")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health_endpoint():
        print("\n❌ API server is not running or not healthy.")
        print("Please start the FastAPI server: python main.py")
        return False
    
    # Test 2: Invalid file upload
    test_invalid_file()
    
    # Test 3: Valid resume upload
    task_id = test_upload_resume()
    if not task_id:
        print("\n❌ Resume upload failed.")
        return False
    
    # Test 4: Task status monitoring
    if not test_task_status(task_id):
        print("\n❌ Task processing failed or timed out.")
        print("Make sure Celery worker is running: celery -A tasks.celery_app worker --loglevel=info")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All API tests passed successfully!")
    print("=" * 60)
    print("\nThe Resume Job Matcher API is working correctly.")
    print("You can now:")
    print("1. Visit http://localhost:8000/docs for interactive API documentation")
    print("2. Upload your own resume files via the API")
    print("3. Monitor tasks and view job matches")
    
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)