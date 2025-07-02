#!/usr/bin/env python3
"""
Test download functionality
"""

import requests
import os

def test_download():
    """Test the download endpoint."""
    
    print("🧪 Testing Download Functionality...")
    
    # Test with the file we know exists
    filename = "llms_BetterStudio_20250701_154856.txt"
    
    print(f"1. Testing download of: {filename}")
    
    # Check if file exists in outputs directory
    file_path = os.path.join('outputs', filename)
    if not os.path.exists(file_path):
        print(f"❌ File not found in outputs directory: {file_path}")
        return False
    
    print(f"✅ File exists in outputs directory ({os.path.getsize(file_path)} bytes)")
    
    # Test download endpoint
    download_url = f"http://localhost:5001/download/{filename}"
    print(f"2. Testing download endpoint: {download_url}")
    
    try:
        response = requests.get(download_url)
        
        if response.status_code == 200:
            print(f"✅ Download endpoint works!")
            print(f"   - Status: {response.status_code}")
            print(f"   - Content-Type: {response.headers.get('Content-Type')}")
            print(f"   - Content-Disposition: {response.headers.get('Content-Disposition')}")
            print(f"   - Content-Length: {response.headers.get('Content-Length')}")
            print(f"   - File size: {len(response.content)} bytes")
            
            # Check if content looks like a valid llms.txt file
            content = response.text
            if 'llms.txt' in content and len(content) > 100:
                print("✅ File content appears to be valid llms.txt")
                print(f"   - First 200 chars: {content[:200]}...")
            else:
                print("⚠️ File content seems unusual")
                
        else:
            print(f"❌ Download failed: {response.status_code}")
            print(f"   - Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Download test failed: {e}")
        return False
    
    # Test with a non-existent file
    print("3. Testing download with non-existent file...")
    try:
        response = requests.get("http://localhost:5001/download/nonexistent.txt")
        
        if response.status_code == 404:
            print("✅ 404 error correctly returned for non-existent file")
        else:
            print(f"⚠️ Unexpected status for non-existent file: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Error testing non-existent file: {e}")
    
    print("🎉 Download functionality test completed!")
    return True

if __name__ == "__main__":
    test_download() 