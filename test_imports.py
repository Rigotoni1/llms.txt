#!/usr/bin/env python3
"""
Test imports for tasks.py
"""

def test_imports():
    """Test that all imports work correctly."""
    
    print("🧪 Testing imports...")
    
    try:
        import os
        print("✅ os imported")
        
        import redis
        print("✅ redis imported")
        
        import json
        print("✅ json imported")
        
        from rq import get_current_job
        print("✅ rq imported")
        
        from main import SitemapParser, ContentScraper, LLMsTxtGenerator
        print("✅ main modules imported")
        
        from utils import validate_config, format_file_size
        print("✅ utils imported")
        
        from datetime import datetime
        print("✅ datetime imported")
        
        import multiprocessing
        print("✅ multiprocessing imported")
        
        # Test Redis connection
        REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        redis_conn = redis.Redis.from_url(REDIS_URL)
        redis_conn.ping()
        print("✅ Redis connection works")
        
        # Test log_progress function
        from tasks import log_progress
        log_progress('test_task', 'Test message')
        print("✅ log_progress function works")
        
        print("🎉 All imports and basic functionality work!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports() 