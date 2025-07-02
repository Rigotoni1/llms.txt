#!/bin/bash

# Deployment Script for LLMs.txt Generator
# This script helps deploy your Flask app to various platforms

set -e  # Exit on any error

echo "🚀 LLMs.txt Generator Deployment Script"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the project root."
    exit 1
fi

# Function to deploy to Railway
deploy_railway() {
    echo "📦 Deploying to Railway..."
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        echo "📥 Installing Railway CLI..."
        npm install -g @railway/cli
    fi
    
    # Login to Railway
    echo "🔐 Logging into Railway..."
    railway login
    
    # Initialize and deploy
    echo "🚀 Deploying application..."
    railway up
    
    echo "✅ Railway deployment complete!"
    echo "🌐 Your app should be available at the URL shown above"
}

# Function to deploy to Heroku
deploy_heroku() {
    echo "📦 Deploying to Heroku..."
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI not found. Please install it first:"
        echo "   brew tap heroku/brew && brew install heroku"
        exit 1
    fi
    
    # Check if we're logged in
    if ! heroku auth:whoami &> /dev/null; then
        echo "🔐 Logging into Heroku..."
        heroku login
    fi
    
    # Get app name
    read -p "Enter your Heroku app name (or press Enter to create one): " app_name
    
    if [ -z "$app_name" ]; then
        echo "🏗️  Creating new Heroku app..."
        heroku create
    else
        echo "🔗 Connecting to existing app: $app_name"
        heroku git:remote -a $app_name
    fi
    
    # Add Redis addon
    echo "🔴 Adding Redis addon..."
    heroku addons:create heroku-redis:hobby-dev
    
    # Deploy
    echo "🚀 Deploying to Heroku..."
    git add .
    git commit -m "Deploy to Heroku"
    git push heroku main
    
    echo "✅ Heroku deployment complete!"
    heroku open
}

# Function to deploy to Render
deploy_render() {
    echo "📦 Render deployment requires manual setup:"
    echo "1. Go to https://render.com"
    echo "2. Connect your GitHub repository"
    echo "3. Create a new Web Service"
    echo "4. Choose 'Docker' as environment"
    echo "5. Set build command: docker build -t myapp ."
    echo "6. Set start command: python run_web.py"
    echo "7. Add environment variables as needed"
    echo ""
    echo "🌐 Your app will be available at a .onrender.com domain"
}

# Function to deploy to VPS
deploy_vps() {
    echo "📦 VPS deployment requires manual setup:"
    echo "1. Set up a VPS (DigitalOcean, Linode, etc.)"
    echo "2. Install Docker: curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh"
    echo "3. Clone your repository"
    echo "4. Run: docker-compose up -d"
    echo "5. Configure Nginx and SSL (see DEPLOYMENT_GUIDE.md)"
    echo ""
    echo "💡 See DEPLOYMENT_GUIDE.md for detailed VPS setup instructions"
}

# Main menu
echo ""
echo "Choose your deployment platform:"
echo "1) Railway (Recommended - Easiest)"
echo "2) Heroku (Classic choice)"
echo "3) Render (Modern alternative)"
echo "4) VPS (Full control)"
echo "5) Exit"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        deploy_railway
        ;;
    2)
        deploy_heroku
        ;;
    3)
        deploy_render
        ;;
    4)
        deploy_vps
        ;;
    5)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment process completed!"
echo "📖 For more details, see DEPLOYMENT_GUIDE.md" 