# Troubleshooting Guide - Meuble de France Chatbot

Common issues and their solutions for the SAV-BOT application.

## Table of Contents

- [Deployment Issues](#deployment-issues)
- [Database Issues](#database-issues)
- [Redis Issues](#redis-issues)
- [API Issues](#api-issues)
- [Authentication Issues](#authentication-issues)
- [Frontend Issues](#frontend-issues)
- [Docker Issues](#docker-issues)
- [Performance Issues](#performance-issues)
- [Getting Help](#getting-help)

---

## Deployment Issues

### Issue: Docker Compose fails to start

**Symptoms:**
```
ERROR: Service 'backend' failed to build
```

**Solutions:**

1. **Check Docker is running:**
   ```bash
   docker --version
   docker ps
   ```

2. **Check docker-compose.yml syntax:**
   ```bash
   docker-compose config
   ```

3. **Remove old containers and volumes:**
   ```bash
   docker-compose down -v
   docker system prune -a
   docker-compose up --build
   ```

4. **Check disk space:**
   ```bash
   df -h
   docker system df
   ```

---

### Issue: Environment variables not loading

**Symptoms:**
```
ValueError: OPENAI_API_KEY not found in environment
```

**Solutions:**

1. **Ensure .env file exists:**
   ```bash
   ls -la .env
   ```

2. **Check .env file location:**
   - For standalone: `backend/.env`
   - For Docker: `.env` in project root

3. **Verify .env format:**
   ```bash
   cat .env
   # Should show: KEY=value (no spaces around =)
   ```

4. **Restart services:**
   ```bash
   docker-compose restart
   ```

---

### Issue: Port already in use

**Symptoms:**
```
ERROR: for backend  Cannot start service backend: driver failed
Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Solutions:**

1. **Find process using the port:**
   ```bash
   # Linux/Mac
   lsof -i :8000
   # Windows
   netstat -ano | findstr :8000
   ```

2. **Kill the process:**
   ```bash
   kill -9 <PID>
   ```

3. **Change port in .env:**
   ```bash
   BACKEND_PORT=8001
   ```

4. **Restart Docker:**
   ```bash
   docker-compose down
   docker-compose up
   ```

---

## Database Issues

### Issue: Database connection refused

**Symptoms:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions:**

1. **Check PostgreSQL is running:**
   ```bash
   docker-compose ps postgres
   docker-compose logs postgres
   ```

2. **Verify DATABASE_URL:**
   ```bash
   echo $DATABASE_URL
   # Should be: postgresql://user:password@postgres:5432/database
   ```

3. **Test connection:**
   ```bash
   docker-compose exec postgres psql -U postgres -d meubledefrance
   ```

4. **Restart PostgreSQL:**
   ```bash
   docker-compose restart postgres
   ```

---

### Issue: Migration fails

**Symptoms:**
```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solutions:**

1. **Check current migration:**
   ```bash
   docker-compose exec backend alembic current
   ```

2. **Upgrade to latest:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

3. **If migrations conflict:**
   ```bash
   # Downgrade one version
   docker-compose exec backend alembic downgrade -1

   # Then upgrade
   docker-compose exec backend alembic upgrade head
   ```

4. **Reset database (CAUTION - loses data!):**
   ```bash
   docker-compose down -v
   docker-compose up -d postgres
   docker-compose exec backend alembic upgrade head
   ```

---

### Issue: Database locked (SQLite)

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Solutions:**

1. **SQLite is for development only!**
   - Use PostgreSQL for production

2. **Close all connections:**
   ```bash
   # Restart backend
   docker-compose restart backend
   ```

3. **Switch to PostgreSQL:**
   ```bash
   DATABASE_URL=postgresql://user:pass@postgres:5432/db
   ```

---

## Redis Issues

### Issue: Redis connection refused

**Symptoms:**
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solutions:**

1. **Check Redis is running:**
   ```bash
   docker-compose ps redis
   docker-compose logs redis
   ```

2. **Test Redis connection:**
   ```bash
   docker-compose exec redis redis-cli ping
   # Should return: PONG
   ```

3. **Verify REDIS_URL:**
   ```bash
   echo $REDIS_URL
   # Should be: redis://:password@redis:6379/0
   ```

4. **Use fallback (development only):**
   ```bash
   REDIS_URL=memory://
   ```

---

### Issue: Redis authentication failed

**Symptoms:**
```
redis.exceptions.AuthenticationError: Authentication required
```

**Solutions:**

1. **Check Redis password:**
   ```bash
   echo $REDIS_PASSWORD
   ```

2. **Update REDIS_URL with password:**
   ```bash
   REDIS_URL=redis://:your_password@redis:6379/0
   ```

3. **Test with password:**
   ```bash
   docker-compose exec redis redis-cli -a your_password ping
   ```

---

## API Issues

### Issue: 500 Internal Server Error

**Symptoms:**
```json
{"detail": "Internal server error"}
```

**Solutions:**

1. **Check backend logs:**
   ```bash
   docker-compose logs backend --tail=100
   ```

2. **Enable debug mode (development only):**
   ```bash
   DEBUG=True
   docker-compose restart backend
   ```

3. **Check OpenAI API key:**
   ```bash
   docker-compose exec backend python -c "import os; print('OK' if os.getenv('OPENAI_API_KEY') else 'MISSING')"
   ```

4. **Restart backend:**
   ```bash
   docker-compose restart backend
   ```

---

### Issue: 401 Unauthorized

**Symptoms:**
```json
{"detail": "Not authenticated"}
```

**Solutions:**

1. **Check token is sent:**
   ```bash
   # Token should be in Authorization header
   curl -H "Authorization: Bearer <token>" http://localhost:8000/api/auth/me
   ```

2. **Check token hasn't expired:**
   ```bash
   # Login again to get new token
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"user@example.com","password":"password"}'
   ```

3. **Verify SECRET_KEY is set:**
   ```bash
   echo $SECRET_KEY
   ```

---

### Issue: 429 Too Many Requests

**Symptoms:**
```json
{"detail": "Rate limit exceeded"}
```

**Solutions:**

1. **Wait for rate limit to reset**
   - Default: 100 requests/minute

2. **Adjust rate limits (development):**
   ```bash
   RATE_LIMIT_DEFAULT=1000/minute
   docker-compose restart backend
   ```

3. **Check IP-based limits:**
   ```bash
   # Rate limits are per IP address
   ```

---

## Authentication Issues

### Issue: Cannot register user

**Symptoms:**
```json
{"detail": "Email already registered"}
```

**Solutions:**

1. **Use different email:**
   ```bash
   # Each email can only be registered once
   ```

2. **Reset user (development):**
   ```bash
   docker-compose exec backend python -c "
   from app.db.session import SessionLocal
   from app.models.user import User
   db = SessionLocal()
   db.query(User).filter_by(email='test@example.com').delete()
   db.commit()
   "
   ```

---

### Issue: Invalid password

**Symptoms:**
```json
{"detail": "Incorrect email or password"}
```

**Solutions:**

1. **Check password requirements:**
   - Minimum 8 characters
   - Case sensitive

2. **Reset password (development):**
   ```bash
   docker-compose exec backend python -m app.scripts.reset_password user@example.com
   ```

---

## Frontend Issues

### Issue: Cannot connect to API

**Symptoms:**
```
Failed to fetch
Network error
CORS error
```

**Solutions:**

1. **Check VITE_API_URL:**
   ```bash
   echo $VITE_API_URL
   # Should be: http://localhost:8000 or production URL
   ```

2. **Verify backend is running:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Check CORS settings:**
   ```bash
   # CORS_ORIGINS should include frontend URL
   CORS_ORIGINS=http://localhost:5173
   ```

4. **Restart frontend:**
   ```bash
   docker-compose restart frontend
   ```

---

### Issue: Build fails

**Symptoms:**
```
npm ERR! code ELIFECYCLE
```

**Solutions:**

1. **Clear cache and rebuild:**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

2. **Check Node version:**
   ```bash
   node --version
   # Should be 20+
   ```

3. **Fix dependencies:**
   ```bash
   npm audit fix
   ```

---

## Docker Issues

### Issue: Container keeps restarting

**Symptoms:**
```bash
docker-compose ps
# Shows "Restarting"
```

**Solutions:**

1. **Check logs:**
   ```bash
   docker-compose logs backend
   ```

2. **Check health:**
   ```bash
   docker-compose exec backend curl http://localhost:8000/health
   ```

3. **Remove restart policy (debug):**
   ```yaml
   # In docker-compose.yml
   restart: "no"
   ```

---

### Issue: Volume permission denied

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

1. **Fix permissions:**
   ```bash
   sudo chown -R $USER:$USER backend/uploads
   sudo chmod -R 755 backend/uploads
   ```

2. **Run as root (not recommended):**
   ```dockerfile
   # Remove USER directive from Dockerfile
   ```

---

### Issue: Out of disk space

**Symptoms:**
```
no space left on device
```

**Solutions:**

1. **Check disk usage:**
   ```bash
   docker system df
   df -h
   ```

2. **Clean Docker:**
   ```bash
   docker system prune -a --volumes
   ```

3. **Remove old images:**
   ```bash
   docker images
   docker rmi <image_id>
   ```

---

## Performance Issues

### Issue: Slow API responses

**Solutions:**

1. **Check database queries:**
   ```bash
   # Enable SQL logging
   DEBUG=True
   ```

2. **Add database indexes:**
   ```python
   # Create Alembic migration
   alembic revision -m "add indexes"
   ```

3. **Check Redis connection:**
   ```bash
   docker-compose logs redis
   ```

4. **Increase resources:**
   ```yaml
   # docker-compose.yml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
   ```

---

### Issue: High memory usage

**Solutions:**

1. **Monitor resources:**
   ```bash
   docker stats
   ```

2. **Limit container memory:**
   ```yaml
   # docker-compose.yml
   services:
     backend:
       mem_limit: 1g
   ```

3. **Check for memory leaks:**
   ```bash
   docker-compose logs backend | grep "memory"
   ```

---

## Getting Help

If you're still experiencing issues:

### 1. Collect Information

```bash
# System info
docker --version
docker-compose --version
python --version
node --version

# Service status
docker-compose ps

# Logs
docker-compose logs backend --tail=100 > backend.log
docker-compose logs frontend --tail=100 > frontend.log

# Environment
docker-compose config
```

### 2. Common Log Locations

```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# Nginx logs
docker-compose logs nginx

# PostgreSQL logs
docker-compose logs postgres

# Redis logs
docker-compose logs redis
```

### 3. Debug Mode

Enable debug mode (development only):

```bash
DEBUG=True
docker-compose restart backend
```

### 4. Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Backend readiness
curl http://localhost:8000/ready

# Frontend health
curl http://localhost:5173/health
```

### 5. Contact Support

- **GitHub Issues:** Open an issue with logs and steps to reproduce
- **Email:** nicolas.bayonne@contact.fr
- **Documentation:** Check [DEPLOYMENT.md](./DEPLOYMENT.md) and [ENVIRONMENT.md](./ENVIRONMENT.md)

---

## Emergency Procedures

### Complete Reset (Development Only)

**WARNING: This will delete all data!**

```bash
# Stop all services
docker-compose down -v

# Remove all containers and images
docker system prune -a --volumes

# Remove project data
rm -rf backend/uploads/*
rm -f backend/chatbot.db

# Rebuild from scratch
docker-compose up --build -d

# Run migrations
docker-compose exec backend alembic upgrade head
```

---

**Last Updated:** 2025-12-09
