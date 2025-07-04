#!/usr/bin/env python3
"""
Firecrawl-based content scraper for LLMs.txt Generator
Replaces the complex BeautifulSoup scraping with Firecrawl's API
"""

import os
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import requests

try:
    from firecrawl import FirecrawlApp, ScrapeOptions, JsonConfig
    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False
    print("Warning: Firecrawl not installed. Run: pip install firecrawl-py")

logger = logging.getLogger(__name__)

class FirecrawlScraper:
    """Firecrawl-based content scraper that replaces the complex BeautifulSoup scraping."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('firecrawl_api_key') or os.environ.get('FIRECRAWL_API_KEY')
        
        if not self.api_key:
            raise ValueError("Firecrawl API key required. Set firecrawl_api_key in config or FIRECRAWL_API_KEY environment variable.")
        
        if not FIRECRAWL_AVAILABLE:
            raise ImportError("Firecrawl not installed. Run: pip install firecrawl-py")
        
        self.app = FirecrawlApp(api_key=self.api_key)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LLMs.txt Generator Bot (+https://github.com/your-repo)'
        })
        
        # Firecrawl configuration
        self.scrape_options = ScrapeOptions(
            formats=['markdown', 'html'],
            only_main_content=config.get('only_main_content', True),
            timeout=config.get('firecrawl_timeout', 120000),  # 2 minutes
            wait_for=config.get('firecrawl_wait_for', 2000),  # 2 seconds
        )
        
        logger.info("Firecrawl scraper initialized")
    
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
            
            if not result or not result.get('success'):
                logger.warning(f"Firecrawl failed to scrape {url}")
                return None
            
            data = result.get('data', {})
            metadata = data.get('metadata', {})
            
            # Extract content from Firecrawl response
            content = {
                'url': url,
                'title': metadata.get('title', ''),
                'description': metadata.get('description', ''),
                'content': data.get('markdown', ''),
                'html': data.get('html', ''),
                'keywords': self._extract_keywords_from_metadata(metadata),
                'scraped_at': datetime.now().isoformat(),
                'source_type': self._detect_source_type(url, metadata)
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
            
            # Start the crawl
            crawl_result = self.app.crawl_url(
                base_url,
                limit=limit,
                formats=['markdown', 'html'],
                only_main_content=config.get('only_main_content', True),
                timeout=config.get('firecrawl_timeout', 120000)
            )
            
            if not crawl_result or not crawl_result.get('success'):
                logger.error(f"Failed to start crawl for {base_url}")
                return {}
            
            crawl_id = crawl_result.get('id')
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
                
                # Handle the status response object
                if hasattr(status_result, 'status'):
                    status = status_result.status
                else:
                    status = getattr(status_result, 'status', 'unknown')
                
                logger.info(f"Crawl status: {status}")
                
                if status == 'completed':
                    # Process completed crawl data
                    if hasattr(status_result, 'data'):
                        data = status_result.data
                    else:
                        data = getattr(status_result, 'data', [])
                    
                    for page_data in data:
                        if hasattr(page_data, 'metadata'):
                            metadata = page_data.metadata
                        else:
                            metadata = getattr(page_data, 'metadata', {})
                        
                        url = getattr(metadata, 'sourceURL', '') if hasattr(metadata, 'sourceURL') else metadata.get('sourceURL', '')
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
    
    def _process_crawl_page_data(self, page_data: Dict[str, Any], url: str) -> Optional[Dict[str, Any]]:
        """Process a single page's data from a crawl result."""
        try:
            metadata = page_data.get('metadata', {})
            
            content = {
                'url': url,
                'title': metadata.get('title', ''),
                'description': metadata.get('description', ''),
                'content': page_data.get('markdown', ''),
                'html': page_data.get('html', ''),
                'keywords': self._extract_keywords_from_metadata(metadata),
                'scraped_at': datetime.now().isoformat(),
                'source_type': self._detect_source_type(url, metadata)
            }
            
            # Apply content length limits
            max_length = self.config.get('max_content_length', 500)
            if content['content'] and len(content['content']) > max_length:
                content['content'] = content['content'][:max_length] + '...'
            
            return content
            
        except Exception as e:
            logger.error(f"Error processing crawl page data for {url}: {e}")
            return None
    
    def _extract_keywords_from_metadata(self, metadata: Dict[str, Any]) -> List[str]:
        """Extract keywords from Firecrawl metadata."""
        keywords = []
        
        # Try meta keywords
        if metadata.get('keywords'):
            keywords.extend(metadata['keywords'].split(','))
        
        # Try to extract from content if available
        if metadata.get('description'):
            # Simple keyword extraction from description
            import re
            words = re.findall(r'\b\w{4,}\b', metadata['description'].lower())
            from collections import Counter
            word_freq = Counter(words)
            keywords.extend([word for word, _ in word_freq.most_common(5)])
        
        return list(set(keywords))  # Remove duplicates
    
    def _detect_source_type(self, url: str, metadata: Dict[str, Any]) -> str:
        """Detect the source type of a page (blog, product, page)."""
        url_lower = url.lower()
        title_lower = metadata.get('title', '').lower()
        description_lower = metadata.get('description', '').lower()
        
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
    
    def extract_structured_data(self, url: str, schema: Any = None, config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Extract structured data from a URL using Firecrawl's extraction feature."""
        if config is None:
            config = self.config
        
        try:
            logger.info(f"Extracting structured data from: {url}")
            
            if schema:
                # Use provided schema
                json_config = JsonConfig(schema=schema)
                result = self.app.scrape_url(
                    url,
                    formats=['json'],
                    json_options=json_config,
                    only_main_content=config.get('only_main_content', True),
                    timeout=config.get('firecrawl_timeout', 120000)
                )
            else:
                # Use prompt-based extraction
                prompt = config.get('extraction_prompt', 'Extract the main information from this page.')
                result = self.app.scrape_url(
                    url,
                    formats=['json'],
                    json_options=JsonConfig(prompt=prompt),
                    only_main_content=config.get('only_main_content', True),
                    timeout=config.get('firecrawl_timeout', 120000)
                )
            
            if not result or not result.get('success'):
                logger.warning(f"Firecrawl extraction failed for {url}")
                return None
            
            data = result.get('data', {})
            return data.get('json', {})
            
        except Exception as e:
            logger.error(f"Error extracting structured data from {url}: {e}")
            return None
    
    def get_site_map(self, base_url: str) -> List[str]:
        """Get all URLs from a website using Firecrawl's map feature."""
        try:
            logger.info(f"Getting site map for: {base_url}")
            
            # Use Firecrawl's map feature to get all URLs
            map_result = self.app.map_url(base_url)
            
            if not map_result or not map_result.get('success'):
                logger.warning(f"Failed to get site map for {base_url}")
                return []
            
            urls = map_result.get('data', [])
            logger.info(f"Found {len(urls)} URLs in site map")
            return urls
            
        except Exception as e:
            logger.error(f"Error getting site map for {base_url}: {e}")
            return []


class FirecrawlSitemapParser:
    """Sitemap parser that can work with Firecrawl's site mapping."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scraper = FirecrawlScraper(config) if FIRECRAWL_AVAILABLE else None
    
    def parse_sitemap(self, sitemap_url: str) -> List[Dict[str, Any]]:
        """Parse sitemap and return URL data."""
        try:
            # First try to get URLs from Firecrawl site mapping
            if self.scraper:
                base_url = self._extract_base_url(sitemap_url)
                urls = self.scraper.get_site_map(base_url)
                
                if urls:
                    logger.info(f"Using Firecrawl site mapping: {len(urls)} URLs found")
                    return self._convert_urls_to_data(urls)
            
            # Fallback to traditional sitemap parsing
            logger.info("Falling back to traditional sitemap parsing")
            return self._parse_traditional_sitemap(sitemap_url)
            
        except Exception as e:
            logger.error(f"Error parsing sitemap {sitemap_url}: {e}")
            return []
    
    def _extract_base_url(self, sitemap_url: str) -> str:
        """Extract base URL from sitemap URL."""
        parsed = urlparse(sitemap_url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def _convert_urls_to_data(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Convert list of URLs to URL data format."""
        url_data = []
        for url in urls:
            url_data.append({
                'loc': url,
                'lastmod': None,
                'source_type': None
            })
        return url_data
    
    def _parse_traditional_sitemap(self, sitemap_url: str) -> List[Dict[str, Any]]:
        """Parse traditional XML sitemap as fallback."""
        # This would be the existing sitemap parsing logic
        # For now, return empty list to avoid duplicating existing code
        return []


# Example usage and testing
if __name__ == "__main__":
    # Test configuration
    test_config = {
        'firecrawl_api_key': 'your-api-key-here',
        'max_pages_to_process': 5,
        'max_content_length': 500,
        'only_main_content': True,
        'firecrawl_timeout': 120000,
        'firecrawl_wait_for': 2000
    }
    
    # Test the scraper
    try:
        scraper = FirecrawlScraper(test_config)
        
        # Test single URL scraping
        test_url = "https://example.com"
        content = scraper.scrape_content(test_url, test_config)
        
        if content:
            print(f"✅ Successfully scraped: {content['title']}")
            print(f"Content length: {len(content['content'])} chars")
        else:
            print("❌ Failed to scrape content")
            
    except Exception as e:
        print(f"❌ Error: {e}") 