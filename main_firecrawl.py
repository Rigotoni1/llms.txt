#!/usr/bin/env python3
"""
Simplified LLMs.txt Generator using Firecrawl
Replaces complex BeautifulSoup scraping with Firecrawl's API
"""

import os
import yaml
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

from firecrawl_scraper import FirecrawlScraper, FirecrawlSitemapParser
from main import LLMsTxtGenerator  # Reuse the existing generator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirecrawlLLMsGenerator:
    """Simplified LLMs.txt generator using Firecrawl."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scraper = FirecrawlScraper(config)
        self.sitemap_parser = FirecrawlSitemapParser(config)
        self.llms_generator = LLMsTxtGenerator(config)
        
        logger.info("Firecrawl LLMs Generator initialized")
    
    def generate_llms_txt(self, sitemap_url: str, site_name: Optional[str] = None) -> Optional[str]:
        """Generate llms.txt using Firecrawl for content extraction."""
        try:
            logger.info(f"Starting LLMs.txt generation for: {sitemap_url}")
            
            # Parse sitemap to get URLs
            logger.info("Parsing sitemap...")
            urls_data = self.sitemap_parser.parse_sitemap(sitemap_url)
            
            if not urls_data:
                logger.warning("No URLs found in sitemap")
                return None
            
            logger.info(f"Found {len(urls_data)} URLs to process")
            
            # Extract base URL for crawling
            base_url = self._extract_base_url(sitemap_url)
            
            # Use Firecrawl to crawl the entire website
            logger.info("Starting Firecrawl crawl...")
            scraped_content = self.scraper.crawl_website(base_url, self.config)
            
            if not scraped_content:
                logger.warning("No content scraped from website")
                return None
            
            logger.info(f"Successfully scraped {len(scraped_content)} pages")
            
            # Generate llms.txt using existing generator
            logger.info("Generating llms.txt...")
            output_path = self.llms_generator.generate_llms_txt(urls_data, scraped_content)
            
            logger.info(f"Successfully generated llms.txt: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating llms.txt: {e}")
            raise
    
    def generate_llms_txt_simple(self, base_url: str, site_name: Optional[str] = None) -> Optional[str]:
        """Generate llms.txt using just a base URL (no sitemap needed)."""
        try:
            logger.info(f"Starting simple LLMs.txt generation for: {base_url}")
            
            # Use Firecrawl to crawl the website
            logger.info("Starting Firecrawl crawl...")
            scraped_content = self.scraper.crawl_website(base_url, self.config)
            
            if not scraped_content:
                logger.warning("No content scraped from website")
                return None
            
            logger.info(f"Successfully scraped {len(scraped_content)} pages")
            
            # Convert scraped content to URL data format
            urls_data = []
            for url, content in scraped_content.items():
                urls_data.append({
                    'loc': url,
                    'lastmod': content.get('lastmod'),
                    'source_type': content.get('source_type')
                })
            
            # Generate llms.txt using existing generator
            logger.info("Generating llms.txt...")
            output_path = self.llms_generator.generate_llms_txt(urls_data, scraped_content)
            
            logger.info(f"Successfully generated llms.txt: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating llms.txt: {e}")
            raise
    
    def _extract_base_url(self, sitemap_url: str) -> str:
        """Extract base URL from sitemap URL."""
        parsed = urlparse(sitemap_url)
        return f"{parsed.scheme}://{parsed.netloc}"


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using defaults")
        return get_default_config()
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """Get default configuration."""
    return {
        'firecrawl_api_key': os.environ.get('FIRECRAWL_API_KEY'),
        'site_name': 'My Website',
        'site_description': '',
        'max_pages_to_process': 10,
        'max_content_length': 500,
        'only_main_content': True,
        'firecrawl_timeout': 120000,  # 2 minutes
        'firecrawl_wait_for': 2000,   # 2 seconds
        'crawl_max_wait_time': 300,   # 5 minutes
        'crawl_poll_interval': 10,    # 10 seconds
        'output_file': 'llms.txt',
        'backup_existing': True
    }


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration."""
    required_fields = ['firecrawl_api_key']
    
    for field in required_fields:
        if not config.get(field):
            logger.error(f"Missing required config field: {field}")
            return False
    
    return True


def main(sitemap_url: Optional[str] = None, base_url: Optional[str] = None, site_name: Optional[str] = None, config_path: str = "config.yaml"):
    """Main function to generate llms.txt using Firecrawl."""
    try:
        # Load configuration
        config = load_config(config_path)
        
        # Override with command line arguments
        if site_name:
            config['site_name'] = site_name
        
        # Validate configuration
        if not validate_config(config):
            logger.error("Configuration validation failed")
            return
        
        # Initialize generator
        generator = FirecrawlLLMsGenerator(config)
        
        # Generate llms.txt
        if sitemap_url:
            output_path = generator.generate_llms_txt(sitemap_url, site_name)
        elif base_url:
            output_path = generator.generate_llms_txt_simple(base_url, site_name)
        else:
            logger.error("Either sitemap_url or base_url must be provided")
            return
        
        if output_path:
            logger.info(f"✅ Successfully generated llms.txt: {output_path}")
        else:
            logger.error("❌ Failed to generate llms.txt")
            
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate LLMs.txt using Firecrawl')
    parser.add_argument('--sitemap', help='Sitemap URL')
    parser.add_argument('--url', help='Base URL (alternative to sitemap)')
    parser.add_argument('--site-name', help='Site name')
    parser.add_argument('--config', default='config.yaml', help='Config file path')
    
    args = parser.parse_args()
    
    if not args.sitemap and not args.url:
        print("Error: Either --sitemap or --url must be provided")
        exit(1)
    
    main(
        sitemap_url=args.sitemap,
        base_url=args.url,
        site_name=args.site_name,
        config_path=args.config
    ) 