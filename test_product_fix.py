#!/usr/bin/env python3
"""
Test script to verify product detection and max_products slider functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import main, load_config
import yaml

def test_product_fix():
    """Test the product detection fix and max_products slider."""
    
    # Create a test config with max_products set to 5
    test_config = {
        'sitemap_url': 'https://bombasurf.com/sitemap_index.xml',
        'site_name': 'Bomba Surf Test',
        'max_pages_to_process': 3,
        'max_blogs': 3,
        'max_products': 5,  # Test the new slider
        'max_detailed_content': 10,
        'request_delay': 0.5,
        'respect_robots_txt': False,
        'max_nested_links': 2,
        'max_sitemaps': 3,
        'output_file': 'outputs/test_product_fix.txt'
    }
    
    print("🧪 Testing Product Detection Fix and Max Products Slider")
    print("=" * 60)
    
    try:
        # Run the main function with test config
        main(sitemap_url=test_config['sitemap_url'], site_name=test_config['site_name'])
        
        # Check the output file
        output_file = 'llms.txt'  # Default output file
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"✅ Generated output file: {output_file}")
            
            # Check for products section
            if '## Products' in content:
                print("✅ Products section found in output")
                
                # Find the products section
                products_start = content.find('## Products')
                products_end = content.find('##', products_start + 1)
                if products_end == -1:
                    products_end = len(content)
                
                products_section = content[products_start:products_end]
                
                # Count product entries (lines starting with "- [")
                product_lines = [line for line in products_section.split('\n') if line.strip().startswith('- [')]
                print(f"📦 Found {len(product_lines)} product entries")
                
                # Check if we have the right number (should be <= max_products)
                if len(product_lines) <= test_config['max_products']:
                    print(f"✅ Product count ({len(product_lines)}) is within max_products limit ({test_config['max_products']})")
                else:
                    print(f"❌ Product count ({len(product_lines)}) exceeds max_products limit ({test_config['max_products']})")
                
                # Show first few products
                if product_lines:
                    print("📦 Sample products:")
                    for i, line in enumerate(product_lines[:3]):
                        print(f"   {i+1}. {line}")
                    
                    # Check if these are actually product URLs
                    product_urls = [line for line in product_lines if '/product/' in line or '/shop/' in line]
                    print(f"✅ Found {len(product_urls)} URLs with product/shop patterns")
                    
                    if product_urls:
                        print("✅ Product URLs detected correctly:")
                        for i, url in enumerate(product_urls[:3]):
                            print(f"   {i+1}. {url}")
                    else:
                        print("❌ No product URLs found in products section")
                else:
                    print("❌ No product entries found in products section")
            else:
                print("❌ Products section not found in output")
            
            # Check for detailed content products
            if '## Detailed Content' in content and '## Products' in content:
                detailed_start = content.find('## Detailed Content')
                detailed_products_start = content.find('## Products', detailed_start)
                if detailed_products_start != -1:
                    print("✅ Products found in detailed content section")
                    
                    # Count detailed product entries
                    detailed_end = content.find('##', detailed_products_start + 1)
                    if detailed_end == -1:
                        detailed_end = len(content)
                    
                    detailed_products_section = content[detailed_products_start:detailed_end]
                    detailed_product_items = detailed_products_section.count('- Published:')
                    print(f"📄 Found {detailed_product_items} detailed product items")
                else:
                    print("❌ Products not found in detailed content section")
            else:
                print("❌ Detailed content section not found")
            
            # Show summary
            print("\n📊 Output Summary:")
            print(f"   - Total content length: {len(content)} characters")
            print(f"   - Contains Products section: {'## Products' in content}")
            print(f"   - Contains Detailed Content: {'## Detailed Content' in content}")
            print(f"   - Max products setting: {test_config['max_products']}")
            
        else:
            print(f"❌ Output file not found: {output_file}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_product_fix() 