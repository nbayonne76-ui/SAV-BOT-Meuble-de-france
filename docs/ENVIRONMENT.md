# Environment Variables Documentation

Complete reference for all environment variables used in the Meuble de France Chatbot application.

## Table of Contents

- [Application Configuration](#application-configuration)
- [Database Configuration](#database-configuration)
- [Redis Configuration](#redis-configuration)
- [Security Configuration](#security-configuration)
- [API Keys](#api-keys)
- [CORS Configuration](#cors-configuration)
- [File Upload Configuration](#file-upload-configuration)
- [Rate Limiting](#rate-limiting)
- [Frontend Configuration](#frontend-configuration)
- [Docker Configuration](#docker-configuration)
- [Validation Rules](#validation-rules)

---

## Application Configuration

### `APP_NAME`
- **Description:** Application display name
- **Type:** String
- **Default:** `Meuble de France Chatbot`
- **Required:** No
- **Example:** `APP_NAME=Meuble de France Chatbot`

### `APP_VERSION`
- **Description:** Application version number
- **Type:** String
- **Default:** `1.0.0`
- **Required:** No
- **Example:** `APP_VERSION=1.0.0`

### `DEBUG`
- **Description:** Enable debug mode
- **Type:** Boolean
- **Default:** `True`
- **Required:** No
- **Values:** `True`, `False`
- **Production:** MUST be `False`
- **Example:** `DEBUG=False`

### `HOST`
- **Description:** Server bind address
- **Type:** String
- **Default:** `0.0.0.0`
- **Required:** No
- **Example:** `HOST=0.0.0.0`

### `PORT`
- **Description:** Server port
- **Type:** Integer
- **Default:** `8000`
- **Required:** No
- **Range:** 1-65535
- **Example:** `PORT=8000`

---

## Database Configuration

### `DATABASE_URL`
- **Description:** Complete database connection string
- **Type:** String
- **Default:** `sqlite:///./chatbot.db`
- **Required:** Yes
- **Format:** `dialect://user:password@host:port/database`
- **Development:** `sqlite:///./chatbot.db`
- **Production:** `postgresql://user:password@host:5432/database`
- **Examples:**
  ```bash
  # SQLite (development)
  DATABASE_URL=sqlite:///./chatbot.db

  # PostgreSQL (production)
  DATABASE_URL=postgresql://mdf_user:SecurePassword@localhost:5432/meubledefrance

  # PostgreSQL (Docker)
  DATABASE_URL=postgresql://postgres:postgres@postgres:5432/meubledefrance
  ```

### `POSTGRES_DB`
- **Description:** PostgreSQL database name
- **Type:** String
- **Default:** `meubledefrance`
- **Required:** Yes (for Docker Compose)
- **Example:** `POSTGRES_DB=meubledefrance`

### `POSTGRES_USER`
- **Description:** PostgreSQL username
- **Type:** String
- **Default:** `postgres`
- **Required:** Yes (for Docker Compose)
- **Example:** `POSTGRES_USER=mdf_user`

### `POSTGRES_PASSWORD`
- **Description:** PostgreSQL password
- **Type:** String
- **Default:** `postgres`
- **Required:** Yes
- **Security:** Use strong password in production!
- **Min Length:** 12 characters
- **Example:** `POSTGRES_PASSWORD=StrongPassword123!`

### `POSTGRES_PORT`
- **Description:** PostgreSQL port
- **Type:** Integer
- **Default:** `5432`
- **Required:** No
- **Example:** `POSTGRES_PORT=5432`

---

## Redis Configuration

### `REDIS_URL`
- **Description:** Redis connection URL
- **Type:** String
- **Default:** `memory://`
- **Required:** No
- **Format:** `redis://[:password@]host:port/db`
- **Development:** `memory://` (in-memory fallback)
- **Production:** `redis://:password@host:6379/0`
- **Examples:**
  ```bash
  # In-memory (development)
  REDIS_URL=memory://

  # Redis without password
  REDIS_URL=redis://localhost:6379/0

  # Redis with password
  REDIS_URL=redis://:MyRedisPassword@localhost:6379/0

  # Docker
  REDIS_URL=redis://:password@redis:6379/0
  ```

### `REDIS_PASSWORD`
- **Description:** Redis password (for Docker Compose)
- **Type:** String
- **Default:** Empty
- **Required:** No (Yes for production)
- **Security:** Use strong password in production!
- **Example:** `REDIS_PASSWORD=RedisSecurePass123`

### `REDIS_PORT`
- **Description:** Redis port
- **Type:** Integer
- **Default:** `6379`
- **Required:** No
- **Example:** `REDIS_PORT=6379`

---

## Security Configuration

### `SECRET_KEY` ⚠️
- **Description:** Secret key for JWT token signing and encryption
- **Type:** String
- **Default:** Auto-generated in development
- **Required:** **YES (CRITICAL for production!)**
- **Min Length:** 32 characters
- **Security:** NEVER commit to git, rotate periodically
- **Generate:**
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- **Example:** `SECRET_KEY=your-generated-secret-key-here-32-chars-minimum`

### `ACCESS_TOKEN_EXPIRE_MINUTES`
- **Description:** JWT access token expiration time
- **Type:** Integer
- **Default:** `30`
- **Required:** No
- **Range:** 5-1440 (5 minutes to 24 hours)
- **Recommended:** 15-30 minutes
- **Example:** `ACCESS_TOKEN_EXPIRE_MINUTES=30`

### `REFRESH_TOKEN_EXPIRE_DAYS`
- **Description:** JWT refresh token expiration time
- **Type:** Integer
- **Default:** `7`
- **Required:** No
- **Range:** 1-30
- **Recommended:** 7-14 days
- **Example:** `REFRESH_TOKEN_EXPIRE_DAYS=7`

---

## API Keys

### `OPENAI_API_KEY` ⚠️
- **Description:** OpenAI API key for GPT models
- **Type:** String
- **Default:** None
- **Required:** **YES (REQUIRED!)**
- **Format:** `sk-...`
- **Security:** NEVER commit to git
- **Get Key:** https://platform.openai.com/api-keys
- **Example:** `OPENAI_API_KEY=sk-your-openai-api-key-here`

---

## CORS Configuration

### `CORS_ORIGINS`
- **Description:** Allowed CORS origins (comma-separated)
- **Type:** String (comma-separated list)
- **Default:** `http://localhost:5173,http://localhost:3000`
- **Required:** Yes
- **Format:** Comma-separated URLs without trailing slash
- **Development:** Allow localhost ports
- **Production:** Only allow production domains
- **Examples:**
  ```bash
  # Development
  CORS_ORIGINS=http://localhost:5173,http://localhost:3000

  # Production
  CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

  # Multiple environments
  CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com,https://admin.yourdomain.com
  ```

---

## File Upload Configuration

### `UPLOAD_DIR`
- **Description:** Directory for uploaded files
- **Type:** String (path)
- **Default:** `./uploads`
- **Required:** No
- **Permissions:** Must be writable
- **Docker:** Use absolute path `/app/uploads`
- **Examples:**
  ```bash
  # Local
  UPLOAD_DIR=./uploads

  # Docker
  UPLOAD_DIR=/app/uploads

  # Absolute path
  UPLOAD_DIR=/var/www/uploads
  ```

### `MAX_FILE_SIZE`
- **Description:** Maximum upload file size in bytes
- **Type:** Integer
- **Default:** `10485760` (10MB)
- **Required:** No
- **Common Values:**
  - 10MB: `10485760`
  - 50MB: `52428800`
  - 100MB: `104857600`
- **Example:** `MAX_FILE_SIZE=10485760`

### `ALLOWED_EXTENSIONS`
- **Description:** Allowed file extensions (comma-separated)
- **Type:** String
- **Default:** `jpg,jpeg,png,gif,heic,mp4,mov,avi,webm`
- **Required:** No
- **Format:** Lowercase, comma-separated, no dots
- **Example:** `ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,heic,mp4,mov`

---

## Rate Limiting

### `RATE_LIMIT_DEFAULT`
- **Description:** Default rate limit for API endpoints
- **Type:** String
- **Default:** `100/minute`
- **Required:** No
- **Format:** `{count}/{period}`
- **Periods:** `second`, `minute`, `hour`, `day`
- **Development:** 1000/minute (relaxed)
- **Production:** 100/minute (strict)
- **Examples:**
  ```bash
  RATE_LIMIT_DEFAULT=100/minute
  RATE_LIMIT_DEFAULT=1000/hour
  RATE_LIMIT_DEFAULT=10/second
  ```

### `RATE_LIMIT_AUTH`
- **Description:** Rate limit for authentication endpoints
- **Type:** String
- **Default:** `5/minute`
- **Required:** No
- **Format:** `{count}/{period}`
- **Recommended:** 5-10/minute (protect against brute force)
- **Example:** `RATE_LIMIT_AUTH=5/minute`

---

## Frontend Configuration

### `VITE_API_URL`
- **Description:** Backend API URL for frontend
- **Type:** String (URL)
- **Default:** `http://localhost:8000`
- **Required:** Yes (for frontend)
- **Format:** Complete URL without trailing slash
- **Examples:**
  ```bash
  # Development
  VITE_API_URL=http://localhost:8000

  # Production
  VITE_API_URL=https://api.yourdomain.com

  # Same domain
  VITE_API_URL=https://yourdomain.com/api
  ```

---

## Docker Configuration

### `BACKEND_PORT`
- **Description:** Host port for backend service
- **Type:** Integer
- **Default:** `8000`
- **Required:** No (for Docker Compose)
- **Example:** `BACKEND_PORT=8000`

### `FRONTEND_PORT`
- **Description:** Host port for frontend service
- **Type:** Integer
- **Default:** `5173`
- **Required:** No (for Docker Compose)
- **Example:** `FRONTEND_PORT=5173`

---

## Validation Rules

### Required Variables by Environment

**Development (Minimum):**
- `OPENAI_API_KEY` ⚠️

**Production (Required):**
- `OPENAI_API_KEY` ⚠️
- `SECRET_KEY` ⚠️
- `DATABASE_URL` (PostgreSQL)
- `POSTGRES_PASSWORD`
- `REDIS_URL` (with password)
- `REDIS_PASSWORD`
- `CORS_ORIGINS` (production domains)
- `DEBUG=False`

### Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` (32+ characters)
- [ ] Strong database password (12+ characters)
- [ ] Strong Redis password (12+ characters)
- [ ] `OPENAI_API_KEY` never committed to git
- [ ] `CORS_ORIGINS` set to production domains only
- [ ] Rate limits configured appropriately
- [ ] File upload limits set
- [ ] All secrets stored securely (not in git)

---

## Example Configurations

### Development (.env)
```bash
DEBUG=True
OPENAI_API_KEY=sk-your-dev-key
DATABASE_URL=sqlite:///./chatbot.db
REDIS_URL=memory://
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
SECRET_KEY=dev-key-auto-generated
```

### Production (.env)
```bash
DEBUG=False
APP_NAME=Meuble de France Chatbot
SECRET_KEY=your-generated-secret-key-32-chars-minimum
OPENAI_API_KEY=sk-your-prod-key
DATABASE_URL=postgresql://mdf_user:StrongPass123@postgres:5432/meubledefrance
POSTGRES_PASSWORD=StrongPass123
REDIS_URL=redis://:RedisPass123@redis:6379/0
REDIS_PASSWORD=RedisPass123
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_AUTH=5/minute
VITE_API_URL=https://yourdomain.com/api
```

---

## Support

For questions or issues:
- Check [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment guide
- Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues
- Open an issue on GitHub

**Last Updated:** 2025-12-09
