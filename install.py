#!/usr/bin/env python3
"""
Installation script for LLMs.txt Generator

This script helps users set up the tool with proper dependencies
and initial configuration.
"""

import subprocess
import sys
import os
import yaml
from utils import create_sample_config

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    required_modules = [
        'requests',
        'bs4',
        'lxml',
        'yaml',
        'urllib3'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"❌ Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("✅ All imports successful")
    return True

def create_initial_config():
    """Create initial configuration file."""
    print("⚙️  Creating initial configuration...")
    
    if os.path.exists("config.yaml"):
        response = input("config.yaml already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Skipping configuration creation")
            return True
    
    try:
        sample_config = create_sample_config()
        
        with open("config.yaml", 'w') as f:
            yaml.dump(sample_config, f, default_flow_style=False, indent=2)
        
        print("✅ Configuration file created: config.yaml")
        print("📝 Please edit config.yaml with your website details")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create configuration: {e}")
        return False

def show_next_steps():
    """Show next steps for the user."""
    print("\n" + "="*50)
    print("🎉 Installation completed successfully!")
    print("="*50)
    print("\nNext steps:")
    print("1. Edit config.yaml with your website details:")
    print("   - Set sitemap_url to your website's sitemap")
    print("   - Update site_name and site_description")
    print("   - Adjust content selectors if needed")
    print("\n2. Test the installation:")
    print("   python cli.py validate-config")
    print("\n3. Generate your first llms.txt:")
    print("   python cli.py generate")
    print("\n4. For help:")
    print("   python cli.py info")
    print("\n5. View the README.md for detailed documentation")
    print("\nHappy generating! 🚀")

def main():
    """Main installation function."""
    print("LLMs.txt Generator - Installation")
    print("="*40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("\nTry running: pip install -r requirements.txt manually")
        sys.exit(1)
    
    # Create initial config
    if not create_initial_config():
        sys.exit(1)
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main() 