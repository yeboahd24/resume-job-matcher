#!/usr/bin/env python3
"""
Test different ways of uploading files to identify the issue
"""

import requests
import json
from io import BytesIO

API_BASE_URL = "http://localhost:8000"
ENDPOINT = f"{API_BASE_URL}/api/v1/jobs/match"

def test_various_upload_methods():
    """Test different upload methods that might cause the error"""
    
    test_content = "John Doe\nSoftware Engineer\nPython, FastAPI, Machine Learning"
    
    print("Testing various upload methods...")
    print("=" * 60)
    
    # Test 1: Correct method (should work)
    print("Test 1: Correct multipart/form-data upload")
    try:
        files = {'file': ('resume.txt', test_content, 'text/plain')}
        response = requests.post(ENDPOINT, files=files)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}...")
        print()
    except Exception as e:
        print(f"  Error: {e}")
        print()
    
    # Test 2: Wrong field name (should fail)
    print("Test 2: Wrong field name (should fail)")
    try:
        files = {'resume': ('resume.txt', test_content, 'text/plain')}
        response = requests.post(ENDPOINT, files=files)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}...")
        print()
    except Exception as e:
        print(f"  Error: {e}")
        print()
    
    # Test 3: Empty file (should fail)
    print("Test 3: Empty file (should fail)")
    try:
        files = {'file': ('resume.txt', '', 'text/plain')}
        response = requests.post(ENDPOINT, files=files)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}...")
        print()
    except Exception as e:
        print(f"  Error: {e}")
        print()
    
    # Test 4: No file at all (should fail with the error you're seeing)
    print("Test 4: No file field (should reproduce your error)")
    try:
        response = requests.post(ENDPOINT, data={'other_field': 'value'})
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}...")
        print()
    except Exception as e:
        print(f"  Error: {e}")
        print()
    
    # Test 5: JSON instead of multipart (should fail)
    print("Test 5: JSON instead of multipart (should fail)")
    try:
        headers = {'Content-Type': 'application/json'}
        data = {'file': 'some content'}
        response = requests.post(ENDPOINT, json=data, headers=headers)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}...")
        print()
    except Exception as e:
        print(f"  Error: {e}")
        print()
    
    # Test 6: Using curl-like approach
    print("Test 6: Simulating curl upload")
    try:
        files = {'file': ('resume.txt', BytesIO(test_content.encode()), 'text/plain')}
        response = requests.post(ENDPOINT, files=files)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}...")
        print()
    except Exception as e:
        print(f"  Error: {e}")
        print()

def show_curl_examples():
    """Show correct curl examples"""
    print("Correct ways to upload files:")
    print("=" * 60)
    print("1. Using curl:")
    print(f"   curl -X POST {ENDPOINT} -F 'file=@resume.txt'")
    print()
    print("2. Using curl with explicit content type:")
    print(f"   curl -X POST {ENDPOINT} -F 'file=@resume.txt;type=text/plain'")
    print()
    print("3. Using Python requests (correct):")
    print("   files = {'file': ('resume.txt', file_content, 'text/plain')}")
    print(f"   requests.post('{ENDPOINT}', files=files)")
    print()

if __name__ == "__main__":
    test_various_upload_methods()
    show_curl_examples()