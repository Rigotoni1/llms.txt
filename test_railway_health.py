#!/usr/bin/env python3
"""
Test script for Railway-deployed LLMs.txt Generator
Replace YOUR_RAILWAY_URL with your actual Railway app URL
"""

import requests
import json
import time

# Replace with your actual Railway app URL
RAILWAY_URL = "https://llms-txt-production.up.railway.app"

def test_health_check():
    """Test if the app is responding"""
    try:
        response = requests.get(f"{RAILWAY_URL}/", timeout=10)
        print(f"✅ Health check: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_api_endpoints():
    """Test basic API endpoints"""
    endpoints = [
        "/api/sample-config",
        "/api/tiers"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{RAILWAY_URL}{endpoint}", timeout=10)
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.json()[:100]}...")
        except Exception as e:
            print(f"❌ {endpoint} failed: {e}")

def test_sitemap_validation():
    """Test sitemap validation endpoint"""
    test_sitemap = "https://example.com/sitemap.xml"
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/api/validate-sitemap",
            json={"sitemap_url": test_sitemap},
            timeout=15
        )
        print(f"✅ Sitemap validation: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Sitemap validation failed: {e}")

def test_generation_flow():
    """Test the complete generation flow"""
    # Sample config for testing
    test_config = {
        "site_name": "Test Site",
        "sitemap_url": "https://example.com/sitemap.xml",
        "max_pages_to_process": 2,
        "max_blogs": 2,
        "max_products": 2
    }
    
    try:
        print("🚀 Testing generation flow...")
        response = requests.post(
            f"{RAILWAY_URL}/generate",
            json=test_config,
            timeout=30
        )
        print(f"✅ Generation request: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Task ID: {result.get('task_id')}")
            print(f"   Status: {result.get('status')}")
            
            # Test log streaming
            if result.get('task_id'):
                test_log_streaming(result['task_id'])
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Generation flow failed: {e}")

def test_log_streaming(task_id):
    """Test log streaming endpoint"""
    try:
        print(f"📊 Testing log streaming for task {task_id}...")
        response = requests.get(
            f"{RAILWAY_URL}/api/logs/{task_id}",
            timeout=10
        )
        print(f"✅ Log streaming: {response.status_code}")
        if response.status_code == 200:
            print(f"   Logs: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Log streaming failed: {e}")

def main():
    """Run all tests"""
    print("🧪 Testing Railway App")
    print("=" * 50)
    
    if not RAILWAY_URL or RAILWAY_URL == "https://your-app-name.railway.app":
        print("❌ Please update RAILWAY_URL with your actual Railway app URL")
        return
    
    # Run tests
    if test_health_check():
        test_api_endpoints()
        test_sitemap_validation()
        test_generation_flow()
    else:
        print("❌ App is not responding. Check your Railway deployment.")

if __name__ == "__main__":
    main() 