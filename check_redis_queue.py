#!/usr/bin/env python3
"""
Check Redis queue directly to see if tasks are being queued
"""

import json
import sys

def check_redis_queues():
    """Check what's in Redis queues"""
    try:
        import redis
        
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        
        print("🔍 Checking Redis Queues")
        print("=" * 30)
        
        # Check all keys
        all_keys = r.keys('*')
        print(f"📊 Total Redis keys: {len(all_keys)}")
        
        if all_keys:
            print("📋 All keys:")
            for key in sorted(all_keys):
                key_str = key.decode() if isinstance(key, bytes) else str(key)
                key_type = r.type(key).decode()
                print(f"   • {key_str} ({key_type})")
        
        # Check common Celery queues
        queue_names = ['celery', 'default', 'celery:1', 'celery:2']
        
        print(f"\n📦 Queue Status:")
        for queue_name in queue_names:
            length = r.llen(queue_name)
            print(f"   • {queue_name}: {length} tasks")
            
            if length > 0:
                print(f"     Tasks in {queue_name}:")
                tasks = r.lrange(queue_name, 0, -1)
                for i, task in enumerate(tasks):
                    try:
                        task_data = json.loads(task)
                        task_id = task_data.get('id', 'unknown')
                        task_name = task_data.get('task', 'unknown')
                        print(f"       {i+1}. {task_name} (ID: {task_id})")
                    except:
                        print(f"       {i+1}. Raw: {task[:100]}...")
        
        # Check task results
        result_keys = r.keys('celery-task-meta-*')
        print(f"\n📊 Task Results: {len(result_keys)}")
        
        if result_keys:
            print("📋 Recent results:")
            for key in result_keys[-5:]:  # Last 5
                try:
                    result = r.get(key)
                    if result:
                        result_data = json.loads(result)
                        task_id = key.decode().replace('celery-task-meta-', '')
                        status = result_data.get('status', 'unknown')
                        print(f"   • {task_id}: {status}")
                except:
                    pass
        
        return True
        
    except ImportError:
        print("❌ Redis module not available")
        return False
    except Exception as e:
        print(f"❌ Error checking Redis: {e}")
        return False

def test_task_creation():
    """Create a task and see if it appears in Redis"""
    try:
        from app.services.tasks import health_check_task
        
        print(f"\n🧪 Creating Test Task")
        print("=" * 25)
        
        # Create task
        result = health_check_task.delay()
        print(f"📋 Created task: {result.id}")
        print(f"📊 State: {result.state}")
        
        # Check if it appears in Redis
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        
        # Check queues again
        queue_names = ['celery', 'default']
        for queue_name in queue_names:
            length = r.llen(queue_name)
            print(f"📦 Queue '{queue_name}': {length} tasks")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating task: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Redis Queue Diagnostic")
    print("=" * 40)
    
    success1 = check_redis_queues()
    success2 = test_task_creation()
    
    if success1 and success2:
        print(f"\n✅ Redis queue check completed")
    else:
        print(f"\n❌ Redis queue check failed")
        sys.exit(1)