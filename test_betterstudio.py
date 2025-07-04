#!/usr/bin/env python3
"""
Test Firecrawl integration with betterstudio.io
"""

import os
import logging
from firecrawl_working import WorkingFirecrawlScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_betterstudio():
    """Test Firecrawl with betterstudio.io."""
    
    api_key = os.environ.get('FIRECRAWL_API_KEY')
    if not api_key:
        print("❌ FIRECRAWL_API_KEY not set")
        return
    
    # Configuration
    config = {
        'firecrawl_api_key': api_key,
        'max_pages_to_process': 5,
        'max_content_length': 1000,  # Longer content for better testing
        'only_main_content': True,
        'firecrawl_timeout': 120000
    }
    
    try:
        print("🚀 Testing Firecrawl with BetterStudio.io")
        print("=" * 60)
        
        # Initialize scraper
        scraper = WorkingFirecrawlScraper(config)
        print("✅ Firecrawl scraper initialized")
        
        # Test URLs from BetterStudio
        test_urls = [
            "https://www.betterstudio.io/",
            "https://www.betterstudio.io/about",
            "https://www.betterstudio.io/services",
            "https://www.betterstudio.io/contact"
        ]
        
        print(f"\n📄 Testing individual pages...")
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
                print(f"   📄 Preview: {content['content'][:200]}...")
            else:
                print(f"   ❌ Failed to scrape")
        
        # Test crawling the entire site
        print(f"\n🕷️ Testing full site crawling...")
        print(f"Crawling: https://www.betterstudio.io")
        
        crawled_content = scraper.crawl_website("https://www.betterstudio.io", config)
        
        if crawled_content:
            print(f"✅ Successfully crawled {len(crawled_content)} pages")
            for url, content in crawled_content.items():
                print(f"   📄 {url}: {content['title'][:50]}...")
        else:
            print("❌ Failed to crawl website")
        
        # Show summary
        print(f"\n📊 Summary:")
        print(f"   Individual pages scraped: {len(scraped_content)}")
        print(f"   Crawled pages: {len(crawled_content)}")
        print(f"   Total unique pages: {len(set(list(scraped_content.keys()) + list(crawled_content.keys())))}")
        
        # Show sample content
        if scraped_content:
            print(f"\n🎯 Sample Content from BetterStudio:")
            print("=" * 60)
            sample_url = list(scraped_content.keys())[0]
            sample_content = scraped_content[sample_url]
            
            print(f"URL: {sample_url}")
            print(f"Title: {sample_content['title']}")
            print(f"Type: {sample_content['source_type']}")
            print(f"Keywords: {sample_content['keywords']}")
            print(f"\nContent Preview:")
            print("-" * 40)
            print(sample_content['content'][:500] + "..." if len(sample_content['content']) > 500 else sample_content['content'])
            print("-" * 40)
        
        print(f"\n🎉 BetterStudio test completed!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_betterstudio() 