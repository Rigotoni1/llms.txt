#!/usr/bin/env python3
"""
Simple test for progress tracking
"""

import requests
import json
import time

def test_progress():
    """Test progress tracking with a simple request."""
    
    print("🧪 Testing Progress Tracking...")
    
    # Test with a simple form submission
    form_data = {
        'sitemap_url': 'https://www.betterstudio.io/sitemap.xml',
        'site_name': 'BetterStudio',
        'site_description': 'AI Photography Services',
        'content_selector': '.content, #main, article',
        'title_selector': 'h1, .title',
        'respect_robots': 'false',
        'max_pages': '3',
        'max_blogs': '3',
        'max_products': '3',
        'max_content_length': '500',
        'max_detailed_content': '3',
        'request_delay': '0.5',
        'max_sitemaps': '3',
        'max_nested_links': '2'
    }
    
    print("1. Starting generation...")
    response = requests.post('http://localhost:5001/generate', data=form_data)
    
    if response.status_code != 200:
        print(f"❌ Failed to start generation: {response.text}")
        return False
    
    result = response.json()
    if not result.get('success'):
        print(f"❌ Generation failed: {result.get('error')}")
        return False
    
    task_id = result['task_id']
    print(f"✅ Generation started with task ID: {task_id}")
    
    # Test the log streaming endpoint
    print("2. Testing log streaming...")
    try:
        import redis
        redis_conn = redis.Redis.from_url('redis://localhost:6379/0')
        
        # Wait a bit for logs to appear
        time.sleep(3)
        
        logs = redis_conn.lrange(f'logs:{task_id}', 0, -1)
        print(f"Found {len(logs)} log entries")
        
        for i, log in enumerate(logs):
            try:
                log_data = json.loads(log.decode())
                print(f"Log {i+1}: {log_data}")
                
                # Check for progress data
                if log_data.get('progress'):
                    progress = log_data['progress']
                    print(f"📊 Progress: {progress['scraped']}/{progress['total']} ({progress['percentage']}%)")
                
                # Check for completion
                if log_data.get('type') == 'complete':
                    print(f"✅ Generation completed: {log_data['data']['filename']}")
                    return True
                    
            except json.JSONDecodeError as e:
                print(f"Failed to parse log {i+1}: {e}")
                
    except Exception as e:
        print(f"❌ Error testing logs: {e}")
        return False
    
    print("⏰ Test completed (no completion detected)")
    return True

if __name__ == "__main__":
    test_progress() 