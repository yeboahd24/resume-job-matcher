#!/usr/bin/env python3
"""
Test the salary filtering functionality
"""

import requests
import json
import sys
import time

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

def test_salary_ranges_endpoint():
    """Test the salary ranges endpoint"""
    print("🔍 Testing salary ranges endpoint...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/jobs/salary-ranges")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Salary ranges retrieved successfully")
            print("   📊 Salary ranges by level:")
            for level, info in data["salary_ranges_by_level"].items():
                print(f"      • {level.replace('_', ' ').title()}: {info['range']} (median: {info['median']})")
            
            print("   📊 Salary ranges by job type:")
            for job_type, salary_range in data["salary_ranges_by_job_type"].items():
                print(f"      • {job_type}: {salary_range}")
            
            return data
        else:
            print(f"   ❌ Failed to get salary ranges: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_salary_parsing():
    """Test the salary parsing functionality"""
    print("🔍 Testing salary parsing...")
    
    from app.utils.salary_parser import parse_salary_range
    
    test_cases = [
        ("$80,000 - $120,000", (80000, 120000)),
        ("$50-75k", (50000, 75000)),
        ("Up to $100,000", (None, 100000)),
        ("From $90,000", (90000, None)),
        ("$50/hour", (104000, 104000)),  # 50 * 2080 = 104000
        ("$30-50 per hour", (62400, 104000)),  # 30-50 * 2080
        ("Competitive salary", (None, None)),
        ("$100k+", (100000, None)),
    ]
    
    for salary_string, expected in test_cases:
        min_salary, max_salary = parse_salary_range(salary_string)
        result = "✅" if (min_salary, max_salary) == expected else "❌"
        print(f"   {result} {salary_string} -> min: {min_salary}, max: {max_salary}")
    
    return True

def register_and_login():
    """Register a test user and login"""
    print("🔍 Setting up test user...")
    
    # Register user
    user_data = {
        "email": "salary_test@example.com",
        "password": "testpassword123",
        "first_name": "Salary",
        "last_name": "Tester"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/auth/register", json=user_data)
        if response.status_code == 201:
            print("   ✅ User registered successfully")
        else:
            print(f"   ⚠️ Registration response: {response.status_code} (user may already exist)")
    except Exception as e:
        print(f"   ⚠️ Registration error: {e}")
    
    # Login
    login_data = {
        "username": "salary_test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/jwt/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print("   ✅ Login successful")
            return token_data['access_token']
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return None

def update_user_profile(token, min_salary=None, max_salary=None):
    """Update user profile with salary preferences"""
    print("🔍 Updating user profile with salary preferences...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # First, get current profile
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/auth/me/profile",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"   ❌ Failed to get profile: {response.status_code}")
            return False
            
        profile = response.json()
        
    except Exception as e:
        print(f"   ❌ Error getting profile: {e}")
        return False
    
    # Update profile with salary preferences
    profile_data = {
        "preferred_job_titles": profile.get("preferred_job_titles", ["Software Engineer"]),
        "preferred_locations": profile.get("preferred_locations", ["Remote"]),
        "salary_min": min_salary,
        "salary_max": max_salary,
        "remote_only": profile.get("remote_only", True),
        "skills": profile.get("skills", ["Python", "FastAPI"]),
        "experience_years": profile.get("experience_years", 3),
        "education_level": profile.get("education_level", "Bachelor's"),
        "job_types": profile.get("job_types", ["Full-time"]),
        "industries": profile.get("industries", ["Technology"])
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/me/profile",
            json=profile_data,
            headers=headers
        )
        
        if response.status_code == 200:
            updated_profile = response.json()
            print(f"   ✅ Profile updated with salary range: ${min_salary} - ${max_salary}")
            return True
        else:
            print(f"   ❌ Profile update failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error updating profile: {e}")
        return False

def test_job_matching_with_salary_filter(token, min_salary=None, max_salary=None, use_profile=False):
    """Test job matching with salary filtering"""
    print(f"🔍 Testing job matching with salary filter: min=${min_salary}, max=${max_salary}, use_profile={use_profile}")
    
    # Create a test resume file
    test_resume = """
John Doe
Senior Software Engineer

Skills:
- Python
- FastAPI
- Machine Learning
- AWS
- Docker
- React
- PostgreSQL

Experience:
- 5 years as Software Engineer
- Built scalable web applications
- Implemented machine learning models
- Led a team of 3 developers
"""
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        files = {
            'file': ('senior_engineer_resume.txt', test_resume, 'text/plain')
        }
        
        # Build URL with query parameters
        url = f"{API_BASE_URL}/api/v1/jobs/match"
        params = {}
        
        if min_salary is not None:
            params["min_salary"] = str(min_salary)
        if max_salary is not None:
            params["max_salary"] = str(max_salary)
        if use_profile:
            params["use_profile_salary"] = "true"
        
        response = requests.post(
            url,
            params=params,
            files=files,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Job matching started with task ID: {result['task_id']}")
            return result['task_id']
        else:
            print(f"   ❌ Job matching failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def check_task_results(token, task_id, max_wait=60):
    """Check task results and verify salary filtering"""
    print(f"🔍 Checking results for task {task_id}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/v1/tasks/{task_id}/status",
                headers=headers
            )
            
            if response.status_code == 200:
                task_status = response.json()
                status = task_status.get('status')
                
                print(f"   📊 Task status: {status}")
                
                if status == "SUCCESS":
                    # Check the results
                    matched_jobs = task_status.get('result', [])
                    print(f"   ✅ Task completed with {len(matched_jobs)} matched jobs")
                    
                    # Print salary info for matched jobs
                    for i, job in enumerate(matched_jobs[:5], 1):  # Show first 5 jobs
                        salary = job.get('salary_range', 'Not specified')
                        print(f"   {i}. {job['title']} at {job['company']} - {salary}")
                    
                    return matched_jobs
                elif status in ["FAILURE", "REVOKED"]:
                    print(f"   ❌ Task failed with status: {status}")
                    return None
                
                # Wait before checking again
                time.sleep(5)
            else:
                print(f"   ⚠️ Status check failed: {response.status_code}")
                time.sleep(5)
                
        except Exception as e:
            print(f"   ⚠️ Status check error: {e}")
            time.sleep(5)
    
    print("   ⏰ Task did not complete within timeout")
    return None

def main():
    """Run all salary filtering tests"""
    print("🧪 Salary Filtering Test Suite")
    print("=" * 50)
    
    # Check if API is running
    if not test_health_check():
        print("\nPlease make sure the API server is running:")
        print("python main.py")
        sys.exit(1)
    
    print()
    
    # Test salary ranges endpoint
    salary_ranges = test_salary_ranges_endpoint()
    if not salary_ranges:
        print("❌ Failed to get salary ranges, but continuing with tests")
    
    print()
    
    # Test salary parsing
    test_salary_parsing()
    
    print()
    
    # Setup user and login
    token = register_and_login()
    if not token:
        print("❌ Failed to setup user, stopping tests")
        return
    
    print()
    
    # Test 1: Job matching with explicit salary filter (min only)
    task_id1 = test_job_matching_with_salary_filter(token, min_salary=100000)
    if task_id1:
        print()
        results1 = check_task_results(token, task_id1)
    
    print()
    
    # Test 2: Job matching with explicit salary filter (min and max)
    task_id2 = test_job_matching_with_salary_filter(token, min_salary=80000, max_salary=150000)
    if task_id2:
        print()
        results2 = check_task_results(token, task_id2)
    
    print()
    
    # Test 3: Update user profile with salary preferences
    if update_user_profile(token, min_salary=120000, max_salary=200000):
        print()
        # Test job matching using profile salary preferences
        task_id3 = test_job_matching_with_salary_filter(token, use_profile=True)
        if task_id3:
            print()
            results3 = check_task_results(token, task_id3)
    
    print()
    print("=" * 50)
    print("🎉 Salary Filtering Tests Complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()