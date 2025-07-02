#!/usr/bin/env python3
"""
Test the subscription system
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"

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

def register_test_user():
    """Register a test user"""
    print("🔍 Registering test user...")
    
    user_data = {
        "email": "subscription_test@example.com",
        "password": "testpassword123",
        "first_name": "Subscription",
        "last_name": "Tester"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/auth/register", json=user_data)
        
        if response.status_code == 201:
            user = response.json()
            print(f"   ✅ User registered successfully")
            print(f"   📧 Email: {user['email']}")
            print(f"   💳 Initial Subscription: {user['subscription_tier']}")
            return user
        else:
            print(f"   ❌ Registration failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def login_user(email: str, password: str):
    """Login user and get token"""
    print("🔍 Logging in user...")
    
    login_data = {
        "username": email,
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
            return token_data['access_token']
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

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
            print(f"   📅 Next reset: {subscription.get('next_reset_date', 'N/A')}")
            print(f"   ⬆️ Upgrade options: {', '.join(subscription.get('upgrade_options', []))}")
            print(f"   💰 Price info: {subscription.get('price_info', 'N/A')}")
            return subscription
        else:
            print(f"   ❌ Subscription info failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_subscription_upgrade(token: str, tier: str):
    """Test upgrading subscription"""
    print(f"🔍 Testing Subscription Upgrade to {tier}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/subscription/upgrade",
            json=tier,
            headers=headers
        )
        
        if response.status_code == 200:
            subscription = response.json()
            print(f"   ✅ Subscription upgraded successfully")
            print(f"   💳 New tier: {subscription['tier']}")
            print(f"   📊 New monthly limit: {subscription['monthly_limit']}")
            print(f"   📈 Matches used (reset): {subscription['matches_used']}")
            print(f"   🎯 New features: {', '.join(subscription['features'])}")
            return subscription
        else:
            print(f"   ❌ Subscription upgrade failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_job_matching_with_limits(token: str):
    """Test job matching to verify subscription limits"""
    print("🔍 Testing Job Matching with Subscription Limits...")
    
    # Create a test resume file
    test_resume = """
John Doe
Software Engineer

Skills:
- Python
- FastAPI
- Subscription Management
- Payment Processing

Experience:
- 3 years as Python Developer
- Built subscription systems
- Implemented payment gateways
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
            print(f"   ✅ Job matching successful")
            print(f"   🆔 Task ID: {result['task_id']}")
            return True
        elif response.status_code == 402:
            print(f"   ⚠️ Payment required (subscription limit reached)")
            print(f"   📝 Message: {response.text}")
            return True  # This is expected behavior
        else:
            print(f"   ❌ Job matching failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all subscription tests"""
    print("🧪 Subscription System Test Suite")
    print("=" * 50)
    
    # Check if API is running
    if not test_health_check():
        print("\nPlease make sure the API server is running:")
        print("python main.py")
        sys.exit(1)
    
    print()
    
    # Register test user
    user = register_test_user()
    if not user:
        print("❌ Registration failed, stopping tests")
        return
    
    print()
    
    # Login user
    token = login_user("subscription_test@example.com", "testpassword123")
    if not token:
        print("❌ Login failed, stopping tests")
        return
    
    print()
    
    # Test initial subscription info
    subscription = test_subscription_info(token)
    if not subscription:
        print("❌ Subscription info failed")
        return
    
    print()
    
    # Test job matching with free tier
    if not test_job_matching_with_limits(token):
        print("❌ Job matching test failed")
        return
    
    print()
    
    # Test subscription upgrade to Pro
    upgraded_subscription = test_subscription_upgrade(token, "pro")
    if not upgraded_subscription:
        print("❌ Subscription upgrade failed")
        return
    
    print()
    
    # Test subscription info after upgrade
    final_subscription = test_subscription_info(token)
    
    print()
    print("=" * 50)
    print("🎉 Subscription System Tests Complete!")
    print("=" * 50)
    
    if final_subscription:
        print("✅ All tests passed successfully!")
        print("\n📋 Summary:")
        print(f"   • User registration: ✅")
        print(f"   • User login: ✅")
        print(f"   • Subscription info retrieval: ✅")
        print(f"   • Job matching with limits: ✅")
        print(f"   • Subscription upgrade: ✅")
        print(f"   • Final tier: {final_subscription['tier']}")
        
        print(f"\n🎯 Next Steps:")
        print(f"   • Integrate with payment provider (Stripe)")
        print(f"   • Add subscription downgrade functionality")
        print(f"   • Implement billing cycles")
        print(f"   • Add usage analytics")
    else:
        print("❌ Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()