# CrystalFish Deployment Guide

This guide covers deploying CrystalFish to a production server using Docker Compose.

## Prerequisites

- Ubuntu 22.04 LTS (or similar Linux distribution)
- Domain name pointing to your server
- Docker and Docker Compose installed

## Server Setup

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. Clone Repository

```bash
cd ~
git clone https://github.com/yourusername/crystalfish.git
cd crystalfish
```

### 4. Configure Environment

Create production environment file:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```bash
# Security - CHANGE THESE!
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Database
DATABASE_URL=postgresql+asyncpg://postgres:your-strong-password@postgres:5432/crystalfish
DATABASE_URL_SYNC=postgresql://postgres:your-strong-password@postgres:5432/crystalfish

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_BROKER_URL=redis://redis:6379/1

# OpenRouter (get free key at openrouter.ai)
OPENROUTER_API_KEY=your-openrouter-api-key

# Frontend URL
FRONTEND_URL=https://your-domain.com
```

### 5. Configure Docker Compose for Production

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: crystalfish
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - crystalfish-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - crystalfish-network
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DEBUG=false
      - DATABASE_URL=${DATABASE_URL}
      - DATABASE_URL_SYNC=${DATABASE_URL_SYNC}
      - REDIS_URL=${REDIS_URL}
      - REDIS_BROKER_URL=${REDIS_BROKER_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - FRONTEND_URL=${FRONTEND_URL}
    volumes:
      - uploads_data:/app/uploads
    depends_on:
      - postgres
      - redis
    networks:
      - crystalfish-network
    restart: unless-stopped
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DEBUG=false
      - DATABASE_URL=${DATABASE_URL}
      - DATABASE_URL_SYNC=${DATABASE_URL_SYNC}
      - REDIS_URL=${REDIS_URL}
      - REDIS_BROKER_URL=${REDIS_BROKER_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    volumes:
      - uploads_data:/app/uploads
    depends_on:
      - postgres
      - redis
    networks:
      - crystalfish-network
    restart: unless-stopped
    command: celery -A app.worker.celery_app worker --loglevel=info --concurrency=4

  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DEBUG=false
      - DATABASE_URL=${DATABASE_URL}
      - DATABASE_URL_SYNC=${DATABASE_URL_SYNC}
      - REDIS_URL=${REDIS_URL}
      - REDIS_BROKER_URL=${REDIS_BROKER_URL}
    depends_on:
      - postgres
      - redis
    networks:
      - crystalfish-network
    restart: unless-stopped
    command: celery -A app.worker.celery_app beat --loglevel=info

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    depends_on:
      - backend
    networks:
      - crystalfish-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
    networks:
      - crystalfish-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  uploads_data:

networks:
  crystalfish-network:
    driver: bridge
```

### 6. Configure Nginx

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    # Frontend
    server {
        listen 80;
        server_name your-domain.com;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL certificates (from Let's Encrypt)
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # Frontend
        location / {
            proxy_pass http://frontend:80;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend API
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket
        location /ws/ {
            proxy_pass http://backend:8000/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }
    }
}
```

### 7. SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot

# Obtain certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo mkdir -p ~/crystalfish/nginx/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ~/crystalfish/nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ~/crystalfish/nginx/ssl/
sudo chown -R $USER:$USER ~/crystalfish/nginx/ssl
```

### 8. Deploy

```bash
cd ~/crystalfish

# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Run database migrations (if needed)
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### 9. Setup Auto-Renewal for SSL

```bash
# Create renewal hook
sudo mkdir -p /etc/letsencrypt/renewal-hooks/deploy
cat << 'EOF' | sudo tee /etc/letsencrypt/renewal-hooks/deploy/crystalfish.sh
#!/bin/bash
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /home/ubuntu/crystalfish/nginx/ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem /home/ubuntu/crystalfish/nginx/ssl/
chown -R ubuntu:ubuntu /home/ubuntu/crystalfish/nginx/ssl
docker-compose -f /home/ubuntu/crystalfish/docker-compose.prod.yml restart nginx
EOF

sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/crystalfish.sh

# Test renewal
sudo certbot renew --dry-run
```

### 10. Monitoring

```bash
# View container status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f celery-worker

# Resource usage
docker stats
```

## Backup

### Database Backup

```bash
# Create backup script
cat << 'EOF' > ~/backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose -f ~/crystalfish/docker-compose.prod.yml exec -T postgres pg_dump -U postgres crystalfish > ~/backups/crystalfish_$DATE.sql
gzip ~/backups/crystalfish_$DATE.sql
# Keep only last 7 days
find ~/backups -name "crystalfish_*.sql.gz" -mtime +7 -delete
EOF

chmod +x ~/backup.sh
mkdir -p ~/backups

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * ~/backup.sh") | crontab -
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs service-name

# Restart service
docker-compose -f docker-compose.prod.yml restart service-name
```

### Database Connection Issues

```bash
# Check postgres is running
docker-compose -f docker-compose.prod.yml ps postgres

# Connect to database
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres -d crystalfish
```

### High Memory Usage

```bash
# Check memory usage
docker stats --no-stream

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

## Updates

```bash
cd ~/crystalfish
git pull

docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

## Security Checklist

- [ ] Changed default passwords
- [ ] Set strong JWT_SECRET_KEY
- [ ] Set strong SECRET_KEY
- [ ] Configured firewall (ufw)
- [ ] Enabled SSL/HTTPS
- [ ] Setup regular backups
- [ ] Disabled debug mode
- [ ] Configured rate limiting

## Support

For issues and questions, please open a GitHub issue or contact support.