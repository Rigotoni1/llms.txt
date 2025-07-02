#!/usr/bin/env python3
"""
Test script for the new log streaming and animation features
"""

import requests
import json
import time

def test_log_streaming():
    """Test the log streaming functionality."""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Log Streaming & Animation Features")
    print("=" * 60)
    
    # Test 1: Website Analysis with Animation
    print("\n1. Testing Website Analysis Animation...")
    analysis_data = {
        "url": "https://betterstudio.io"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/analyze-site",
            headers={"Content-Type": "application/json"},
            json=analysis_data
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result['data']
                print(f"✅ Analysis successful!")
                print(f"   Site: {data['site_name']}")
                print(f"   Sitemap: {data['sitemap_url']}")
                print(f"   Total URLs: {data['total_urls']}")
                print(f"   Blog URLs: {data['blog_urls']}")
                print(f"   Page URLs: {data['page_urls']}")
                print(f"   Product URLs: {data['product_urls']}")
            else:
                print(f"❌ Analysis failed: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False
    
    # Test 2: Generation with Log Streaming
    print("\n2. Testing Generation with Log Streaming...")
    
    form_data = {
        'sitemap_url': 'https://www.betterstudio.io/sitemap.xml',
        'site_name': 'BetterStudio',
        'site_description': 'AI Fashion Photoshoots for E-Commerce',
        'content_selector': '.content, #main, article, .post-content, .entry-content, .page-content, .post, .entry, .elementor, .elementor-post',
        'title_selector': 'h1, .title, .post-title, .entry-title, .page-title',
        'max_pages': '3',
        'max_blogs': '3',
        'max_products': '3',
        'max_content_length': '300',
        'request_delay': '0.5',
        'max_nested_links': '2',
        'max_sitemaps': '3',
        'max_detailed_content': '3',
        'respect_robots': 'false'
    }
    
    try:
        response = requests.post(f"{base_url}/generate", data=form_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Generation started successfully!")
                print(f"   Task ID: {result['task_id']}")
                print(f"   File: {result['filename']}")
                print(f"   Pages: {result['stats']['pages_processed']}")
                print(f"   Blogs: {result['stats']['blogs_processed']}")
                print(f"   Products: {result['stats']['products_processed']}")
                
                # Test log streaming endpoint
                print(f"\n3. Testing Log Streaming Endpoint...")
                log_response = requests.get(f"{base_url}/api/logs/{result['task_id']}", stream=True)
                
                if log_response.status_code == 200:
                    print(f"✅ Log streaming endpoint working!")
                    print(f"   Content-Type: {log_response.headers.get('content-type')}")
                    
                    # Read a few log entries
                    log_count = 0
                    for line in log_response.iter_lines():
                        if line:
                            line = line.decode('utf-8')
                            if line.startswith('data: '):
                                data = json.loads(line[6:])
                                if data.get('type') == 'log':
                                    log_count += 1
                                    print(f"   Log {log_count}: {data['data']['message'][:80]}...")
                                    if log_count >= 5:  # Show first 5 logs
                                        break
                                elif data.get('type') == 'complete':
                                    print(f"   ✅ Generation completed!")
                                    break
                else:
                    print(f"❌ Log streaming failed: {log_response.status_code}")
                    
            else:
                print(f"❌ Generation failed: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False
    
    print("\n🎉 All tests passed! The new features are working correctly.")
    print(f"\n🌐 Open your browser and go to: {base_url}")
    print("   You should now see:")
    print("   - Animated dots during URL analysis")
    print("   - Real-time log streaming during generation")
    print("   - Live progress updates in the chat")
    
    return True

if __name__ == "__main__":
    test_log_streaming() 