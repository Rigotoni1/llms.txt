#!/usr/bin/env python3
"""
Test script to debug web interface content extraction
"""

from main import ContentScraper, RobotsTxtChecker
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_web_content_extraction():
    """Test the exact web interface configuration."""
    
    # Web interface config
    config = {
        'sitemap_url': 'https://aimodelagency.com/sitemap_index.xml',
        'site_name': 'AI Model Agency',
        'site_description': '',
        'content_selector': '.content, #main, article, .post-content, .entry-content, .page-content, .post, .entry, .elementor, .elementor-post',
        'title_selector': 'h1, .title, .post-title, .entry-title, .page-title',
        'max_pages_to_process': 3,
        'max_content_length': 500,
        'min_content_length': 50,
        'max_sitemaps_to_process': 5,
        'max_nested_links': 5,
        'default_topics': ['Technology', 'Business', 'Web Development'],
        'respect_robots_txt': False,
        'request_delay': 1.0,
        'output_file': 'llms.txt',
        'backup_existing': True
    }
    
    # Test URLs from AI Model Agency
    test_urls = [
        'https://aimodelagency.com/blog/',
        'https://aimodelagency.com/daydream-unveils-ai-chatbot-to-revolutionize-fashion-shopping/',
        'https://aimodelagency.com/'
    ]
    
    # Initialize scraper
    scraper = ContentScraper(config)
    
    # Set up robots.txt checker
    base_url = urlparse(config['sitemap_url']).scheme + '://' + urlparse(config['sitemap_url']).netloc
    robots_checker = RobotsTxtChecker(base_url)
    scraper.set_robots_checker(robots_checker)
    
    # Test each URL
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing: {url}")
        print(f"{'='*60}")
        
        content = scraper.scrape_content(url, config)
        
        if content:
            print(f"✅ SUCCESS")
            print(f"Title: {content.get('title', 'No title')}")
            print(f"Description: {content.get('description', 'No description')[:100]}...")
            print(f"Content length: {len(content.get('content', ''))}")
            print(f"Content preview: {content.get('content', 'No content')[:200]}...")
        else:
            print(f"❌ FAILED - No content extracted")

if __name__ == "__main__":
    test_web_content_extraction() 