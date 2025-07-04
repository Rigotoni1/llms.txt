#!/bin/bash
# Startup script for Railway deployment

echo "🚀 Starting LLMs.txt Generator..."

# Ensure directories exist with proper permissions
echo "📁 Creating directories..."
mkdir -p /app/outputs /app/uploads /app/static/css /app/static/js /app/templates
chmod -R 777 /app/outputs /app/uploads
chmod -R 755 /app/static /app/templates

# Check if directories are writable
echo "🔍 Checking directory permissions..."
if [ -w /app/outputs ]; then
    echo "✅ outputs directory is writable"
else
    echo "❌ outputs directory is not writable"
    ls -la /app/
    exit 1
fi

if [ -w /app/uploads ]; then
    echo "✅ uploads directory is writable"
else
    echo "❌ uploads directory is not writable"
    ls -la /app/
    exit 1
fi

# Test file creation
echo "🧪 Testing file creation..."
echo "test" > /app/outputs/.test_write
if [ $? -eq 0 ]; then
    echo "✅ File creation test passed"
    rm /app/outputs/.test_write
else
    echo "❌ File creation test failed"
    exit 1
fi

# Check Redis connection
echo "🔗 Checking Redis connection..."
if [ -n "$REDIS_URL" ]; then
    echo "✅ Redis URL is set: $REDIS_URL"
else
    echo "⚠️  Redis URL not set, using default"
fi

# Start the application
echo "🌐 Starting web application..."
exec "$@" 