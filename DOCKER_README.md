# Docker Setup for LLMs.txt Generator

This document explains how to run the LLMs.txt Generator using Docker.

## 🐳 Quick Start

### Prerequisites
- Docker
- Docker Compose

### 1. Build and Start Services
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 2. Access the Application
- **Web Interface**: http://localhost:5000
- **Redis**: localhost:6380

### 3. Stop Services
```bash
docker-compose down
```

## 🏗️ Architecture

The Docker setup includes three services:

### Redis Service
- **Image**: `redis:7-alpine`
- **Port**: 6380 (external) → 6379 (internal)
- **Purpose**: Message queue for background jobs

### Web Service
- **Image**: Built from local Dockerfile
- **Port**: 5000
- **Purpose**: Flask web application
- **Dependencies**: Redis (waits for health check)

### Worker Service
- **Image**: Built from local Dockerfile
- **Purpose**: Background job processing (RQ worker)
- **Dependencies**: Redis (waits for health check)

## 🔧 Configuration

### Environment Variables
- `REDIS_URL`: Redis connection string (default: `redis://redis:6379/0`)
- `FLASK_ENV`: Flask environment (set to `production` in Docker)

### Volumes
- `./outputs` → `/app/outputs`: Generated files
- `./uploads` → `/app/uploads`: Uploaded configuration files

## 🚀 Development vs Production

### Development
```bash
# Run with live code reloading
docker-compose up --build

# View logs
docker-compose logs -f web
docker-compose logs -f worker
docker-compose logs -f redis
```

### Production
```bash
# Run in detached mode
docker-compose up -d --build

# Scale worker if needed
docker-compose up -d --scale worker=3
```

## 🔍 Troubleshooting

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web
docker-compose logs worker
docker-compose logs redis

# Follow logs
docker-compose logs -f web
```

### Health Checks
```bash
# Check Redis health
docker-compose exec redis redis-cli ping

# Check web service health
curl http://localhost:5000/
```

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find process using port 5000
   lsof -ti:5000
   
   # Kill process
   lsof -ti:5000 | xargs kill -9
   ```

2. **Permission Issues**
   ```bash
   # Fix volume permissions
   sudo chown -R $USER:$USER outputs uploads
   ```

3. **Build Issues**
   ```bash
   # Clean build
   docker-compose down
   docker system prune -f
   docker-compose up --build
   ```

## 🧹 Maintenance

### Clean Up
```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Full cleanup
docker system prune -a
```

### Update Dependencies
```bash
# Rebuild with latest dependencies
docker-compose build --no-cache
docker-compose up -d
```

## 📊 Monitoring

### Resource Usage
```bash
# View resource usage
docker stats

# View container details
docker-compose ps
```

### Log Analysis
```bash
# Search logs for errors
docker-compose logs | grep ERROR

# View recent logs
docker-compose logs --tail=100 web
```

## 🔒 Security Notes

1. **Redis**: Exposed on port 6380 (change in production)
2. **Web App**: Runs on port 5000 (use reverse proxy in production)
3. **Volumes**: Only necessary directories are mounted
4. **Health Checks**: All services have health checks configured

## 🚀 Production Deployment

For production deployment, consider:

1. **Reverse Proxy**: Use nginx or traefik
2. **SSL/TLS**: Configure HTTPS
3. **Secrets Management**: Use Docker secrets or environment files
4. **Monitoring**: Add Prometheus/Grafana
5. **Backup**: Configure Redis persistence and volume backups

### Example Production docker-compose.yml
```yaml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

  web:
    build: .
    environment:
      - FLASK_ENV=production
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./outputs:/app/outputs
      - ./uploads:/app/uploads
    depends_on:
      redis:
        condition: service_healthy
    restart: unless-stopped

  # ... other services
``` 