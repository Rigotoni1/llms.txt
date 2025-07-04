#!/usr/bin/env python3
"""
Simple and robust test script for Railway-deployed LLMs.txt Generator
"""

import requests
import json
import time

# Your actual Railway app URL
RAILWAY_URL = "https://llms-txt-production.up.railway.app"

def test_endpoint(endpoint, method="GET", data=None, timeout=15):
    """Test a single endpoint with better error handling"""
    try:
        if method == "GET":
            response = requests.get(f"{RAILWAY_URL}{endpoint}", timeout=timeout)
        elif method == "POST":
            response = requests.post(f"{RAILWAY_URL}{endpoint}", json=data, timeout=timeout)
        
        print(f"✅ {endpoint}: {response.status_code}")
        
        if response.status_code == 200:
            try:
                # Try to parse JSON response
                json_data = response.json()
                if isinstance(json_data, dict):
                    print(f"   Response keys: {list(json_data.keys())}")
                elif isinstance(json_data, list):
                    print(f"   Response items: {len(json_data)}")
                else:
                    print(f"   Response type: {type(json_data)}")
            except json.JSONDecodeError:
                print(f"   Response: {response.text[:100]}...")
        
        return response.status_code == 200
        
    except requests.exceptions.Timeout:
        print(f"❌ {endpoint}: Timeout after {timeout}s")
        return False
    except Exception as e:
        print(f"❌ {endpoint}: {str(e)}")
        return False

def test_health_check():
    """Test basic health check"""
    print("🏥 Testing health check...")
    return test_endpoint("/")

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🔌 Testing API endpoints...")
    
    endpoints = [
        ("/api/sample-config", "GET"),
        ("/api/tiers", "GET"),
    ]
    
    results = []
    for endpoint, method in endpoints:
        success = test_endpoint(endpoint, method)
        results.append(success)
    
    return all(results)

def test_sitemap_validation():
    """Test sitemap validation with a real sitemap"""
    print("\n🗺️ Testing sitemap validation...")
    
    # Use a real sitemap that should work
    test_sitemap = "https://www.google.com/sitemap.xml"
    
    return test_endpoint("/api/validate-sitemap", "POST", {"sitemap_url": test_sitemap})

def test_generation_flow():
    """Test the generation flow with minimal config"""
    print("\n🚀 Testing generation flow...")
    
    # Minimal test config
    test_config = {
        "site_name": "Test Site",
        "sitemap_url": "https://example.com/sitemap.xml",
        "max_pages_to_process": 1,
        "max_blogs": 1,
        "max_products": 1
    }
    
    success = test_endpoint("/generate", "POST", test_config)
    
    if success:
        print("   ⚠️ Generation request sent - this may take time to process")
        print("   💡 Check Railway logs for processing status")
    
    return success

def test_log_streaming():
    """Test log streaming with a dummy task ID"""
    print("\n📊 Testing log streaming...")
    
    # Use a dummy task ID to test the endpoint
    dummy_task_id = "test_task_123"
    return test_endpoint(f"/api/logs/{dummy_task_id}")

def main():
    """Run all tests"""
    print("🧪 Simple Railway App Test")
    print("=" * 50)
    print(f"🎯 Target: {RAILWAY_URL}")
    print()
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("API Endpoints", test_api_endpoints),
        ("Sitemap Validation", test_sitemap_validation),
        ("Generation Flow", test_generation_flow),
        ("Log Streaming", test_log_streaming),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your Railway app is working well.")
    elif passed >= len(results) * 0.8:
        print("⚠️ Most tests passed. Some minor issues detected.")
    else:
        print("🚨 Several tests failed. Check your Railway deployment.")

if __name__ == "__main__":
    main() 