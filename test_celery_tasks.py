#!/usr/bin/env python3
"""
Test script to diagnose Celery task issues
"""

import sys
import time
import logging
from app.core.celery_app import celery_app
from app.services.tasks import process_resume_and_match_jobs, health_check_task

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_celery_connection():
    """Test basic Celery connection"""
    print("🔍 Testing Celery connection...")
    
    try:
        # Test broker connection
        inspector = celery_app.control.inspect()
        active_queues = inspector.active_queues()
        
        if active_queues:
            print("✅ Celery broker connection successful")
            print(f"   Active workers: {list(active_queues.keys())}")
            for worker, queues in active_queues.items():
                print(f"   Worker {worker}: {len(queues)} queues")
        else:
            print("❌ No active Celery workers found")
            return False
            
    except Exception as e:
        print(f"❌ Celery connection failed: {e}")
        return False
    
    return True

def test_registered_tasks():
    """Test if tasks are properly registered"""
    print("\n🔍 Checking registered tasks...")
    
    registered_tasks = list(celery_app.tasks.keys())
    print(f"   Total registered tasks: {len(registered_tasks)}")
    
    expected_tasks = [
        'app.services.tasks.process_resume_and_match_jobs',
        'app.services.tasks.health_check_task',
        'app.services.tasks.cleanup_old_results'
    ]
    
    for task_name in expected_tasks:
        if task_name in registered_tasks:
            print(f"   ✅ {task_name}")
        else:
            print(f"   ❌ {task_name} - NOT FOUND")
    
    print(f"\n   All registered tasks:")
    for task in sorted(registered_tasks):
        if not task.startswith('celery.'):
            print(f"      - {task}")
    
    return all(task in registered_tasks for task in expected_tasks)

def test_health_check_task():
    """Test the simple health check task"""
    print("\n🔍 Testing health check task...")
    
    try:
        # Send task
        result = health_check_task.delay()
        print(f"   Task ID: {result.id}")
        print(f"   Task state: {result.state}")
        
        # Wait for result
        print("   Waiting for task to complete...")
        task_result = result.get(timeout=30)
        
        print(f"   ✅ Health check task completed successfully")
        print(f"   Result: {task_result}")
        return True
        
    except Exception as e:
        print(f"   ❌ Health check task failed: {e}")
        return False

def test_resume_processing_task():
    """Test the resume processing task with sample data"""
    print("\n🔍 Testing resume processing task...")
    
    # Sample resume content
    sample_resume = """
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
    
    try:
        # Send task
        result = process_resume_and_match_jobs.delay(
            file_content=sample_resume.encode('utf-8'),
            filename="test_resume.txt",
            content_type="text/plain"
        )
        
        print(f"   Task ID: {result.id}")
        print(f"   Task state: {result.state}")
        
        # Monitor task progress
        print("   Monitoring task progress...")
        timeout = 60  # 60 seconds timeout
        start_time = time.time()
        
        while not result.ready() and (time.time() - start_time) < timeout:
            print(f"   Current state: {result.state}")
            if hasattr(result, 'info') and result.info:
                if isinstance(result.info, dict) and 'progress' in result.info:
                    print(f"   Progress: {result.info['progress']}")
            time.sleep(2)
        
        if result.ready():
            if result.successful():
                task_result = result.get()
                print(f"   ✅ Resume processing task completed successfully")
                print(f"   Found {len(task_result.get('matched_jobs', []))} matched jobs")
                print(f"   Processing time: {task_result.get('processing_time_seconds', 0):.2f} seconds")
                return True
            else:
                print(f"   ❌ Resume processing task failed: {result.info}")
                return False
        else:
            print(f"   ❌ Resume processing task timed out after {timeout} seconds")
            return False
            
    except Exception as e:
        print(f"   ❌ Resume processing task failed: {e}")
        return False

def test_task_routing():
    """Test task routing and queue configuration"""
    print("\n🔍 Testing task routing...")
    
    try:
        inspector = celery_app.control.inspect()
        
        # Check active queues
        active_queues = inspector.active_queues()
        if active_queues:
            print("   Active queues:")
            for worker, queues in active_queues.items():
                for queue in queues:
                    print(f"      {worker}: {queue['name']}")
        
        # Check routing
        routes = celery_app.conf.task_routes
        print(f"   Task routes: {routes}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Task routing test failed: {e}")
        return False

def main():
    """Run all Celery diagnostic tests"""
    print("🧪 Celery Task Diagnostic Tool")
    print("=" * 50)
    
    tests = [
        ("Celery Connection", test_celery_connection),
        ("Registered Tasks", test_registered_tasks),
        ("Task Routing", test_task_routing),
        ("Health Check Task", test_health_check_task),
        ("Resume Processing Task", test_resume_processing_task),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 Test Summary:")
    print(f"{'='*50}")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Celery is working correctly.")
        return True
    else:
        print(f"\n❌ {len(results) - passed} test(s) failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)