# Use official Python image
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p outputs uploads static/css static/js templates && \
    chmod 755 outputs uploads && \
    chmod -R 755 static templates

# Ensure outputs and uploads are writable by any user (for Railway)
RUN chmod 777 outputs uploads

# Make startup script executable
RUN chmod +x startup.sh

# Expose port for Flask
EXPOSE 5000

# Use startup script as entrypoint
ENTRYPOINT ["./startup.sh"]

# Default command (can be overridden by docker-compose)
CMD ["python", "run_web.py"] 