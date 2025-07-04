# Firecrawl Integration for LLMs.txt Generator

This integration replaces the complex BeautifulSoup-based web scraping with [Firecrawl's](https://docs.firecrawl.dev/introduction) powerful API, significantly simplifying the codebase while providing better reliability and features.

## 🚀 Benefits of Firecrawl Integration

### Before (Complex BeautifulSoup Scraping)
- **500+ lines** of complex scraping logic
- Manual HTML parsing and content extraction
- Custom pagination handling
- Robots.txt checking
- Anti-bot detection workarounds
- Complex nested link following
- Manual error handling for different site structures

### After (Firecrawl API)
- **~200 lines** of clean, simple code
- Automatic content extraction in markdown format
- Built-in crawling with intelligent page discovery
- Automatic handling of dynamic content (JavaScript)
- Built-in anti-bot protection
- Structured data extraction capabilities
- Reliable and maintained by Firecrawl team

## 📦 Installation

1. **Install Firecrawl**:
   ```bash
   pip install firecrawl-py
   ```

2. **Get a Firecrawl API Key**:
   - Sign up at [firecrawl.dev](https://firecrawl.dev)
   - Get your API key from the dashboard

3. **Set Environment Variable**:
   ```bash
   export FIRECRAWL_API_KEY="fc-your-api-key-here"
   ```

## 🔧 Configuration

Create a `config_firecrawl.yaml` file:

```yaml
# Firecrawl API Configuration
firecrawl_api_key: ${FIRECRAWL_API_KEY}

# Site Information
site_name: "My Website"
site_description: "A comprehensive resource"

# Content Processing Limits
max_pages_to_process: 10
max_content_length: 500

# Firecrawl Specific Settings
only_main_content: true
firecrawl_timeout: 120000  # 2 minutes
firecrawl_wait_for: 2000   # 2 seconds

# Output Configuration
output_file: "llms.txt"
backup_existing: true
```

## 🎯 Usage

### Command Line Usage

**Using a sitemap**:
```bash
python main_firecrawl.py --sitemap "https://example.com/sitemap.xml" --site-name "Example Site"
```

**Using just a base URL** (no sitemap needed):
```bash
python main_firecrawl.py --url "https://example.com" --site-name "Example Site"
```

### Programmatic Usage

```python
from main_firecrawl import FirecrawlLLMsGenerator, get_default_config

# Load configuration
config = get_default_config()
config['firecrawl_api_key'] = 'your-api-key-here'

# Initialize generator
generator = FirecrawlLLMsGenerator(config)

# Generate llms.txt
output_path = generator.generate_llms_txt_simple("https://example.com", "Example Site")
print(f"Generated: {output_path}")
```

### Web Interface Integration

The Firecrawl integration can be easily integrated into your existing web interface by replacing the `ContentScraper` with `FirecrawlScraper` in your Flask app.

## 🧪 Testing

Run the test suite to verify everything works:

```bash
python test_firecrawl.py
```

This will test:
- ✅ Single URL scraping
- ✅ Website crawling
- ✅ Full llms.txt generation
- ✅ Error handling

## 🔄 Migration from Existing System

### Step 1: Install Dependencies
```bash
pip install firecrawl-py
```

### Step 2: Update Configuration
Add Firecrawl settings to your existing `config.yaml`:

```yaml
# Add these to your existing config
firecrawl_api_key: ${FIRECRAWL_API_KEY}
only_main_content: true
firecrawl_timeout: 120000
firecrawl_wait_for: 2000
```

### Step 3: Replace Scraper in Code

**Before**:
```python
from main import ContentScraper
scraper = ContentScraper(config)
content = scraper.scrape_content(url, config)
```

**After**:
```python
from firecrawl_scraper import FirecrawlScraper
scraper = FirecrawlScraper(config)
content = scraper.scrape_content(url, config)
```

### Step 4: Update Web Interface

In your `app.py`, replace the scraper initialization:

```python
# Replace this:
# content_scraper = ContentScraper(config)

# With this:
from firecrawl_scraper import FirecrawlScraper
content_scraper = FirecrawlScraper(config)
```

## 🎨 Advanced Features

### Structured Data Extraction

Extract structured data from pages:

```python
from pydantic import BaseModel

class ProductInfo(BaseModel):
    name: str
    price: str
    description: str

# Extract structured data
data = scraper.extract_structured_data(url, schema=ProductInfo)
```

### Custom Actions

Handle interactive pages:

```python
config['actions'] = [
    {"type": "wait", "milliseconds": 2000},
    {"type": "click", "selector": "button.load-more"},
    {"type": "wait", "milliseconds": 3000},
    {"type": "scrape"}
]
```

### Site Mapping

Get all URLs from a website:

```python
urls = scraper.get_site_map("https://example.com")
print(f"Found {len(urls)} URLs")
```

## 📊 Performance Comparison

| Feature | BeautifulSoup | Firecrawl |
|---------|---------------|-----------|
| Code Complexity | High (500+ lines) | Low (200 lines) |
| Content Quality | Manual extraction | Automatic markdown |
| JavaScript Support | Limited | Full support |
| Anti-bot Protection | Manual | Built-in |
| Structured Data | Manual | AI-powered |
| Maintenance | High | Low |
| Reliability | Variable | High |

## 🛠️ Troubleshooting

### Common Issues

1. **API Key Not Set**:
   ```
   Error: Firecrawl API key required
   ```
   Solution: Set `FIRECRAWL_API_KEY` environment variable

2. **Import Error**:
   ```
   ImportError: Firecrawl not installed
   ```
   Solution: Run `pip install firecrawl-py`

3. **Timeout Issues**:
   ```
   Error: Firecrawl timeout
   ```
   Solution: Increase `firecrawl_timeout` in config

### Rate Limits

Firecrawl has rate limits based on your plan:
- Free: 100 requests/month
- Paid: Higher limits

Monitor your usage in the Firecrawl dashboard.

## 🔗 Resources

- [Firecrawl Documentation](https://docs.firecrawl.dev/introduction)
- [Firecrawl API Reference](https://docs.firecrawl.dev/api-reference)
- [Firecrawl Pricing](https://firecrawl.dev/pricing)

## 🤝 Contributing

The Firecrawl integration is designed to be a drop-in replacement for the existing scraping system. If you find issues or want to add features:

1. Test with `python test_firecrawl.py`
2. Check Firecrawl documentation for new features
3. Update the integration accordingly

## 📝 License

This integration uses Firecrawl's API. Please review their [terms of service](https://firecrawl.dev/terms) and [privacy policy](https://firecrawl.dev/privacy). 