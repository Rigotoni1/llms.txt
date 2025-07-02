#!/bin/bash
# Startup script for Railway deployment

echo "🚀 Starting LLMs.txt Generator..."

# Ensure directories exist with proper permissions
echo "📁 Creating directories..."
mkdir -p /app/outputs /app/uploads
chmod 777 /app/outputs /app/uploads

# Check if directories are writable
echo "🔍 Checking directory permissions..."
if [ -w /app/outputs ]; then
    echo "✅ outputs directory is writable"
else
    echo "❌ outputs directory is not writable"
    exit 1
fi

if [ -w /app/uploads ]; then
    echo "✅ uploads directory is writable"
else
    echo "❌ uploads directory is not writable"
    exit 1
fi

# Start the application
echo "🌐 Starting web application..."
exec "$@" 