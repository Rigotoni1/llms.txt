# Deployment Guide: Publishing Your Flask App to a Domain

## Quick Start Options

### Option 1: Railway (Recommended - Easiest)

1. **Sign up for Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy your app**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   
   # Initialize and deploy
   railway init
   railway up
   ```

3. **Get your domain**
   - Railway automatically provides a `.railway.app` domain
   - You can add a custom domain in the Railway dashboard

### Option 2: Heroku (Classic Choice)

1. **Sign up for Heroku**
   - Go to [heroku.com](https://heroku.com)
   - Create an account

2. **Install Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Or download from heroku.com
   ```

3. **Deploy your app**
   ```bash
   # Login to Heroku
   heroku login
   
   # Create a new app
   heroku create your-app-name
   
   # Add Redis addon (for your background tasks)
   heroku addons:create heroku-redis:hobby-dev
   
   # Deploy
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

4. **Open your app**
   ```bash
   heroku open
   ```

### Option 3: Render (Modern Alternative)

1. **Sign up for Render**
   - Go to [render.com](https://render.com)
   - Connect your GitHub account

2. **Create a new Web Service**
   - Connect your GitHub repository
   - Choose "Docker" as the environment
   - Set build command: `docker build -t myapp .`
   - Set start command: `python run_web.py`

3. **Configure environment variables**
   - Add `REDIS_URL` if using Redis
   - Add any other environment variables

## Production Configuration

### 1. Update Environment Variables

Create a `.env` file for local development:
```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
REDIS_URL=your-redis-url
STRIPE_PUBLISHABLE_KEY=your-stripe-key
STRIPE_SECRET_KEY=your-stripe-secret
```

### 2. Update Production Settings

In your `run_web.py`, update for production:
```python
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        debug=False,  # Set to False in production
        host='0.0.0.0',
        port=port,
        threaded=True
    )
```

### 3. Configure Redis for Production

For Railway/Heroku/Render, you'll need to:
- Add Redis as a service
- Update your `REDIS_URL` environment variable
- Ensure your app connects to the production Redis instance

## Custom Domain Setup

### 1. Buy a Domain
- **Namecheap** (cheap domains)
- **Google Domains** (simple setup)
- **GoDaddy** (popular choice)

### 2. Configure DNS

#### For Railway:
1. Go to your Railway project dashboard
2. Click on your web service
3. Go to "Settings" → "Domains"
4. Add your custom domain
5. Update your domain's DNS records:
   - Add a CNAME record pointing to your Railway app URL

#### For Heroku:
```bash
# Add custom domain
heroku domains:add yourdomain.com

# Get the DNS target
heroku domains

# Add CNAME record in your domain provider pointing to the target
```

#### For Render:
1. Go to your service dashboard
2. Click "Settings" → "Custom Domains"
3. Add your domain
4. Update DNS records as instructed

### 3. SSL Certificate
- Railway, Heroku, and Render all provide automatic SSL certificates
- Your site will be available at `https://yourdomain.com`

## Advanced: VPS Deployment

If you want more control, you can deploy to a VPS:

### 1. Set up a VPS
- **DigitalOcean** ($5/month)
- **Linode** ($5/month)
- **Vultr** ($2.50/month)

### 2. Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python, Nginx, Redis
sudo apt install python3 python3-pip nginx redis-server -y

# Install Docker (optional, for containerized deployment)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 3. Deploy with Docker
```bash
# Clone your repository
git clone your-repo-url
cd your-repo

# Build and run with Docker Compose
docker-compose up -d
```

### 4. Configure Nginx
Create `/etc/nginx/sites-available/yourdomain.com`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5. Enable SSL with Let's Encrypt
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Monitoring and Maintenance

### 1. Set up Monitoring
- **UptimeRobot** (free uptime monitoring)
- **Sentry** (error tracking)
- **LogRocket** (user session replay)

### 2. Backup Strategy
- Database backups (if using external database)
- File backups (uploads, outputs)
- Code backups (Git repository)

### 3. Scaling Considerations
- Use Redis for session storage
- Implement caching
- Consider CDN for static files
- Monitor resource usage

## Troubleshooting

### Common Issues:

1. **Port conflicts**: Ensure your app uses the `PORT` environment variable
2. **Redis connection**: Verify `REDIS_URL` is set correctly
3. **Static files**: Ensure static files are served correctly
4. **Environment variables**: Double-check all required env vars are set

### Debug Commands:
```bash
# Check logs
heroku logs --tail  # Heroku
railway logs        # Railway
render logs         # Render

# Check app status
heroku ps           # Heroku
railway status      # Railway
```

## Cost Comparison

| Platform | Free Tier | Paid Plans | Best For |
|----------|-----------|------------|----------|
| Railway | $5/month | $20+/month | Small to medium apps |
| Heroku | $7/month | $25+/month | Established apps |
| Render | Free | $7+/month | Budget-friendly |
| VPS | $5/month | $5+/month | Full control |

## Next Steps

1. Choose your deployment platform
2. Set up your environment variables
3. Deploy your application
4. Configure your custom domain
5. Set up monitoring and backups
6. Test thoroughly in production

Remember to:
- Never commit sensitive information (API keys, secrets)
- Use environment variables for configuration
- Set up proper logging
- Monitor your application's performance
- Keep your dependencies updated 