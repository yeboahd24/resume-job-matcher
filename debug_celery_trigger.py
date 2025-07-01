#!/usr/bin/env python3
"""
Debug script to test Celery task triggering
"""

import sys
import os
import time

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

def test_imports():
    """Test if we can import required modules"""
    print("🔍 Testing imports...")
    
    try:
        from app.core.celery_app import celery_app
        print("✅ Successfully imported celery_app")
    except Exception as e:
        print(f"❌ Failed to import celery_app: {e}")
        return False
    
    try:
        from app.services.tasks import process_resume_and_match_jobs, health_check_task
        print("✅ Successfully imported tasks")
    except Exception as e:
        print(f"❌ Failed to import tasks: {e}")
        return False
    
    return True

def test_celery_config():
    """Test Celery configuration"""
    print("\n🔍 Testing Celery configuration...")
    
    try:
        from app.core.celery_app import celery_app
        
        print(f"   Broker URL: {celery_app.conf.broker_url}")
        print(f"   Result Backend: {celery_app.conf.result_backend}")
        print(f"   Task Serializer: {celery_app.conf.task_serializer}")
        print(f"   Include: {celery_app.conf.include}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to check Celery config: {e}")
        return False

def test_task_registration():
    """Test if tasks are registered"""
    print("\n🔍 Testing task registration...")
    
    try:
        from app.core.celery_app import celery_app
        
        registered_tasks = list(celery_app.tasks.keys())
        print(f"   Total registered tasks: {len(registered_tasks)}")
        
        expected_tasks = [
            'app.services.tasks.process_resume_and_match_jobs',
            'app.services.tasks.health_check_task'
        ]
        
        for task_name in expected_tasks:
            if task_name in registered_tasks:
                print(f"   ✅ {task_name}")
            else:
                print(f"   ❌ {task_name} - NOT REGISTERED")
        
        print(f"\n   Custom tasks found:")
        for task in registered_tasks:
            if task.startswith('app.'):
                print(f"      - {task}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to check task registration: {e}")
        return False

def test_redis_connection():
    """Test Redis connection"""
    print("\n🔍 Testing Redis connection...")
    
    try:
        import redis
        
        # Try to connect to Redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def test_task_creation():
    """Test creating a task without executing it"""
    print("\n🔍 Testing task creation...")
    
    try:
        from app.services.tasks import health_check_task
        
        # Create task signature without executing
        task_sig = health_check_task.s()
        print(f"✅ Task signature created: {task_sig}")
        
        # Try to delay the task (this should work if Celery is properly configured)
        result = health_check_task.delay()
        print(f"✅ Task delayed successfully: {result.id}")
        print(f"   Task state: {result.state}")
        
        return True
    except Exception as e:
        print(f"❌ Task creation failed: {e}")
        return False

def test_worker_status():
    """Test if workers are available"""
    print("\n🔍 Testing worker status...")
    
    try:
        from app.core.celery_app import celery_app
        
        # Check for active workers
        inspector = celery_app.control.inspect()
        active_workers = inspector.active()
        
        if active_workers:
            print(f"✅ Found {len(active_workers)} active workers:")
            for worker in active_workers.keys():
                print(f"   - {worker}")
        else:
            print("❌ No active workers found")
            print("   Make sure Celery worker is running:")
            print("   celery -A app.core.celery_app.celery_app worker --loglevel=info")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Worker status check failed: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    print("🧪 Celery Task Trigger Diagnostic")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("Celery Config", test_celery_config),
        ("Task Registration", test_task_registration),
        ("Redis Connection", test_redis_connection),
        ("Task Creation", test_task_creation),
        ("Worker Status", test_worker_status),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*15} {test_name} {'='*15}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*40}")
    print("📊 Diagnostic Summary:")
    print(f"{'='*40}")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed < len(results):
        print(f"\n💡 Common solutions:")
        print(f"   1. Install dependencies: pip install -r requirements.txt")
        print(f"   2. Start Redis: redis-server --daemonize yes")
        print(f"   3. Start Celery worker: celery -A app.core.celery_app.celery_app worker --loglevel=info")
        print(f"   4. Check .env file for correct Redis configuration")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)