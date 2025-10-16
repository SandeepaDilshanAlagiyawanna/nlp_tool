# 🚀 Deployment Guide

## Deployment Options

### Option 1: Local Development (Recommended for Testing)

```bash
# Quick start
./start.sh

# Or manual
python integrated_app.py
```

**Access:** http://localhost:8000

---

### Option 2: Docker Deployment

#### Prerequisites

- Docker installed
- Docker Compose (optional)

#### Build and Run

**Using Docker:**

```bash
# Build image
docker build -t nlp-pipeline .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  --name nlp-pipeline \
  nlp-pipeline

# View logs
docker logs -f nlp-pipeline

# Stop container
docker stop nlp-pipeline
```

**Using Docker Compose:**

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access:** http://localhost:8000

---

### Option 3: Production Server (Linux)

#### 1. Setup Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv ffmpeg git

# Clone or copy project
cd /opt
sudo mkdir nlp-pipeline
cd nlp-pipeline
# Copy your files here
```

#### 2. Install Application

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test
python test_modules.py
```

#### 3. Setup Systemd Service

Create `/etc/systemd/system/nlp-pipeline.service`:

```ini
[Unit]
Description=NLP Pipeline Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/nlp-pipeline
Environment="PATH=/opt/nlp-pipeline/venv/bin"
ExecStart=/opt/nlp-pipeline/venv/bin/python integrated_app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable nlp-pipeline
sudo systemctl start nlp-pipeline
sudo systemctl status nlp-pipeline
```

#### 4. Setup Nginx Reverse Proxy

Install Nginx:

```bash
sudo apt install nginx
```

Create `/etc/nginx/sites-available/nlp-pipeline`:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Change this

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed later)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeout settings for long processing
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/nlp-pipeline /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. Setup SSL (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

**Access:** https://your-domain.com

---

### Option 4: Cloud Deployment

#### AWS EC2

1. **Launch EC2 Instance**

   - AMI: Ubuntu 22.04 LTS
   - Instance type: t3.medium or larger (4GB+ RAM)
   - Storage: 20GB+
   - Security Group: Allow ports 22, 80, 443

2. **Connect and Setup**

   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip

   # Follow "Production Server" steps above
   ```

3. **Configure Security Group**
   - Inbound: HTTP (80), HTTPS (443), SSH (22)
   - Outbound: All

#### Google Cloud Platform (GCP)

1. **Create VM Instance**

   - Machine type: e2-medium or larger
   - Boot disk: Ubuntu 22.04 LTS, 20GB
   - Firewall: Allow HTTP, HTTPS

2. **Setup**

   ```bash
   gcloud compute ssh your-instance-name

   # Follow "Production Server" steps above
   ```

#### Heroku

Create `Procfile`:

```
web: python integrated_app.py
```

Create `runtime.txt`:

```
python-3.9.18
```

Update `config.py`:

```python
import os
SERVER_PORT = int(os.environ.get("PORT", 8000))
```

Deploy:

```bash
heroku create your-app-name
git push heroku main
```

---

## Performance Tuning

### 1. Use Multiple Workers

```bash
# Using Gunicorn
pip install gunicorn

gunicorn integrated_app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300
```

### 2. Optimize Models

```python
# Use smaller Vosk model for faster processing
VOSK_MODEL_PATH = "vosk-model-small-en-us-0.15"

# Reduce summary sentences
SUMMARY_SENTENCES = 2

# Limit max translation length
MAX_TRANSLATION_LENGTH = 256
```

### 3. Add Caching (Redis)

```bash
pip install redis aioredis
```

```python
import redis
cache = redis.Redis(host='localhost', port=6379)

# Cache translations
def translate_with_cache(text):
    cached = cache.get(f"trans:{text}")
    if cached:
        return cached.decode()

    result = translate_to_sinhala(text)
    cache.setex(f"trans:{text}", 3600, result)
    return result
```

### 4. Database for Results

```bash
pip install sqlalchemy databases
```

Store processing results for history and analytics.

---

## Monitoring

### 1. Application Logs

```bash
# View systemd logs
sudo journalctl -u nlp-pipeline -f

# Save to file
sudo journalctl -u nlp-pipeline > nlp-pipeline.log
```

### 2. Add Prometheus Metrics

```bash
pip install prometheus-fastapi-instrumentator
```

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### 3. Health Monitoring

Setup monitoring service to check `/health` endpoint:

- UptimeRobot (free)
- Pingdom
- AWS CloudWatch

---

## Backup and Recovery

### Backup

```bash
# Backup configuration
cp config.py config.py.backup

# Backup models (if custom trained)
tar -czf models-backup.tar.gz "vosk assignment/"

# Backup database (if used)
# pg_dump or sqlite3 backup
```

### Recovery

```bash
# Restore from backup
cp config.py.backup config.py
tar -xzf models-backup.tar.gz
```

---

## Security Hardening

### 1. Environment Variables

Create `.env` file:

```bash
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
MAX_UPLOAD_SIZE=104857600
DEBUG_MODE=False
```

Load in application:

```python
from dotenv import load_dotenv
load_dotenv()
```

### 2. Add Authentication

```bash
pip install python-jose passlib
```

Implement JWT authentication for API endpoints.

### 3. Rate Limiting

```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/process-audio")
@limiter.limit("5/minute")
async def process_audio():
    ...
```

### 4. File Validation

Add virus scanning:

```bash
pip install pyclamd
```

Validate file types properly (not just extension).

---

## Troubleshooting Deployment

### Issue: Out of Memory

**Solution:**

- Increase server RAM
- Use model quantization
- Process in batches
- Add swap space

### Issue: Slow Performance

**Solution:**

- Use multiple workers
- Add caching layer
- Optimize model inference
- Use GPU if available

### Issue: Models Not Loading

**Solution:**

- Check file permissions
- Verify model paths
- Download models separately
- Check disk space

---

## Maintenance

### Updates

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart nlp-pipeline
```

### Monitoring Checklist

- [ ] Check disk space (models ~1GB)
- [ ] Monitor memory usage (4GB+ recommended)
- [ ] Review error logs
- [ ] Test API endpoints
- [ ] Verify model loading times
- [ ] Check SSL certificate expiry

---

## Cost Estimates

### AWS EC2 (t3.medium)

- Instance: ~$30/month
- Storage: ~$2/month
- Traffic: Variable
- **Total: ~$32-50/month**

### Google Cloud (e2-medium)

- VM: ~$25/month
- Storage: ~$2/month
- **Total: ~$27-45/month**

### Heroku

- Dyno: $7-25/month
- Limited by memory/processing

### VPS (DigitalOcean, Linode)

- 4GB RAM droplet: $24/month
- **Best value for this app**

---

## Support

For deployment issues:

1. Check logs: `docker logs` or `journalctl`
2. Test modules: `python test_modules.py`
3. Verify dependencies: `pip list`
4. Check ports: `netstat -tlnp | grep 8000`

---

**Deployment Guide Version:** 1.0  
**Last Updated:** October 2025
