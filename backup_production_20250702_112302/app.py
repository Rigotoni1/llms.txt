#!/usr/bin/env python3
"""
Flask Web Application for LLMs.txt Generator
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for, Response, stream_with_context, session
import os
import yaml
import tempfile
import zipfile
from datetime import datetime
import logging
from werkzeug.utils import secure_filename
import queue
import threading
import time
import json
import uuid
from functools import wraps
import stripe
from tasks import generate_llms_background, log_progress
from rq import Queue
import redis

from main import SitemapParser, ContentScraper, LLMsTxtGenerator, RobotsTxtChecker
from utils import validate_config, create_sample_config, format_file_size

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'yaml', 'yml'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Global log queue for streaming
log_queue = queue.Queue()
generation_status = {}

# Tier limits
TIER_LIMITS = {
    'free': {
        'max_pages': 5,
        'max_blogs': 10,
        'max_products': 10,
        'max_content_length': 500,
        'name': 'Free',
        'price': 0
    },
    'premium': {
        'max_pages': 100,
        'max_blogs': 100,
        'max_products': 100,
        'max_content_length': 2000,
        'name': 'Premium',
        'price': 19.00
    },
    'pro': {
        'max_pages': 1000,
        'max_blogs': 1000,
        'max_products': 1000,
        'max_content_length': 5000,
        'name': 'Pro',
        'price': 4.99,
        'recurring': True
    }
}

# Mock user database (in production, use a real database)
users_db = {}

# Stripe test keys (replace with your own from dashboard)
STRIPE_PUBLISHABLE_KEY = 'pk_test_XXXXXXXXXXXXXXXXXXXXXXXX'
STRIPE_SECRET_KEY = 'sk_test_XXXXXXXXXXXXXXXXXXXXXXXX'
stripe.api_key = STRIPE_SECRET_KEY

# Stripe product/price IDs (replace with your own from Stripe dashboard)
STRIPE_PREMIUM_PRICE_ID = 'price_1PremiumTest'  # one-time
STRIPE_PRO_PRICE_ID = 'price_1ProTest'          # recurring

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
redis_conn = redis.Redis.from_url(REDIS_URL)
rq_queue = Queue(connection=redis_conn)

def get_user_tier(user_id=None):
    """Get user's current tier. Default to free if no user or not found."""
    if not user_id or user_id not in users_db:
        return 'free'
    return users_db[user_id].get('tier', 'free')

def get_tier_limits(tier):
    """Get limits for a specific tier."""
    return TIER_LIMITS.get(tier, TIER_LIMITS['free'])

