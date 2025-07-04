#!/usr/bin/env python3
"""
Test Firecrawl with a more traditional website
"""

import os
import logging
from firecrawl_working import WorkingFirecrawlScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_traditional_site():
    """Test Firecrawl with a traditional website."""
    
    api_key = os.environ.get('FIRECRAWL_API_KEY')
    if not api_key:
        print("❌ FIRECRAWL_API_KEY not set")
        return
    
    # Configuration
    config = {
        'firecrawl_api_key': api_key,
        'max_pages_to_process': 5,
        'max_content_length': 1000,
        'only_main_content': True,
        'firecrawl_timeout': 120000
    }
    
    try:
        print("🚀 Testing Firecrawl with Traditional Website")
        print("=" * 60)
        
        # Initialize scraper
        scraper = WorkingFirecrawlScraper(config)
        print("✅ Firecrawl scraper initialized")
        
        # Test with a traditional website that has good content
        test_urls = [
            "https://www.apple.com/",
            "https://www.github.com/",
            "https://www.stackoverflow.com/",
            "https://www.wikipedia.org/"
        ]
        
        print(f"\n📄 Testing traditional websites...")
        scraped_content = {}
        
        for i, url in enumerate(test_urls, 1):
            print(f"\n{i}. Testing: {url}")
            content = scraper.scrape_content(url, config)
            
            if content:
                scraped_content[url] = content
                print(f"   ✅ Title: {content['title']}")
                print(f"   📝 Content: {len(content['content'])} chars")
                print(f"   🏷️ Keywords: {content['keywords']}")
                print(f"   📂 Type: {content['source_type']}")
                print(f"   📄 Preview: {content['content'][:300]}...")
            else:
                print(f"   ❌ Failed to scrape")
        
        # Show detailed results
        if scraped_content:
            print(f"\n🎯 Detailed Results:")
            print("=" * 60)
            
            for url, content in scraped_content.items():
                print(f"\n📄 {url}")
                print(f"Title: {content['title']}")
                print(f"Type: {content['source_type']}")
                print(f"Keywords: {content['keywords']}")
                print(f"Content Length: {len(content['content'])} chars")
                print(f"Content Preview:")
                print("-" * 40)
                print(content['content'][:500] + "..." if len(content['content']) > 500 else content['content'])
                print("-" * 40)
        
        print(f"\n📊 Summary:")
        print(f"   Pages successfully scraped: {len(scraped_content)}")
        print(f"   Average content length: {sum(len(c['content']) for c in scraped_content.values()) // len(scraped_content) if scraped_content else 0} chars")
        
        print(f"\n🎉 Traditional website test completed!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_traditional_site() 