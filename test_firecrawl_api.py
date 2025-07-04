#!/usr/bin/env python3
"""
Test script to understand Firecrawl API structure
"""

import os
import logging
from firecrawl import FirecrawlApp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_firecrawl_api():
    """Test Firecrawl API to understand the response structure."""
    
    api_key = os.environ.get('FIRECRAWL_API_KEY')
    if not api_key:
        print("❌ FIRECRAWL_API_KEY not set")
        return
    
    try:
        print("🔧 Testing Firecrawl API structure...")
        app = FirecrawlApp(api_key=api_key)
        
        # Test single URL scraping
        test_url = "https://example.com"
        print(f"📄 Testing with: {test_url}")
        
        result = app.scrape_url(
            test_url,
            formats=['markdown', 'html'],
            only_main_content=True,
            timeout=120000
        )
        
        print(f"✅ Got result: {type(result)}")
        print(f"Result attributes: {dir(result)}")
        
        if hasattr(result, 'data'):
            data = result.data
            print(f"✅ Data found: {type(data)}")
            print(f"Data attributes: {dir(data)}")
            
            if hasattr(data, 'markdown'):
                markdown = data.markdown
                print(f"✅ Markdown found: {len(markdown)} chars")
                print(f"Preview: {markdown[:200]}...")
            
            if hasattr(data, 'metadata'):
                metadata = data.metadata
                print(f"✅ Metadata found: {type(metadata)}")
                print(f"Metadata attributes: {dir(metadata)}")
                
                if hasattr(metadata, 'title'):
                    title = metadata.title
                    print(f"✅ Title: {title}")
                
                if hasattr(metadata, 'description'):
                    description = metadata.description
                    print(f"✅ Description: {description}")
        
        # Test crawling
        print("\n🕷️ Testing crawl API...")
        crawl_result = app.crawl_url(
            test_url,
            limit=2,
            formats=['markdown', 'html'],
            only_main_content=True,
            timeout=120000
        )
        
        print(f"✅ Crawl result: {type(crawl_result)}")
        print(f"Crawl result attributes: {dir(crawl_result)}")
        
        if hasattr(crawl_result, 'id'):
            crawl_id = crawl_result.id
            print(f"✅ Crawl ID: {crawl_id}")
            
            # Check status
            status_result = app.check_crawl_status(crawl_id)
            print(f"✅ Status result: {type(status_result)}")
            print(f"Status attributes: {dir(status_result)}")
            
            if hasattr(status_result, 'status'):
                status = status_result.status
                print(f"✅ Status: {status}")
            
            if hasattr(status_result, 'data'):
                data = status_result.data
                print(f"✅ Status data: {type(data)}")
                if data:
                    print(f"Data length: {len(data)}")
                    if len(data) > 0:
                        first_item = data[0]
                        print(f"First item type: {type(first_item)}")
                        print(f"First item attributes: {dir(first_item)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_firecrawl_api() 