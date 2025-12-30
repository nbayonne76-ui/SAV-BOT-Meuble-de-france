# Deployment Guide - Meuble de France Chatbot

This guide covers deploying the SAV-BOT Meuble de France application to production.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development Deployment](#local-development-deployment)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Database Migration](#database-migration)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Monitoring Setup](#monitoring-setup)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **OS:** Linux (Ubuntu 22.04 LTS recommended) or macOS
- **CPU:** 2+ cores
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 20GB minimum
- **Docker:** 24.0+ and Docker Compose 2.0+
- **Python:** 3.11+ (if running without Docker)
- **Node.js:** 20+ (if running frontend without Docker)
- **PostgreSQL:** 16+ (production)
- **Redis:** 7+ (production)

### Required Accounts/Services

- OpenAI API account with GPT-4 access
- Domain name (for production)
- SSL certificate (Let's Encrypt recommended)
- (Optional) Cloud provider account (AWS, GCP, Azure, etc.)

---

## Local Development Deployment

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/meuble-de-france-chatbot.git
cd meuble-de-france-chatbot
```

### 2. Set Up Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your configuration
nano .env

# Required: Add your OpenAI API key
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Option A: Run with Docker Compose (Recommended)

```bash
# Start all services (backend, frontend, PostgreSQL, Redis)
docker-compose up -d

# Check logs
docker-compose logs -f

# Access:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### 3. Option B: Run Locally Without Docker

**Backend:**

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## Production Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
```

### 2. Clone and Configure

```bash
# Clone repository
git clone https://github.com/yourusername/meuble-de-france-chatbot.git
cd meuble-de-france-chatbot

# Copy production environment file
cp .env.production .env

# IMPORTANT: Edit .env with production values
nano .env
```

**Critical Production Settings:**

```bash
# Application
DEBUG=False
APP_NAME=Meuble de France Chatbot

# Database (use strong passwords!)
DATABASE_URL=postgresql://mdf_user:STRONG_PASSWORD@postgres:5432/meubledefrance
POSTGRES_PASSWORD=STRONG_PASSWORD

# Redis (use strong password!)
REDIS_URL=redis://:REDIS_PASSWORD@redis:6379/0
REDIS_PASSWORD=STRONG_REDIS_PASSWORD

# Security (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_HERE

# API Keys
OPENAI_API_KEY=sk-your-production-api-key

# CORS (your production domain)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_AUTH=5/minute
```

### 3. Generate SSL Certificates

**Option A: Let's Encrypt (Recommended)**

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificates will be in:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem

# Copy to project
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
sudo chown $USER:$USER nginx/ssl/*
```

**Option B: Self-Signed (Development Only)**

```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem
```

### 4. Deploy with Docker Compose

```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Access:
# - Frontend: https://yourdomain.com
# - Backend API: https://yourdomain.com/api
```

### 5. Run Database Migrations

```bash
# Run migrations in backend container
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Create initial admin user (optional)
docker-compose -f docker-compose.prod.yml exec backend python -m app.scripts.create_admin
```

---

## Docker Deployment

### Build Images

```bash
# Build backend image
docker build -t mdf-backend:latest ./backend

# Build frontend image
docker build -t mdf-frontend:latest ./frontend

# Tag for registry (optional)
docker tag mdf-backend:latest registry.example.com/mdf-backend:latest
docker tag mdf-frontend:latest registry.example.com/mdf-frontend:latest

# Push to registry
docker push registry.example.com/mdf-backend:latest
docker push registry.example.com/mdf-frontend:latest
```

### Docker Compose Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart a service
docker-compose restart backend

# View logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend bash

# Rebuild and restart
docker-compose up -d --build

# Remove all containers and volumes
docker-compose down -v
```

---

## Database Migration

### Using Alembic

```bash
# Inside backend container or with activated venv

# Check current version
alembic current

# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Create new migration
alembic revision --autogenerate -m "description"

# View migration history
alembic history
```

### Backup and Restore

```bash
# Backup PostgreSQL database
docker-compose exec postgres pg_dump -U postgres meubledefrance > backup_$(date +%Y%m%d).sql

# Restore database
cat backup_20240101.sql | docker-compose exec -T postgres psql -U postgres meubledefrance

# Backup uploads directory
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz backend/uploads/
```

---

## SSL/TLS Configuration

### Update Nginx Configuration

Edit `nginx/conf.d/default.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # Rest of configuration...
}
```

### Renew Let's Encrypt Certificates

```bash
# Renew certificate
sudo certbot renew

# Restart nginx
docker-compose restart nginx
```

---

## Monitoring Setup

### Health Checks

```bash
# Check application health
curl https://yourdomain.com/health

# Check readiness
curl https://yourdomain.com/ready

# Check backend directly
curl https://yourdomain.com/api/health
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend

# Since timestamp
docker-compose logs --since 2024-01-01T00:00:00 backend
```

### Resource Monitoring

```bash
# Container stats
docker stats

# Disk usage
df -h
docker system df

# Clean up unused resources
docker system prune -a
```

---

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for detailed troubleshooting guide.

### Quick Fixes

**Service won't start:**

```bash
# Check logs
docker-compose logs backend

# Restart service
docker-compose restart backend

# Rebuild if needed
docker-compose up -d --build backend
```

**Database connection error:**

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec backend python -c "from app.db.session import engine; print(engine.connect())"
```

**Redis connection error:**

```bash
# Check Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping
```

---

## Post-Deployment Checklist

- [ ] All services are running (`docker-compose ps`)
- [ ] Health checks pass (`/health` and `/ready`)
- [ ] Database migrations applied
- [ ] SSL certificate installed and valid
- [ ] Environment variables configured correctly
- [ ] CORS origins set to production domains
- [ ] Rate limiting configured
- [ ] Backups scheduled
- [ ] Monitoring configured
- [ ] Logs accessible
- [ ] Admin user created
- [ ] API documentation accessible (if enabled)
- [ ] Test registration and login
- [ ] Test chatbot functionality
- [ ] Test file upload

---

## Support

For issues or questions:
- Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- Review logs: `docker-compose logs`
- Open an issue on GitHub
- Contact: nicolas.bayonne@contact.fr

---

**Last Updated:** 2025-12-09
