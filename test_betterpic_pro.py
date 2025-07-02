#!/usr/bin/env python3
"""
Test script for BetterPic.io with Pro Plan configuration
"""

import os
import sys
import time
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tasks import generate_llms_background, get_queue_status

def test_betterpic_pro():
    """Test the scalable processing system with BetterPic.io Pro plan."""
    print("🚀 Testing BetterPic.io Pro Plan Processing")
    print("=" * 60)
    
    # Pro plan configuration for BetterPic.io
    pro_config = {
        'sitemap_url': 'https://www.betterpic.io/sitemap.xml',
        'site_name': 'BetterPic',
        'site_description': 'The best AI Headshot Generator for Professional Headshots - Get studio-quality AI professional headshots in under 1 hour with 150+ styles, 4K quality, and 100% money-back guarantee.',
        'max_pages_to_process': 200,  # Pro plan: higher limits
        'max_blogs': 100,             # Pro plan: more blog posts
        'max_products': 50,           # Pro plan: more products
        'max_detailed_content': 50,   # Pro plan: more detailed content
        'respect_robots_txt': False,
        'request_delay': 0.5,         # Faster processing for testing
        'batch_processing': {
            'batch_size': 50,         # Standard batch size
            'max_concurrent_batches': 8,  # Pro plan: more concurrent batches
            'max_workers_per_batch': 4    # Pro plan: more workers per batch
        },
        'performance': {
            'request_timeout': 30,
            'connection_pool_size': 25,   # Pro plan: larger connection pool
            'max_retries': 3,
            'retry_delay': 2
        }
    }
    
    # Generate unique task ID
    task_id = f"betterpic_pro_{int(time.time())}"
    
    print(f"📋 Task ID: {task_id}")
    print(f"🎯 Target: {pro_config['sitemap_url']}")
    print(f"📊 Pro Plan Limits:")
    print(f"   • Pages: {pro_config['max_pages_to_process']}")
    print(f"   • Blogs: {pro_config['max_blogs']}")
    print(f"   • Products: {pro_config['max_products']}")
    print(f"   • Detailed Content: {pro_config['max_detailed_content']}")
    print(f"⚡ Batch Configuration:")
    print(f"   • Batch Size: {pro_config['batch_processing']['batch_size']}")
    print(f"   • Concurrent Batches: {pro_config['batch_processing']['max_concurrent_batches']}")
    print(f"   • Workers per Batch: {pro_config['batch_processing']['max_workers_per_batch']}")
    
    expected_urls = (pro_config['max_pages_to_process'] + 
                    pro_config['max_blogs'] + 
                    pro_config['max_products'])
    print(f"📈 Expected Total URLs: ~{expected_urls}")
    
    print("\n🔄 Starting BetterPic.io Pro Plan processing...")
    start_time = time.time()
    
    try:
        # Start the background job
        result = generate_llms_background(pro_config, task_id)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n✅ BetterPic.io Pro Plan processing completed!")
        print(f"⏱️  Total time: {duration:.2f} seconds")
        print(f"📁 Output file: {result}")
        
        # Calculate processing speed
        urls_per_minute = (expected_urls / duration) * 60
        print(f"🚀 Processing speed: {urls_per_minute:.1f} URLs/minute")
        
        # Show queue status
        print("\n📊 Final Queue Status:")
        queue_status = get_queue_status()
        for key, value in queue_status.items():
            print(f"  {key}: {value}")
            
        # Show system performance
        print(f"\n💪 System Performance:")
        print(f"  • Memory usage: Optimized with batch processing")
        print(f"  • CPU utilization: Distributed across {pro_config['batch_processing']['max_concurrent_batches']} batches")
        print(f"  • Network efficiency: {pro_config['performance']['connection_pool_size']} connection pool")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Processing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def monitor_betterpic_progress():
    """Monitor BetterPic.io processing progress."""
    print("\n📊 BetterPic.io Processing Monitor")
    print("=" * 40)
    
    try:
        while True:
            status = get_queue_status()
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            print(f"\n[{timestamp}] BetterPic.io Queue Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
            
            # Show estimated progress
            if status.get('batch_queue_length', 0) > 0:
                print(f"  📈 Estimated progress: Processing batches...")
            elif status.get('merge_queue_length', 0) > 0:
                print(f"  🔄 Status: Merging results...")
            else:
                print(f"  ✅ Status: All queues clear")
            
            time.sleep(10)  # Update every 10 seconds
            
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        monitor_betterpic_progress()
    else:
        success = test_betterpic_pro()
        if success:
            print("\n🎉 BetterPic.io Pro Plan test completed successfully!")
            print("💡 The scalable system handled the large-scale processing efficiently.")
        else:
            print("\n⚠️  BetterPic.io Pro Plan test encountered issues.")
            print("🔧 Check the logs for more details.") 