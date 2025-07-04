#!/usr/bin/env python3
"""
Demo script showing the working Firecrawl integration
"""

import os
import logging
from firecrawl_working import WorkingFirecrawlScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demo_firecrawl():
    """Demo the working Firecrawl integration."""
    
    api_key = os.environ.get('FIRECRAWL_API_KEY')
    if not api_key:
        print("❌ FIRECRAWL_API_KEY not set")
        return
    
    # Configuration
    config = {
        'firecrawl_api_key': api_key,
        'max_pages_to_process': 3,
        'max_content_length': 300,
        'only_main_content': True,
        'firecrawl_timeout': 120000
    }
    
    try:
        print("🚀 Firecrawl Integration Demo")
        print("=" * 50)
        
        # Initialize scraper
        scraper = WorkingFirecrawlScraper(config)
        print("✅ Firecrawl scraper initialized")
        
        # Test URLs
        test_urls = [
            "https://example.com",
            "https://httpbin.org/html",
            "https://jsonplaceholder.typicode.com/posts/1"
        ]
        
        print(f"\n📄 Testing single URL scraping...")
        for i, url in enumerate(test_urls, 1):
            print(f"\n{i}. Testing: {url}")
            content = scraper.scrape_content(url, config)
            
            if content:
                print(f"   ✅ Title: {content['title'][:50]}...")
                print(f"   📝 Content: {len(content['content'])} chars")
                print(f"   🏷️ Keywords: {content['keywords']}")
                print(f"   📂 Type: {content['source_type']}")
            else:
                print(f"   ❌ Failed to scrape")
        
        # Test crawling
        print(f"\n🕷️ Testing website crawling...")
        crawl_url = "https://example.com"
        print(f"Crawling: {crawl_url}")
        
        scraped_content = scraper.crawl_website(crawl_url, config)
        
        if scraped_content:
            print(f"✅ Successfully crawled {len(scraped_content)} pages")
            for url, content in scraped_content.items():
                print(f"   📄 {url}: {content['title'][:50]}...")
        else:
            print("❌ Failed to crawl website")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"\n💡 Key Benefits:")
        print(f"   • Simple API: Just 3 lines to scrape a page")
        print(f"   • Automatic content extraction")
        print(f"   • Built-in markdown formatting")
        print(f"   • JavaScript support")
        print(f"   • Anti-bot protection")
        print(f"   • Reliable and maintained")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_firecrawl() 