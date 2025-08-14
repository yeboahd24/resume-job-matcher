#!/usr/bin/env python3
"""
Test the authentication system
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"

def test_user_registration():
    """Test user registration"""
    print("🔍 Testing User Registration...")
    
    user_data = {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/auth/register", json=user_data)
        
        if response.status_code == 201:
            user = response.json()
            print(f"   ✅ User registered successfully")
            print(f"   📧 Email: {user['email']}")
            print(f"   🆔 ID: {user['id']}")
            print(f"   💳 Subscription: {user['subscription_tier']}")
            return user
        else:
            print(f"   ❌ Registration failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_user_login(email: str, password: str):
    """Test user login"""
    print("🔍 Testing User Login...")
    
    login_data = {
        "username": email,  # FastAPI Users uses 'username' field
        "password": password
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/jwt/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"   ✅ Login successful")
            print(f"   🔑 Token type: {token_data['token_type']}")
            print(f"   ⏰ Access token: {token_data['access_token'][:20]}...")
            return token_data['access_token']
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_protected_endpoint(token: str):
    """Test accessing protected endpoint"""
    print("🔍 Testing Protected Endpoint...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test getting user profile
        response = requests.get(f"{API_BASE_URL}/api/v1/auth/me/profile", headers=headers)
        
        if response.status_code == 200:
            profile = response.json()
            print(f"   ✅ Profile access successful")
            print(f"   👤 User ID: {profile['user_id']}")
            print(f"   📅 Created: {profile['created_at']}")
            return True
        else:
            print(f"   ❌ Profile access failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_subscription_info(token: str):
    """Test getting subscription information"""
    print("🔍 Testing Subscription Info...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/auth/me/subscription", headers=headers)
        
        if response.status_code == 200:
            subscription = response.json()
            print(f"   ✅ Subscription info retrieved")
            print(f"   💳 Tier: {subscription['tier']}")
            print(f"   📊 Monthly limit: {subscription['monthly_limit']}")
            print(f"   📈 Matches used: {subscription['matches_used']}")
            print(f"   📉 Matches remaining: {subscription['matches_remaining']}")
            print(f"   🎯 Features: {', '.join(subscription['features'])}")
            return subscription
        else:
            print(f"   ❌ Subscription info failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_authenticated_job_match(token: str):
    """Test job matching with authentication"""
    print("🔍 Testing Authenticated Job Matching...")
    
    # Create a test resume file
    test_resume = """
John Doe
Software Engineer

Skills:
- Python
- FastAPI
- Machine Learning
- Authentication Systems

Experience:
- 3 years as Python Developer
- Built REST APIs with FastAPI
- Implemented user authentication
"""
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        files = {
            'file': ('test_resume.txt', test_resume, 'text/plain')
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/jobs/match",
            files=files,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Authenticated job matching successful")
            print(f"   🆔 Task ID: {result['task_id']}")
            print(f"   📊 Status: {result['status']}")
            print(f"   💬 Message: {result['message']}")
            return result['task_id']
        else:
            print(f"   ❌ Job matching failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_job_match_history(token: str):
    """Test getting job match history"""
    print("🔍 Testing Job Match History...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/auth/me/job-matches", headers=headers)
        
        if response.status_code == 200:
            matches = response.json()
            print(f"   ✅ Job match history retrieved")
            print(f"   📊 Total matches: {len(matches)}")
            
            for i, match in enumerate(matches, 1):
                print(f"   {i}. {match['resume_filename']} - {match['jobs_found']} jobs found")
            
            return matches
        else:
            print(f"   ❌ Job match history failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

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

def main():
    """Run all authentication tests"""
    print("🧪 Authentication System Test Suite")
    print("=" * 50)
    
    # Check if API is running
    if not test_health_check():
        print("\nPlease make sure the API server is running:")
        print("python main.py")
        sys.exit(1)
    
    print()
    
    # Test user registration
    user = test_user_registration()
    if not user:
        print("❌ Registration failed, stopping tests")
        return
    
    print()
    
    # Test user login
    token = test_user_login("testuser@example.com", "testpassword123")
    if not token:
        print("❌ Login failed, stopping tests")
        return
    
    print()
    
    # Test protected endpoint
    if not test_protected_endpoint(token):
        print("❌ Protected endpoint access failed")
        return
    
    print()
    
    # Test subscription info
    subscription = test_subscription_info(token)
    if not subscription:
        print("❌ Subscription info failed")
        return
    
    print()
    
    # Test authenticated job matching
    task_id = test_authenticated_job_match(token)
    if not task_id:
        print("❌ Authenticated job matching failed")
        return
    
    print()
    
    # Wait a moment for the job to be recorded
    import time
    time.sleep(2)
    
    # Test job match history
    matches = test_job_match_history(token)
    
    print()
    print("=" * 50)
    print("🎉 Authentication System Tests Complete!")
    print("=" * 50)
    
    if matches is not None:
        print("✅ All tests passed successfully!")
        print("\n📋 Summary:")
        print(f"   • User registration: ✅")
        print(f"   • User login: ✅")
        print(f"   • Protected endpoints: ✅")
        print(f"   • Subscription management: ✅")
        print(f"   • Authenticated job matching: ✅")
        print(f"   • Job match history: ✅")
        
        print(f"\n🎯 Next Steps:")
        print(f"   • Visit http://localhost:8000/docs to explore the API")
        print(f"   • Test the web interface with authentication")
        print(f"   • Implement frontend login/registration")
    else:
        print("❌ Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()