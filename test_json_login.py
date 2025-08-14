#!/usr/bin/env python3
"""
Test the JSON login endpoint
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"

def test_json_login(email, password):
    """Test JSON login endpoint"""
    print("🔍 Testing JSON Login...")
    
    login_data = {
        "username": email,
        "password": password
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/json-login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Login successful!")
            print(f"🔑 Token type: {token_data['token_type']}")
            print(f"🔑 Access token: {token_data['access_token'][:20]}...")
            return token_data['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_form_login(email, password):
    """Test form-based login endpoint"""
    print("\n🔍 Testing Form-Based Login...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/jwt/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Login successful!")
            print(f"🔑 Token type: {token_data['token_type']}")
            print(f"🔑 Access token: {token_data['access_token'][:20]}...")
            return token_data['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_protected_endpoint(token):
    """Test accessing protected endpoint"""
    print("\n🔍 Testing Protected Endpoint...")
    
    if not token:
        print("❌ No token available, skipping test")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/auth/users/me", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Protected endpoint access successful!")
            print(f"👤 User: {user_data['email']}")
            print(f"🆔 ID: {user_data['id']}")
            return True
        else:
            print(f"❌ Protected endpoint access failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health_check():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health")
        if response.status_code == 200:
            print("✅ API is running and healthy")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

if __name__ == "__main__":
    print("🧪 JSON Login Test")
    print("=" * 50)
    
    # Check if API is running
    if not test_health_check():
        print("\nPlease make sure the API server is running:")
        print("python main.py")
        sys.exit(1)
    
    print()
    
    # Get credentials
    if len(sys.argv) >= 3:
        email = sys.argv[1]
        password = sys.argv[2]
    else:
        email = input("Email: ")
        password = input("Password: ")
    
    # Test JSON login
    json_token = test_json_login(email, password)
    
    # Test form login
    form_token = test_form_login(email, password)
    
    # Test protected endpoint with JSON token
    if json_token:
        test_protected_endpoint(json_token)
    
    print("\n=" * 50)
    if json_token and form_token:
        print("✅ Both login methods work!")
        print("✅ You can use either JSON or form data for login")
    elif form_token:
        print("✅ Form login works, but JSON login failed")
        print("❌ Use form data for login")
    elif json_token:
        print("✅ JSON login works, but form login failed")
        print("❌ Use JSON for login")
    else:
        print("❌ Both login methods failed")
        print("❌ Check your credentials and server status")