def require_tier(min_tier):
    """Decorator to require minimum tier for endpoints."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            current_tier = get_user_tier(user_id)
            
            # Check if user meets minimum tier requirement
            tier_order = ['free', 'premium', 'pro']
            if tier_order.index(current_tier) < tier_order.index(min_tier):
                return jsonify({
                    'error': f'This feature requires {TIER_LIMITS[min_tier]["name"]} tier or higher',
                    'upgrade_required': True,
                    'current_tier': current_tier,
                    'required_tier': min_tier
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class LogHandler(logging.Handler):
    """Custom log handler to capture logs for streaming."""
    def emit(self, record):
        try:
            msg = self.format(record)
            log_queue.put({
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'level': record.levelname,
                'message': msg
            })
        except Exception:
            self.handleError(record)

# Add custom log handler
log_handler = LogHandler()
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(log_handler)

@app.route('/')
def index():
    """Main page with form."""
    user_id = session.get('user_id')
    current_tier = get_user_tier(user_id)
    tier_limits = get_tier_limits(current_tier)
    
    return render_template('index.html', 
                         current_tier=current_tier,
                         tier_limits=tier_limits,
                         tier_info=TIER_LIMITS)

@app.route('/api/tiers')
def get_tiers():
    """Get available tiers information."""
    user_id = session.get('user_id')
    current_tier = get_user_tier(user_id)
    
    return jsonify({
        'current_tier': current_tier,
        'tiers': TIER_LIMITS,
        'user_limits': get_tier_limits(current_tier)
    })

@app.route('/api/upgrade', methods=['POST'])
def upgrade_tier():
    """Handle tier upgrade payment."""
    try:
        data = request.get_json()
        tier = data.get('tier')
        payment_method = data.get('payment_method', 'stripe')
        
        if tier not in TIER_LIMITS:
            return jsonify({'error': 'Invalid tier'}), 400
        
        # Generate or get user ID
        user_id = session.get('user_id')
        if not user_id:
            user_id = str(uuid.uuid4())
            session['user_id'] = user_id
        
        # Initialize user if not exists
        if user_id not in users_db:
            users_db[user_id] = {
                'tier': 'free',
                'created_at': datetime.now().isoformat(),
                'upgrades': []
            }
        
        # Mock payment processing (in production, integrate with Stripe/PayPal)
        payment_successful = True  # Mock successful payment
        
        if payment_successful:
            # Update user tier
            users_db[user_id]['tier'] = tier
            users_db[user_id]['upgrades'].append({
                'tier': tier,
                'upgraded_at': datetime.now().isoformat(),
                'payment_method': payment_method
            })
            
            return jsonify({
                'success': True,
                'message': f'Successfully upgraded to {TIER_LIMITS[tier]["name"]} tier!',
                'new_tier': tier,
                'new_limits': get_tier_limits(tier)
            })
        else:
            return jsonify({'error': 'Payment failed'}), 400
            
    except Exception as e:
        logger.error(f"Upgrade error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs/<task_id>')
def stream_logs(task_id):
    def event_stream():
        log_key = f'logs:{task_id}'
        last_index = 0
        logger.info(f"Starting log stream for task {task_id}")
        while True:
            logs = redis_conn.lrange(log_key, last_index, -1)
            if logs:
                for log in logs:
                    try:
                        log_data = json.loads(log.decode())
                        logger.info(f"Processing log entry: {log_data}")
                        
                        # Check if it's a special message type (complete, error)
                        if log_data.get('type') in ['complete', 'error']:
                            message = json.dumps(log_data)
                            logger.info(f"Sending special message: {message}")
                            yield f'data: {message}\n\n'
                        else:
                            # Wrap regular log messages in the expected format
                            wrapped_data = {
                                'type': 'log',
                                'data': log_data
                            }
                            message = json.dumps(wrapped_data)
                            logger.info(f"Sending wrapped log message: {message}")
                            yield f'data: {message}\n\n'
                            
                    except json.JSONDecodeError:
                        # If it's not JSON, treat as a simple log message
                        wrapped_data = {
                            'type': 'log',
                            'data': {
                                'timestamp': datetime.now().strftime('%H:%M:%S'),
                                'level': 'INFO',
                                'message': log.decode()
                            }
                        }
                        message = json.dumps(wrapped_data)
                        logger.info(f"Sending fallback log message: {message}")
                        yield f'data: {message}\n\n'
                        
                last_index += len(logs)
            import time
            time.sleep(1)
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/generate', methods=['POST'])
def generate():
    """Generate llms.txt from form data (enqueue background job for all tiers)."""
    try:
        user_id = session.get('user_id')
        current_tier = get_user_tier(user_id)
        tier_limits = get_tier_limits(current_tier)
        task_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        generation_status[task_id] = {
            'status': 'running',
            'progress': 0,
            'message': 'Starting generation...'
        }
        # Parse form and build config (as before)
        max_pages = tier_limits['max_pages']
        max_blogs = tier_limits['max_blogs']
        max_products = tier_limits['max_products']
        max_content_length = tier_limits['max_content_length']
        request_delay = float(request.form.get('request_delay', 1.0))
        respect_robots = request.form.get('respect_robots', 'off') == 'on'
        max_sitemaps = int(request.form.get('max_sitemaps', 5))
        max_nested_links = int(request.form.get('max_nested_links', 3))
        max_detailed_content = int(request.form.get('max_detailed_content', 10))
        sitemap_url = request.form.get('sitemap_url', '').strip()
        site_name = request.form.get('site_name', '').strip()
        site_description = request.form.get('site_description', '').strip()
        content_selector = request.form.get('content_selector', '.content, #main, article, .post-content, .entry-content, .page-content, .post, .entry').strip()
        title_selector = request.form.get('title_selector', 'h1, .title, .post-title, .entry-title, .page-title').strip()
        config = {
            'sitemap_url': sitemap_url,
            'site_name': site_name,
            'site_description': site_description or f"Comprehensive resource for {site_name}",
            'content_selector': content_selector or '.content, #main, article, .post-content, .entry-content, .page-content, .post, .entry, .elementor, .elementor-post',
            'title_selector': title_selector or 'h1, .title, .post-title, .entry-title, .page-title',
            'max_pages_to_process': max_pages,
            'max_content_length': max_content_length,
            'min_content_length': 50,
            'max_sitemaps_to_process': max_sitemaps,
            'max_nested_links': max_nested_links,
            'max_blogs': max_blogs,
            'max_detailed_content': max_detailed_content,
            'max_products': max_products,
            'default_topics': ['Technology', 'Business', 'Web Development'],
            'respect_robots_txt': respect_robots,
            'request_delay': request_delay,
            'output_file': 'llms.txt',
            'backup_existing': True
        }
        # Enqueue background job for all tiers
        rq_queue.enqueue(generate_llms_background, config, task_id, job_id=task_id)
        return jsonify({
            'success': True,
            'message': 'Generation started in background.',
            'task_id': task_id,
            'tier_info': {
                'current_tier': current_tier,
                'limits': tier_limits,
                'upgrade_available': current_tier == 'free'
            }
        })
    except Exception as e:
        logger.exception("Error in /generate endpoint")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated file."""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload-config', methods=['POST'])
