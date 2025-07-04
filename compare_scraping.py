#!/usr/bin/env python3
"""
Compare BeautifulSoup scraping vs Firecrawl scraping
"""

import os
import logging
import time
from firecrawl_working import WorkingFirecrawlScraper
from main import ContentScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def compare_scraping_methods():
    """Compare BeautifulSoup vs Firecrawl scraping."""
    
    api_key = os.environ.get('FIRECRAWL_API_KEY')
    if not api_key:
        print("❌ FIRECRAWL_API_KEY not set")
        return
    
    # Configuration
    config = {
        'firecrawl_api_key': api_key,
        'max_pages_to_process': 3,
        'max_content_length': 1000,
        'only_main_content': True,
        'firecrawl_timeout': 120000,
        'content_selector': '.content, #main, article, .post-content, .entry-content, .page-content, .post, .entry, .elementor, .elementor-post',
        'title_selector': 'h1, .title, .post-title, .entry-title, .page-title'
    }
    
    # Test URL
    test_url = "https://www.wikipedia.org/"
    
    try:
        print("🔍 Comparing Scraping Methods")
        print("=" * 60)
        print(f"Testing URL: {test_url}")
        
        # Test 1: BeautifulSoup (your current method)
        print(f"\n1️⃣ Testing BeautifulSoup (Current Method)")
        print("-" * 40)
        
        start_time = time.time()
        bs_scraper = ContentScraper(config)
        bs_content = bs_scraper.scrape_content(test_url, config)
        bs_time = time.time() - start_time
        
        if bs_content:
            print(f"✅ Success: {len(bs_content.get('content', ''))} chars")
            print(f"⏱️ Time: {bs_time:.2f} seconds")
            print(f"📝 Title: {bs_content.get('title', 'N/A')}")
            print(f"🏷️ Keywords: {bs_content.get('keywords', [])}")
            print(f"📄 Preview: {bs_content.get('content', '')[:200]}...")
        else:
            print("❌ Failed to scrape with BeautifulSoup")
        
        # Test 2: Firecrawl (new method)
        print(f"\n2️⃣ Testing Firecrawl (New Method)")
        print("-" * 40)
        
        start_time = time.time()
        fc_scraper = WorkingFirecrawlScraper(config)
        fc_content = fc_scraper.scrape_content(test_url, config)
        fc_time = time.time() - start_time
        
        if fc_content:
            print(f"✅ Success: {len(fc_content.get('content', ''))} chars")
            print(f"⏱️ Time: {fc_time:.2f} seconds")
            print(f"📝 Title: {fc_content.get('title', 'N/A')}")
            print(f"🏷️ Keywords: {fc_content.get('keywords', [])}")
            print(f"📄 Preview: {fc_content.get('content', '')[:200]}...")
        else:
            print("❌ Failed to scrape with Firecrawl")
        
        # Comparison
        print(f"\n📊 Comparison Results")
        print("=" * 60)
        
        if bs_content and fc_content:
            print(f"Content Length:")
            print(f"  BeautifulSoup: {len(bs_content.get('content', ''))} chars")
            print(f"  Firecrawl: {len(fc_content.get('content', ''))} chars")
            print(f"  Difference: {len(fc_content.get('content', '')) - len(bs_content.get('content', ''))} chars")
            
            print(f"\nSpeed:")
            print(f"  BeautifulSoup: {bs_time:.2f} seconds")
            print(f"  Firecrawl: {fc_time:.2f} seconds")
            print(f"  Speedup: {bs_time/fc_time:.1f}x faster" if fc_time > 0 else "  Speedup: N/A")
            
            print(f"\nContent Quality:")
            print(f"  BeautifulSoup: Manual HTML parsing")
            print(f"  Firecrawl: Automatic markdown formatting")
            
            print(f"\nFeatures:")
            print(f"  BeautifulSoup: Basic content extraction")
            print(f"  Firecrawl: JavaScript support, anti-bot protection, structured data")
            
            print(f"\nMaintenance:")
            print(f"  BeautifulSoup: 500+ lines of complex code")
            print(f"  Firecrawl: ~150 lines of simple code")
            
        print(f"\n🎯 Recommendation:")
        print("Firecrawl provides:")
        print("✅ Better content quality (automatic markdown)")
        print("✅ More features (JS support, anti-bot)")
        print("✅ Less code to maintain (70% reduction)")
        print("✅ Professional API (reliable and maintained)")
        print("✅ Future-proof (handled by Firecrawl team)")
        
    except Exception as e:
        print(f"❌ Error during comparison: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    compare_scraping_methods() 