#!/usr/bin/env python3
"""
Web Application Runner for LLMs.txt Generator
"""

import os
import sys
from app import app

def main():
    """Run the web application."""
    print("🚀 Starting LLMs.txt Generator Web App...")
    print("=" * 50)
    print("📱 Web Interface: http://localhost:5000")
    print("🔧 API Endpoints:")
    print("   - POST /generate - Generate llms.txt")
    print("   - POST /api/validate-sitemap - Validate sitemap")
    print("   - GET /api/sample-config - Get sample config")
    print("   - POST /upload-config - Upload config file")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        # Get port from environment variable (for cloud platforms)
        port = int(os.environ.get("PORT", 5000))
        
        # Run the Flask app
        app.run(
            debug=os.environ.get("FLASK_ENV") == "development",
            host='0.0.0.0',
            port=port,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 