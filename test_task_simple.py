#!/usr/bin/env python3
"""
Simple test to verify Celery task execution
"""

import sys
import time

def test_task_execution():
    """Test if tasks are being executed"""
    print("🧪 Testing Celery Task Execution")
    print("=" * 40)
    
    try:
        # Import the task
        from app.services.tasks import health_check_task
        
        print("✅ Successfully imported health_check_task")
        
        # Create and send task
        print("🚀 Sending health check task...")
        result = health_check_task.delay()
        
        print(f"📋 Task ID: {result.id}")
        print(f"📊 Initial state: {result.state}")
        
        # Wait for completion
        print("⏳ Waiting for task completion (max 30 seconds)...")
        
        for i in range(30):
            state = result.state
            print(f"   [{i+1:2d}s] State: {state}")
            
            if state == 'SUCCESS':
                task_result = result.get()
                print(f"✅ Task completed successfully!")
                print(f"📊 Result: {task_result}")
                return True
            elif state == 'FAILURE':
                print(f"❌ Task failed: {result.info}")
                return False
            
            time.sleep(1)
        
        print(f"⏰ Task did not complete within 30 seconds")
        print(f"📊 Final state: {result.state}")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_resume_task():
    """Test the resume processing task"""
    print("\n🧪 Testing Resume Processing Task")
    print("=" * 40)
    
    try:
        from app.services.tasks import process_resume_and_match_jobs
        
        print("✅ Successfully imported process_resume_and_match_jobs")
        
        # Simple test content
        test_content = "John Doe\nSoftware Engineer\nPython, FastAPI, Machine Learning"
        
        print("🚀 Sending resume processing task...")
        result = process_resume_and_match_jobs.delay(
            file_content=test_content.encode('utf-8'),
            filename="test_resume.txt",
            content_type="text/plain"
        )
        
        print(f"📋 Task ID: {result.id}")
        print(f"📊 Initial state: {result.state}")
        
        # Monitor for longer time since this task takes more time
        print("⏳ Waiting for task completion (max 60 seconds)...")
        
        for i in range(60):
            state = result.state
            print(f"   [{i+1:2d}s] State: {state}")
            
            if state == 'SUCCESS':
                task_result = result.get()
                print(f"✅ Task completed successfully!")
                matched_jobs = task_result.get('matched_jobs', [])
                print(f"📊 Found {len(matched_jobs)} matched jobs")
                print(f"⏱️  Processing time: {task_result.get('processing_time_seconds', 0):.2f}s")
                return True
            elif state == 'FAILURE':
                print(f"❌ Task failed: {result.info}")
                return False
            elif state == 'STARTED':
                # Try to get progress info
                if hasattr(result, 'info') and result.info:
                    if isinstance(result.info, dict):
                        progress = result.info.get('progress', '')
                        percentage = result.info.get('percentage', '')
                        if progress:
                            print(f"       Progress: {progress} ({percentage}%)")
            
            time.sleep(1)
        
        print(f"⏰ Task did not complete within 60 seconds")
        print(f"📊 Final state: {result.state}")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Celery Task Execution Test")
    print("=" * 50)
    
    # Test simple task first
    health_success = test_task_execution()
    
    if health_success:
        print("\n" + "="*50)
        # Test complex task
        resume_success = test_resume_task()
        
        if resume_success:
            print(f"\n🎉 All tests passed! Celery is working correctly.")
            sys.exit(0)
        else:
            print(f"\n❌ Resume task failed, but health check worked.")
            sys.exit(1)
    else:
        print(f"\n❌ Basic health check failed. Check Celery worker.")
        sys.exit(1)