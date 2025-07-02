#!/usr/bin/env python3
"""
LLMs.txt Generator

A Python tool that dynamically generates an llms.txt file for a website
using its sitemap.xml to guide content scraping.
"""

import requests
from bs4 import BeautifulSoup
import lxml.etree as ET
import yaml
from urllib.parse import urljoin, urlparse
import os
import time
from datetime import datetime
import re
from collections import Counter
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RobotsTxtChecker:
    """Check robots.txt for allowed/disallowed URLs."""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.allowed_urls = set()
        self.disallowed_urls = set()
        self._load_robots_txt()
    
    def _load_robots_txt(self):
        """Load and parse robots.txt file."""
        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            response = requests.get(robots_url, timeout=10)
            if response.status_code == 200:
                self._parse_robots_txt(response.text)
        except Exception as e:
            logger.warning(f"Could not load robots.txt: {e}")
    
    def _parse_robots_txt(self, content):
        """Parse robots.txt content."""
        current_user_agent = None
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('User-agent:'):
                current_user_agent = line.split(':', 1)[1].strip()
            elif line.startswith('Allow:') and (current_user_agent == '*' or current_user_agent is None):
                path = line.split(':', 1)[1].strip()
                self.allowed_urls.add(urljoin(self.base_url, path))
            elif line.startswith('Disallow:') and (current_user_agent == '*' or current_user_agent is None):
                path = line.split(':', 1)[1].strip()
                self.disallowed_urls.add(urljoin(self.base_url, path))
    
    def is_allowed(self, url):
        """Check if a URL is allowed by robots.txt."""
        if not self.disallowed_urls and not self.allowed_urls:
            return True
        
        url_path = urlparse(url).path
        for disallowed in self.disallowed_urls:
            if url_path.startswith(urlparse(disallowed).path):
                return False
        return True


