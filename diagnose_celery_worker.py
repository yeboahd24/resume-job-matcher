#!/usr/bin/env python3
"""
Comprehensive Celery worker diagnostic
"""

import sys
import time
import json
from datetime import datetime

def test_celery_worker_status():
    """Test if Celery worker is running and accessible"""
    print("🔍 Testing Celery Worker Status")
    print("=" * 40)
    
    try:
        from app.core.celery_app import celery_app
        
        # Get worker stats
        inspector = celery_app.control.inspect()
        
        print("📊 Worker Information:")
        
        # Check active workers
        active = inspector.active()
        if active:
            print(f"   ✅ Active workers: {len(active)}")
            for worker_name, tasks in active.items():
                print(f"      - {worker_name}: {len(tasks)} active tasks")
        else:
            print("   ❌ No active workers found")
            return False
        
        # Check registered tasks
        registered = inspector.registered()
        if registered:
            print(f"   📋 Registered tasks per worker:")
            for worker_name, tasks in registered.items():
                print(f"      - {worker_name}: {len(tasks)} registered tasks")
                for task in tasks:
                    if task.startswith('app.'):
                        print(f"         • {task}")
        else:
            print("   ❌ No registered tasks found")
        
        # Check worker stats
        stats = inspector.stats()
        if stats:
            print(f"   📈 Worker statistics:")
            for worker_name, worker_stats in stats.items():
                print(f"      - {worker_name}:")
                print(f"         • Total tasks: {worker_stats.get('total', {})}")
                print(f"         • Pool: {worker_stats.get('pool', {})}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to get worker status: {e}")
        return False

def test_task_in_queue():
    """Check if tasks are in the queue"""
    print("\n🔍 Testing Task Queue")
    print("=" * 30)
    
    try:
        import redis
        
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        
        # Check queue length
        queue_length = r.llen('celery')
        print(f"   📦 Tasks in 'celery' queue: {queue_length}")
        
        if queue_length > 0:
            print("   📋 Tasks in queue:")
            tasks = r.lrange('celery', 0, -1)
            for i, task in enumerate(tasks):
                try:
                    task_data = json.loads(task)
                    task_id = task_data.get('id', 'unknown')
                    task_name = task_data.get('task', 'unknown')
                    print(f"      {i+1}. ID: {task_id}")
                    print(f"         Task: {task_name}")
                except:
                    print(f"      {i+1}. Raw: {task[:100]}...")
        
        # Check other common queue names
        for queue_name in ['default', 'celery:1', 'celery:2']:
            length = r.llen(queue_name)
            if length > 0:
                print(f"   📦 Tasks in '{queue_name}' queue: {length}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to check queue: {e}")
        return False

def test_task_result_backend():
    """Check task results in Redis"""
    print("\n🔍 Testing Task Results")
    print("=" * 30)
    
    try:
        import redis
        
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        
        # Look for task results
        task_keys = r.keys('celery-task-meta-*')
        print(f"   📊 Task results in Redis: {len(task_keys)}")
        
        if task_keys:
            print("   📋 Recent task results:")
            for key in task_keys[-5:]:  # Show last 5
                try:
                    result = r.get(key)
                    if result:
                        result_data = json.loads(result)
                        task_id = key.decode().replace('celery-task-meta-', '')
                        status = result_data.get('status', 'unknown')
                        print(f"      • {task_id}: {status}")
                except:
                    pass
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to check results: {e}")
        return False

def test_specific_task():
    """Test the specific task that's failing"""
    print("\n🔍 Testing Specific Task")
    print("=" * 30)
    
    try:
        from app.services.tasks import process_resume_and_match_jobs
        
        # Create a simple test task
        sample_content = "John Doe\nSoftware Engineer\nPython, FastAPI"
        
        print("   🚀 Creating test task...")
        result = process_resume_and_match_jobs.delay(
            file_content=sample_content.encode('utf-8'),
            filename="test.txt",
            content_type="text/plain"
        )
        
        print(f"   📋 Task ID: {result.id}")
        print(f"   📊 Initial state: {result.state}")
        
        # Wait and monitor
        print("   ⏳ Monitoring task for 30 seconds...")
        for i in range(30):
            state = result.state
            print(f"   [{i+1:2d}s] State: {state}")
            
            if state == 'SUCCESS':
                task_result = result.get()
                print(f"   ✅ Task completed successfully!")
                print(f"   📊 Result: {len(task_result.get('matched_jobs', []))} jobs found")
                return True
            elif state == 'FAILURE':
                print(f"   ❌ Task failed: {result.info}")
                return False
            elif state in ['PENDING', 'STARTED']:
                if hasattr(result, 'info') and result.info:
                    if isinstance(result.info, dict):
                        progress = result.info.get('progress', '')
                        if progress:
                            print(f"       Progress: {progress}")
            
            time.sleep(1)
        
        print(f"   ⏰ Task did not complete within 30 seconds")
        print(f"   📊 Final state: {result.state}")
        return False
        
    except Exception as e:
        print(f"❌ Failed to test specific task: {e}")
        return False

def test_worker_logs():
    """Check for worker process"""
    print("\n🔍 Testing Worker Process")
    print("=" * 30)
    
    try:
        import subprocess
        
        # Check for celery processes
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        celery_processes = [line for line in result.stdout.split('\n') if 'celery' in line.lower()]
        
        if celery_processes:
            print(f"   ✅ Found {len(celery_processes)} Celery processes:")
            for proc in celery_processes:
                print(f"      • {proc}")
        else:
            print("   ❌ No Celery processes found")
            print("   💡 Start worker with: celery -A app.core.celery_app.celery_app worker --loglevel=info")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to check processes: {e}")
        return False

def test_redis_connection():
    """Test Redis connection with detailed info"""
    print("\n🔍 Testing Redis Connection")
    print("=" * 30)
    
    try:
        import redis
        
        # Test connection
        r = redis.Redis(host='localhost', port=6379, db=0)
        info = r.info()
        
        print(f"   ✅ Redis connection successful")
        print(f"   📊 Redis version: {info.get('redis_version', 'unknown')}")
        print(f"   📊 Connected clients: {info.get('connected_clients', 'unknown')}")
        print(f"   📊 Used memory: {info.get('used_memory_human', 'unknown')}")
        
        # Test specific keys
        all_keys = r.keys('*')
        celery_keys = [k for k in all_keys if b'celery' in k]
        
        print(f"   📋 Total Redis keys: {len(all_keys)}")
        print(f"   📋 Celery-related keys: {len(celery_keys)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def main():
    """Run comprehensive Celery diagnostics"""
    print("🧪 Comprehensive Celery Worker Diagnostic")
    print("=" * 50)
    print(f"🕐 Started at: {datetime.now()}")
    print()
    
    tests = [
        test_redis_connection,
        test_worker_logs,
        test_celery_worker_status,
        test_task_in_queue,
        test_task_result_backend,
        test_specific_task,
    ]
    
    results = []
    
    for test_func in tests:
        try:
            success = test_func()
            results.append(success)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 Diagnostic Summary")
    print(f"{'='*50}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total} tests")
    
    if passed < total:
        print(f"\n💡 Recommended actions:")
        print(f"   1. Make sure Redis is running: redis-server --daemonize yes")
        print(f"   2. Start Celery worker: celery -A app.core.celery_app.celery_app worker --loglevel=info")
        print(f"   3. Check worker logs for errors")
        print(f"   4. Verify task registration")
    else:
        print(f"\n✅ All tests passed! Celery should be working correctly.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)