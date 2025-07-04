#!/usr/bin/env python3
"""
Integration script to add Firecrawl to the existing web app
"""

import os
import sys

def show_integration_steps():
    """Show step-by-step integration instructions."""
    
    print("🔄 Integrating Firecrawl into Your Web App")
    print("=" * 60)
    
    print("\n📋 Step-by-Step Integration:")
    print("\n1️⃣ Update app.py imports:")
    print("   Add this line at the top of app.py:")
    print("   ```python")
    print("   from firecrawl_working import WorkingFirecrawlScraper")
    print("   ```")
    
    print("\n2️⃣ Replace scraper initialization in the generate() function:")
    print("   Find this line in app.py:")
    print("   ```python")
    print("   content_scraper = ContentScraper(config)")
    print("   ```")
    print("   Replace it with:")
    print("   ```python")
    print("   content_scraper = WorkingFirecrawlScraper(config)")
    print("   ```")
    
    print("\n3️⃣ Remove robots.txt setup (Firecrawl handles this automatically):")
    print("   Remove these lines:")
    print("   ```python")
    print("   base_url = urlparse(config['sitemap_url']).scheme + '://' + urlparse(config['sitemap_url']).netloc")
    print("   robots_checker = RobotsTxtChecker(base_url)")
    print("   content_scraper.set_robots_checker(robots_checker)")
    print("   ```")
    
    print("\n4️⃣ Update config.yaml:")
    print("   Add these lines to your config.yaml:")
    print("   ```yaml")
    print("   firecrawl_api_key: ${FIRECRAWL_API_KEY}")
    print("   only_main_content: true")
    print("   firecrawl_timeout: 120000")
    print("   ```")

def show_optional_enhancements():
    """Show optional enhancements for the web interface."""
    
    print("\n🎨 Optional Web Interface Enhancements:")
    print("=" * 50)
    
    print("\n1️⃣ Add Firecrawl toggle to the form:")
    print("   In templates/index.html, add:")
    print("   ```html")
    print("   <div class='form-group'>")
    print("     <label for='use_firecrawl'>Use Firecrawl (Recommended)</label>")
    print("     <input type='checkbox' id='use_firecrawl' name='use_firecrawl' checked>")
    print("     <small class='form-text text-muted'>Use Firecrawl for better content extraction</small>")
    print("   </div>")
    print("   ```")
    
    print("\n2️⃣ Update the Flask route to handle the toggle:")
    print("   In the generate() function, add:")
    print("   ```python")
    print("   use_firecrawl = request.form.get('use_firecrawl') == 'on'")
    print("   if use_firecrawl:")
    print("       config['firecrawl_api_key'] = os.environ.get('FIRECRAWL_API_KEY')")
    print("       content_scraper = WorkingFirecrawlScraper(config)")
    print("   else:")
    print("       content_scraper = ContentScraper(config)")
    print("   ```")

def show_testing_steps():
    """Show testing steps."""
    
    print("\n🧪 Testing Steps:")
    print("=" * 30)
    
    print("\n1️⃣ Test the integration:")
    print("   ```bash")
    print("   python demo_firecrawl.py")
    print("   ```")
    
    print("\n2️⃣ Test with your web app:")
    print("   ```bash")
    print("   python app.py")
    print("   # Then visit http://localhost:5000")
    print("   ```")
    
    print("\n3️⃣ Test with a real website:")
    print("   Use the web interface to generate llms.txt for a website")
    print("   Compare the results with the old method")

def show_deployment_steps():
    """Show deployment steps."""
    
    print("\n🚀 Deployment Steps:")
    print("=" * 30)
    
    print("\n1️⃣ Update requirements.txt:")
    print("   ✅ Already done - firecrawl-py is included")
    
    print("\n2️⃣ Set environment variable in production:")
    print("   ```bash")
    print("   export FIRECRAWL_API_KEY='fc-974c3dce1f064d47be7151b35c419ff0'")
    print("   ```")
    
    print("\n3️⃣ Deploy your updated app")
    print("   Your app will now use Firecrawl for better content extraction!")

def main():
    """Main function."""
    
    show_integration_steps()
    show_optional_enhancements()
    show_testing_steps()
    show_deployment_steps()
    
    print("\n" + "=" * 60)
    print("🎯 Quick Start:")
    print("1. Update app.py with the changes above")
    print("2. Test with: python demo_firecrawl.py")
    print("3. Deploy and enjoy better content extraction!")
    print("=" * 60)

if __name__ == "__main__":
    main() 