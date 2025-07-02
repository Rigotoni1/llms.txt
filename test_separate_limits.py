#!/usr/bin/env python3
"""
Test script to verify that max_pages and max_blogs are now separate limits.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import main
import yaml

def test_separate_limits():
    """Test that max_pages and max_blogs are processed independently."""
    
    # Create a test config with separate limits
    test_config = {
        'sitemap_url': 'https://aimodelagency.com/sitemap_index.xml',
        'site_name': 'Test Site',
        'max_pages_to_process': 5,  # Should process 5 pages
        'max_blogs': 3,             # Should process 3 blogs
        'max_content_length': 100,
        'request_delay': 0.1,
        'respect_robots_txt': False
    }
    
    # Save test config
    with open('test_config.yaml', 'w') as f:
        yaml.dump(test_config, f)
    
    print("🧪 Testing separate limits for max_pages and max_blogs")
    print(f"📋 Config: max_pages={test_config['max_pages_to_process']}, max_blogs={test_config['max_blogs']}")
    print(f"📊 Expected total: {test_config['max_pages_to_process'] + test_config['max_blogs']} items")
    print("=" * 60)
    
    try:
        # Run the main function
        main(
            sitemap_url=test_config['sitemap_url'],
            site_name=test_config['site_name'],
            auto_detect=False
        )
        
        print("✅ Test completed successfully!")
        print("📁 Check the generated file in outputs/ directory")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        # Clean up test config
        if os.path.exists('test_config.yaml'):
            os.remove('test_config.yaml')
    
    return True

if __name__ == "__main__":
    test_separate_limits() 