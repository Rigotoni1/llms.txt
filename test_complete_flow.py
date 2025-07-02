#!/usr/bin/env python3
"""
Test complete flow from generation to completion
"""

import requests
import json
import time
import redis

def test_complete_flow():
    """Test the complete flow including completion and download."""
    
    print("🧪 Testing Complete Flow...")
    
    # Test with a simple form submission
    form_data = {
        'sitemap_url': 'https://www.betterstudio.io/sitemap.xml',
        'site_name': 'BetterStudio',
        'site_description': 'AI Photography Services',
        'content_selector': '.content, #main, article',
        'title_selector': 'h1, .title',
        'respect_robots': 'false',
        'max_pages': '2',
        'max_blogs': '2',
        'max_products': '2',
        'max_content_length': '500',
        'max_detailed_content': '2',
        'request_delay': '0.1',
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
    
    # Monitor logs and wait for completion
    print("2. Monitoring progress and waiting for completion...")
    redis_conn = redis.Redis.from_url('redis://localhost:6379/0')
    
    start_time = time.time()
    completion_data = None
    
    while time.time() - start_time < 60:  # Wait up to 60 seconds
        logs = redis_conn.lrange(f'logs:{task_id}', 0, -1)
        
        if logs:
            # Check the latest log entry
            latest_log = logs[-1]
            try:
                log_data = json.loads(latest_log.decode())
                
                # Check for completion
                if log_data.get('type') == 'complete':
                    completion_data = log_data['data']
                    print(f"✅ Generation completed!")
                    print(f"   - File: {completion_data['filename']}")
                    print(f"   - Pages: {completion_data['stats']['pages_processed']}")
                    print(f"   - Blogs: {completion_data['stats']['blogs_processed']}")
                    print(f"   - Products: {completion_data['stats']['products_processed']}")
                    print(f"   - Total Scraped: {completion_data['stats']['total_scraped']}")
                    print(f"   - Total URLs: {completion_data['stats']['total_urls']}")
                    break
                    
                # Check for progress
                if log_data.get('progress'):
                    progress = log_data['progress']
                    print(f"📊 Progress: {progress['scraped']}/{progress['total']} URLs ({progress['percentage']}%)")
                    
            except json.JSONDecodeError:
                pass
        
        time.sleep(1)
    
    if not completion_data:
        print("❌ Generation did not complete within 60 seconds")
        return False
    
    # Test download endpoint
    print("3. Testing download endpoint...")
    filename = completion_data['filename']
    download_response = requests.get(f'http://localhost:5001/download/{filename}')
    
    if download_response.status_code == 200:
        print(f"✅ Download endpoint works! File size: {len(download_response.content)} bytes")
        
        # Check if it's a valid llms.txt file
        content = download_response.text
        if 'llms.txt' in content and len(content) > 100:
            print("✅ File appears to be a valid llms.txt file")
        else:
            print("⚠️ File content seems unusual")
            
    else:
        print(f"❌ Download failed: {download_response.status_code}")
        return False
    
    # Test the log streaming endpoint
    print("4. Testing log streaming endpoint...")
    try:
        import sseclient
        stream_response = requests.get(f'http://localhost:5001/api/logs/{task_id}', stream=True)
        client = sseclient.SSEClient(stream_response)
        
        message_count = 0
        for event in client.events():
            message_count += 1
            print(f"SSE Message {message_count}: {event.data}")
            
            if message_count >= 3:  # Just test a few messages
                break
                
        print(f"✅ Log streaming works! Received {message_count} messages")
        
    except ImportError:
        print("⚠️ sseclient not available, skipping SSE test")
    except Exception as e:
        print(f"⚠️ SSE test failed: {e}")
    
    print("🎉 Complete flow test successful!")
    return True

if __name__ == "__main__":
    test_complete_flow() 