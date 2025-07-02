#!/usr/bin/env python3
"""
Test Redis connection for Railway deployment
"""

import os
import redis
import requests
import json

def test_redis_direct():
    """Test direct Redis connection"""
    print("🔍 Testing direct Redis connection...")
    
    # Get Redis URL from environment
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    print(f"📡 Redis URL: {redis_url}")
    
    try:
        # Try to connect to Redis
        redis_conn = redis.Redis.from_url(redis_url)
        
        # Test basic operations
        redis_conn.set('test_key', 'test_value')
        value = redis_conn.get('test_key')
        redis_conn.delete('test_key')
        
        if value == b'test_value':
            print("✅ Redis connection successful!")
            return True
        else:
            print("❌ Redis connection failed - data mismatch")
            return False
            
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def test_railway_redis():
    """Test Railway app Redis connection"""
    print("\n🔍 Testing Railway app Redis connection...")
    
    railway_url = "https://llms-txt-production.up.railway.app"
    
    try:
        # Test if the app is responding
        response = requests.get(f"{railway_url}/", timeout=10)
        print(f"✅ Web app responds: {response.status_code}")
        
        # Try to get any Redis-related endpoint
        redis_endpoints = [
            "/api/health",
            "/api/status",
            "/health",
            "/status"
        ]
        
        for endpoint in redis_endpoints:
            try:
                response = requests.get(f"{railway_url}{endpoint}", timeout=10)
                print(f"✅ {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   📊 Data: {data}")
                    except:
                        print(f"   📄 Text: {response.text[:100]}...")
            except Exception as e:
                print(f"❌ {endpoint}: {str(e)}")
                
    except Exception as e:
        print(f"❌ Railway app test failed: {e}")

def check_environment():
    """Check environment variables"""
    print("\n🔧 Checking environment variables...")
    
    env_vars = [
        'REDIS_URL',
        'PORT',
        'RAILWAY_ENVIRONMENT',
        'RAILWAY_PROJECT_ID',
        'RAILWAY_SERVICE_ID'
    ]
    
    for var in env_vars:
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

def main():
    """Run all Redis tests"""
    print("🔍 Redis Connection Diagnostics")
    print("=" * 40)
    
    check_environment()
    test_redis_direct()
    test_railway_redis()
    
    print("\n" + "=" * 40)
    print("📋 SUMMARY")
    print("=" * 40)
    print("If Redis connection fails, you need to:")
    print("1. Add Redis service to railway.json (already done)")
    print("2. Redeploy to Railway")
    print("3. Check that REDIS_URL is automatically set")
    print("4. Verify worker service can connect to Redis")

if __name__ == "__main__":
    main() 