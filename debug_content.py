#!/usr/bin/env python3
"""
Debug script to test content extraction from AI Model Agency
"""

import requests
from bs4 import BeautifulSoup

def debug_content_extraction():
    """Debug content extraction from AI Model Agency."""
    url = 'https://aimodelagency.com/daydream-unveils-ai-chatbot-to-revolutionize-fashion-shopping/'
    
    print(f"Testing content extraction from: {url}")
    
    # Get the page
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Test different selectors
    selectors = [
        '.elementor',
        '.elementor-post', 
        '.elementor-widget-container',
        '.entry-content',
        '.post-content',
        'article',
        '.content',
        '#main',
        'main'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        print(f"\nSelector '{selector}': {len(elements)} elements found")
        
        for i, elem in enumerate(elements[:2]):
            text = elem.get_text(strip=True)
            print(f"  Element {i+1}: {len(text)} characters")
            print(f"  Preview: {text[:100]}...")
    
    # Test the actual content extraction logic
    print("\n" + "="*50)
    print("Testing actual content extraction logic:")
    
    # Try multiple selectors for better compatibility
    selectors_to_try = [
        '.elementor, .elementor-post, .elementor-widget-container',
        '.entry-content, .post-content, .page-content',
        'article, .post, .entry',
        '.content, #main, #content',
        'main, .main-content'
    ]
    
    content_elem = None
    for selector in selectors_to_try:
        content_elem = soup.select_one(selector)
        if content_elem:
            print(f"Found content with selector: {selector}")
            break
    
    if content_elem:
        # Remove script and style elements
        for script in content_elem(["script", "style", "nav", "header", "footer", ".menu", ".navigation"]):
            script.decompose()
        
        # Get text content
        content = content_elem.get_text(separator=' ', strip=True)
        content = ' '.join(content.split())
        
        print(f"Extracted content length: {len(content)}")
        print(f"Content preview: {content[:200]}...")
    else:
        print("No content found with any selector")

if __name__ == "__main__":
    debug_content_extraction() 