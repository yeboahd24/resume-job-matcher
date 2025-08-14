#!/usr/bin/env python3
"""
Test the PDF report generation system
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

def register_and_login():
    """Register a test user and login"""
    print("🔍 Setting up test user...")
    
    # Register user
    user_data = {
        "email": "report_test@example.com",
        "password": "testpassword123",
        "first_name": "Report",
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
        "username": "report_test@example.com",
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

def upgrade_to_pro(token):
    """Upgrade user to Pro subscription for PDF access"""
    print("🔍 Upgrading to Pro subscription...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/subscription/upgrade",
            json="pro",
            headers=headers
        )
        
        if response.status_code == 200:
            subscription = response.json()
            print(f"   ✅ Upgraded to {subscription['tier']}")
            return True
        else:
            print(f"   ❌ Upgrade failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Upgrade error: {e}")
        return False

def submit_job_matching_task(token):
    """Submit a job matching task to get results for report generation"""
    print("🔍 Submitting job matching task...")
    
    # Create a test resume
    test_resume = """
John Doe
Senior Software Engineer

SKILLS:
- Python (5 years)
- FastAPI and Django
- Machine Learning and Data Science
- AWS and Docker
- PostgreSQL and Redis
- React and JavaScript
- Git and CI/CD

EXPERIENCE:
Senior Software Engineer at TechCorp (2020-2023)
- Built scalable web applications using Python and FastAPI
- Implemented machine learning models for recommendation systems
- Led a team of 5 developers
- Deployed applications on AWS using Docker and Kubernetes

Software Engineer at StartupXYZ (2018-2020)
- Developed REST APIs and microservices
- Worked with React frontend and Python backend
- Implemented automated testing and CI/CD pipelines

EDUCATION:
Bachelor of Science in Computer Science
University of Technology (2014-2018)

