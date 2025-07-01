#!/usr/bin/env python3
"""
Debug script to test file upload to the job matching endpoint
"""

import requests
import json
from pathlib import Path

API_BASE_URL = "http://localhost:8000"
ENDPOINT = f"{API_BASE_URL}/api/v1/jobs/match"

def test_file_upload():
    """Test file upload with different approaches"""
    
    # Create a simple test resume content
    test_content = """
John Doe
Software Engineer

Skills:
- Python
- FastAPI
- Machine Learning
- Data Analysis

Experience:
- 3 years as Python Developer
- Built REST APIs with FastAPI
- Worked with ML models
"""
    
    print(f"Testing endpoint: {ENDPOINT}")
    print("=" * 50)
    
    # Test 1: Upload as text file
    print("Test 1: Uploading as text file...")
    try:
        files = {'file': ('resume.txt', test_content, 'text/plain')}
        response = requests.post(ENDPOINT, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success! Task ID: {data.get('task_id')}")
            return data.get('task_id')
        else:
            print(f"✗ Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 2: Upload with explicit multipart/form-data
    print("Test 2: Uploading with explicit content-type...")
    try:
        files = {'file': ('resume.txt', test_content, 'text/plain')}
        headers = {'Accept': 'application/json'}
        response = requests.post(ENDPOINT, files=files, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Success! Task ID: {data.get('task_id')}")
            return data.get('task_id')
        else:
            print(f"✗ Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 3: Check what the server expects
    print("Test 3: Checking API documentation...")
    try:
        docs_response = requests.get(f"{API_BASE_URL}/docs")
        if docs_response.status_code == 200:
            print("✓ API docs are available at http://localhost:8000/docs")
        else:
            print("✗ API docs not available")
            
        # Try to get OpenAPI spec
        openapi_response = requests.get(f"{API_BASE_URL}/openapi.json")
        if openapi_response.status_code == 200:
            openapi_data = openapi_response.json()
            # Look for the jobs/match endpoint
            paths = openapi_data.get('paths', {})
            match_endpoint = paths.get('/api/v1/jobs/match', {})
            post_spec = match_endpoint.get('post', {})
            
            print("Endpoint specification:")
            print(json.dumps(post_spec, indent=2))
        else:
            print("✗ OpenAPI spec not available")
            
    except Exception as e:
        print(f"✗ Error checking docs: {e}")
    
    return None

def test_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health")
        if response.status_code == 200:
            print("✓ API is running and healthy")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        return False

if __name__ == "__main__":
    print("Resume Job Matcher - Upload Debug Tool")
    print("=" * 50)
    
    if not test_health():
        print("\nPlease make sure the API server is running:")
        print("python main.py")
        exit(1)
    
    print()
    task_id = test_file_upload()
    
    if task_id:
        print(f"\n✓ File upload successful! Task ID: {task_id}")
        print("You can check the task status at:")
        print(f"  {API_BASE_URL}/api/v1/tasks/{task_id}/status")
    else:
        print("\n✗ File upload failed. Check the error messages above.")