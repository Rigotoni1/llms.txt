# Railway App Testing Guide

This guide covers various ways to test your LLMs.txt Generator app deployed on Railway.

## 🚀 Quick Start

1. **Get your Railway URL**: Find your app URL in the Railway dashboard
2. **Update the scripts**: Replace `https://your-app-name.railway.app` with your actual URL
3. **Install dependencies**: `pip install requests`
4. **Run tests**: Choose from the testing options below

## 📋 Testing Options

### 1. Quick Health Check
```bash
python test_railway_quick.py
```
- Fastest test (30 seconds)
- Checks basic endpoints
- Good for daily verification

### 2. Comprehensive Testing
```bash
python test_railway_health.py
```
- Tests all major endpoints
- Validates sitemap functionality
- Tests generation flow
- Takes 2-3 minutes

### 3. Load Testing
```bash
python test_railway_load.py
```
- Tests concurrent requests
- Measures performance under load
- **Warning**: Can be resource intensive
- Takes 5-10 minutes

### 4. Real-time Monitoring
```bash
python test_railway_monitor.py [interval_seconds]
```
- Continuous monitoring
- Alerts for issues
- Performance tracking
- Runs until stopped (Ctrl+C)

## 🔧 Manual Testing

### Browser Testing
1. **Homepage**: Visit your Railway URL
2. **API Endpoints**: 
   - `https://your-app.railway.app/api/sample-config`
   - `https://your-app.railway.app/api/tiers`
3. **Web Interface**: Test the form submission

### cURL Testing
```bash
# Health check
curl https://your-app.railway.app/

# Get sample config
curl https://your-app.railway.app/api/sample-config

# Test sitemap validation
curl -X POST https://your-app.railway.app/api/validate-sitemap \
  -H "Content-Type: application/json" \
  -d '{"sitemap_url": "https://example.com/sitemap.xml"}'

# Test generation (be careful!)
curl -X POST https://your-app.railway.app/generate \
  -H "Content-Type: application/json" \
  -d '{
    "site_name": "Test Site",
    "sitemap_url": "https://example.com/sitemap.xml",
    "max_pages_to_process": 1,
    "max_blogs": 1,
    "max_products": 1
  }'
```

## 📊 What to Test

### ✅ Basic Functionality
- [ ] App responds to requests
- [ ] Homepage loads correctly
- [ ] API endpoints return valid JSON
- [ ] Error handling works

### ✅ Core Features
- [ ] Sitemap validation
- [ ] Configuration upload
- [ ] Generation process
- [ ] File download
- [ ] Progress tracking

### ✅ Performance
- [ ] Response times under 5 seconds
- [ ] Handles concurrent requests
- [ ] Memory usage is reasonable
- [ ] No memory leaks

### ✅ Reliability
- [ ] App stays up for extended periods
- [ ] Handles network errors gracefully
- [ ] Recovers from failures
- [ ] Logs are generated correctly

## 🚨 Common Issues

### App Not Responding
- Check Railway dashboard for deployment status
- Verify environment variables are set
- Check logs for startup errors

### Slow Response Times
- Monitor Railway resource usage
- Check if Redis is accessible
- Verify worker processes are running

### Generation Failures
- Check sitemap URL accessibility
- Verify content scraping limits
- Monitor worker queue status

## 📈 Monitoring Best Practices

### Daily Checks
- Run quick health check
- Verify core endpoints
- Check error logs

### Weekly Checks
- Run comprehensive tests
- Test with real sitemaps
- Monitor performance trends

### Monthly Checks
- Load testing
- Security review
- Performance optimization

## 🔍 Debugging Tips

### Check Railway Logs
```bash
# View deployment logs
railway logs

# View specific service logs
railway logs --service web
railway logs --service worker
```

### Check Environment Variables
```bash
# List environment variables
railway variables
```

### Restart Services
```bash
# Restart web service
railway service restart web

# Restart worker service
railway service restart worker
```

## 📝 Test Results Interpretation

### Success Indicators
- ✅ All endpoints return 200 status
- ✅ Response times under 5 seconds
- ✅ No error messages in logs
- ✅ Generation completes successfully

### Warning Signs
- ⚠️ Response times over 5 seconds
- ⚠️ Occasional 500 errors
- ⚠️ High memory usage
- ⚠️ Worker queue backups

### Critical Issues
- ❌ App not responding
- ❌ Consistent 500 errors
- ❌ Generation failures
- ❌ Memory exhaustion

## 🛠️ Custom Testing

### Add Custom Endpoints
If you add new endpoints, update the test scripts:

```python
# Add to test_railway_health.py
def test_custom_endpoint():
    response = requests.get(f"{RAILWAY_URL}/api/custom-endpoint")
    print(f"✅ Custom endpoint: {response.status_code}")
```

### Test Specific Features
Create targeted tests for new functionality:

```python
def test_specific_feature():
    # Test your specific feature
    pass
```

## 📞 Getting Help

If tests reveal issues:

1. **Check Railway logs** for error details
2. **Verify environment variables** are correct
3. **Test locally** to isolate issues
4. **Check dependencies** are properly installed
5. **Review recent changes** that might have caused issues

## 🔄 Continuous Testing

Consider setting up automated testing:

- **GitHub Actions**: Run tests on every deployment
- **Cron jobs**: Regular health checks
- **External monitoring**: Services like UptimeRobot
- **Railway webhooks**: Trigger tests on deployment

---

**Remember**: Always test in a safe environment first, and be careful with generation tests as they can be resource-intensive! 