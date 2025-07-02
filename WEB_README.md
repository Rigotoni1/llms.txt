# LLMs.txt Generator - Web Application

A beautiful, modern web interface for the LLMs.txt Generator that makes it easy to create structured documentation for websites.

## 🌟 Features

- **Modern Web Interface**: Clean, responsive design with Bootstrap 5
- **Real-time Validation**: Validate sitemap URLs before generation
- **Configuration Management**: Upload YAML config files or use the form
- **Live Status Updates**: See progress and results in real-time
- **File Download**: Download generated files directly from the browser
- **Content Preview**: View generated content before downloading
- **Auto-save**: Form data is automatically saved to browser storage
- **Keyboard Shortcuts**: Ctrl/Cmd + Enter to generate, Escape to close modals

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Web Server
```bash
python run_web.py
```

### 3. Open Your Browser
Navigate to: http://localhost:5000

## 📱 Web Interface Guide

### Main Form
The main form allows you to configure all aspects of the LLMs.txt generation:

- **Sitemap URL**: Enter your website's sitemap.xml URL
- **Site Name**: The name of your website
- **Site Description**: Brief description of your site
- **Content Selectors**: CSS selectors for finding content and titles
- **Processing Options**: Control how many pages to process and content length
- **Behavior Settings**: Respect robots.txt, request delays, etc.

### Quick Actions
- **Load Sample Config**: Populate the form with default settings
- **Upload Config File**: Upload a YAML configuration file
- **Help & Tips**: View detailed help and best practices

### Results Section
After generation, you'll see:
- **Statistics**: Total URLs, pages scraped, file size
- **Download**: Download the generated file
- **View Content**: Preview the generated content

## 🔧 API Endpoints

The web app also provides a REST API:

### Generate LLMs.txt
```http
POST /generate
Content-Type: application/x-www-form-urlencoded

sitemap_url=https://example.com/sitemap.xml
site_name=My Website
site_description=Description of my website
content_selector=.content, #main, article
title_selector=h1, .title
max_pages=10
max_content_length=500
request_delay=1.0
respect_robots=on
```

### Validate Sitemap
```http
POST /api/validate-sitemap
Content-Type: application/json

{
  "sitemap_url": "https://example.com/sitemap.xml"
}
```

### Get Sample Configuration
```http
GET /api/sample-config
```

### Upload Configuration File
```http
POST /upload-config
Content-Type: multipart/form-data

config_file: [YAML file]
```

### Download Generated File
```http
GET /download/<filename>
```

## 🎨 Customization

### Styling
The web interface uses custom CSS in `static/css/style.css`. You can modify:
- Color scheme and gradients
- Card shadows and animations
- Button styles and hover effects
- Form styling and focus states

### Templates
The main template is in `templates/index.html`. You can customize:
- Layout and structure
- Form fields and validation
- Modal dialogs
- Status messages

### JavaScript
The frontend logic is in `static/js/app.js`. You can extend:
- Form validation
- API interactions
- UI animations
- Keyboard shortcuts

## 🔒 Security Considerations

### Production Deployment
For production use:

1. **Change the secret key** in `app.py`:
   ```python
   app.secret_key = 'your-secure-secret-key-here'
   ```

2. **Use HTTPS** with a proper SSL certificate

3. **Set up proper logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.WARNING)
   ```

4. **Configure file upload limits**:
   ```python
   app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
   ```

5. **Add rate limiting** for API endpoints

6. **Use environment variables** for sensitive configuration

### Example Production Setup
```python
import os
from app import app

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=False
    )
```

## 🐳 Docker Support

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "run_web.py"]
```

Build and run:
```bash
docker build -t llms-txt-generator .
docker run -p 5000:5000 llms-txt-generator
```

## 🔧 Configuration

### Environment Variables
- `FLASK_ENV`: Set to 'production' for production mode
- `FLASK_DEBUG`: Set to '0' to disable debug mode
- `PORT`: Port number (default: 5000)

### File Structure
```
LLMs.txt/
├── app.py                 # Flask application
├── run_web.py            # Web server runner
├── templates/
│   └── index.html        # Main web interface
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── app.js        # Frontend JavaScript
├── uploads/              # Uploaded config files
└── outputs/              # Generated files
```

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Find and kill the process
   lsof -ti:5000 | xargs kill -9
   ```

2. **Import errors**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

3. **Permission errors**
   ```bash
   # Create directories with proper permissions
   mkdir -p uploads outputs
   chmod 755 uploads outputs
   ```

4. **CORS issues** (if accessing from different domain)
   ```python
   # Add CORS support
   from flask_cors import CORS
   CORS(app)
   ```

### Debug Mode
For development, enable debug mode:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

This will:
- Show detailed error messages
- Auto-reload on code changes
- Enable debug toolbar

## 📊 Monitoring

### Logging
The application logs to the console. For production, consider:
- File-based logging
- Structured logging (JSON)
- Log aggregation (ELK stack)

### Health Check
Add a health check endpoint:
```python
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

---

**Happy generating! 🚀** 