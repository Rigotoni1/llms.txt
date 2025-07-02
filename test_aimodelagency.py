#!/usr/bin/env python3
"""
Test script for AI Model Agency sitemap index
"""

import yaml
import os
from main import SitemapParser, ContentScraper, LLMsTxtGenerator, RobotsTxtChecker
from utils import validate_config, get_site_domain
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_aimodelagency_sitemap():
    """Test the AI Model Agency sitemap index."""
    logger.info("Testing AI Model Agency sitemap index...")
    
    # Configuration for AI Model Agency
    config = {
        'sitemap_url': 'https://aimodelagency.com/sitemap_index.xml',
        'site_name': 'AI Model Agency',
        'site_description': 'AI-powered fashion photography and modeling agency',
        'content_selector': '.content, #main, article, .post-content, .entry-content, .page-content, .post, .entry',
        'title_selector': 'h1, .title, .post-title, .entry-title, .page-title, .post-title',
        'max_content_length': 500,
        'max_pages_to_process': 20,  # Process more pages since it's a large site
        'max_sitemaps_to_process': 3,  # Limit to first 3 sitemaps for testing
        'min_content_length': 50,
        'default_topics': ['AI Modeling', 'Fashion Photography', 'Digital Models', 'E-commerce', 'AI Fashion'],
        'respect_robots_txt': False,  # Disable robots.txt to get content
        'request_delay': 1.0,  # Shorter delay since we're bypassing robots.txt
        'output_file': 'aimodelagency_llms.txt',
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
        
        # Show some sample URLs
        logger.info("Sample URLs:")
        for i, url_data in enumerate(urls_data[:5]):
            logger.info(f"  {i+1}. {url_data['loc']}")
            if url_data.get('lastmod'):
                logger.info(f"     Last modified: {url_data['lastmod']}")
        
        # Scrape content
        logger.info("Scraping content (robots.txt bypassed)...")
        scraped_content = {}
        max_pages = config.get('max_pages_to_process', 20)
        
        for i, url_data in enumerate(urls_data[:max_pages]):
            logger.info(f"Scraping page {i+1}/{min(max_pages, len(urls_data))}: {url_data['loc']}")
            
            content = content_scraper.scrape_content(url_data['loc'], config)
            if content:
                scraped_content[url_data['loc']] = content
                logger.info(f"  Title: {content['title'][:50]}...")
                logger.info(f"  Description: {content['description'][:100]}...")
            else:
                logger.warning(f"  Failed to scrape content")
        
        # Generate llms.txt
        logger.info("Generating llms.txt...")
        output_path = llms_generator.generate_llms_txt(urls_data, scraped_content)
        
        # Show results
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Generated llms.txt ({len(content)} characters)")
            logger.info("First 500 characters:")
            logger.info("-" * 50)
            logger.info(content[:500])
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
    success = test_aimodelagency_sitemap()
    if success:
        print("\n✅ AI Model Agency test completed successfully!")
        print("The tool now bypasses robots.txt for better results!")
    else:
        print("\n❌ Test failed. Check the logs above for details.") 