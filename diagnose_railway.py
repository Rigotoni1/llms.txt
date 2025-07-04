#!/usr/bin/env python3
"""
Diagnostic script for Railway LLMs.txt Generator
Helps identify issues with generation process
"""

import requests
import json
import time
import os

# Your Railway app URL
RAILWAY_URL = "https://llms-txt-production.up.railway.app"

def test_redis_connection():
    """Test if Redis connection is working"""
    print("🔍 Testing Redis connection...")
    
    try:
        # Test if there's a Redis health endpoint
        response = requests.get(f"{RAILWAY_URL}/api/health/redis", timeout=10)
        if response.status_code == 200:
            print("✅ Redis health endpoint responds")
            return True
    except:
        pass
    
    # Try to get queue status
    try:
        response = requests.get(f"{RAILWAY_URL}/api/queue-status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Queue status: {data}")
            return True
    except:
        pass
    
    print("❌ No Redis health endpoints found")
    return False

def test_generation_with_logging():
    """Test generation and monitor the process"""
    print("\n🚀 Testing generation with detailed logging...")
    
    # Create a test config
    test_config = {
        "site_name": "Diagnostic Test",
        "sitemap_url": "https://example.com/sitemap.xml",
        "max_pages_to_process": 1,
        "max_blogs": 1,
        "max_products": 1
    }
    
    try:
        print("📤 Sending generation request...")
        response = requests.post(f"{RAILWAY_URL}/generate", json=test_config, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('task_id')
            print(f"✅ Generation request accepted")
            print(f"📋 Task ID: {task_id}")
            print(f"📊 Response: {data}")
            
            if task_id:
                print(f"\n📊 Monitoring task {task_id}...")
                monitor_task(task_id)
            
            return True
        else:
            print(f"❌ Generation request failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Generation test failed: {e}")
        return False

def monitor_task(task_id, max_attempts=10):
    """Monitor a task for progress"""
    print(f"👀 Monitoring task {task_id} for up to 2 minutes...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{RAILWAY_URL}/api/logs/{task_id}", timeout=15)
            
            if response.status_code == 200:
                logs = response.text.strip()
                if logs:
                    print(f"📝 Logs (attempt {attempt + 1}): {logs[:200]}...")
                else:
                    print(f"📝 No logs yet (attempt {attempt + 1})")
            else:
                print(f"❌ Log request failed: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Log request timed out (attempt {attempt + 1})")
        except Exception as e:
            print(f"❌ Log monitoring error: {e}")
        
        time.sleep(12)  # Wait 12 seconds between attempts

def test_environment_variables():
    """Check if critical environment variables are set"""
    print("\n🔧 Checking environment variables...")
    
    # These are the critical env vars for Railway
    critical_vars = [
        'REDIS_URL',
        'PORT',
        'RAILWAY_ENVIRONMENT'
    ]
    
    for var in critical_vars:
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if 'REDIS' in var and value:
                masked = value.split('@')[0] + '@***' if '@' in value else '***'
                print(f"✅ {var}: {masked}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")

def test_worker_communication():
    """Test if web service can communicate with worker"""
    print("\n🔗 Testing worker communication...")
    
    # Try to get any worker-related endpoints
    worker_endpoints = [
        "/api/workers",
        "/api/queue-status", 
        "/api/health/worker",
        "/api/tasks"
    ]
    
    for endpoint in worker_endpoints:
        try:
            response = requests.get(f"{RAILWAY_URL}{endpoint}", timeout=10)
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   📊 Data: {data}")
                except:
                    print(f"   📄 Text: {response.text[:100]}...")
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)}")

def check_railway_status():
    """Check Railway service status"""
    print("\n🚂 Checking Railway service status...")
    
    try:
        # This would require Railway CLI, but we can check if services are responding
        print("🔍 Checking if both web and worker services are accessible...")
        
        # Web service is definitely working
        web_response = requests.get(RAILWAY_URL, timeout=10)
        print(f"✅ Web service: {web_response.status_code}")
        
        # Try to infer worker status from generation response
        print("🔍 Worker service status will be determined by generation test...")
        
    except Exception as e:
        print(f"❌ Railway status check failed: {e}")

def main():
    """Run all diagnostics"""
    print("🔍 Railway LLMs.txt Generator Diagnostics")
    print("=" * 50)
    print(f"🎯 Target: {RAILWAY_URL}")
    print()
    
    # Run diagnostics
    diagnostics = [
        ("Environment Variables", test_environment_variables),
        ("Redis Connection", test_redis_connection),
        ("Worker Communication", test_worker_communication),
        ("Railway Status", check_railway_status),
        ("Generation Process", test_generation_with_logging),
    ]
    
    results = []
    for test_name, test_func in diagnostics:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print("1. Check Railway dashboard for service status")
    print("2. Verify Redis URL is correctly set")
    print("3. Ensure worker service is running")
    print("4. Check Railway logs for specific errors")
    print("5. Verify environment variables are set correctly")

if __name__ == "__main__":
    main() 