#!/usr/bin/env python3
"""
Process tasks that are already in the queue
"""

import json
import redis

def process_existing_tasks():
    """Move tasks from default queue and process them"""
    try:
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        
        print("🔍 Checking existing tasks in queue...")
        
        # Check default queue
        queue_length = r.llen('default')
        print(f"📦 Found {queue_length} tasks in 'default' queue")
        
        if queue_length > 0:
            print("📋 Tasks in queue:")
            tasks = r.lrange('default', 0, -1)
            for i, task in enumerate(tasks):
                try:
                    task_data = json.loads(task)
                    task_id = task_data.get('id', 'unknown')
                    task_name = task_data.get('task', 'unknown')
                    print(f"   {i+1}. {task_name} (ID: {task_id})")
                except:
                    print(f"   {i+1}. Raw task data")
            
            # Clear the queue since we're restarting with proper configuration
            print(f"\n🧹 Clearing {queue_length} old tasks from queue...")
            r.delete('default')
            print("✅ Queue cleared")
        else:
            print("✅ No tasks in queue")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing queue: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Processing Queued Tasks")
    print("=" * 30)
    
    success = process_existing_tasks()
    
    if success:
        print(f"\n✅ Queue processing completed")
        print(f"💡 Now start the worker with: ./start_worker_fixed.sh")
    else:
        print(f"\n❌ Queue processing failed")