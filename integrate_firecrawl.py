#!/usr/bin/env python3
"""
Integration script to add Firecrawl to existing LLMs.txt Generator
This script shows how to modify your existing app.py to use Firecrawl
"""

import os
import sys
from typing import Dict, Any

def show_integration_steps():
    """Show step-by-step integration instructions."""
    
    print("🔄 Firecrawl Integration Steps")
    print("=" * 50)
    
    print("\n1. 📦 Install Firecrawl:")
    print("   pip install firecrawl-py")
    
    print("\n2. 🔑 Get Firecrawl API Key:")
    print("   - Sign up at https://firecrawl.dev")
    print("   - Get your API key from dashboard")
    print("   - Set environment variable:")
    print("     export FIRECRAWL_API_KEY='fc-your-key-here'")
    
    print("\n3. ⚙️ Update Configuration:")
    print("   Add to your config.yaml:")
    print("   ```yaml")
    print("   # Firecrawl settings")
    print("   firecrawl_api_key: ${FIRECRAWL_API_KEY}")
    print("   only_main_content: true")
    print("   firecrawl_timeout: 120000")
    print("   firecrawl_wait_for: 2000")
    print("   ```")
    
    print("\n4. 🔧 Modify app.py:")
    print("   Replace ContentScraper with FirecrawlScraper")

def generate_app_modifications():
    """Generate the modifications needed for app.py."""
    
    modifications = """
# In app.py, make these changes:

# 1. Add import at the top:
from firecrawl_scraper import FirecrawlScraper

# 2. Replace the scraper initialization in the generate() function:
# OLD:
# content_scraper = ContentScraper(config)

# NEW:
content_scraper = FirecrawlScraper(config)

# 3. Remove robots.txt checker setup (Firecrawl handles this):
# OLD:
# base_url = urlparse(config['sitemap_url']).scheme + '://' + urlparse(config['sitemap_url']).netloc
# robots_checker = RobotsTxtChecker(base_url)
# content_scraper.set_robots_checker(robots_checker)

# NEW:
# (No robots.txt setup needed - Firecrawl handles this automatically)

# 4. Update the scraping loop to use Firecrawl's simpler API:
# OLD:
# content = content_scraper.scrape_content(url_data['loc'], config)

# NEW:
# (Same API - no changes needed!)

# 5. Optional: Add Firecrawl-specific error handling:
try:
    content = content_scraper.scrape_content(url_data['loc'], config)
except Exception as e:
    logger.error(f"Firecrawl error for {url_data['loc']}: {e}")
    content = None
"""
    
    return modifications

def show_web_interface_updates():
    """Show updates needed for the web interface."""
    
    updates = """
# Web Interface Updates (app.py)

# 1. Add Firecrawl configuration to the form:
# In the HTML template (templates/index.html), add:
"""
    
    html_updates = """
<!-- Add these fields to your form -->
<div class="form-group">
    <label for="use_firecrawl">Use Firecrawl (Recommended)</label>
    <input type="checkbox" id="use_firecrawl" name="use_firecrawl" checked>
    <small class="form-text text-muted">Use Firecrawl for better content extraction</small>
</div>

<div class="form-group">
    <label for="firecrawl_timeout">Firecrawl Timeout (ms)</label>
    <input type="number" id="firecrawl_timeout" name="firecrawl_timeout" value="120000">
    <small class="form-text text-muted">Timeout for each page (default: 120000ms = 2 minutes)</small>
</div>
"""
    
    updates += html_updates
    
    updates += """
# 2. Update the Flask route to handle Firecrawl settings:
# In the generate() function, add:

use_firecrawl = request.form.get('use_firecrawl') == 'on'
if use_firecrawl:
    config['firecrawl_api_key'] = os.environ.get('FIRECRAWL_API_KEY')
    config['only_main_content'] = True
    config['firecrawl_timeout'] = int(request.form.get('firecrawl_timeout', 120000))
    
    # Use Firecrawl scraper
    content_scraper = FirecrawlScraper(config)
else:
    # Fallback to original scraper
    content_scraper = ContentScraper(config)
"""
    
    return updates

def show_benefits_comparison():
    """Show the benefits of using Firecrawl."""
    
    print("\n🎯 Benefits of Firecrawl Integration:")
    print("=" * 50)
    
    benefits = [
        ("Code Complexity", "500+ lines → 200 lines", "60% reduction"),
        ("Content Quality", "Manual extraction → Automatic markdown", "Better formatting"),
        ("JavaScript Support", "Limited → Full support", "Dynamic content handled"),
        ("Anti-bot Protection", "Manual workarounds → Built-in", "More reliable"),
        ("Maintenance", "High → Low", "Firecrawl team maintains"),
        ("Error Handling", "Complex → Simple", "Fewer edge cases"),
        ("Performance", "Variable → Consistent", "Optimized API"),
        ("Features", "Basic → Advanced", "Structured data, actions")
    ]
    
    for benefit, change, impact in benefits:
        print(f"✅ {benefit}: {change} ({impact})")

def show_migration_checklist():
    """Show a migration checklist."""
    
    print("\n📋 Migration Checklist:")
    print("=" * 30)
    
    checklist = [
        "Install firecrawl-py",
        "Get Firecrawl API key",
        "Set FIRECRAWL_API_KEY environment variable",
        "Update config.yaml with Firecrawl settings",
        "Replace ContentScraper with FirecrawlScraper in app.py",
        "Remove robots.txt checker setup",
        "Test with python test_firecrawl.py",
        "Update web interface form (optional)",
        "Deploy and test in production"
    ]
    
    for i, item in enumerate(checklist, 1):
        print(f"{i}. ☐ {item}")

def main():
    """Main function to show integration information."""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        # Check if Firecrawl is available
        try:
            import firecrawl
            print("✅ Firecrawl is installed")
        except ImportError:
            print("❌ Firecrawl is not installed. Run: pip install firecrawl-py")
        
        api_key = os.environ.get('FIRECRAWL_API_KEY')
        if api_key:
            print("✅ FIRECRAWL_API_KEY is set")
        else:
            print("❌ FIRECRAWL_API_KEY is not set")
        
        return
    
    show_integration_steps()
    show_benefits_comparison()
    
    print("\n" + "=" * 50)
    print("🔧 CODE MODIFICATIONS NEEDED:")
    print("=" * 50)
    print(generate_app_modifications())
    
    print("\n" + "=" * 50)
    print("🌐 WEB INTERFACE UPDATES:")
    print("=" * 50)
    print(show_web_interface_updates())
    
    show_migration_checklist()
    
    print("\n" + "=" * 50)
    print("🚀 NEXT STEPS:")
    print("=" * 50)
    print("1. Run: python integrate_firecrawl.py --check")
    print("2. Follow the migration checklist above")
    print("3. Test with: python test_firecrawl.py")
    print("4. Deploy your updated application")

if __name__ == "__main__":
    main() 