def upload_config():
    """Upload configuration file."""
    try:
        if 'config_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['config_file']
        if file.filename == '' or file.filename is None:
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Load and validate config
            with open(file_path, 'r') as f:
                config = yaml.safe_load(f)
            
            validate_config(config)
            
            return jsonify({
                'success': True,
                'message': 'Configuration uploaded successfully',
                'config': config
            })
        else:
            return jsonify({'error': 'Invalid file type. Please upload a YAML file.'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate-sitemap', methods=['POST'])
def validate_sitemap():
    """Validate sitemap URL and detect if it's a sitemap index."""
    try:
        if not request.json:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        sitemap_url = request.json.get('sitemap_url', '').strip()
        
        if not sitemap_url:
            return jsonify({'error': 'Sitemap URL is required'}), 400
        
        # Test sitemap parsing
        config = {'sitemap_url': sitemap_url, 'max_sitemaps_to_process': 5}
        parser = SitemapParser(config)
        urls_data = parser.parse_sitemap(sitemap_url)
        
        # Check if it's a sitemap index by looking at the URL
        is_sitemap_index = 'sitemap_index' in sitemap_url or 'sitemap-index' in sitemap_url
        
        return jsonify({
            'success': True,
            'message': f'Valid sitemap with {len(urls_data)} URLs found',
            'url_count': len(urls_data),
            'is_sitemap_index': is_sitemap_index,
            'sample_urls': [url['loc'] for url in urls_data[:5]]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sample-config')
def get_sample_config():
    """Get sample configuration."""
    try:
        sample_config = create_sample_config()
        return jsonify({
            'success': True,
            'config': sample_config
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-site', methods=['POST'])
def analyze_site():
    """Analyze a website to automatically detect site information and optimal selectors."""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Get user tier and limits
        user_id = session.get('user_id')
        current_tier = get_user_tier(user_id)
        tier_limits = get_tier_limits(current_tier)
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Auto-detect sitemap if needed
        original_url = url
        sitemap_url = url
        if not url.endswith(('.xml', 'sitemap')):
            try:
                from main import SitemapDetector
                detector = SitemapDetector()
                detected_sitemap = detector.detect_sitemap_url(url)
                sitemap_url = detected_sitemap
            except Exception as e:
                return jsonify({'error': f'Could not auto-detect sitemap: {str(e)}'}), 400
        
        # Parse sitemap to get URL counts
        config = {
            'sitemap_url': sitemap_url,
            'max_sitemaps_to_process': 5,
            'respect_robots_txt': False
        }
        
        sitemap_parser = SitemapParser(config)
        urls_data = sitemap_parser.parse_sitemap(sitemap_url)
        
        # Count different types of URLs
        blog_urls = len([url for url in urls_data if url.get('source_type') == 'blog'])
        page_urls = len([url for url in urls_data if url.get('source_type') == 'page'])
        product_urls = len([url for url in urls_data if url.get('source_type') == 'product'])
        uncategorized_urls = len([url for url in urls_data if url.get('source_type') not in ['blog', 'page', 'product']])
        
        # Extract site name from URL
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        site_name = parsed_url.netloc.replace('www.', '').replace('.com', '').replace('.org', '').replace('.net', '')
        site_name = site_name.replace('-', ' ').replace('_', ' ').title()
        
        # Check if website exceeds free tier limits
        upgrade_prompt = None
        if current_tier == 'free':
            total_allowed = tier_limits['max_pages'] + tier_limits['max_blogs'] + tier_limits['max_products']
            exceeds_limits = (
                page_urls > tier_limits['max_pages'] or
                blog_urls > tier_limits['max_blogs'] or
                product_urls > tier_limits['max_products'] or
                len(urls_data) > total_allowed
            )
            
            if exceeds_limits:
                upgrade_prompt = {
                    'show': True,
                    'message': f"Your website has {page_urls} pages, {blog_urls} blog posts, {product_urls} products, and {uncategorized_urls} uncategorized URLs. The free tier is limited to {tier_limits['max_pages']} pages, {tier_limits['max_blogs']} blogs, and {tier_limits['max_products']} products, or a total of {tier_limits['max_pages'] + tier_limits['max_blogs'] + tier_limits['max_products']} unique URLs. You'll receive a sample llms.txt with these limitations, or upgrade for full access.",
                    'limits_exceeded': {
                        'pages': page_urls > tier_limits['max_pages'],
                        'blogs': blog_urls > tier_limits['max_blogs'],
                        'products': product_urls > tier_limits['max_products'],
                        'total_urls': len(urls_data) > total_allowed
                    },
                    'current_counts': {
                        'pages': page_urls,
                        'blogs': blog_urls,
                        'products': product_urls,
                        'uncategorized': uncategorized_urls,
                        'total': len(urls_data)
                    },
                    'free_limits': tier_limits
                }
        
        return jsonify({
            'success': True,
            'data': {
                'sitemap_url': sitemap_url,
                'site_name': site_name,
                'site_description': f"Comprehensive resource for {site_name}",
                'total_urls': len(urls_data),
                'blog_urls': blog_urls,
                'page_urls': page_urls,
                'product_urls': product_urls,
                'uncategorized_urls': uncategorized_urls
            },
            'upgrade_prompt': upgrade_prompt,
            'tier_info': {
                'current_tier': current_tier,
                'limits': tier_limits
            }
        })
        
    except Exception as e:
        logger.error(f"Site analysis error: {e}")
        return jsonify({'error': str(e)}), 500

# @app.route('/api/create-checkout-session', methods=['POST'])
# def create_checkout_session():
#     """DISABLED FOR TESTING: Stripe Checkout session creation."""
#     pass

# @app.route('/webhook/stripe', methods=['POST'])
# def stripe_webhook():
#     """DISABLED FOR TESTING: Stripe webhook handler."""
#     pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 