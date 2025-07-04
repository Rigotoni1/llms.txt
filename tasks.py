import os
import redis
import json
import gc
import time
from rq import get_current_job, Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from main import SitemapParser, LLMsTxtGenerator
from firecrawl_working import WorkingFirecrawlScraper
from utils import validate_config, format_file_size
from datetime import datetime
import multiprocessing
import threading
from collections import defaultdict

multiprocessing.set_start_method('spawn', force=True)

# Create necessary directories
os.makedirs('outputs', exist_ok=True)
os.makedirs('uploads', exist_ok=True)

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
redis_conn = redis.Redis.from_url(REDIS_URL)

# Configure queues for different job types
batch_queue = Queue('batch_processing', connection=redis_conn)
merge_queue = Queue('merge_processing', connection=redis_conn)

# Batch processing configuration
BATCH_SIZE = 50  # URLs per batch
MAX_CONCURRENT_BATCHES = 10  # Maximum concurrent batches per job
MAX_WORKERS_PER_BATCH = 4  # Threads per batch

def log_progress(task_id, message, progress_data=None):
    """Log progress with optional progress data for frontend."""
    log_entry = {
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'level': 'INFO',
        'message': message
    }
    
    if progress_data:
        log_entry['progress'] = progress_data
    
    redis_conn.rpush(f'logs:{task_id}', json.dumps(log_entry))
    redis_conn.expire(f'logs:{task_id}', 3600)

def process_url_batch(batch_data, task_id, batch_id):
    """Process a single batch of URLs with memory management."""
    print("DEBUG: process_url_batch called, scraped_content will be initialized")
    scraped_content = {}  # Always define at the top
    try:
        config = batch_data['config']
        urls = batch_data['urls']
        batch_start = batch_data.get('batch_start', 0)
        
        # DEBUG: Check config for firecrawl_api_key
        firecrawl_api_key = config.get('firecrawl_api_key')
        print(f"🔍 DEBUG: firecrawl_api_key in batch config: {'SET' if firecrawl_api_key else 'NOT SET'}")
        if firecrawl_api_key:
            print(f"🔍 DEBUG: firecrawl_api_key length: {len(firecrawl_api_key)}")
            print(f"🔍 DEBUG: firecrawl_api_key starts with: {firecrawl_api_key[:10]}...")
        else:
            print("❌ DEBUG: firecrawl_api_key is missing from config!")
            print(f"🔍 DEBUG: Available config keys: {list(config.keys())}")
        
        log_progress(task_id, f'Starting batch {batch_id} with {len(urls)} URLs')
        
        content_scraper = WorkingFirecrawlScraper(config)
        
        # Process URLs in parallel within the batch
        with ThreadPoolExecutor(max_workers=MAX_WORKERS_PER_BATCH) as executor:
            future_to_url = {}
            
            for i, url_data in enumerate(urls):
                future = executor.submit(
                    scrape_single_url, 
                    content_scraper, 
                    url_data, 
                    config
                )
                future_to_url[future] = (url_data, i)
            
            # Collect results as they complete
            for future in as_completed(future_to_url):
                url_data, index = future_to_url[future]
                try:
                    content = future.result()
                    if content:
                        scraped_content[url_data['loc']] = content
                        
                        # Log progress every 10 URLs
                        if (batch_start + index + 1) % 10 == 0:
                            log_progress(task_id, f'Batch {batch_id}: Processed {index + 1}/{len(urls)} URLs')
                            
                except Exception as e:
                    log_progress(task_id, f'Error processing {url_data["loc"]}: {str(e)}')
        
        # Save batch results to Redis
        batch_key = f'batch:{task_id}:{batch_id}'
        redis_conn.setex(batch_key, 3600, json.dumps(scraped_content))
        
        log_progress(task_id, f'Completed batch {batch_id}: {len(scraped_content)} URLs scraped')
        result = len(scraped_content)
        # Force garbage collection
        del scraped_content
        gc.collect()
        return result
    except Exception as e:
        log_progress(task_id, f'Batch {batch_id} failed: {str(e)}')
        raise

def scrape_single_url(content_scraper, url_data, config):
    """Scrape a single URL with error handling."""
    try:
        if url_data.get('lastmod'):
            content = content_scraper.scrape_content_with_lastmod(url_data['loc'], url_data['lastmod'], config)
        else:
            content = content_scraper.scrape_content(url_data['loc'], config)
            
        if content and url_data.get('source_type'):
            content['source_type'] = url_data['source_type']
            
        return content
    except Exception as e:
        return None

