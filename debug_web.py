#!/usr/bin/env python3
"""
Debug script to test web interface configuration for AI Model Agency
"""

import yaml
import os
from main import SitemapParser, ContentScraper, LLMsTxtGenerator, RobotsTxtChecker
from utils import validate_config
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def debug_web_config():
    """Debug the exact web interface configuration."""
    logger.info("Testing web interface configuration for AI Model Agency...")
    
    # This is the exact config the web interface would create
    config = {
        'sitemap_url': 'https://aimodelagency.com/sitemap_index.xml',
        'site_name': 'AI Model Agency',
        'site_description': '',
        'content_selector': '.content, #main, article, .post-content',
        'title_selector': 'h1, .title, .post-title',
        'max_pages_to_process': 10,
        'max_content_length': 500,
        'min_content_length': 50,
        'max_sitemaps_to_process': 5,
        'default_topics': ['Technology', 'Business', 'Web Development'],
        'respect_robots_txt': False,  # This should be False when checkbox is unchecked
        'request_delay': 1.0,
        'output_file': 'llms.txt',
        'backup_existing': True
    }
    
    try:
        # Validate config
        validate_config(config)
        logger.info("Configuration validation passed")
        
        # Initialize components
        sitemap_parser = SitemapParser(config)
        content_scraper = ContentScraper(config)
        llms_generator = LLMsTxtGenerator(config)
        
        # Set up robots.txt checker (but it won't block since respect_robots_txt is False)
        base_url = urlparse(config['sitemap_url']).scheme + '://' + urlparse(config['sitemap_url']).netloc
        robots_checker = RobotsTxtChecker(base_url)
        content_scraper.set_robots_checker(robots_checker)
        
        # Parse sitemap index
        logger.info("Parsing sitemap index...")
        urls_data = sitemap_parser.parse_sitemap(config['sitemap_url'])
        
        logger.info(f"Found {len(urls_data)} total URLs from sitemap index")
        
        # Test scraping with web interface selectors
        logger.info("Testing content scraping with web interface selectors...")
        test_urls = urls_data[:5]
        
        scraped_content = {}
        for i, url_data in enumerate(test_urls):
            logger.info(f"Testing page {i+1}: {url_data['loc']}")
            
            content = content_scraper.scrape_content(url_data['loc'], config)
            if content:
                scraped_content[url_data['loc']] = content
                logger.info(f"  ✅ SUCCESS - Title: {content['title'][:50]}...")
                logger.info(f"     Description: {content['description'][:100]}...")
            else:
                logger.warning(f"  ❌ FAILED - No content found")
        
        # Generate llms.txt
        logger.info("Generating llms.txt...")
        output_path = llms_generator.generate_llms_txt(urls_data, scraped_content)
        
        # Show results
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Generated llms.txt ({len(content)} characters)")
            logger.info("Content preview:")
            logger.info("-" * 50)
            logger.info(content[:1000])
            logger.info("-" * 50)
            
            logger.info("✅ Debug completed!")
            logger.info(f"Total URLs: {len(urls_data)}")
            logger.info(f"Pages scraped: {len(scraped_content)}")
            logger.info(f"Success rate: {len(scraped_content)/len(test_urls)*100:.1f}%")
            
        else:
            logger.error("Generated file not found")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = debug_web_config()
    if success:
        print("\n✅ Debug completed successfully!")
        print("Check the logs above to see what's happening with the web interface config.")
    else:
        print("\n❌ Debug failed. Check the logs above for details.") 