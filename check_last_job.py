#!/usr/bin/env python3
"""
Check the last job for success status
"""

import redis
import json
from rq import Queue, Worker
from datetime import datetime
import os

def check_last_job():
    """Check the status of the last job."""
    
    print("🔍 Checking last job status...")
    
    # Connect to Redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    redis_conn = redis.Redis.from_url(REDIS_URL)
    
    try:
        # Test Redis connection
        redis_conn.ping()
        print("✅ Redis connection successful")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False
    
    # Get all log keys to find the most recent task
    log_keys = []
    for key in redis_conn.scan_iter(match="logs:*"):
        log_keys.append(key.decode())
    
    if not log_keys:
        print("❌ No jobs found in Redis")
        return False
    
    # Sort by creation time (approximate) and get the most recent
    log_keys.sort(reverse=True)
    latest_task_key = log_keys[0]
    task_id = latest_task_key.replace('logs:', '')
    
    print(f"📋 Found latest task ID: {task_id}")
    
    # Get all logs for this task
    logs = redis_conn.lrange(latest_task_key, 0, -1)
    print(f"📝 Found {len(logs)} log entries")
    
    if not logs:
        print("❌ No log entries found for this task")
        return False
    
    # Check the latest log entry for completion status
    latest_log = logs[-1]
    try:
        log_data = json.loads(latest_log.decode())
        
        # Check for completion
        if log_data.get('type') == 'complete':
            completion_data = log_data['data']
            print("✅ Last job completed successfully!")
            print(f"   📁 File: {completion_data['filename']}")
            print(f"   📊 Pages processed: {completion_data['stats']['pages_processed']}")
            print(f"   📊 Blogs processed: {completion_data['stats']['blogs_processed']}")
            print(f"   📊 Products processed: {completion_data['stats']['products_processed']}")
            print(f"   📊 Total scraped: {completion_data['stats']['total_scraped']}")
            print(f"   📊 Total URLs: {completion_data['stats']['total_urls']}")
            return True
            
        # Check for error
        elif log_data.get('type') == 'error':
            print(f"❌ Last job failed with error: {log_data['error']}")
            return False
            
        # Check for progress
        elif log_data.get('progress'):
            progress = log_data['progress']
            print(f"🔄 Last job is in progress: {progress['scraped']}/{progress['total']} URLs ({progress['percentage']}%)")
            
            # Show recent log messages
            print("\n📝 Recent log messages:")
            for log_entry in logs[-5:]:  # Last 5 entries
                try:
                    entry_data = json.loads(log_entry.decode())
                    if entry_data.get('message'):
                        timestamp = entry_data.get('timestamp', 'N/A')
                        print(f"   [{timestamp}] {entry_data['message']}")
                except json.JSONDecodeError:
                    continue
            return False
            
        else:
            print("⚠️ Last job status unclear - showing recent logs:")
            for log_entry in logs[-3:]:  # Last 3 entries
                try:
                    entry_data = json.loads(log_entry.decode())
                    print(f"   {entry_data}")
                except json.JSONDecodeError:
                    print(f"   (Invalid JSON: {log_entry})")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse latest log: {e}")
        return False
    
    # Also check RQ job status
    print("\n🔍 Checking RQ job status...")
    try:
        queue = Queue(connection=redis_conn)
        job = queue.fetch_job(task_id)
        
        if job:
            print(f"📋 RQ Job ID: {job.id}")
            print(f"📋 RQ Job Status: {job.get_status()}")
            print(f"📋 RQ Job Created: {job.created_at}")
            print(f"📋 RQ Job Started: {job.started_at}")
            print(f"📋 RQ Job Ended: {job.ended_at}")
            
            if job.is_finished:
                print("✅ RQ Job finished successfully")
            elif job.is_failed:
                print(f"❌ RQ Job failed: {job.exc_info}")
            elif job.is_started:
                print("🔄 RQ Job is running")
            elif job.is_queued:
                print("⏳ RQ Job is queued")
            else:
                print("❓ RQ Job status unknown")
        else:
            print("⚠️ RQ Job not found")
            
    except Exception as e:
        print(f"⚠️ Could not check RQ job status: {e}")

if __name__ == "__main__":
    check_last_job() 