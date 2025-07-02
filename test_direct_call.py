#!/usr/bin/env python3
"""
Test direct call to background function
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tasks import generate_llms_background
import json
import time

def test_direct_call():
    """Test the background function directly."""
    
    print("🧪 Testing direct function call...")
    
    # Simple config
    config = {
        'sitemap_url': 'https://www.betterstudio.io/sitemap.xml',
        'site_name': 'BetterStudio',
        'site_description': 'AI Photography Services',
        'content_selector': '.content, #main, article',
        'title_selector': 'h1, .title',
        'max_pages_to_process': 2,
        'max_blogs': 2,
        'max_products': 2,
        'max_content_length': 500,
        'max_detailed_content': 2,
        'request_delay': 0.1,
        'max_sitemaps_to_process': 3,
        'max_nested_links': 2,
        'min_content_length': 50,
        'default_topics': ['Technology', 'Business'],
        'respect_robots_txt': False,
        'output_file': 'llms.txt',
        'backup_existing': True
    }
    
    task_id = 'test_direct_' + str(int(time.time()))
    print(f"Task ID: {task_id}")
    
    try:
        # Call the function directly
        result = generate_llms_background(config, task_id)
        print(f"✅ Function completed successfully: {result}")
        
        # Check logs
        import redis
        redis_conn = redis.Redis.from_url('redis://localhost:6379/0')
        logs = redis_conn.lrange(f'logs:{task_id}', 0, -1)
        print(f"Found {len(logs)} log entries")
        
        for i, log in enumerate(logs):
            try:
                log_data = json.loads(log.decode())
                print(f"Log {i+1}: {log_data}")
                
                if log_data.get('progress'):
                    progress = log_data['progress']
                    print(f"📊 Progress: {progress['scraped']}/{progress['total']} ({progress['percentage']}%)")
                    
            except json.JSONDecodeError as e:
                print(f"Failed to parse log {i+1}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Function failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_direct_call() 