#!/usr/bin/env python3
"""
Test script to verify the directory fix works
"""

import os
import requests
import json

# Your Railway app URL
RAILWAY_URL = "https://llms-txt-production.up.railway.app"

def test_generation_with_directory_check():
    """Test generation and check if directory issue is fixed"""
    print("🧪 Testing generation with directory fix...")
    
    # Create a test config
    test_config = {
        "site_name": "Directory Test",
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
            
            if task_id:
                print(f"\n📊 Monitoring task {task_id} for directory issues...")
                monitor_task_for_errors(task_id)
            
            return True
        else:
            print(f"❌ Generation request failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Generation test failed: {e}")
        return False

def monitor_task_for_errors(task_id, max_attempts=15):
    """Monitor a task specifically for directory errors"""
    print(f"👀 Monitoring task {task_id} for up to 3 minutes...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{RAILWAY_URL}/api/logs/{task_id}", timeout=15)
            
            if response.status_code == 200:
                logs = response.text.strip()
                if logs:
                    print(f"📝 Logs (attempt {attempt + 1}): {logs}")
                    
                    # Check for directory errors
                    if "No such file or directory" in logs:
                        print("❌ Directory error still present!")
                        return False
                    elif "Generated llms.txt" in logs:
                        print("✅ Generation completed successfully!")
                        return True
                    elif "error" in logs.lower():
                        print("❌ Other error detected")
                        return False
                else:
                    print(f"📝 No logs yet (attempt {attempt + 1})")
            else:
                print(f"❌ Log request failed: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Log request timed out (attempt {attempt + 1})")
        except Exception as e:
            print(f"❌ Log monitoring error: {e}")
        
        import time
        time.sleep(12)  # Wait 12 seconds between attempts
    
    print("⏰ Monitoring timeout - check Railway logs for final status")
    return False

def main():
    """Run the directory fix test"""
    print("🔍 Testing Directory Fix")
    print("=" * 40)
    print(f"🎯 Target: {RAILWAY_URL}")
    print()
    
    success = test_generation_with_directory_check()
    
    if success:
        print("\n🎉 Directory fix appears to be working!")
    else:
        print("\n❌ Directory issue may still be present")
        print("💡 Check Railway logs for more details")

if __name__ == "__main__":
    main() 