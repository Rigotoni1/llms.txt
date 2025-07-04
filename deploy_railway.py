#!/usr/bin/env python3
"""
Railway Deployment Helper Script
"""

import os
import sys
import subprocess
import time

def run_command(command, description):
    """Run a command and return the result."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return result.stdout
        else:
            print(f"❌ {description} failed:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return None

def check_railway_status():
    """Check Railway deployment status."""
    print("=" * 50)
    print("🚂 RAILWAY DEPLOYMENT DIAGNOSTICS")
    print("=" * 50)
    
    # Check Railway CLI
    result = run_command("railway --version", "Checking Railway CLI")
    if not result:
        print("❌ Railway CLI not found. Please install it first.")
        return False
    
    # Check project status
    result = run_command("railway status", "Checking Railway project status")
    if not result:
        print("❌ Railway project not connected. Please run 'railway login' and 'railway link'")
        return False
    
    # Check services
    result = run_command("railway service list", "Checking Railway services")
    if not result:
        print("❌ Could not list services")
        return False
    
    return True

def check_logs():
    """Check Railway logs for errors."""
    print("\n📋 Checking Railway logs...")
    print("Press Ctrl+C to stop log streaming")
    
    try:
        subprocess.run("railway logs --follow", shell=True)
    except KeyboardInterrupt:
        print("\n⏹️  Log streaming stopped")

def deploy_to_railway():
    """Deploy the application to Railway."""
    print("\n🚀 Deploying to Railway...")
    
    # Build and deploy
    result = run_command("railway up", "Deploying to Railway")
    if result:
        print("✅ Deployment completed!")
        print("\n🔗 Your app should be available at:")
        run_command("railway domain", "Getting Railway domain")
    else:
        print("❌ Deployment failed!")

def main():
    """Main deployment function."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            check_railway_status()
        elif command == "logs":
            check_logs()
        elif command == "deploy":
            if check_railway_status():
                deploy_to_railway()
        elif command == "fix":
            print("🔧 Running Railway fixes...")
            
            # Create necessary directories
            os.makedirs("outputs", exist_ok=True)
            os.makedirs("uploads", exist_ok=True)
            
            # Set permissions
            run_command("chmod -R 777 outputs uploads", "Setting directory permissions")
            
            # Check if files exist
            required_files = ["railway.json", "Dockerfile", "requirements.txt", "app.py"]
            for file in required_files:
                if os.path.exists(file):
                    print(f"✅ {file} exists")
                else:
                    print(f"❌ {file} missing")
            
            print("\n🔧 Railway fixes completed!")
        else:
            print("Usage: python deploy_railway.py [status|logs|deploy|fix]")
    else:
        print("Railway Deployment Helper")
        print("Usage: python deploy_railway.py [status|logs|deploy|fix]")
        print("\nCommands:")
        print("  status  - Check Railway deployment status")
        print("  logs    - View Railway logs")
        print("  deploy  - Deploy to Railway")
        print("  fix     - Run fixes for common issues")

if __name__ == "__main__":
    main() 