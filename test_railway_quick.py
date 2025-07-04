#!/usr/bin/env python3
"""
Quick test script for Railway-deployed LLMs.txt Generator
Simple one-liner tests to verify your app is working
"""

import requests
import sys

# Replace with your actual Railway app URL
RAILWAY_URL = "https://llms-txt-production.up.railway.app"

def quick_test():
    """Run a quick test of the Railway app"""
    if not RAILWAY_URL or RAILWAY_URL == "https://your-app-name.railway.app":
        print("❌ Please update RAILWAY_URL with your actual Railway app URL")
        return False
    
    print(f"🧪 Quick Test: {RAILWAY_URL}")
    print("=" * 40)
    
    # Test 1: Health check
    try:
        response = requests.get(RAILWAY_URL, timeout=10)
        print(f"✅ Health Check: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False
    
    # Test 2: Sample config
    try:
        response = requests.get(f"{RAILWAY_URL}/api/sample-config", timeout=10)
        print(f"✅ Sample Config: {response.status_code}")
    except Exception as e:
        print(f"❌ Sample Config Failed: {e}")
    
    # Test 3: Tiers
    try:
        response = requests.get(f"{RAILWAY_URL}/api/tiers", timeout=10)
        print(f"✅ Tiers: {response.status_code}")
    except Exception as e:
        print(f"❌ Tiers Failed: {e}")
    
    print("✅ Quick test completed!")
    return True

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1) 