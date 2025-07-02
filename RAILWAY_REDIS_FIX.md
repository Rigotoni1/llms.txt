# Railway Redis Connection Fix

## 🚨 Problem Identified

Your Railway deployment is failing because **Redis is not properly configured**. The diagnostic shows:

- ❌ `REDIS_URL: Not set`
- ❌ Worker endpoints returning 404
- ❌ Generation not starting

## 🔧 Root Cause

The `railway.json` file was missing the Redis service definition. Railway needs to know about Redis to:
1. Provision a Redis instance
2. Set the `REDIS_URL` environment variable automatically
3. Allow services to communicate with each other

## ✅ Solution Applied

### 1. Fixed railway.json
Added the missing Redis service:

```json
{
  "name": "redis",
  "build": {
    "builder": "IMAGE",
    "image": "redis:7-alpine"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 2. Added Health Endpoint
Added `/api/health` endpoint to monitor Redis connection status.

## 🚀 Next Steps

### 1. Redeploy to Railway
```bash
# Commit your changes
git add railway.json app.py
git commit -m "Fix Redis configuration for Railway deployment"
git push origin main
```

### 2. Verify Deployment
After redeployment, test the health endpoint:
```bash
curl https://llms-txt-production.up.railway.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "web": "healthy",
    "redis": "healthy",
    "rq_queue": "healthy"
  },
  "environment": {
    "redis_url_set": true,
    "port": "5000"
  }
}
```

### 3. Test Generation
Once Redis is working, test generation:
```bash
curl -X POST https://llms-txt-production.up.railway.app/generate \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "site_name=Test&sitemap_url=https://example.com/sitemap.xml&max_pages_to_process=1"
```

## 🔍 Monitoring

### Health Check Script
Run this to monitor your deployment:
```bash
python test_redis_connection.py
```

### Railway Dashboard
1. Go to your Railway project
2. Check that all 3 services are running:
   - `redis` (Redis database)
   - `web` (Flask application)
   - `worker` (Background job processor)
3. Verify environment variables are set automatically

## 🛠️ Troubleshooting

### If Redis Still Doesn't Work:

1. **Check Railway Logs**:
   ```bash
   railway logs --service redis
   railway logs --service web
   railway logs --service worker
   ```

2. **Manual Environment Variable**:
   If Railway doesn't set `REDIS_URL` automatically, add it manually in the Railway dashboard:
   - Go to your project → Variables
   - Add: `REDIS_URL=redis://redis:6379/0`

3. **Service Dependencies**:
   Make sure services start in the correct order:
   - Redis first
   - Web and Worker after Redis is ready

### Common Issues:

1. **Service Communication**: Services need to be in the same Railway project to communicate
2. **Port Configuration**: Redis runs on port 6379 internally
3. **Network Access**: Railway handles internal networking automatically

## 📊 Expected Behavior After Fix

✅ **Web Service**: Responds to requests  
✅ **Redis Service**: Available for job queuing  
✅ **Worker Service**: Processes background jobs  
✅ **Generation**: Starts and completes successfully  
✅ **Health Endpoint**: Shows all services healthy  

## 🔄 Verification Commands

```bash
# Test health endpoint
curl https://llms-txt-production.up.railway.app/api/health

# Test generation (small test)
curl -X POST https://llms-txt-production.up.railway.app/generate \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "site_name=Test&sitemap_url=https://example.com/sitemap.xml&max_pages_to_process=1&max_blogs=1&max_products=1"

# Monitor logs
railway logs --follow
```

## 🎯 Success Criteria

After redeployment, you should see:
- ✅ Health endpoint returns `redis: "healthy"`
- ✅ Generation requests are accepted
- ✅ Background jobs are processed
- ✅ Files are generated and downloadable

---

**The fix is ready! Just redeploy to Railway and the generation should start working.** 