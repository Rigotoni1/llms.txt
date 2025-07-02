#!/usr/bin/env python3
"""
Test script for the LLMs.txt Generator

This script demonstrates how to use the generator with a sample website.
You can modify the configuration to test with your own website.
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


def create_test_config():
    """Create a test configuration for demonstration."""
    test_config = {
        'sitemap_url': 'https://example.com/sitemap.xml',  # Replace with your sitemap
        'site_name': 'Example Website',
        'site_description': 'A demonstration website for testing the LLMs.txt generator',
        'content_selector': '.content, #main, article, .post-content, .entry-content',
        'title_selector': 'h1, .title, .post-title, .entry-title',
        'max_content_length': 300,
        'max_pages_to_process': 5,  # Limit for testing
        'min_content_length': 50,
        'default_topics': ['Technology', 'Tutorials', 'Web Development'],
        'respect_robots_txt': True,
        'request_delay': 2.0,  # Longer delay for testing
        'output_file': 'test_llms.txt',
        'backup_existing': True
    }
    
    # Save test config
    with open('test_config.yaml', 'w') as f:
        yaml.dump(test_config, f, default_flow_style=False, indent=2)
    
    logger.info("Created test configuration: test_config.yaml")
    return test_config


def test_sitemap_parsing(config):
    """Test sitemap parsing functionality."""
    logger.info("Testing sitemap parsing...")
    
    try:
        parser = SitemapParser(config)
        urls_data = parser.parse_sitemap(config['sitemap_url'])
        
        logger.info(f"Successfully parsed sitemap with {len(urls_data)} URLs")
        
        # Show first few URLs
        for i, url_data in enumerate(urls_data[:3]):
            logger.info(f"  {i+1}. {url_data['loc']}")
            if url_data.get('lastmod'):
                logger.info(f"     Last modified: {url_data['lastmod']}")
        
        return urls_data
        
    except Exception as e:
        logger.error(f"Sitemap parsing failed: {e}")
        return []


def test_content_scraping(config, urls_data):
    """Test content scraping functionality."""
    logger.info("Testing content scraping...")
    
    try:
        scraper = ContentScraper(config)
        
        # Set up robots.txt checker
        base_url = urlparse(config['sitemap_url']).scheme + '://' + urlparse(config['sitemap_url']).netloc
        robots_checker = RobotsTxtChecker(base_url)
        scraper.set_robots_checker(robots_checker)
        
        scraped_content = {}
        max_pages = config.get('max_pages_to_process', 5)
        
        for i, url_data in enumerate(urls_data[:max_pages]):
            logger.info(f"Scraping page {i+1}/{min(max_pages, len(urls_data))}: {url_data['loc']}")
            
            content = scraper.scrape_content(url_data['loc'], config)
            if content:
                scraped_content[url_data['loc']] = content
                logger.info(f"  Title: {content['title'][:50]}...")
                logger.info(f"  Description: {content['description'][:100]}...")
            else:
                logger.warning(f"  Failed to scrape content")
        
        logger.info(f"Successfully scraped {len(scraped_content)} pages")
        return scraped_content
        
    except Exception as e:
        logger.error(f"Content scraping failed: {e}")
        return {}


def test_llms_generation(config, urls_data, scraped_content):
    """Test llms.txt generation."""
    logger.info("Testing llms.txt generation...")
    
    try:
        generator = LLMsTxtGenerator(config)
        output_path = generator.generate_llms_txt(urls_data, scraped_content)
        
        # Show generated content
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Generated llms.txt ({len(content)} characters)")
            logger.info("First 500 characters:")
            logger.info("-" * 50)
            logger.info(content[:500])
            logger.info("-" * 50)
            
            return output_path
        else:
            logger.error("Generated file not found")
            return None
            
    except Exception as e:
        logger.error(f"LLMs.txt generation failed: {e}")
        return None


def run_test():
    """Run the complete test."""
    logger.info("Starting LLMs.txt Generator Test")
    logger.info("=" * 50)
    
    # Create test configuration
    config = create_test_config()
    
    # Validate configuration
    try:
        validate_config(config)
        logger.info("Configuration validation passed")
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False
    
    # Test sitemap parsing
    urls_data = test_sitemap_parsing(config)
    if not urls_data:
        logger.error("Sitemap parsing test failed")
        return False
    
    # Test content scraping
    scraped_content = test_content_scraping(config, urls_data)
    if not scraped_content:
        logger.warning("Content scraping test failed or no content found")
        # Continue anyway to test generation with empty content
    
    # Test llms.txt generation
    output_path = test_llms_generation(config, urls_data, scraped_content)
    if not output_path:
        logger.error("LLMs.txt generation test failed")
        return False
    
    logger.info("=" * 50)
    logger.info("Test completed successfully!")
    logger.info(f"Generated file: {output_path}")
    
    return True


if __name__ == "__main__":
    success = run_test()
    if success:
        print("\n✅ Test completed successfully!")
        print("You can now modify the configuration and run the tool on your own website.")
    else:
        print("\n❌ Test failed. Check the logs above for details.")
        print("Make sure you have a valid sitemap URL in the configuration.") 