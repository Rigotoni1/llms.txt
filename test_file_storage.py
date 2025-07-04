#!/usr/bin/env python3
"""
Test script to check file storage capabilities
"""

import requests
import json
import time

# Your Railway app URL
RAILWAY_URL = "https://llms-txt-production.up.railway.app"

def test_file_download():
    """Test if file download endpoint works"""
    print("📁 Testing file download endpoint...")
    
    # Try to download a non-existent file to see the response
    try:
        response = requests.get(f"{RAILWAY_URL}/download/test_file.txt", timeout=10)
        print(f"📥 Download endpoint response: {response.status_code}")
        if response.status_code == 404:
            print("✅ Download endpoint works (correctly returns 404 for missing file)")
        else:
            print(f"📄 Response: {response.text[:100]}...")
    except Exception as e:
        print(f"❌ Download test failed: {e}")

def test_generation_and_download():
    """Test complete generation and download flow"""
    print("\n🚀 Testing complete generation and download flow...")
    
    # Create a test config
    test_config = {
        "site_name": "Storage Test",
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
                print(f"\n📊 Monitoring task {task_id}...")
                filename = monitor_task_for_completion(task_id)
                
                if filename:
                    print(f"\n📥 Testing download of {filename}...")
                    test_download_specific_file(filename)
            
            return True
        else:
            print(f"❌ Generation request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Generation test failed: {e}")
        return False

def monitor_task_for_completion(task_id, max_attempts=20):
    """Monitor a task and return the filename when completed"""
    print(f"👀 Monitoring task {task_id} for completion...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{RAILWAY_URL}/api/logs/{task_id}", timeout=15)
            
            if response.status_code == 200:
                logs = response.text.strip()
                if logs:
                    print(f"📝 Logs (attempt {attempt + 1}): {logs}")
                    
                    # Look for completion message with filename
                    if "Generated llms.txt:" in logs:
                        # Extract filename from log
                        import re
                        match = re.search(r'Generated llms\.txt: (.+\.txt)', logs)
                        if match:
                            filename = match.group(1)
                            print(f"✅ Generation completed! Filename: {filename}")
                            return filename
                    
                    # Check for errors
                    if "error" in logs.lower() and "No such file or directory" in logs:
                        print("❌ Directory error detected")
                        return None
                        
                else:
                    print(f"📝 No logs yet (attempt {attempt + 1})")
            else:
                print(f"❌ Log request failed: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Log request timed out (attempt {attempt + 1})")
        except Exception as e:
            print(f"❌ Log monitoring error: {e}")
        
        time.sleep(12)  # Wait 12 seconds between attempts
    
    print("⏰ Monitoring timeout")
    return None

def test_download_specific_file(filename):
    """Test downloading a specific file"""
    try:
        response = requests.get(f"{RAILWAY_URL}/download/{filename}", timeout=15)
        print(f"📥 Download response: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ File download successful!")
            print(f"📄 File size: {len(response.content)} bytes")
            print(f"📄 Content preview: {response.text[:200]}...")
        elif response.status_code == 404:
            print("❌ File not found - storage issue confirmed")
        else:
            print(f"❌ Download failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Download test failed: {e}")

def main():
    """Run file storage tests"""
    print("🔍 Testing File Storage")
    print("=" * 40)
    print(f"🎯 Target: {RAILWAY_URL}")
    print()
    
    # Test basic download endpoint
    test_file_download()
    
    # Test complete flow
    test_generation_and_download()
    
    print("\n💡 RECOMMENDATIONS:")
    print("1. If files are not persisting, use Railway volumes")
    print("2. Consider cloud storage (S3, GCS) for production")
    print("3. For small files, store content in Redis")

if __name__ == "__main__":
    main() 