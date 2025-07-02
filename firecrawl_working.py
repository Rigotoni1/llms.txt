#!/usr/bin/env python3
"""
Working Firecrawl-based content scraper for LLMs.txt Generator
Based on actual API structure
"""

import os
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

try:
    from firecrawl import FirecrawlApp
    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False
    print("Warning: Firecrawl not installed. Run: pip install firecrawl-py")

logger = logging.getLogger(__name__)

class WorkingFirecrawlScraper:
    """Working Firecrawl-based content scraper."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('firecrawl_api_key') or os.environ.get('FIRECRAWL_API_KEY')
        
        if not self.api_key:
            raise ValueError("Firecrawl API key required. Set firecrawl_api_key in config or FIRECRAWL_API_KEY environment variable.")
        
        if not FIRECRAWL_AVAILABLE:
            raise ImportError("Firecrawl not installed. Run: pip install firecrawl-py")
        
        self.app = FirecrawlApp(api_key=self.api_key)
        logger.info("Working Firecrawl scraper initialized")
    
    def scrape_content(self, url: str, config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Scrape content from a URL using Firecrawl."""
        if config is None:
            config = self.config
        
        try:
            logger.info(f"Scraping content from: {url}")
            
            # Use Firecrawl to scrape the page
            result = self.app.scrape_url(
                url,
                formats=['markdown', 'html'],
                only_main_content=config.get('only_main_content', True),
                timeout=config.get('firecrawl_timeout', 120000)
            )
            
            if not result or not result.success:
                logger.warning(f"Firecrawl failed to scrape {url}")
                return None
            
            # Extract content from result
            markdown_content = result.markdown or ""
            title = result.title or ""
            description = result.description or ""
            
            content = {
                'url': url,
                'title': title,
                'description': description,
                'content': markdown_content,
                'keywords': self._extract_keywords_from_text(markdown_content),
                'scraped_at': datetime.now().isoformat(),
                'source_type': self._detect_source_type(url, title, description)
            }
            
            # Apply content length limits
            max_length = config.get('max_content_length', 500)
            if content['content'] and len(content['content']) > max_length:
                content['content'] = content['content'][:max_length] + '...'
            
            logger.info(f"Successfully extracted content from {url}: {len(content.get('content', ''))} chars")
            return content
            
        except Exception as e:
            logger.error(f"Error scraping {url} with Firecrawl: {e}")
            return None
    
    def scrape_content_with_lastmod(self, url: str, lastmod: str, config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Scrape content from a URL with lastmod date."""
        content = self.scrape_content(url, config)
        if content and lastmod:
            content['lastmod'] = lastmod
        return content
    
    def crawl_website(self, base_url: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Crawl an entire website using Firecrawl's crawl functionality."""
        if config is None:
            config = self.config
        
        try:
            logger.info(f"Starting Firecrawl crawl for: {base_url}")
            
            # Configure crawl options
            limit = config.get('max_pages_to_process', 10)
            
            # Start the crawl (using correct API parameters)
            crawl_result = self.app.crawl_url(
                base_url,
                limit=limit
            )
            
            if not crawl_result:
                logger.error(f"Failed to start crawl for {base_url}")
                return {}
            
            # Get crawl ID
            crawl_id = crawl_result.id
            logger.info(f"Crawl started with ID: {crawl_id}")
            
            # Poll for completion
            scraped_content = {}
            max_wait_time = config.get('crawl_max_wait_time', 300)  # 5 minutes
            poll_interval = config.get('crawl_poll_interval', 10)  # 10 seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                status_result = self.app.check_crawl_status(crawl_id)
                
                if not status_result:
                    logger.warning(f"Could not check crawl status for {crawl_id}")
                    time.sleep(poll_interval)
                    continue
                
                status = status_result.status
                logger.info(f"Crawl status: {status}")
                
                if status == 'completed':
                    # Process completed crawl data
                    data = status_result.data or []
                    
                    for page_data in data:
                        # Extract URL and content from page data
                        url = page_data.url if hasattr(page_data, 'url') else ""
                        
                        if url:
                            content = self._process_crawl_page_data(page_data, url)
                            if content:
                                scraped_content[url] = content
                    
                    logger.info(f"Crawl completed: {len(scraped_content)} pages scraped")
                    break
                
                elif status == 'failed':
                    logger.error(f"Crawl failed for {base_url}")
                    break
                
                # Wait before next poll
                time.sleep(poll_interval)
            
            return scraped_content
            
        except Exception as e:
            logger.error(f"Error crawling {base_url} with Firecrawl: {e}")
            return {}
    
    def _process_crawl_page_data(self, page_data: Any, url: str) -> Optional[Dict[str, Any]]:
        """Process a single page's data from a crawl result."""
        try:
            # Extract content from page data
            markdown_content = page_data.markdown if hasattr(page_data, 'markdown') else ""
            title = page_data.title if hasattr(page_data, 'title') else ""
            description = page_data.description if hasattr(page_data, 'description') else ""
            
            content = {
                'url': url,
                'title': title,
                'description': description,
                'content': markdown_content,
                'keywords': self._extract_keywords_from_text(markdown_content),
                'scraped_at': datetime.now().isoformat(),
                'source_type': self._detect_source_type(url, title, description)
            }
            
            # Apply content length limits
            max_length = self.config.get('max_content_length', 500)
            if content['content'] and len(content['content']) > max_length:
                content['content'] = content['content'][:max_length] + '...'
            
            return content
            
        except Exception as e:
            logger.error(f"Error processing crawl page data for {url}: {e}")
            return None
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract keywords from text content."""
        if not text:
            return []
        
        # Simple keyword extraction
        import re
        words = re.findall(r'\b\w{4,}\b', text.lower())
        from collections import Counter
        word_freq = Counter(words)
        keywords = [word for word, _ in word_freq.most_common(5)]
        
        return list(set(keywords))  # Remove duplicates
    
    def _detect_source_type(self, url: str, title: str, description: str) -> str:
        """Detect the source type of a page (blog, product, page)."""
        url_lower = url.lower()
        title_lower = title.lower()
        description_lower = description.lower()
        
        # Check for product indicators
        product_indicators = ['product', 'shop', 'buy', 'purchase', 'price', 'cart', 'store']
        if any(indicator in url_lower or indicator in title_lower or indicator in description_lower 
               for indicator in product_indicators):
            return 'product'
        
        # Check for blog indicators
        blog_indicators = ['blog', 'post', 'article', 'news', 'story', 'tutorial']
        if any(indicator in url_lower or indicator in title_lower or indicator in description_lower 
               for indicator in blog_indicators):
            return 'blog'
        
        # Default to page
        return 'page'


# Test the working scraper
if __name__ == "__main__":
    # Test configuration
    test_config = {
        'firecrawl_api_key': os.environ.get('FIRECRAWL_API_KEY'),
        'max_pages_to_process': 5,
        'max_content_length': 500,
        'only_main_content': True,
        'firecrawl_timeout': 120000
    }
    
    # Test the scraper
    try:
        scraper = WorkingFirecrawlScraper(test_config)
        
        # Test single URL scraping
        test_url = "https://example.com"
        content = scraper.scrape_content(test_url, test_config)
        
        if content:
            print(f"✅ Successfully scraped: {content['title']}")
            print(f"Content length: {len(content['content'])} chars")
            print(f"Keywords: {content['keywords']}")
            print(f"Source type: {content['source_type']}")
        else:
            print("❌ Failed to scrape content")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc() 