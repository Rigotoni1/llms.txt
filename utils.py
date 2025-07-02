#!/usr/bin/env python3
"""
Utility functions for the LLMs.txt Generator
"""

import os
import json
import hashlib
from datetime import datetime
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class IncrementalUpdater:
    """Handle incremental updates based on lastmod dates."""
    
    def __init__(self, cache_file=".llms_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Load cache from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save cache: {e}")
    
    def get_updated_urls(self, urls_data):
        """Get URLs that have been updated since last run."""
        updated_urls = []
        
        for url_data in urls_data:
            url = url_data['loc']
            lastmod = url_data.get('lastmod')
            
            # Check if URL is new or has been updated
            if url not in self.cache:
                updated_urls.append(url_data)
            elif lastmod and self.cache[url].get('lastmod') != lastmod:
                updated_urls.append(url_data)
        
        return updated_urls
    
    def update_cache(self, urls_data, scraped_content):
        """Update cache with new data."""
        for url_data in urls_data:
            url = url_data['loc']
            self.cache[url] = {
                'lastmod': url_data.get('lastmod'),
                'scraped_at': datetime.now().isoformat(),
                'title': scraped_content.get(url, {}).get('title', ''),
                'content_hash': self._get_content_hash(scraped_content.get(url, {}).get('content', ''))
            }
        
        self._save_cache()
    
    def _get_content_hash(self, content):
        """Get hash of content for change detection."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()


class FTPUploader:
    """Handle FTP upload of generated llms.txt file."""
    
    def __init__(self, config):
        self.config = config.get('ftp', {})
        self.enabled = self.config.get('enabled', False)
    
    def upload_file(self, local_file_path):
        """Upload file via FTP."""
        if not self.enabled:
            logger.info("FTP upload is disabled in configuration")
            return False
        
        try:
            from ftplib import FTP
            
            host = self.config.get('host')
            username = self.config.get('username')
            password = self.config.get('password')
            remote_path = self.config.get('remote_path', '/')
            
            if not all([host, username, password]):
                logger.error("FTP configuration incomplete")
                return False
            
            with FTP(host) as ftp:
                ftp.login(username, password)
                
                # Change to remote directory
                if remote_path:
                    ftp.cwd(remote_path)
                
                # Upload file
                with open(local_file_path, 'rb') as f:
                    ftp.storbinary(f'STOR llms.txt', f)
                
                logger.info(f"Successfully uploaded llms.txt to FTP server")
                return True
                
        except Exception as e:
            logger.error(f"FTP upload failed: {e}")
            return False


def validate_config(config):
    """Validate configuration file."""
    required_fields = ['sitemap_url', 'site_name']
    missing_fields = []
    
    for field in required_fields:
        if field not in config:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Missing required configuration fields: {', '.join(missing_fields)}")
    
    # Validate sitemap URL
    sitemap_url = config['sitemap_url']
    if not sitemap_url.startswith(('http://', 'https://')):
        raise ValueError("sitemap_url must be a valid HTTP/HTTPS URL")
    
    # Validate numeric fields
    numeric_fields = ['max_content_length', 'max_pages_to_process', 'min_content_length', 'request_delay']
    for field in numeric_fields:
        if field in config and not isinstance(config[field], (int, float)):
            raise ValueError(f"{field} must be a number")
    
    logger.info("Configuration validation passed")
    return True


def create_sample_config():
    """Create a sample configuration file."""
    sample_config = {
        'sitemap_url': 'https://example.com/sitemap.xml',
        'site_name': 'Example Website',
        'site_description': 'A comprehensive resource for technology and tutorials',
        'content_selector': '.content, #main, article, .post-content',
        'title_selector': 'h1, .title, .post-title',
        'max_content_length': 500,
        'max_pages_to_process': 10,
        'min_content_length': 50,
        'default_topics': ['Technology', 'Tutorials', 'Web Development'],
        'respect_robots_txt': True,
        'request_delay': 1.0,
        'output_file': 'llms.txt',
        'backup_existing': True,
        'ftp': {
            'enabled': False,
            'host': '',
            'username': '',
            'password': '',
            'remote_path': '/public_html/'
        }
    }
    
    return sample_config


def get_site_domain(sitemap_url):
    """Extract domain from sitemap URL."""
    parsed = urlparse(sitemap_url)
    return parsed.netloc


def format_file_size(file_path):
    """Format file size in human readable format."""
    if not os.path.exists(file_path):
        return "0 B"
    
    size = os.path.getsize(file_path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB" 