def merge_batches(task_id, total_urls, config):
    """Merge all batch results into final llms.txt file."""
    try:
        log_progress(task_id, 'Starting batch merge...')
        
        # Collect all batch results
        all_scraped_content = {}
        batch_count = 0
        
        while True:
            batch_key = f'batch:{task_id}:{batch_count}'
            batch_data = redis_conn.get(batch_key)
            
            if not batch_data:
                break
                
            batch_content = json.loads(batch_data)
            all_scraped_content.update(batch_content)
            batch_count += 1
            
            # Clear batch data from Redis
            redis_conn.delete(batch_key)
        
        log_progress(task_id, f'Merged {batch_count} batches, total content: {len(all_scraped_content)} URLs')
        
        # Generate final llms.txt
        llms_generator = LLMsTxtGenerator(config)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"llms_{config['site_name'].replace(' ', '_')}_{timestamp}.txt"
        
        # Ensure outputs directory exists with proper permissions
        os.makedirs('outputs', exist_ok=True)
        try:
            # Test if directory is writable
            test_file = os.path.join('outputs', '.test_write')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except Exception as e:
            log_progress(task_id, f'Warning: outputs directory not writable: {str(e)}')
            # Try to fix permissions
            try:
                os.chmod('outputs', 0o777)
                log_progress(task_id, 'Fixed outputs directory permissions')
            except Exception as perm_error:
                log_progress(task_id, f'Could not fix permissions: {str(perm_error)}')
        
        output_path = os.path.join('outputs', output_filename)
        
        # Create dummy urls_data for generation (we only need the count)
        urls_data = [{'loc': url} for url in all_scraped_content.keys()]
        
        llms_generator.generate_llms_txt(urls_data, all_scraped_content, output_path)
        
        # Send completion data
        completion_data = {
            'type': 'complete',
            'data': {
                'filename': output_filename,
                'stats': {
                    'total_scraped': len(all_scraped_content),
                    'total_urls': total_urls,
                    'batches_processed': batch_count
                }
            }
        }
        
        redis_conn.rpush(f'logs:{task_id}', json.dumps(completion_data))
        redis_conn.expire(f'logs:{task_id}', 3600)
        
        log_progress(task_id, f'Generated llms.txt: {output_filename}')
        
        # Clear memory
        del all_scraped_content
        gc.collect()
        
        return output_filename
        
    except Exception as e:
        error_data = {
            'type': 'error',
            'error': str(e)
        }
        redis_conn.rpush(f'logs:{task_id}', json.dumps(error_data))
        redis_conn.expire(f'logs:{task_id}', 3600)
        log_progress(task_id, f'Merge failed: {str(e)}')
        raise

def generate_llms_background(config, task_id):
    """Background job for llms.txt generation with scalable batch processing."""
    try:
        validate_config(config)
        log_progress(task_id, 'Configuration validated.')
        
        sitemap_parser = SitemapParser(config)
        
        log_progress(task_id, 'Parsing sitemap...')
        urls_data = sitemap_parser.parse_sitemap(config['sitemap_url'])
        total_urls = len(urls_data)
        
        log_progress(task_id, f'Found {total_urls} URLs.', {
            'scraped': 0,
            'total': total_urls,
            'percentage': 0
        })
        
        # Separate URLs by type
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
                page_urls.append(url_data)
        
        log_progress(task_id, f'Categorized URLs: {len(blog_urls)} blogs, {len(page_urls)} pages, {len(product_urls)} products')
        
        # Apply tier limits
        max_blogs = config.get('max_blogs', 10)
        max_pages = config.get('max_pages_to_process', 10)
        max_products = config.get('max_products', 10)
        
        blog_urls = blog_urls[:max_blogs]
        page_urls = page_urls[:max_pages]
        product_urls = product_urls[:max_products]
        
        # Combine all URLs for batch processing
        all_urls = blog_urls + page_urls + product_urls
        total_to_process = len(all_urls)
        
        log_progress(task_id, f'Will process {total_to_process} URLs in batches of {BATCH_SIZE}')
        
        # Create batches
        batches = []
        for i in range(0, len(all_urls), BATCH_SIZE):
            batch_urls = all_urls[i:i + BATCH_SIZE]
            batches.append({
                'config': config,
                'urls': batch_urls,
                'batch_start': i
            })
        
        log_progress(task_id, f'Created {len(batches)} batches')
        
        # Process batches with limited concurrency
        completed_batches = 0
        total_scraped = 0
        
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_BATCHES) as executor:
            future_to_batch = {}
            
            # Submit initial batches
            for i, batch_data in enumerate(batches):
                future = executor.submit(process_url_batch, batch_data, task_id, i)
                future_to_batch[future] = i
            
            # Process completed batches and submit new ones
            for future in as_completed(future_to_batch):
                batch_id = future_to_batch[future]
                try:
                    batch_scraped = future.result()
                    completed_batches += 1
                    total_scraped += batch_scraped
                    
                    # Update progress
                    percentage = int((completed_batches / len(batches)) * 100)
                    log_progress(task_id, f'Completed {completed_batches}/{len(batches)} batches ({percentage}%)', {
                        'scraped': total_scraped,
                        'total': total_to_process,
                        'percentage': percentage
                    })
                    
                except Exception as e:
                    log_progress(task_id, f'Batch {batch_id} failed: {str(e)}')
        
        log_progress(task_id, f'All batches completed! Total scraped: {total_scraped}/{total_to_process}')
        
        # Merge batches into final file
        return merge_batches(task_id, total_to_process, config)
        
    except Exception as e:
        error_data = {
            'type': 'error',
            'error': str(e)
        }
        redis_conn.rpush(f'logs:{task_id}', json.dumps(error_data))
        redis_conn.expire(f'logs:{task_id}', 3600)
        log_progress(task_id, f'Error: {str(e)}')
        raise

def get_queue_status():
    """Get current queue status for monitoring."""
    return {
        'batch_queue': len(batch_queue),
        'merge_queue': len(merge_queue),
        'workers': len(redis_conn.smembers('rq:workers'))
    }

def cleanup_failed_jobs():
    """Clean up failed jobs and their associated data."""
    try:
        # Get all batch keys
        batch_keys = redis_conn.keys('batch:*')
        for key in batch_keys:
            # Check if job is still active
            task_id = key.split(':')[1]
            if not redis_conn.exists(f'logs:{task_id}'):
                redis_conn.delete(key)
    except Exception as e:
        print(f"Cleanup error: {e}")

# Schedule cleanup every hour
def schedule_cleanup():
    """Schedule periodic cleanup of failed jobs."""
    while True:
        time.sleep(3600)  # 1 hour
        cleanup_failed_jobs()

# Start cleanup thread
cleanup_thread = threading.Thread(target=schedule_cleanup, daemon=True)
cleanup_thread.start() 