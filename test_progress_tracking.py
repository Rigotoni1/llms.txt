#!/usr/bin/env python3
"""
Test script to verify progress tracking functionality
"""

import requests
import json
import time
import os

def test_progress_tracking():
    """Test the progress tracking functionality."""
    
    # Test URL - use a small site for quick testing
    test_url = "https://www.betterstudio.io"
    
    print("🧪 Testing Progress Tracking...")
    print(f"Test URL: {test_url}")
    
    # Step 1: Analyze the site
    print("\n1. Analyzing site...")
    analyze_response = requests.post('http://localhost:5001/api/analyze-site', 
                                   json={'url': test_url})
    
    if analyze_response.status_code != 200:
        print(f"❌ Site analysis failed: {analyze_response.text}")
        return False
    
    analyze_data = analyze_response.json()
    if not analyze_data.get('success'):
        print(f"❌ Site analysis failed: {analyze_data.get('error')}")
        return False
    
    print(f"✅ Site analysis successful")
    print(f"   - Total URLs: {analyze_data['data']['total_urls']}")
    print(f"   - Sitemap: {analyze_data['data']['sitemap_url']}")
    
    # Step 2: Start generation
    print("\n2. Starting generation...")
    
    form_data = {
        'sitemap_url': analyze_data['data']['sitemap_url'],
        'site_name': analyze_data['data']['site_name'],
        'site_description': analyze_data['data']['site_description'],
        'content_selector': '.content, #main, article, .post-content, .entry-content, .page-content, .post, .entry, .elementor, .elementor-post',
        'title_selector': 'h1, .title, .post-title, .entry-title, .page-title',
        'respect_robots': 'false',
        'max_pages': '3',
        'max_blogs': '5',
        'max_products': '5',
        'max_content_length': '500',
        'max_detailed_content': '5',
        'request_delay': '0.5',
        'max_sitemaps': '3',
        'max_nested_links': '2'
    }
    
    generate_response = requests.post('http://localhost:5001/generate', data=form_data)
    
    if generate_response.status_code != 200:
        print(f"❌ Generation start failed: {generate_response.text}")
        return False
    
    generate_data = generate_response.json()
    if not generate_data.get('success'):
        print(f"❌ Generation start failed: {generate_data.get('error')}")
        return False
    
    task_id = generate_data['task_id']
    print(f"✅ Generation started with task ID: {task_id}")
    
    # Step 3: Monitor progress
    print("\n3. Monitoring progress...")
    
    import redis
    redis_conn = redis.Redis.from_url('redis://localhost:6379/0')
    
    last_progress = 0
    start_time = time.time()
    
    while True:
        # Get logs from Redis
        logs = redis_conn.lrange(f'logs:{task_id}', 0, -1)
        
        if not logs:
            time.sleep(1)
            continue
        
        # Process latest log entries
        for log_entry in logs[-5:]:  # Check last 5 entries
            try:
                log_data = json.loads(log_entry.decode())
                
                # Check if it's a completion message
                if log_data.get('type') == 'complete':
                    print(f"\n✅ Generation completed!")
                    print(f"   - File: {log_data['data']['filename']}")
                    print(f"   - Pages: {log_data['data']['stats']['pages_processed']}")
                    print(f"   - Blogs: {log_data['data']['stats']['blogs_processed']}")
                    print(f"   - Products: {log_data['data']['stats']['products_processed']}")
                    print(f"   - Total Scraped: {log_data['data']['stats']['total_scraped']}")
                    print(f"   - Total URLs: {log_data['data']['stats']['total_urls']}")
                    return True
                
                # Check if it's an error
                if log_data.get('type') == 'error':
                    print(f"\n❌ Generation failed: {log_data['error']}")
                    return False
                
                # Check for progress updates
                if log_data.get('progress'):
                    progress = log_data['progress']
                    current_progress = progress.get('percentage', 0)
                    
                    if current_progress > last_progress:
                        print(f"📊 Progress: {progress['scraped']}/{progress['total']} URLs ({current_progress}%)")
                        last_progress = current_progress
                
                # Show regular log messages
                if log_data.get('message'):
                    print(f"📝 {log_data['message']}")
                    
            except json.JSONDecodeError:
                continue
        
        # Check for timeout (5 minutes)
        if time.time() - start_time > 300:
            print("\n⏰ Test timed out after 5 minutes")
            return False
        
        time.sleep(2)

if __name__ == "__main__":
    try:
        success = test_progress_tracking()
        if success:
            print("\n🎉 Progress tracking test completed successfully!")
        else:
            print("\n💥 Progress tracking test failed!")
    except Exception as e:
        print(f"\n💥 Test error: {e}") 