CERTIFICATIONS:
- AWS Certified Solutions Architect
- Google Cloud Professional Data Engineer
"""
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        files = {
            'file': ('senior_engineer_resume.txt', test_resume, 'text/plain')
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/jobs/match",
            files=files,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result['task_id']
            print(f"   ✅ Job matching task submitted: {task_id}")
            return task_id
        else:
            print(f"   ❌ Job matching failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Job matching error: {e}")
        return None

def wait_for_task_completion(task_id, token, max_wait=60):
    """Wait for task to complete"""
    print(f"🔍 Waiting for task {task_id} to complete...")
    
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
                    print("   ✅ Task completed successfully")
                    return True
                elif status in ["FAILURE", "REVOKED"]:
                    print(f"   ❌ Task failed with status: {status}")
                    return False
                
                # Wait before checking again
                time.sleep(5)
            else:
                print(f"   ⚠️ Status check failed: {response.status_code}")
                time.sleep(5)
                
        except Exception as e:
            print(f"   ⚠️ Status check error: {e}")
            time.sleep(5)
    
    print("   ⏰ Task did not complete within timeout")
    return False

def test_report_formats(token):
    """Test getting available report formats"""
    print("🔍 Testing available report formats...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/reports/formats",
            headers=headers
        )
        
        if response.status_code == 200:
            formats = response.json()
            print("   ✅ Available formats retrieved")
            print(f"   📋 Formats: {formats['available_formats']}")
            print(f"   🎨 Themes: {formats['available_themes']}")
            print(f"   📄 PDF Available: {formats['pdf_available']}")
            return formats
        else:
            print(f"   ❌ Failed to get formats: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error getting formats: {e}")
        return None

def test_report_templates(token):
    """Test getting report templates"""
    print("🔍 Testing report templates...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/reports/templates",
            headers=headers
        )
        
        if response.status_code == 200:
            templates = response.json()
            print("   ✅ Templates retrieved")
            for template_id, template_info in templates['templates'].items():
                print(f"   🎨 {template_info['name']}: {template_info['description']}")
            return templates
        else:
            print(f"   ❌ Failed to get templates: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error getting templates: {e}")
        return None

def generate_pdf_report(task_id, token):
    """Generate a PDF report"""
    print("🔍 Generating PDF report...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    report_request = {
        "task_id": task_id,
        "format": "pdf",
        "theme": "professional",
        "sections": [
            "summary",
            "matched_jobs",
            "skills_analysis",
            "recommendations",
            "statistics"
        ],
        "include_charts": True,
        "custom_title": "My Job Matching Report"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/reports/generate",
            json=report_request,
            headers=headers
        )
        
        if response.status_code == 200:
            report_response = response.json()
            print("   ✅ PDF report generated successfully")
            print(f"   📄 Report ID: {report_response['report_id']}")
            print(f"   📊 File size: {report_response['file_size_bytes']} bytes")
            print(f"   🔗 Download URL: {report_response['download_url']}")
            print(f"   ⏰ Expires: {report_response['expires_at']}")
            return report_response
        else:
            print(f"   ❌ PDF generation failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ PDF generation error: {e}")
        return None

def generate_html_report(task_id, token):
    """Generate an HTML report"""
    print("🔍 Generating HTML report...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    report_request = {
        "task_id": task_id,
        "format": "html",
        "theme": "modern",
        "sections": [
            "summary",
            "matched_jobs",
            "skills_analysis",
            "recommendations"
        ],
        "custom_title": "My HTML Job Report"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/reports/generate",
            json=report_request,
            headers=headers
        )
        
        if response.status_code == 200:
            report_response = response.json()
            print("   ✅ HTML report generated successfully")
            print(f"   📄 Report ID: {report_response['report_id']}")
            print(f"   📊 File size: {report_response['file_size_bytes']} bytes")
            return report_response
        else:
            print(f"   ❌ HTML generation failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ HTML generation error: {e}")
        return None

def download_report(report_id, token, filename):
    """Download a generated report"""
    print(f"🔍 Downloading report {report_id}...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/reports/{report_id}/download",
            headers=headers
        )
        
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"   ✅ Report downloaded as {filename}")
            print(f"   📊 File size: {len(response.content)} bytes")
            return True
        else:
            print(f"   ❌ Download failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Download error: {e}")
        return False

def main():
    """Run all PDF report tests"""
    print("🧪 PDF Report Generation Test Suite")
    print("=" * 50)
    
    # Check if API is running
    if not test_health_check():
        print("\nPlease make sure the API server is running:")
        print("python main.py")
        sys.exit(1)
    
    print()
    
    # Setup user and login
    token = register_and_login()
    if not token:
        print("❌ Failed to setup user, stopping tests")
        return
    
    print()
    
    # Upgrade to Pro for PDF access
    if not upgrade_to_pro(token):
        print("❌ Failed to upgrade to Pro, stopping tests")
        return
    
    print()
    
    # Test report formats
    formats = test_report_formats(token)
    if not formats:
        print("❌ Failed to get report formats")
        return
    
    print()
    
    # Test report templates
    templates = test_report_templates(token)
    if not templates:
        print("❌ Failed to get report templates")
        return
    
    print()
    
    # Submit job matching task
    task_id = submit_job_matching_task(token)
    if not task_id:
        print("❌ Failed to submit job matching task")
        return
    
    print()
    
    # Wait for task completion
    if not wait_for_task_completion(task_id, token):
        print("❌ Task did not complete successfully")
        return
    
    print()
    
    # Generate PDF report
    pdf_report = generate_pdf_report(task_id, token)
    if not pdf_report:
        print("❌ Failed to generate PDF report")
        return
    
    print()
    
    # Generate HTML report
    html_report = generate_html_report(task_id, token)
    if not html_report:
        print("❌ Failed to generate HTML report")
        return
    
    print()
    
    # Download reports
    pdf_downloaded = download_report(pdf_report['report_id'], token, "test_report.pdf")
    html_downloaded = download_report(html_report['report_id'], token, "test_report.html")
    
    print()
    print("=" * 50)
    print("🎉 PDF Report Generation Tests Complete!")
    print("=" * 50)
    
    if pdf_downloaded and html_downloaded:
        print("✅ All tests passed successfully!")
        print("\n📋 Summary:")
        print(f"   • User setup and Pro upgrade: ✅")
        print(f"   • Report formats and templates: ✅")
        print(f"   • Job matching task: ✅")
        print(f"   • PDF report generation: ✅")
        print(f"   • HTML report generation: ✅")
        print(f"   • Report downloads: ✅")
        
        print(f"\n📄 Generated Files:")
        print(f"   • test_report.pdf")
        print(f"   • test_report.html")
        
        print(f"\n🎯 Next Steps:")
        print(f"   • Open the generated PDF to review formatting")
        print(f"   • Test different themes and sections")
        print(f"   • Integrate with frontend for user downloads")
        print(f"   • Add more advanced charts and visualizations")
    else:
        print("❌ Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()