class SitemapIndexParser:
    """Parse sitemap index files."""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LLMs.txt Generator Bot (+https://github.com/your-repo)'
        })
    
    def parse_sitemap_index(self, sitemap_index_url):
        """Parse sitemap index and extract sitemap URLs."""
        try:
            logger.info(f"Parsing sitemap index: {sitemap_index_url}")
            response = self.session.get(sitemap_index_url, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            sitemaps = []
            for sitemap_elem in root.findall('ns:sitemap', namespace):
                sitemap_data = self._extract_sitemap_data(sitemap_elem, namespace)
                if sitemap_data:
                    sitemaps.append(sitemap_data)
            
            logger.info(f"Found {len(sitemaps)} sitemaps in index")
            return sitemaps
            
        except Exception as e:
            logger.error(f"Error parsing sitemap index: {e}")
            raise
    
    def _extract_sitemap_data(self, sitemap_elem, namespace):
        """Extract data from a sitemap element in sitemap index."""
        try:
            loc_elem = sitemap_elem.find('ns:loc', namespace)
            if loc_elem is None:
                return None
            
            sitemap_data = {
                'loc': loc_elem.text.strip(),
                'lastmod': None
            }
            
            # Extract lastmod
            lastmod_elem = sitemap_elem.find('ns:lastmod', namespace)
            if lastmod_elem is not None:
                sitemap_data['lastmod'] = lastmod_elem.text.strip()
            
            return sitemap_data
            
        except Exception as e:
            logger.warning(f"Error extracting sitemap data: {e}")
            return None


class SitemapParser:
    """Parse sitemap.xml files and sitemap indexes."""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LLMs.txt Generator Bot (+https://github.com/your-repo)'
        })
        self.sitemap_index_parser = SitemapIndexParser(config)
    
    def parse_sitemap(self, sitemap_url):
        """Parse sitemap.xml or sitemap index and extract URLs with metadata."""
        try:
            logger.info(f"Parsing sitemap: {sitemap_url}")
            response = self.session.get(sitemap_url, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # Check if this is a sitemap index
            if root.findall('ns:sitemap', namespace):
                logger.info("Detected sitemap index, processing all sitemaps...")
                return self._process_sitemap_index(sitemap_url)
            else:
                # Regular sitemap
                return self._process_regular_sitemap(root, namespace)
                
        except Exception as e:
            logger.error(f"Error parsing sitemap: {e}")
            raise
    
    def _process_sitemap_index(self, sitemap_index_url):
        """Process a sitemap index by parsing all contained sitemaps."""
        sitemaps = self.sitemap_index_parser.parse_sitemap_index(sitemap_index_url)
        all_urls = []
        max_sitemaps = self.config.get('max_sitemaps_to_process', 5)
        for i, sitemap_data in enumerate(sitemaps[:max_sitemaps]):
            try:
                logger.info(f"Processing sitemap {i+1}/{min(len(sitemaps), max_sitemaps)}: {sitemap_data['loc']}")
                response = self.session.get(sitemap_data['loc'], timeout=30)
                response.raise_for_status()
                root = ET.fromstring(response.content)
                namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                # Determine if this sitemap is a blog/post sitemap, page sitemap, or product sitemap
                source_type = None
                loc_lower = sitemap_data['loc'].lower()
                if 'post' in loc_lower or 'blog' in loc_lower:
                    source_type = 'blog'
                elif 'page' in loc_lower:
                    source_type = 'page'
                elif 'product' in loc_lower:
                    source_type = 'product'
                sitemap_urls = self._process_regular_sitemap(root, namespace, source_type=source_type)
                all_urls.extend(sitemap_urls)
                if i < len(sitemaps) - 1:
                    time.sleep(1)
            except Exception as e:
                logger.warning(f"Error processing sitemap {sitemap_data['loc']}: {e}")
                continue
        logger.info(f"Total URLs from all sitemaps: {len(all_urls)}")
        return all_urls
    
    def _process_regular_sitemap(self, root, namespace, source_type=None):
        """Process a regular sitemap (not an index)."""
        urls = []
        for url_elem in root.findall('ns:url', namespace):
            url_data = self._extract_url_data(url_elem, namespace)
            if url_data:
                if source_type:
                    url_data['source_type'] = source_type
                urls.append(url_data)
        logger.info(f"Found {len(urls)} URLs in sitemap")
        return urls
    
    def _extract_url_data(self, url_elem, namespace):
        """Extract data from a URL element in sitemap."""
        try:
            loc_elem = url_elem.find('ns:loc', namespace)
            if loc_elem is None:
                return None
            
            url_data = {
                'loc': loc_elem.text.strip(),
                'lastmod': None,
                'changefreq': None,
                'priority': None
            }
            
            # Extract lastmod
            lastmod_elem = url_elem.find('ns:lastmod', namespace)
            if lastmod_elem is not None:
                url_data['lastmod'] = lastmod_elem.text.strip()
            
            # Extract changefreq
            changefreq_elem = url_elem.find('ns:changefreq', namespace)
            if changefreq_elem is not None:
                url_data['changefreq'] = changefreq_elem.text.strip()
            
            # Extract priority
            priority_elem = url_elem.find('ns:priority', namespace)
            if priority_elem is not None:
                url_data['priority'] = float(priority_elem.text.strip())
            
            return url_data
            
        except Exception as e:
            logger.warning(f"Error extracting URL data: {e}")
            return None


class ContentScraper:
    """Scrape content from web pages."""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LLMs.txt Generator Bot (+https://github.com/your-repo)'
        })
        self.robots_checker = None
    
    def set_robots_checker(self, robots_checker):
        """Set robots.txt checker."""
        self.robots_checker = robots_checker
    
    def scrape_content(self, url, config=None):
        """Scrape content from a URL, including following nested links if needed."""
        if config is None:
            config = self.config
        
        # Check robots.txt ONLY if explicitly enabled
        respect_robots = config.get('respect_robots_txt', False)  # Default to False
        if respect_robots and self.robots_checker:
            if not self.robots_checker.is_allowed(url):
                logger.info(f"Skipping {url} (disallowed by robots.txt)")
                return None
        else:
            logger.info(f"Robots.txt bypassed for {url}")
        
        try:
            logger.info(f"Scraping content from: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if this is a pagination/archive page that needs to follow links
            if self._is_pagination_page(soup, url):
                logger.info(f"Detected pagination/archive page: {url}")
                return self._scrape_pagination_page(soup, url, config)
            else:
                logger.info(f"Processing as regular content page: {url}")
            
            # Regular content extraction
            content = self._extract_page_content(soup, url, config)
            if content:
                logger.info(f"Successfully extracted content from {url}: {len(content.get('content', ''))} chars")
            else:
                logger.warning(f"No content extracted from {url}")
            return content
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def _is_pagination_page(self, soup, url):
        """Check if this is a pagination or archive page that contains links to actual content."""
        # ONLY follow nested links if URL contains 'sitemap' anywhere
        if 'sitemap' not in url.lower():
            return False
        
        # Check URL patterns - be very specific
        pagination_patterns = [
            r'/blog/?$',  # Only exact blog directory, not blog posts
            r'/category/', r'/tag/', r'/archive/', r'/page/\d+', 
            r'/search/', r'/author/', r'/year/', r'/month/',
            r'/index\.php$', r'/index\.html$'
        ]
        
        for pattern in pagination_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        # Check for pagination indicators in content - be very specific
        pagination_indicators = [
            'archive', 'category', 'tag', 'search results', 'blog posts',
            'recent posts', 'latest articles', 'more posts', 'older posts',
            'newer posts', 'previous posts', 'next posts'
        ]
        
        page_text = soup.get_text().lower()
        if any(indicator in page_text for indicator in pagination_indicators):
            # Additional check: make sure it's not just a single article
            article_links = soup.find_all('a', href=True)
            content_links = [link for link in article_links if self._is_content_link(link['href'])]
            return len(content_links) >= 10  # Require many more links to be considered pagination
        
        # Check for multiple article links - be very conservative
        article_links = soup.find_all('a', href=True)
        content_links = [link for link in article_links if self._is_content_link(link['href'])]
        
        # Only consider it pagination if it has many content links AND looks like an archive
        if len(content_links) >= 15:  # Much higher threshold
            # Additional check: look for archive-like structure
            archive_indicators = ['archive', 'blog', 'posts', 'articles', 'recent', 'latest']
            page_title = soup.find('title')
            if page_title:
                title_text = page_title.get_text().lower()
                if any(indicator in title_text for indicator in archive_indicators):
                    return True
            
            # Check for pagination navigation
            pagination_nav = soup.find_all(['nav', 'div'], class_=re.compile(r'pagination|navigation|pager'))
            if pagination_nav:
                return True
            
            # Check if the page has article/post structure
            articles = soup.find_all(['article', '.post', '.entry'])
            if len(articles) >= 5:  # Multiple articles indicate archive
                return True
        
        return False
    
    def _is_content_link(self, href):
        """Check if a link points to actual content."""
        # Skip external links, anchors, and non-content URLs
        if href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
            return False
        
        # Skip common non-content patterns
        non_content_patterns = [
            r'/wp-admin/', r'/wp-content/', r'/wp-includes/', r'/feed/', 
            r'/rss/', r'/atom/', r'/sitemap', r'/robots', r'/admin/',
            r'/login', r'/register', r'/contact', r'/about', r'/privacy',
            r'/terms', r'/cookie', r'/sitemap'
        ]
        
        for pattern in non_content_patterns:
            if re.search(pattern, href, re.IGNORECASE):
                return False
        
        # Look for content indicators in the URL
        content_patterns = [
            r'/\d{4}/', r'/\d{2}/', r'/post/', r'/article/', r'/blog/',
            r'/news/', r'/story/', r'/page/', r'/entry/'
        ]
        
        for pattern in content_patterns:
            if re.search(pattern, href, re.IGNORECASE):
                return True
        
        return True  # Assume it's content if it doesn't match non-content patterns
    
    def _scrape_pagination_page(self, soup, url, config):
        """Scrape content from a pagination page by following links to actual content."""
        # Find all content links on the page
        article_links = soup.find_all('a', href=True)
        content_links = []
        
        for link in article_links:
            href = link['href']
            if self._is_content_link(href):
                # Make relative URLs absolute
                if href.startswith('/'):
                    from urllib.parse import urljoin
                    href = urljoin(url, href)
                content_links.append(href)
        
        # Remove duplicates while preserving order
        content_links = list(dict.fromkeys(content_links))
        
        logger.info(f"Found {len(content_links)} content links on pagination page")
        
        # Limit the number of links to follow
        max_nested_links = config.get('max_nested_links', 5)
        content_links = content_links[:max_nested_links]
        
        # Scrape content from each link
        all_content = []
        for i, link_url in enumerate(content_links):
            logger.info(f"Following nested link {i+1}/{len(content_links)}: {link_url}")
            
            try:
                nested_content = self._extract_page_content_from_url(link_url, config)
                if nested_content:
                    all_content.append(nested_content)
                
                # Respect request delay
                request_delay = config.get('request_delay', 1.0)
                if request_delay > 0 and i < len(content_links) - 1:
                    import time
                    time.sleep(request_delay)
                    
            except Exception as e:
                logger.warning(f"Error scraping nested link {link_url}: {e}")
        
        # Combine content from all nested pages
        if all_content:
            return self._combine_nested_content(all_content, url)
        else:
            # Fallback to extracting content from the pagination page itself
            return self._extract_page_content(soup, url, config)
    
    def _extract_page_content_from_url(self, url, config):
        """Extract content from a URL."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._extract_page_content(soup, url, config)
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def _extract_page_content(self, soup, url, config):
        """Extract content from a single page."""
        # Extract title
        title = self._extract_title(soup, config)
        
        # Extract meta description
        description = self._extract_meta_description(soup, config)
        
        # Extract main content
        content = self._extract_main_content(soup, config)
        
        # Extract keywords/tags
        keywords = self._extract_keywords(soup, config)
        
        return {
            'url': url,
            'title': title,
            'description': description,
            'content': content,
            'keywords': keywords,
            'scraped_at': datetime.now().isoformat()
        }
    
    def _extract_page_content_with_lastmod(self, soup, url, lastmod, config):
        """Extract content from a single page with lastmod date."""
        content = self._extract_page_content(soup, url, config)
        if content and lastmod:
            content['lastmod'] = lastmod
        return content
    
    def _combine_nested_content(self, content_list, original_url):
        """Combine content from multiple nested pages."""
        if not content_list:
            return None
        
        # Use the first page's metadata as base
        combined = content_list[0].copy()
        combined['url'] = original_url
        
        # Combine titles
        titles = [c['title'] for c in content_list if c.get('title')]
        if titles:
            combined['title'] = titles[0]  # Use first title as main title
        
        # Combine descriptions
        descriptions = [c['description'] for c in content_list if c.get('description')]
        if descriptions:
            combined['description'] = ' '.join(descriptions[:3])  # Combine first 3 descriptions
        
        # Combine content
        contents = [c['content'] for c in content_list if c.get('content')]
        if contents:
            max_length = self.config.get('max_content_length', 500)
            combined_content = ' '.join(contents)
            combined['content'] = combined_content[:max_length]
        
        # Combine keywords
        all_keywords = []
        for content in content_list:
            if content.get('keywords'):
                all_keywords.extend(content['keywords'])
        combined['keywords'] = list(set(all_keywords))  # Remove duplicates
        
        return combined
    
    def _extract_title(self, soup, config):
        """Extract page title."""
        # Try title selector first
        title_selector = config.get('title_selector', 'h1, .title, .post-title')
        title_elem = soup.select_one(title_selector)
        if title_elem:
            return title_elem.get_text(strip=True)
        
        # Fallback to HTML title tag
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        return ""
    
    def _extract_meta_description(self, soup, config):
        """Extract meta description with multiple fallbacks."""
        # Try meta description first
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # Try Open Graph description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        # Try Twitter description
        twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
        if twitter_desc and twitter_desc.get('content'):
            return twitter_desc['content'].strip()
        
        # Fallback: extract from content
        content = self._extract_main_content(soup, config)
        if content:
            return content[:150] + '...' if len(content) > 150 else content
        
        return ""
    
    def _extract_main_content(self, soup, config):
        """Extract main content using CSS selectors."""
        content_selector = config.get('content_selector', '.content, #main, article, .post-content, .entry-content, .page-content, .post, .entry')
        
        # Try multiple selectors for better compatibility
        selectors_to_try = [
            content_selector,
            '.elementor, .elementor-post, .elementor-widget-container',
            '.entry-content, .post-content, .page-content',
            'article, .post, .entry',
            '.content, #main, #content',
            'main, .main-content',
            '.widget-area, .sidebar-content'
        ]
        
        # Find the best content element (one with the most text)
        best_content_elem = None
        best_content_length = 0
        
        for selector in selectors_to_try:
            elements = soup.select(selector)
            for elem in elements:
                # Remove script and style elements
                for script in elem(["script", "style", "nav", "header", "footer", ".menu", ".navigation"]):
                    script.decompose()
                
                # Get text content
                content = elem.get_text(separator=' ', strip=True)
                content = ' '.join(content.split())
                
                # Check if this element has more meaningful content
                if len(content) > best_content_length and len(content) > 50:  # Minimum 50 chars
                    best_content_elem = elem
                    best_content_length = len(content)
        
        if best_content_elem:
            # Get text content from the best element
            content = best_content_elem.get_text(separator=' ', strip=True)
            content = ' '.join(content.split())
            
            max_length = config.get('max_content_length', 500)
            return content[:max_length] if len(content) > max_length else content
        
        # Fallback: try to get content from body
        body = soup.find('body')
        if body:
            # Remove navigation, header, footer
            for elem in body(['nav', 'header', 'footer', 'script', 'style']):
                elem.decompose()
            
            content = body.get_text(separator=' ', strip=True)
            content = ' '.join(content.split())
            
            max_length = config.get('max_content_length', 500)
            return content[:max_length] if len(content) > max_length else content
        
        return ""
    
    def _extract_keywords(self, soup, config):
        """Extract keywords from meta tags or content."""
        keywords = []
        
        # Try meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            keywords.extend(meta_keywords['content'].split(','))
        
        # Try to extract from content (simple approach)
        content = self._extract_main_content(soup, config)
        if content:
            # Extract potential keywords (words with 4+ characters)
            words = re.findall(r'\b\w{4,}\b', content.lower())
            word_freq = Counter(words)
            # Get top 5 most frequent words
            keywords.extend([word for word, _ in word_freq.most_common(5)])
        
        return list(set(keywords))  # Remove duplicates

    def scrape_content_with_lastmod(self, url, lastmod, config=None):
        """Scrape content from a URL with lastmod date."""
        content = self.scrape_content(url, config)
        if content and lastmod:
            content['lastmod'] = lastmod
        return content


class LLMsTxtGenerator:
    """Generate llms.txt file from scraped content."""
    
    def __init__(self, config):
        self.config = config
    
    def generate_llms_txt(self, urls_data, scraped_content, output_path=None):
        """Generate llms.txt file."""
        if output_path is None:
            output_path = self.config.get('output_file', 'llms.txt')
        
        # Backup existing file if enabled
        if self.config.get('backup_existing', True) and os.path.exists(output_path):
            backup_path = f"{output_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(output_path, backup_path)
            logger.info(f"Backed up existing file to: {backup_path}")
        
        # Prepare data for template
        template_data = self._prepare_template_data(urls_data, scraped_content)
        # Always define all_content_section for the template
        if template_data.get('all_content'):
            template_data['all_content_section'] = '\n## All Content (Uncategorized URLs)\n' + template_data['all_content'] + '\n'
        else:
            template_data['all_content_section'] = ''
        
        # Generate content
        template = self.config.get('template', self._get_default_template())
        content = template.format(**template_data)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Generated llms.txt: {output_path}")
        return output_path
    
    def _prepare_template_data(self, urls_data, scraped_content):
        """Prepare data for template formatting."""
        # Extract topics from content
        topics = self._extract_topics(scraped_content)
        
        # Generate smart description
        site_name = self.config.get('site_name', 'My Website')
        site_description = self.config.get('site_description', '')
        if not site_description:
            site_description = self._generate_smart_description(scraped_content, site_name)
        
        # Prepare pages data
        pages_data = self._prepare_pages_data(scraped_content)
        
        # Prepare detailed content data
        detailed_content = self._prepare_detailed_content(scraped_content)
        
        # Get site overview
        total_pages = len(urls_data)
        last_updated = self._get_last_updated(urls_data)
        
        return {
            'site_name': site_name,
            'site_description': site_description,
            'topics': topics,
            'pages': pages_data['pages'],
            'blogs': pages_data['blogs'],
            'products': pages_data['products'],
            'all_content': pages_data['all_content'],
            'detailed_content': detailed_content,
            'total_pages': total_pages,
            'pages_count': pages_data['pages_count'],
            'blogs_count': pages_data['blogs_count'],
            'products_count': pages_data['products_count'],
            'all_content_count': pages_data['all_content_count'],
            'last_updated': last_updated,
            'sitemap_url': self.config.get('sitemap_url', ''),
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _extract_topics(self, scraped_content):
        """Extract topics from scraped content with intelligent keyword detection."""
        topics = set()
        
        # Collect all content for analysis
        all_content = []
        all_titles = []
        all_descriptions = []
        
        for content in scraped_content.values():
            if content:
                if content.get('title'):
                    all_titles.append(content['title'])
                if content.get('description'):
                    all_descriptions.append(content['description'])
                if content.get('content'):
                    all_content.append(content['content'])
        
        # Combine all text for analysis
        combined_text = ' '.join(all_titles + all_descriptions + all_content).lower()
        
        # Extract meaningful topics using multiple strategies
        
        # 1. Extract AI and fashion related terms
        ai_fashion_terms = self._extract_ai_fashion_terms(combined_text)
        topics.update(ai_fashion_terms)
        
        # 2. Extract common industry terms
        industry_terms = self._extract_industry_terms(combined_text)
        topics.update(industry_terms)
        
        # 3. Extract high-frequency meaningful words
        common_terms = self._extract_common_terms(combined_text)
        topics.update(common_terms)
        
        # 4. Add default topics if we don't have enough content-based topics
        if len(topics) < 3:
            default_topics = self.config.get('default_topics', [])
            topics.update(default_topics)
        
        # Sort topics by relevance (AI/fashion terms first, then others)
        sorted_topics = self._sort_topics_by_relevance(list(topics))
        
        return '\n'.join(f"- {topic}" for topic in sorted_topics[:15])  # Limit to top 15
    
    def _extract_ai_fashion_terms(self, text):
        """Extract AI and fashion related terms from text."""
        ai_fashion_patterns = [
            r'\bai\s+(?:fashion|model|photography|influencer|modeling)\b',
            r'\b(?:fashion|model|photography|influencer)\s+ai\b',
            r'\bdigital\s+(?:model|twin|fashion|photography)\b',
            r'\b(?:model|fashion|photography)\s+digital\b',
            r'\bvirtual\s+(?:model|fashion|try.?on|fitting)\b',
            r'\b(?:model|fashion)\s+virtual\b',
            r'\bgenerative\s+(?:ai|fashion|model)\b',
            r'\b(?:ai|fashion)\s+generative\b',
            r'\bai.?powered\s+(?:fashion|model|photography)\b',
            r'\b(?:fashion|model|photography)\s+ai.?powered\b',
            r'\bartificial\s+intelligence\s+(?:fashion|model|photography)\b',
            r'\b(?:fashion|model|photography)\s+artificial\s+intelligence\b'
        ]
        
        terms = set()
        for pattern in ai_fashion_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean and capitalize the term
                term = ' '.join(word.capitalize() for word in match.split())
                terms.add(term)
        
        return terms
    
    def _extract_industry_terms(self, text):
        """Extract industry-specific terms."""
        industry_keywords = [
            'fashion', 'modeling', 'photography', 'influencer', 'ecommerce',
            'retail', 'branding', 'marketing', 'digital', 'virtual', 'online',
            'shopping', 'style', 'trend', 'design', 'creative', 'agency',
            'platform', 'technology', 'innovation', 'sustainability'
        ]
        
        terms = set()
        for keyword in industry_keywords:
            if keyword in text:
                terms.add(keyword.capitalize())
        
        return terms
    
    def _extract_common_terms(self, text):
        """Extract common meaningful terms from content."""
        # Remove common stop words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'a', 'an', 'as', 'from', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'you', 'your', 'yours', 'yourself', 'yourselves', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'what', 'which', 'who', 'whom', 'whose', 'whichever', 'whoever', 'whomever', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves'}
        
        # Extract words with 4+ characters, excluding stop words
        words = re.findall(r'\b\w{4,}\b', text)
        meaningful_words = [word for word in words if word.lower() not in stop_words]
        
        # Count frequency
        word_freq = Counter(meaningful_words)
        
        # Get top meaningful terms
        common_terms = []
        for word, count in word_freq.most_common(10):
            if count >= 2:  # Only include terms that appear at least twice
                common_terms.append(word.capitalize())
        
        return set(common_terms)
    
    def _sort_topics_by_relevance(self, topics):
        """Sort topics by relevance (AI/fashion terms first)."""
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for topic in topics:
            topic_lower = topic.lower()
            if any(term in topic_lower for term in ['ai', 'artificial intelligence', 'digital', 'virtual', 'generative']):
                high_priority.append(topic)
            elif any(term in topic_lower for term in ['fashion', 'model', 'photography', 'influencer', 'ecommerce']):
                medium_priority.append(topic)
            else:
                low_priority.append(topic)
        
        return high_priority + medium_priority + low_priority
    
    def _generate_smart_description(self, scraped_content, site_name):
        """Generate a smart site description based on content analysis."""
        if not scraped_content:
            return f"Comprehensive resource for {site_name}"
        
        # Analyze content to understand the site's focus
        all_titles = []
        all_descriptions = []
        
        for content in scraped_content.values():
            if content:
                if content.get('title'):
                    all_titles.append(content['title'])
                if content.get('description'):
                    all_descriptions.append(content['description'])
        
        # Look for patterns in titles and descriptions
        combined_text = ' '.join(all_titles + all_descriptions).lower()
        
        # Detect site type and generate appropriate description
        if any(term in combined_text for term in ['ai', 'artificial intelligence', 'digital', 'virtual']):
            if any(term in combined_text for term in ['fashion', 'model', 'photography']):
                return f"AI-powered fashion photography and modeling agency specializing in digital models, virtual fashion, and AI influencers. Leading platform for {site_name}."
            else:
                return f"AI-powered platform and agency specializing in digital innovation and artificial intelligence solutions for {site_name}."
        elif any(term in combined_text for term in ['fashion', 'model', 'photography']):
            return f"Professional fashion photography and modeling agency providing high-quality content and influencer services for {site_name}."
        else:
            return f"Comprehensive resource and platform for {site_name}, offering professional services and industry insights."
    
    def _prepare_pages_data(self, scraped_content):
        """Prepare pages data for template, separating pages from blogs and products, and collecting uncategorized URLs for 'All Content'."""
        pages = []
        blogs = []
        products = []
        all_content = []
        max_pages = self.config.get('max_pages_to_process', 10)
        max_blogs = self.config.get('max_blogs', 10)
        max_products = self.config.get('max_products', 10)
        
        for url, content in scraped_content.items():
            if content:
                title = content.get('title', 'Untitled')
                description = content.get('description', '')
                if not description:
                    description = content.get('content', '')[:100] + '...'
                source_type = content.get('source_type')
                if source_type == 'product':
                    products.append({
                        'url': url,
                        'title': title,
                        'description': description,
                        'lastmod': content.get('lastmod', ''),
                        'scraped_at': content.get('scraped_at', '')
                    })
                elif source_type == 'blog':
                    blogs.append({
                        'url': url,
                        'title': title,
                        'description': description,
                        'lastmod': content.get('lastmod', ''),
                        'scraped_at': content.get('scraped_at', '')
                    })
                elif self._is_product_page(url, content, source_type=source_type):
                    products.append({
                        'url': url,
                        'title': title,
                        'description': description,
                        'lastmod': content.get('lastmod', ''),
                        'scraped_at': content.get('scraped_at', '')
                    })
                elif self._is_blog_post(url, content, source_type=source_type):
                    blogs.append({
                        'url': url,
                        'title': title,
                        'description': description,
                        'lastmod': content.get('lastmod', ''),
                        'scraped_at': content.get('scraped_at', '')
                    })
                elif source_type == 'page':
                    pages.append({
                        'url': url,
                        'title': title,
                        'description': description
                    })
                else:
                    all_content.append({
                        'url': url,
                        'title': title,
                        'description': description
                    })
        blogs.sort(key=lambda x: x.get('lastmod', x.get('scraped_at', '')), reverse=True)
        blogs = blogs[:max_blogs]
        products.sort(key=lambda x: x.get('lastmod', x.get('scraped_at', '')), reverse=True)
        products = products[:max_products]
        pages = pages[:max_pages]
        pages_text = '\n'.join([f"- [{page['title']}]({page['url']}): {page['description']}" for page in pages])
        blogs_text = '\n'.join([f"- [{blog['title']}]({blog['url']}): {blog['description']}" for blog in blogs])
        products_text = '\n'.join([f"- [{product['title']}]({product['url']}): {product['description']}" for product in products])
        all_content_text = '\n'.join([f"- [{item['title']}]({item['url']}): {item['description']}" for item in all_content])
        return {
            'pages': pages_text,
            'blogs': blogs_text,
            'products': products_text,
            'all_content': all_content_text,
            'pages_count': len(pages),
            'blogs_count': len(blogs),
            'products_count': len(products),
            'all_content_count': len(all_content)
        }
    
    def _prepare_detailed_content(self, scraped_content):
        """Prepare detailed content data for template with full content and dates."""
        detailed_items = []
        max_detailed_items = self.config.get('max_detailed_content', 10)
        
        # Combine all content and sort by recency
        all_content = []
        for url, content in scraped_content.items():
            if content:
                all_content.append({
                    'url': url,
                    'title': content.get('title', 'Untitled'),
                    'description': content.get('description', ''),
                    'content': content.get('content', ''),
                    'lastmod': content.get('lastmod', ''),
                    'scraped_at': content.get('scraped_at', ''),
                    'source_type': content.get('source_type')
                })
        
        # Sort by lastmod or scraped_at date (most recent first)
        all_content.sort(key=lambda x: x.get('lastmod', x.get('scraped_at', '')), reverse=True)
        
        # Take the latest items
        latest_content = all_content[:max_detailed_items]
        
        # Group by type (pages vs blogs vs products)
        pages = []
        blogs = []
        products = []
        
        for item in latest_content:
            if self._is_product_page(item['url'], item, item.get('source_type')):
                products.append(item)
            elif item.get('source_type') == 'blog' or self._is_blog_post(item['url'], item, item.get('source_type')):
                blogs.append(item)
            else:
                pages.append(item)
        
        # Format the detailed content
        detailed_text = []
        
        # Add pages section
        if pages:
            detailed_text.append("## Pages")
            detailed_text.append("")
            for page in pages:
                detailed_text.append(self._format_detailed_item(page))
                detailed_text.append("")
        
        # Add blogs section
        if blogs:
            detailed_text.append("## Blogs")
            detailed_text.append("")
            for blog in blogs:
                detailed_text.append(self._format_detailed_item(blog))
                detailed_text.append("")
        
        # Add products section
        if products:
            detailed_text.append("## Products")
            detailed_text.append("")
            for product in products:
                detailed_text.append(self._format_detailed_item(product))
                detailed_text.append("")
        
        return '\n'.join(detailed_text)
    
    def _format_detailed_item(self, item):
        """Format a single detailed content item."""
        lines = []
        
        # Add published and modified dates
        if item.get('lastmod'):
            # Try to parse the date and format it
            try:
                # Handle various date formats
                date_str = item['lastmod']
                if 'T' in date_str:
                    date_str = date_str.split('T')[0]  # Remove time part
                elif ' ' in date_str:
                    date_str = date_str.split(' ')[0]  # Remove time part
                
                # Parse and format the date
                from datetime import datetime
                parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                formatted_date = parsed_date.strftime('%Y-%m-%d')
                lines.append(f"- Published: {formatted_date}")
                lines.append(f"- Modified: {formatted_date}")
            except:
                lines.append(f"- Published: {item['lastmod']}")
                lines.append(f"- Modified: {item['lastmod']}")
        else:
            lines.append("- Published: Unknown")
            lines.append("- Modified: Unknown")
        
        # Add URL
        lines.append(f"- URL: {item['url']}")
        lines.append("")
        
        # Add content (truncate if too long)
        content = item.get('content', '')
        if not content:
            content = item.get('description', '')
        
        # Clean up the content
        content = self._clean_content_for_display(content)
        
        # Truncate if too long (keep first 2000 characters)
        if len(content) > 2000:
            content = content[:2000] + "..."
        
        lines.append(content)
        lines.append("")
        lines.append("---")
        
        return '\n'.join(lines)
    
    def _clean_content_for_display(self, content):
        """Clean content for display in detailed section."""
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove HTML tags if present
        content = re.sub(r'<[^>]+>', '', content)
        
        # Clean up common artifacts
        content = content.replace('&nbsp;', ' ')
        content = content.replace('&amp;', '&')
        content = content.replace('&lt;', '<')
        content = content.replace('&gt;', '>')
        content = content.replace('&quot;', '"')
        
        # Remove excessive periods and spaces
        content = re.sub(r'\.{3,}', '...', content)
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    def _is_blog_post(self, url, content, source_type=None):
        """Determine if a URL/content represents a blog post."""
        if source_type == 'blog' or (isinstance(content, dict) and content.get('source_type') == 'blog'):
            return True
        # Check URL patterns for blog posts
        blog_patterns = [
            r'/blog/', r'/post/', r'/article/', r'/news/', r'/story/',
            r'/\d{4}/\d{2}/', r'/\d{4}/',  # Date patterns
            r'/category/', r'/tag/', r'/author/'
        ]
        
        for pattern in blog_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        # Check content indicators
        title = content.get('title', '').lower()
        description = content.get('description', '').lower()
        
        blog_indicators = [
            'blog', 'post', 'article', 'news', 'story', 'published',
            'author', 'category', 'tag', 'comment', 'share'
        ]
        
        if any(indicator in title or indicator in description for indicator in blog_indicators):
            return True
        
        # Check for date patterns in title or description
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}', r'\d{2}/\d{2}/\d{4}', r'\d{4}/\d{2}/\d{2}',
            r'january|february|march|april|may|june|july|august|september|october|november|december'
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, title + ' ' + description, re.IGNORECASE):
                return True
        
        return False
    
    def _is_product_page(self, url, content, source_type=None):
        """Determine if a URL/content represents a product page."""
        # Check URL patterns for product pages
        product_patterns = [
            r'/product/', r'/products/', r'/shop/', r'/store/',
            r'/item/', r'/goods/', r'/merchandise/', r'/catalog/',
            r'/buy/', r'/purchase/', r'/order/', r'/cart/',
            r'/ecommerce/', r'/e-commerce/', r'/retail/'
        ]
        
        for pattern in product_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        # Check content indicators
        title = content.get('title', '').lower()
        description = content.get('description', '').lower()
        content_text = content.get('content', '').lower()
        
        product_indicators = [
            'product', 'shop', 'store', 'buy', 'purchase', 'order',
            'price', 'cost', 'sale', 'discount', 'add to cart',
            'shopping cart', 'checkout', 'payment', 'shipping',
            'in stock', 'out of stock', 'quantity', 'size', 'color',
            'material', 'brand', 'model', 'sku', 'upc', 'ean'
        ]
        
        if any(indicator in title or indicator in description or indicator in content_text for indicator in product_indicators):
            return True
        
        # Check for price patterns
        price_patterns = [
            r'\$\d+\.?\d*', r'€\d+\.?\d*', r'£\d+\.?\d*',
            r'\d+\.?\d*\s*(dollars?|euros?|pounds?)',
            r'price:\s*\$\d+\.?\d*', r'cost:\s*\$\d+\.?\d*'
        ]
        
        for pattern in price_patterns:
            if re.search(pattern, title + ' ' + description + ' ' + content_text, re.IGNORECASE):
                return True
        
        return False
    
    def _get_last_updated(self, urls_data):
        """Get the most recent lastmod date."""
        lastmod_dates = [url.get('lastmod') for url in urls_data if url.get('lastmod')]
        if lastmod_dates:
            return max(lastmod_dates)
        return "Unknown"
    
    def _get_default_template(self):
        """Get default template if none provided, now with All Content section."""
        return """# {site_name}

{site_description}

## Key Topics
{topics}

## Important Pages
{pages}

## Recent Blog Posts
{blogs}

## Products
{products}

{all_content_section}

## Detailed Content

{detailed_content}

## Site Overview
- **Total Pages**: {total_pages}
- **Pages Listed**: {pages_count}
- **Blog Posts Listed**: {blogs_count}
- **Products Listed**: {products_count}
- **All Content Listed**: {all_content_count}
- **Last Updated**: {last_updated}
- **Sitemap**: {sitemap_url}

---
*Generated on {generation_date}*"""


class SitemapDetector:
    """Detect sitemap URLs from a main website URL."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LLMs.txt Generator Bot (+https://github.com/your-repo)'
        })
    
    def detect_sitemap_url(self, main_url):
        """Detect sitemap URL from main website URL."""
        try:
            # Normalize the URL
            if not main_url.startswith(('http://', 'https://')):
                main_url = 'https://' + main_url
            
            # Remove trailing slash
            main_url = main_url.rstrip('/')
            
            logger.info(f"Detecting sitemap for: {main_url}")
            
            # Common sitemap locations to try
            sitemap_candidates = [
                f"{main_url}/sitemap.xml",
                f"{main_url}/sitemap_index.xml",
                f"{main_url}/sitemap/sitemap.xml",
                f"{main_url}/sitemap/sitemap_index.xml",
                f"{main_url}/sitemaps/sitemap.xml",
                f"{main_url}/sitemaps/sitemap_index.xml",
                f"{main_url}/wp-sitemap.xml",
                f"{main_url}/sitemap1.xml"
            ]
            
            # Try each candidate
            for sitemap_url in sitemap_candidates:
                try:
                    logger.info(f"Trying sitemap candidate: {sitemap_url}")
                    response = self.session.head(sitemap_url, timeout=10)
                    if response.status_code == 200:
                        logger.info(f"Found sitemap at: {sitemap_url}")
                        return sitemap_url
                except Exception as e:
                    logger.debug(f"Failed to access {sitemap_url}: {e}")
                    continue
            
            # If no direct sitemap found, try robots.txt
            robots_sitemap = self._check_robots_txt(main_url)
            if robots_sitemap:
                logger.info(f"Found sitemap in robots.txt: {robots_sitemap}")
                return robots_sitemap
            
            # If still no sitemap found, try to discover from HTML
            html_sitemap = self._discover_from_html(main_url)
            if html_sitemap:
                logger.info(f"Found sitemap link in HTML: {html_sitemap}")
                return html_sitemap
            
            raise Exception(f"Could not detect sitemap URL for {main_url}. Please provide the sitemap URL directly.")
            
        except Exception as e:
            logger.error(f"Error detecting sitemap: {e}")
            raise
    
    def _check_robots_txt(self, main_url):
        """Check robots.txt for sitemap location."""
        try:
            robots_url = f"{main_url}/robots.txt"
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    line = line.strip()
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        return sitemap_url
        except Exception as e:
            logger.debug(f"Error checking robots.txt: {e}")
        return None
    
    def _discover_from_html(self, main_url):
        """Try to discover sitemap from HTML head section."""
        try:
            response = self.session.get(main_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for sitemap in link tags
                for link in soup.find_all('link', rel='sitemap'):
                    href = link.get('href')
                    if href:
                        return urljoin(main_url, href)
                
                # Look for sitemap in meta tags
                for meta in soup.find_all('meta', attrs={'name': 'sitemap'}):
                    content = meta.get('content')
                    if content:
                        return urljoin(main_url, content)
                
                # Look for common sitemap links in the page
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    if 'sitemap' in href.lower():
                        return urljoin(main_url, href)
                        
        except Exception as e:
            logger.debug(f"Error discovering from HTML: {e}")
        return None


class SiteAnalyzer:
    """Analyzes a website to automatically detect site name, description, and optimal selectors."""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def analyze_site(self, url):
        """Analyze a website to detect site information and optimal selectors."""
        try:
            # Get the homepage
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Detect site name
            site_name = self._detect_site_name(soup, url)
            
            # Detect site description
            site_description = self._detect_site_description(soup)
            
            # Detect optimal content selector
            content_selector = self._detect_content_selector(soup)
            
            # Detect optimal title selector
            title_selector = self._detect_title_selector(soup)
            
            return {
                'site_name': site_name,
                'site_description': site_description,
                'content_selector': content_selector,
                'title_selector': title_selector
            }
            
        except Exception as e:
            logger.warning(f"Could not analyze site {url}: {e}")
            return {
                'site_name': 'Unknown Site',
                'site_description': 'A comprehensive resource',
                'content_selector': '.content, #main, article, .post-content, .entry-content, .page-content, .post, .entry, .elementor, .elementor-post',
                'title_selector': 'h1, .title, .post-title, .entry-title, .page-title'
            }
    
    def _detect_site_name(self, soup, url):
        """Detect the site name from various sources."""
        # Try title tag first
        title_tag = soup.find('title')
        if title_tag and title_tag.get_text().strip():
            title = title_tag.get_text().strip()
            # Clean up common title patterns
            if ' - ' in title:
                title = title.split(' - ')[0]
            elif ' | ' in title:
                title = title.split(' | ')[0]
            elif ' » ' in title:
                title = title.split(' » ')[0]
            return title
        
        # Try h1 tag
        h1_tag = soup.find('h1')
        if h1_tag and h1_tag.get_text().strip():
            return h1_tag.get_text().strip()
        
        # Try logo alt text
        logo = soup.find('img', alt=True)
        if logo and logo.get('alt'):
            return logo.get('alt').strip()
        
        # Fallback to domain name
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return domain.replace('www.', '').title()
    
    def _detect_site_description(self, soup):
        """Detect the site description from meta tags."""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc.get('content').strip()
        
        # Try Open Graph description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc.get('content').strip()
        
        # Try first paragraph
        first_p = soup.find('p')
        if first_p and first_p.get_text().strip():
            text = first_p.get_text().strip()
            if len(text) > 50:
                return text[:200] + '...' if len(text) > 200 else text
        
        return "A comprehensive resource"
    
    def _detect_content_selector(self, soup):
        """Detect the optimal content selector by analyzing the page structure."""
        selectors_to_try = [
            '.elementor-post__content',
            '.elementor',
            '.post-content',
            '.entry-content',
            '.content',
            'article',
            '.main-content',
            '#main',
            '.post',
            '.entry'
        ]
        
        for selector in selectors_to_try:
            elements = soup.select(selector)
            if elements:
                # Check if the element has substantial content
                for element in elements:
                    text = element.get_text().strip()
                    if len(text) > 100:  # Substantial content
                        return selector
        
        # If no good selector found, return the default
        return '.content, #main, article, .post-content, .entry-content, .page-content, .post, .entry, .elementor, .elementor-post'
    
    def _detect_title_selector(self, soup):
        """Detect the optimal title selector by analyzing the page structure."""
        # Check if h1 exists and has content
        h1_tags = soup.find_all('h1')
        if h1_tags:
            for h1 in h1_tags:
                if h1.get_text().strip():
                    return 'h1'
        
        # Check for common title classes
        title_selectors = [
            '.post-title',
            '.entry-title',
            '.page-title',
            '.title',
            'h2'
        ]
        
        for selector in title_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    if element.get_text().strip():
                        return selector
        
        # Fallback to default
        return 'h1, .title, .post-title, .entry-title, .page-title'


def load_config(config_path="config.yaml"):
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        logger.info(f"Loaded configuration from: {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise


def main(sitemap_url=None, site_name=None, auto_detect=False):
    """Main function to run the llms.txt generator."""
    try:
        # Load configuration
        config = load_config()
        
        # If sitemap_url is provided, use it; otherwise use config
        if sitemap_url:
            config['sitemap_url'] = sitemap_url
        if site_name:
            config['site_name'] = site_name
        
        # Auto-detect sitemap if requested or if main URL is provided
        if auto_detect or (sitemap_url and not sitemap_url.endswith(('.xml', 'sitemap'))):
            detector = SitemapDetector()
            detected_sitemap = detector.detect_sitemap_url(config['sitemap_url'])
            config['sitemap_url'] = detected_sitemap
            logger.info(f"Auto-detected sitemap: {detected_sitemap}")
        
        # Initialize components
        sitemap_parser = SitemapParser(config)
        content_scraper = ContentScraper(config)
        llms_generator = LLMsTxtGenerator(config)
        
        # Set up robots.txt checker ONLY if explicitly enabled
        respect_robots = config.get('respect_robots_txt', False)  # Default to False
        if respect_robots:
            base_url = urlparse(config['sitemap_url']).scheme + '://' + urlparse(config['sitemap_url']).netloc
            robots_checker = RobotsTxtChecker(base_url)
            content_scraper.set_robots_checker(robots_checker)
            logger.info("Robots.txt checking enabled")
        else:
            logger.info("Robots.txt checking disabled - will scrape all content")
        
        # Parse sitemap
        urls_data = sitemap_parser.parse_sitemap(config['sitemap_url'])
        
        # Separate blogs, pages, and products
        blog_urls = []
        page_urls = []
        product_urls = []
        
        for url_data in urls_data:
            if url_data.get('source_type') == 'blog':
                blog_urls.append(url_data)
            elif url_data.get('source_type') == 'page':
                page_urls.append(url_data)
            elif url_data.get('source_type') == 'product':
                product_urls.append(url_data)
            else:
                # For URLs without explicit source_type, use fallback logic
                page_urls.append(url_data)
        
        logger.info(f"Found {len(blog_urls)} blog URLs, {len(page_urls)} page URLs, and {len(product_urls)} product URLs")
        
        # Debug: Show first few page URLs
        if page_urls:
            logger.info(f"DEBUG: First 5 page URLs to process: {[url['loc'] for url in page_urls[:5]]}")
        else:
            logger.warning("DEBUG: No page URLs found!")
        
        # Scrape content from URLs - process blogs, pages, and products independently
        scraped_content = {}
        max_pages = config.get('max_pages_to_process', 10)
        max_blogs = config.get('max_blogs', 10)
        max_products = config.get('max_products', 10)
        request_delay = config.get('request_delay', 1.0)
        
        logger.info(f"DEBUG: max_pages={max_pages}, max_blogs={max_blogs}")
        
        # Process blogs (up to max_blogs)
        blogs_processed = 0
        for url_data in blog_urls:
            if blogs_processed >= max_blogs:
                break
            
            # Extract content with lastmod date if available
            if url_data.get('lastmod'):
                content = content_scraper.scrape_content_with_lastmod(url_data['loc'], url_data['lastmod'], config)
            else:
                content = content_scraper.scrape_content(url_data['loc'], config)
                
            if content:
                # Preserve source_type if present
                if url_data.get('source_type'):
                    content['source_type'] = url_data['source_type']
                scraped_content[url_data['loc']] = content
                blogs_processed += 1
            
            # Respect request delay
            if request_delay > 0:
                time.sleep(request_delay)
        
        logger.info(f"DEBUG: Finished processing blogs. blogs_processed={blogs_processed}")
        
        # Process pages (up to max_pages) - independent of blogs
        pages_processed = 0
        logger.info(f"DEBUG: Starting page processing loop. page_urls count: {len(page_urls)}")
        
        for url_data in page_urls:
            if pages_processed >= max_pages:
                logger.info(f"DEBUG: Reached max_pages limit ({max_pages}), stopping page processing")
                break
            
            logger.info(f"DEBUG: Processing page {pages_processed + 1}/{min(max_pages, len(page_urls))}: {url_data['loc']}")
            
            # Extract content with lastmod date if available
            if url_data.get('lastmod'):
                content = content_scraper.scrape_content_with_lastmod(url_data['loc'], url_data['lastmod'], config)
            else:
                content = content_scraper.scrape_content(url_data['loc'], config)
                
            if content:
                # Preserve source_type if present
                if url_data.get('source_type'):
                    content['source_type'] = url_data['source_type']
                scraped_content[url_data['loc']] = content
                pages_processed += 1
                logger.info(f"DEBUG: Successfully processed page {pages_processed}: {url_data['loc']}")
            else:
                logger.warning(f"DEBUG: Failed to extract content from page: {url_data['loc']}")
            
            # Respect request delay
            if request_delay > 0:
                time.sleep(request_delay)
        
        logger.info(f"DEBUG: Finished processing pages. pages_processed={pages_processed}")
        
        # Process products (up to max_products limit)
        products_processed = 0
        logger.info(f"DEBUG: Starting product processing loop. product_urls count: {len(product_urls)}")
        
        for url_data in product_urls:
            if products_processed >= max_products:  # Use max_products limit
                logger.info(f"DEBUG: Reached max_products limit ({max_products}), stopping product processing")
                break
            
            logger.info(f"DEBUG: Processing product {products_processed + 1}/{min(max_blogs, len(product_urls))}: {url_data['loc']}")
            
            # Extract content with lastmod date if available
            if url_data.get('lastmod'):
                content = content_scraper.scrape_content_with_lastmod(url_data['loc'], url_data['lastmod'], config)
            else:
                content = content_scraper.scrape_content(url_data['loc'], config)
                
            if content:
                # Preserve source_type if present
                if url_data.get('source_type'):
                    content['source_type'] = url_data['source_type']
                scraped_content[url_data['loc']] = content
                products_processed += 1
                logger.info(f"DEBUG: Successfully processed product {products_processed}: {url_data['loc']}")
            else:
                logger.warning(f"DEBUG: Failed to extract content from product: {url_data['loc']}")
            
            # Respect request delay
            if request_delay > 0:
                time.sleep(request_delay)
        
        logger.info(f"DEBUG: Finished processing products. products_processed={products_processed}")
        logger.info(f"Processed {blogs_processed} blogs, {pages_processed} pages, and {products_processed} products")
        
        # Generate llms.txt
        output_path = llms_generator.generate_llms_txt(urls_data, scraped_content)
        
        logger.info(f"Successfully generated llms.txt with {len(scraped_content)} pages")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise


if __name__ == "__main__":
    main() 
    main() 
    main() 