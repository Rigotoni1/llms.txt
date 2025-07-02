#!/usr/bin/env python3
"""
Test script for scalable batch processing
"""

import os
import sys
import time
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tasks import generate_llms_background, get_queue_status
from utils import load_config

def test_scalable_processing():
    """Test the scalable processing system."""
    print("🚀 Testing Scalable Batch Processing System")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    
    # Test configuration for a large site
    test_config = {
        'sitemap_url': 'https://www.betterpic.io/sitemap.xml',
        'site_name': 'BetterPic Test',
        'site_description': 'AI headshot generation platform',
        'max_pages_to_process': 100,  # Large number for testing
        'max_blogs': 50,
        'max_products': 25,
        'respect_robots_txt': False,
        'request_delay': 0.5,  # Faster processing for testing
        'batch_processing': {
            'batch_size': 25,  # Smaller batches for testing
            'max_concurrent_batches': 5,
            'max_workers_per_batch': 3
        }
    }
    
    # Generate unique task ID
    task_id = f"test_{int(time.time())}"
    
    print(f"📋 Task ID: {task_id}")
    print(f"🎯 Target: {test_config['sitemap_url']}")
    print(f"📊 Expected URLs: ~{test_config['max_pages_to_process'] + test_config['max_blogs'] + test_config['max_products']}")
    print(f"⚡ Batch Size: {test_config['batch_processing']['batch_size']}")
    print(f"🔄 Concurrent Batches: {test_config['batch_processing']['max_concurrent_batches']}")
    print(f"🧵 Workers per Batch: {test_config['batch_processing']['max_workers_per_batch']}")
    
    print("\n🔄 Starting scalable processing...")
    start_time = time.time()
    
    try:
        # Start the background job
        result = generate_llms_background(test_config, task_id)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n✅ Processing completed!")
        print(f"⏱️  Total time: {duration:.2f} seconds")
        print(f"📁 Output file: {result}")
        
        # Show queue status
        print("\n📊 Final Queue Status:")
        queue_status = get_queue_status()
        for key, value in queue_status.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"\n❌ Processing failed: {str(e)}")
        return False
    
    return True

def monitor_queue_status():
    """Monitor queue status in real-time."""
    print("\n📊 Queue Status Monitor")
    print("=" * 30)
    
    try:
        while True:
            status = get_queue_status()
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            print(f"\n[{timestamp}] Queue Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
            
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        monitor_queue_status()
    else:
        test_scalable_processing() 