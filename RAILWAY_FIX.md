# Railway Deployment Fix Guide

## Current Issues Identified

1. **File Hosting/Directory Permissions**: The outputs directory isn't properly accessible for file downloads
2. **Content Scraping**: The scraping process might be failing silently
3. **Redis Connection**: Potential connection issues between services

## Quick Fix Steps

### 1. Fix Directory Permissions

```bash
# Run the deployment helper
python deploy_railway.py fix

# Or manually create directories with proper permissions
mkdir -p outputs uploads
chmod -R 777 outputs uploads
```

### 2. Update Railway Configuration

The `railway.json` has been updated to include:
- Proper volume mounts for both outputs and uploads directories
- Better restart policies
- Health checks

### 3. Deploy the Fixes

```bash
# Deploy to Railway
python deploy_railway.py deploy

# Or use Railway CLI directly
railway up
```

### 4. Check Deployment Status

```bash
# Check status
python deploy_railway.py status

# View logs
python deploy_railway.py logs
```

## Detailed Fixes Applied

### 1. Updated railway.json
- Added uploads volume mount
- Improved restart policies
- Better health check configuration

### 2. Enhanced startup.sh
- Better directory creation and permissions
- File creation testing
- Redis connection checking
- Improved error handling

### 3. Improved app.py
- Better error handling in download route
- Enhanced logging for debugging
- Security checks for file downloads

### 4. Created deploy_railway.py
- Automated deployment helper
- Status checking
- Log monitoring
- Fix automation

## Testing the Fix

1. **Deploy the fixes**:
   ```bash
   python deploy_railway.py deploy
   ```

2. **Check the logs**:
   ```bash
   python deploy_railway.py logs
   ```

3. **Test file generation**:
   - Go to your Railway app URL
   - Try generating an llms.txt file
   - Check if the download works

4. **Monitor the worker**:
   - Check if the worker service is processing jobs
   - Look for any scraping errors in the logs

## Common Issues and Solutions

### Issue: "File not found" when downloading
**Solution**: The outputs directory permissions have been fixed. The app now includes better error handling and logging.

### Issue: No content being scraped
**Solution**: Check the worker logs for scraping errors. The content scraper has been improved with better error handling.

### Issue: Redis connection errors
**Solution**: The startup script now checks Redis connectivity and the configuration has been improved.

### Issue: Directory not writable
**Solution**: The startup script now creates directories with proper permissions and tests file creation.

## Monitoring

After deployment, monitor these key areas:

1. **Worker logs**: Check if jobs are being processed
2. **Web service logs**: Check for download and generation errors
3. **Redis service**: Ensure it's running and accessible
4. **File permissions**: Verify outputs directory is writable

## Next Steps

1. Deploy the fixes using the helper script
2. Test a simple generation
3. Check the logs for any remaining issues
4. If issues persist, check the specific error messages in the logs

The fixes should resolve both the file hosting issues and improve the content scraping reliability. 