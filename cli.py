#!/usr/bin/env python3
"""
Command-line interface for the LLMs.txt Generator
"""

import argparse
import sys
import os
import yaml
from datetime import datetime
import logging

from main import main as run_generator
from utils import validate_config, create_sample_config, format_file_size

# Configure logging for CLI
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_config_command(args):
    """Create a sample configuration file."""
    config_path = args.output or "config.yaml"
    
    if os.path.exists(config_path) and not args.force:
        logger.error(f"Configuration file {config_path} already exists. Use --force to overwrite.")
        return 1
    
    sample_config = create_sample_config()
    
    with open(config_path, 'w') as f:
        yaml.dump(sample_config, f, default_flow_style=False, indent=2)
    
    logger.info(f"Created sample configuration file: {config_path}")
    logger.info("Please edit the configuration file with your website details before running the generator.")
    return 0


def validate_config_command(args):
    """Validate configuration file."""
    config_path = args.config or "config.yaml"
    
    if not os.path.exists(config_path):
        logger.error(f"Configuration file {config_path} not found.")
        return 1
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        validate_config(config)
        logger.info("Configuration is valid!")
        return 0
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return 1


def generate_command(args):
    """Generate llms.txt file."""
    config_path = args.config or "config.yaml"
    
    if not os.path.exists(config_path):
        logger.error(f"Configuration file {config_path} not found.")
        logger.info("Run 'python cli.py create-config' to create a sample configuration.")
        return 1
    
    try:
        # Validate config first
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        validate_config(config)
        
        # Check if we should auto-detect sitemap
        auto_detect = args.auto_detect
        sitemap_url = args.sitemap_url
        site_name = args.site_name
        
        # Run the generator with auto-detection if requested
        if auto_detect or sitemap_url:
            run_generator(sitemap_url=sitemap_url, site_name=site_name, auto_detect=auto_detect)
        else:
            run_generator()
        
        # Show results
        output_file = config.get('output_file', 'llms.txt')
        if os.path.exists(output_file):
            file_size = format_file_size(output_file)
            logger.info(f"Successfully generated {output_file} ({file_size})")
        else:
            logger.error("Generation completed but output file not found.")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return 1


def info_command(args):
    """Show information about the project."""
    print("""
LLMs.txt Generator
==================

A Python tool that dynamically generates an llms.txt file for a website
using its sitemap.xml to guide content scraping.

Features:
- Parse sitemap.xml to extract URLs and metadata
- Scrape content from web pages (title, description, main content)
- Generate structured llms.txt files in Markdown format
- Support incremental updates based on lastmod dates
- Respect robots.txt and implement request delays
- Optional FTP upload capability
- Configurable content selectors and templates

Usage:
  python cli.py create-config          # Create sample configuration
  python cli.py validate-config        # Validate configuration
  python cli.py generate               # Generate llms.txt
  python cli.py info                   # Show this information

For more information, see the README.md file.
""")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="LLMs.txt Generator - Create llms.txt files from website sitemaps",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py create-config
  python cli.py validate-config
  python cli.py generate
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create config command
    create_parser = subparsers.add_parser('create-config', help='Create a sample configuration file')
    create_parser.add_argument('-o', '--output', help='Output file path (default: config.yaml)')
    create_parser.add_argument('-f', '--force', action='store_true', help='Overwrite existing file')
    create_parser.set_defaults(func=create_config_command)
    
    # Validate config command
    validate_parser = subparsers.add_parser('validate-config', help='Validate configuration file')
    validate_parser.add_argument('-c', '--config', help='Configuration file path (default: config.yaml)')
    validate_parser.set_defaults(func=validate_config_command)
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate llms.txt file')
    generate_parser.add_argument('-c', '--config', help='Configuration file path (default: config.yaml)')
    generate_parser.add_argument('-a', '--auto-detect', action='store_true', help='Auto-detect sitemap')
    generate_parser.add_argument('-s', '--sitemap-url', help='Main URL of the website')
    generate_parser.add_argument('-n', '--site-name', help='Site name')
    generate_parser.set_defaults(func=generate_command)
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show project information')
    info_parser.set_defaults(func=info_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main()) 