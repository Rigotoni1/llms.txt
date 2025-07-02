# LLMs.txt Generator

A Python tool that dynamically generates an `llms.txt` file for a website using its `sitemap.xml` to guide content scraping. This tool helps create structured documentation for websites that can be used by Large Language Models (LLMs) to understand site content and structure.

## Features

- **Sitemap Parsing**: Parse `sitemap.xml` files to extract URLs and their `<lastmod>` dates
- **Content Scraping**: Scrape content from web pages (title, meta description, and main content)
- **Smart Content Processing**: Create summaries and identify key topics from scraped content
- **Structured Output**: Generate well-formatted `llms.txt` files in Markdown format
- **Incremental Updates**: Check `<lastmod>` dates and only process new or updated URLs
- **Configuration Driven**: YAML configuration file for easy customization
- **Robots.txt Compliance**: Respect `robots.txt` files and implement request delays
- **FTP Upload**: Optional FTP upload capability for generated files
- **Error Handling**: Comprehensive error handling and logging

## Installation

1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

1. **Create a configuration file**:
   ```bash
   python cli.py create-config
   ```

2. **Edit the configuration** (`config.yaml`):
   ```yaml
   sitemap_url: "https://your-website.com/sitemap.xml"
   site_name: "Your Website Name"
   site_description: "Description of your website"
   ```

3. **Generate your llms.txt file**:
   ```bash
   python cli.py generate
   ```

## Configuration

The tool uses a YAML configuration file (`config.yaml`) with the following options:

### Basic Settings
- `sitemap_url`: URL of your website's sitemap.xml
- `site_name`: Name of your website
- `site_description`: Description of your website

### Content Scraping
- `content_selector`: CSS selector for main content (default: `.content, #main, article, .post-content`)
- `title_selector`: CSS selector for page titles (default: `h1, .title, .post-title`)
- `max_content_length`: Maximum length of scraped content (default: 500 characters)
- `max_pages_to_process`: Maximum number of pages to process (default: 10)

### Behavior
- `respect_robots_txt`: Whether to respect robots.txt (default: true)
- `request_delay`: Delay between requests in seconds (default: 1.0)
- `backup_existing`: Backup existing llms.txt before overwriting (default: true)

### FTP Upload (Optional)
```yaml
ftp:
  enabled: false
  host: "ftp.your-server.com"
  username: "your-username"
  password: "your-password"
  remote_path: "/public_html/"
```

## Usage

### Command Line Interface

The tool provides a command-line interface with several commands:

```bash
# Create a sample configuration file
python cli.py create-config

# Validate your configuration
python cli.py validate-config

# Generate llms.txt file
python cli.py generate

# Show project information
python cli.py info
```

### Programmatic Usage

You can also use the tool programmatically:

```python
from main import main as run_generator

# Run the generator with default config.yaml
run_generator()
```

## Output Format

The generated `llms.txt` file follows this structure:

```markdown
# Your Website Name

Your website description

## Key Topics
- Topic 1
- Topic 2
- Topic 3

## Important Pages
- [Page Title 1](https://example.com/page1): Page description
- [Page Title 2](https://example.com/page2): Page description

## Site Overview
- **Total Pages**: 25
- **Last Updated**: 2024-01-15
- **Sitemap**: https://example.com/sitemap.xml

---
*Generated on 2024-01-15 14:30:00*
```

## Advanced Features

### Incremental Updates

The tool supports incremental updates by caching processed URLs and their metadata. This means subsequent runs will only process new or updated pages, making the tool much faster for regular updates.

### Custom Templates

You can customize the output format by modifying the `template` field in your configuration:

```yaml
template: |
  # {site_name}
  
  {site_description}
  
  ## Key Topics
  {topics}
  
  ## Important Pages
  {pages}
  
  ## Site Overview
  - **Total Pages**: {total_pages}
  - **Last Updated**: {last_updated}
  - **Sitemap**: {sitemap_url}
  
  ---
  *Generated on {generation_date}*
```

### Content Selectors

The tool uses CSS selectors to extract content from web pages. You can customize these selectors based on your website's structure:

```yaml
content_selector: ".content, #main, article, .post-content"
title_selector: "h1, .title, .post-title"
```

## Error Handling

The tool includes comprehensive error handling:

- **Invalid sitemap**: Graceful handling of malformed sitemap.xml files
- **Failed requests**: Retry logic and timeout handling
- **Missing content**: Fallback strategies for missing page elements
- **Network issues**: Proper exception handling for network problems

## Logging

The tool provides detailed logging to help you understand what's happening:

```
2024-01-15 14:30:00 - INFO - Loaded configuration from: config.yaml
2024-01-15 14:30:01 - INFO - Parsing sitemap: https://example.com/sitemap.xml
2024-01-15 14:30:02 - INFO - Found 25 URLs in sitemap
2024-01-15 14:30:03 - INFO - Scraping content from: https://example.com/page1
2024-01-15 14:30:05 - INFO - Generated llms.txt: llms.txt
2024-01-15 14:30:05 - INFO - Successfully generated llms.txt with 10 pages
```

## Best Practices

1. **Respect robots.txt**: Always enable `respect_robots_txt` to be a good web citizen
2. **Use appropriate delays**: Set `request_delay` to avoid overwhelming servers
3. **Test with small sites first**: Start with a few pages to test your configuration
4. **Monitor logs**: Check the logs to ensure everything is working correctly
5. **Backup existing files**: Enable `backup_existing` to preserve previous versions

## Troubleshooting

### Common Issues

1. **"Configuration file not found"**
   - Run `python cli.py create-config` to create a sample configuration

2. **"Invalid sitemap URL"**
   - Ensure the sitemap URL is accessible and returns valid XML

3. **"No content found"**
   - Check your `content_selector` configuration
   - Verify the CSS selectors match your website's structure

4. **"FTP upload failed"**
   - Verify FTP credentials and server settings
   - Check if the remote directory exists and is writable

### Getting Help

If you encounter issues:

1. Check the logs for detailed error messages
2. Validate your configuration with `python cli.py validate-config`
3. Test with a simple website first
4. Ensure all dependencies are installed correctly

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is open source and available under the MIT License.

## Changelog

### Version 1.0.0
- Initial release
- Basic sitemap parsing and content scraping
- Configuration-driven approach
- Command-line interface
- Incremental updates support
- FTP upload capability 