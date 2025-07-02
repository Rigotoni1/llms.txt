#!/usr/bin/env python3
"""
Test script to verify blog/page separation functionality
"""

from main import SitemapParser, ContentScraper, LLMsTxtGenerator, RobotsTxtChecker
from utils import validate_config
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_blog_separation():
    """Test the blog/page separation functionality."""
    logger.info("Testing blog/page separation for AI Model Agency...")
    
    config = {
        'sitemap_url': 'https://aimodelagency.com/sitemap_index.xml',
        'site_name': 'AI Model Agency',
        'site_description': 'AI-powered fashion photography and modeling agency',
        'content_selector': '.content, #main, article, .post-content, .entry-content, .page-content, .post, .entry, .elementor, .elementor-post',
        'title_selector': 'h1, .title, .post-title, .entry-title, .page-title',
        'max_pages_to_process': 15,  # Process more pages to test separation
        'max_content_length': 500,
        'min_content_length': 50,
        'max_sitemaps_to_process': 3,
        'max_nested_links': 0,
        'max_blogs': 8,  # Limit blogs to 8
        'respect_robots_txt': False,
        'request_delay': 1.0,
        'output_file': 'test_blog_separation.txt'
    }
    
    try:
        # Validate config
        validate_config(config)
        logger.info("Configuration validation passed")
        
        # Initialize components
        sitemap_parser = SitemapParser(config)
        content_scraper = ContentScraper(config)
        llms_generator = LLMsTxtGenerator(config)
        
        # Set up robots.txt checker
        base_url = urlparse(config['sitemap_url']).scheme + '://' + urlparse(config['sitemap_url']).netloc
        robots_checker = RobotsTxtChecker(base_url)
        content_scraper.set_robots_checker(robots_checker)
        
        # Parse sitemap index
        logger.info("Parsing sitemap index...")
        urls_data = sitemap_parser.parse_sitemap(config['sitemap_url'])
        
        logger.info(f"Found {len(urls_data)} total URLs from sitemap index")
        
        # Scrape content
        logger.info("Scraping content...")
        scraped_content = {}
        max_pages = config.get('max_pages_to_process', 15)
        
        for i, url_data in enumerate(urls_data[:max_pages]):
            logger.info(f"Scraping page {i+1}/{min(max_pages, len(urls_data))}: {url_data['loc']}")
            
            # Extract content with lastmod date if available
            if url_data.get('lastmod'):
                content = content_scraper.scrape_content_with_lastmod(url_data['loc'], url_data['lastmod'], config)
            else:
                content = content_scraper.scrape_content(url_data['loc'], config)
                
            if content:
                scraped_content[url_data['loc']] = content
                logger.info(f"  Title: {content['title'][:50]}...")
                logger.info(f"  Description: {content['description'][:100]}...")
                if content.get('lastmod'):
                    logger.info(f"  Last modified: {content['lastmod']}")
            else:
                logger.warning(f"  Failed to scrape content")
        
        # Generate llms.txt
        logger.info("Generating llms.txt with blog/page separation...")
        output_path = llms_generator.generate_llms_txt(urls_data, scraped_content)
        
        # Show results
        if output_path:
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Generated llms.txt ({len(content)} characters)")
            logger.info("Content preview:")
            logger.info("-" * 50)
            logger.info(content[:1500])
            logger.info("-" * 50)
            
            logger.info("✅ Test completed successfully!")
            logger.info(f"Generated file: {output_path}")
            logger.info(f"Total URLs processed: {len(urls_data)}")
            logger.info(f"Pages scraped: {len(scraped_content)}")
            
        else:
            logger.error("Generated file not found")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_blog_separation()
    if success:
        print("\n✅ Blog/page separation test completed successfully!")
        print("Check the generated file to see the separated sections!")
    else:
        print("\n❌ Test failed. Check the logs above for details.") 