#!/usr/bin/env python3
"""
Test script for products section and detailed content slider functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import main, load_config
import yaml

def test_products_and_detailed_content():
    """Test the new products section and detailed content functionality."""
    
    # Create a test config
    test_config = {
        'sitemap_url': 'https://bombasurf.com/sitemap_index.xml',  # Known to have products
        'site_name': 'Bomba Surf Test',
        'max_pages_to_process': 5,
        'max_blogs': 5,
        'max_detailed_content': 15,  # Test the new slider
        'request_delay': 0.5,
        'respect_robots_txt': False,
        'max_nested_links': 2,
        'max_sitemaps': 3,
        'output_file': 'outputs/test_products_detailed.txt'
    }
    
    # Save test config
    with open('test_products_config.yaml', 'w') as f:
        yaml.dump(test_config, f)
    
    print("🧪 Testing Products Section and Detailed Content Slider")
    print("=" * 60)
    
    try:
        # Run the main function with test config
        main(sitemap_url=test_config['sitemap_url'], site_name=test_config['site_name'])
        
        # Check the output file
        output_file = test_config['output_file']
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"✅ Generated output file: {output_file}")
            
            # Check for products section
            if '## Products' in content:
                print("✅ Products section found in output")
                
                # Count product entries
                product_lines = [line for line in content.split('\n') if line.strip().startswith('- [') and '## Products' in content[:content.find(line)]]
                print(f"📦 Found {len(product_lines)} product entries")
                
                # Show first few products
                if product_lines:
                    print("📦 Sample products:")
                    for i, line in enumerate(product_lines[:3]):
                        print(f"   {i+1}. {line}")
            else:
                print("❌ Products section not found in output")
            
            # Check for detailed content
            if '## Detailed Content' in content:
                print("✅ Detailed Content section found")
                
                # Check if we have the right number of detailed items
                detailed_sections = content.count('## Pages') + content.count('## Blogs') + content.count('## Products')
                print(f"📄 Found {detailed_sections} detailed content sections")
                
                # Check for products in detailed content
                if '## Products' in content and '## Detailed Content' in content:
                    detailed_products_start = content.find('## Products', content.find('## Detailed Content'))
                    if detailed_products_start != -1:
                        print("✅ Products found in detailed content section")
                    else:
                        print("❌ Products not found in detailed content section")
            else:
                print("❌ Detailed Content section not found")
            
            # Show summary
            print("\n📊 Output Summary:")
            print(f"   - Total content length: {len(content)} characters")
            print(f"   - Contains Products section: {'## Products' in content}")
            print(f"   - Contains Detailed Content: {'## Detailed Content' in content}")
            print(f"   - Max detailed content setting: {test_config['max_detailed_content']}")
            
        else:
            print(f"❌ Output file not found: {output_file}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_products_and_detailed_content() 