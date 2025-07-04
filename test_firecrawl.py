#!/usr/bin/env python3
"""
Test script for Firecrawl integration
"""

import os
import logging
from main_firecrawl import FirecrawlLLMsGenerator, get_default_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_firecrawl_integration():
    """Test the Firecrawl integration."""
    
    # Check if Firecrawl API key is available
    api_key = os.environ.get('FIRECRAWL_API_KEY')
    if not api_key:
        print("❌ FIRECRAWL_API_KEY environment variable not set")
        print("Please set your Firecrawl API key:")
        print("export FIRECRAWL_API_KEY='your-api-key-here'")
        return False
    
    # Test configuration
    config = get_default_config()
    config.update({
        'firecrawl_api_key': api_key,
        'site_name': 'Test Website',
        'max_pages_to_process': 3,  # Small limit for testing
        'max_content_length': 300,
        'only_main_content': True
    })
    
    try:
        print("🚀 Testing Firecrawl integration...")
        
        # Initialize generator
        generator = FirecrawlLLMsGenerator(config)
        print("✅ Firecrawl generator initialized")
        
        # Test with a simple website
        test_url = "https://example.com"
        print(f"📄 Testing with: {test_url}")
        
        # Generate llms.txt using simple method
        output_path = generator.generate_llms_txt_simple(test_url, "Example Website")
        
        if output_path:
            print(f"✅ Successfully generated llms.txt: {output_path}")
            
            # Read and display a snippet of the generated file
            try:
                with open(output_path, 'r') as f:
                    content = f.read()
                    print(f"📄 Generated content preview ({len(content)} chars):")
                    print("=" * 50)
                    print(content[:500] + "..." if len(content) > 500 else content)
                    print("=" * 50)
            except Exception as e:
                print(f"⚠️ Could not read generated file: {e}")
            
            return True
        else:
            print("❌ Failed to generate llms.txt")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def test_firecrawl_scraper():
    """Test just the Firecrawl scraper component."""
    
    api_key = os.environ.get('FIRECRAWL_API_KEY')
    if not api_key:
        print("❌ FIRECRAWL_API_KEY not set")
        return False
    
    try:
        from firecrawl_scraper import FirecrawlScraper
        
        config = {
            'firecrawl_api_key': api_key,
            'max_pages_to_process': 2,
            'max_content_length': 200
        }
        
        print("🔧 Testing Firecrawl scraper...")
        scraper = FirecrawlScraper(config)
        
        # Test single URL scraping
        test_url = "https://example.com"
        content = scraper.scrape_content(test_url, config)
        
        if content:
            print(f"✅ Successfully scraped: {content['title']}")
            print(f"📝 Content length: {len(content['content'])} chars")
            print(f"🏷️ Keywords: {content['keywords']}")
            return True
        else:
            print("❌ Failed to scrape content")
            return False
            
    except Exception as e:
        print(f"❌ Error testing scraper: {e}")
        return False

def test_firecrawl_crawl():
    """Test Firecrawl crawling functionality."""
    
    api_key = os.environ.get('FIRECRAWL_API_KEY')
    if not api_key:
        print("❌ FIRECRAWL_API_KEY not set")
        return False
    
    try:
        from firecrawl_scraper import FirecrawlScraper
        
        config = {
            'firecrawl_api_key': api_key,
            'max_pages_to_process': 3,
            'max_content_length': 200,
            'crawl_max_wait_time': 120  # 2 minutes for testing
        }
        
        print("🕷️ Testing Firecrawl crawling...")
        scraper = FirecrawlScraper(config)
        
        # Test crawling a small website
        test_url = "https://example.com"
        scraped_content = scraper.crawl_website(test_url, config)
        
        if scraped_content:
            print(f"✅ Successfully crawled {len(scraped_content)} pages")
            for url, content in scraped_content.items():
                print(f"  📄 {url}: {content['title'][:50]}...")
            return True
        else:
            print("❌ Failed to crawl website")
            return False
            
    except Exception as e:
        print(f"❌ Error testing crawl: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Firecrawl Integration Test Suite")
    print("=" * 50)
    
    # Test individual components
    print("\n1. Testing Firecrawl scraper...")
    scraper_success = test_firecrawl_scraper()
    
    print("\n2. Testing Firecrawl crawling...")
    crawl_success = test_firecrawl_crawl()
    
    print("\n3. Testing full integration...")
    integration_success = test_firecrawl_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Scraper: {'✅ PASS' if scraper_success else '❌ FAIL'}")
    print(f"  Crawler: {'✅ PASS' if crawl_success else '❌ FAIL'}")
    print(f"  Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
    
    if all([scraper_success, crawl_success, integration_success]):
        print("\n🎉 All tests passed! Firecrawl integration is working.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.") 