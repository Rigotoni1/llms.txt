#!/usr/bin/env python3
"""
Test script for the new chat-based LLMs.txt Generator interface
"""

import requests
import json
import time

def test_chat_interface():
    """Test the complete chat interface flow."""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Chat-Based LLMs.txt Generator Interface")
    print("=" * 60)
    
    # Test 1: Website Analysis
    print("\n1. Testing Website Analysis...")
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
    
    # Test 2: Generation (simplified test)
    print("\n2. Testing Generation Endpoint...")
    
    form_data = {
        'sitemap_url': 'https://www.betterstudio.io/sitemap.xml',
        'site_name': 'BetterStudio',
        'site_description': 'AI Fashion Photoshoots for E-Commerce',
        'content_selector': '.content, #main, article, .post-content, .entry-content, .page-content, .post, .entry, .elementor, .elementor-post',
        'title_selector': 'h1, .title, .post-title, .entry-title, .page-title',
        'max_pages': '5',
        'max_blogs': '5',
        'max_products': '5',
        'max_content_length': '500',
        'request_delay': '0.5',
        'max_nested_links': '3',
        'max_sitemaps': '5',
        'max_detailed_content': '5',
        'respect_robots': 'false'
    }
    
    try:
        response = requests.post(f"{base_url}/generate", data=form_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Generation successful!")
                print(f"   File: {result['filename']}")
                print(f"   Pages: {result['stats']['pages_processed']}")
                print(f"   Blogs: {result['stats']['blogs_processed']}")
                print(f"   Products: {result['stats']['products_processed']}")
            else:
                print(f"❌ Generation failed: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False
    
    print("\n🎉 All tests passed! The chat interface is working correctly.")
    print(f"\n🌐 Open your browser and go to: {base_url}")
    print("   The new chat-based interface should be ready to use!")
    
    return True

if __name__ == "__main__":
    test_chat_interface() 