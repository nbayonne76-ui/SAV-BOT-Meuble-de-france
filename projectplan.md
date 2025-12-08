# SAV-BOT Meuble de France - Production Readiness Plan

**Document Version:** 1.0
**Created:** 2025-12-08
**Project:** SAV-BOT Meuble de France
**Objective:** Transform the current development prototype into a production-ready application

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Assessment](#current-state-assessment)
3. [Production Requirements](#production-requirements)
4. [Implementation Phases](#implementation-phases)
5. [Detailed Task Breakdown](#detailed-task-breakdown)
6. [Risk Assessment](#risk-assessment)
7. [Success Criteria](#success-criteria)
8. [Maintenance Plan](#maintenance-plan)

---

## Executive Summary

The SAV-BOT Meuble de France is a customer service chatbot that handles shopping assistance and after-sales service (SAV) for a French furniture company. While the core functionality is complete, the application requires significant hardening before production deployment.

### Key Gaps Identified

| Category | Current State | Target State |
|----------|---------------|--------------|
| Authentication | None | JWT + API Keys |
| Database | SQLite (dev) | PostgreSQL |
| Session Storage | In-memory dict | Redis |
| Containerization | None | Docker + Compose |
| CI/CD | None | GitHub Actions |
| Testing | Minimal | 80%+ coverage |
| Security | Basic | OWASP compliant |
| Monitoring | Logs only | Full observability |

---

## Current State Assessment

### Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React Frontend │────▶│  FastAPI Backend │────▶│   OpenAI API    │
│   (Port 5173)   │     │   (Port 8000)   │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                        ┌──────┴──────┐
                        │             │
                   ┌────▼────┐  ┌─────▼─────┐
                   │ SQLite  │  │ JSON Files│
                   │   DB    │  │ (catalog) │
                   └─────────┘  └───────────┘
```

### Strengths
- Well-structured service layer architecture
- Comprehensive business logic (SAV workflow, priority scoring, tone analysis)
- Good documentation in French and English
- Proper separation of concerns
- Async FastAPI implementation

### Weaknesses
- No authentication/authorization
- In-memory session storage (not scalable)
- SQLite database (not production-grade)
- No containerization
- No CI/CD pipeline
- Minimal automated testing
- Debug mode enabled by default
- No rate limiting
- Swagger/docs exposed

---

## Production Requirements

### Functional Requirements
- [ ] All existing features must continue working
- [ ] API response times < 2 seconds (excluding AI processing)
- [ ] Support 100+ concurrent users
- [ ] 99.9% uptime target

### Non-Functional Requirements
- [ ] HTTPS/TLS encryption
- [ ] Authentication for all endpoints
- [ ] Rate limiting (100 requests/minute/user)
- [ ] Automated backups
- [ ] Log retention (90 days)
- [ ] GDPR compliance for EU users

### Security Requirements
- [ ] OWASP Top 10 compliance
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] Secure file upload handling

---

## Implementation Phases

### Phase 1: Security Hardening (Priority: CRITICAL)

**Objective:** Secure all endpoints and protect user data

#### 1.1 Authentication System
- [ ] Implement JWT authentication
- [ ] Add refresh token mechanism
- [ ] Create user model and database table
- [ ] Add login/logout endpoints
- [ ] Implement password hashing (bcrypt)
- [ ] Add API key authentication for service-to-service calls

**Files to modify/create:**
- `backend/app/core/security.py` (new)
- `backend/app/models/user.py` (new)
- `backend/app/api/endpoints/auth.py` (new)
- `backend/app/api/deps.py` (new)
- `backend/app/main.py` (modify)

#### 1.2 Rate Limiting
- [ ] Install slowapi package
- [ ] Configure rate limits per endpoint
- [ ] Add rate limit headers to responses
- [ ] Implement IP-based and user-based limiting

**Files to modify/create:**
- `backend/app/core/rate_limit.py` (new)
- `backend/app/main.py` (modify)
- `backend/requirements.txt` (modify)

#### 1.3 Input Validation
- [ ] Add Pydantic validators to all request models
- [ ] Sanitize string inputs
- [ ] Validate file uploads (magic bytes check)
- [ ] Add request size limits

**Files to modify:**
- `backend/app/api/endpoints/chat.py`
- `backend/app/api/endpoints/upload.py`
- `backend/app/api/endpoints/sav.py`

#### 1.4 Security Headers & CORS
- [ ] Add security middleware (helmet-like)
- [ ] Restrict CORS to production domains
- [ ] Add Content-Security-Policy headers
- [ ] Disable debug mode in production

**Files to modify/create:**
- `backend/app/core/middleware.py` (new)
- `backend/app/main.py` (modify)
- `backend/app/core/config.py` (modify)

---

### Phase 2: Database & Storage (Priority: HIGH)

**Objective:** Implement production-grade data persistence

#### 2.1 PostgreSQL Migration
- [ ] Create database schema migrations
- [ ] Set up Alembic for migrations
- [ ] Migrate from SQLite to PostgreSQL
- [ ] Add connection pooling
- [ ] Implement database health checks

**Files to create/modify:**
- `backend/alembic/` (new directory)
- `backend/alembic.ini` (new)
- `backend/app/db/` (new directory)
- `backend/app/db/base.py` (new)
- `backend/app/db/session.py` (new)
- `backend/app/models/` (modify existing)

#### 2.2 Redis Session Storage
- [ ] Install redis package
- [ ] Create Redis connection manager
- [ ] Migrate session storage from dict to Redis
- [ ] Implement session expiration (24 hours)
- [ ] Add session cleanup job

**Files to create/modify:**
- `backend/app/core/redis.py` (new)
- `backend/app/services/session_manager.py` (new)
- `backend/app/api/endpoints/chat.py` (modify)
- `backend/requirements.txt` (modify)

#### 2.3 File Storage
- [ ] Implement cloud storage option (S3-compatible)
- [ ] Add file cleanup for old uploads
- [ ] Implement virus scanning integration point
- [ ] Add file metadata tracking in database

**Files to create/modify:**
- `backend/app/services/storage.py` (new)
- `backend/app/api/endpoints/upload.py` (modify)

---

### Phase 3: Containerization & Infrastructure (Priority: HIGH)

**Objective:** Containerize application for consistent deployments

#### 3.1 Docker Setup
- [ ] Create backend Dockerfile
- [ ] Create frontend Dockerfile
- [ ] Create docker-compose.yml for local development
- [ ] Create docker-compose.prod.yml for production
- [ ] Add .dockerignore files

**Files to create:**
- `backend/Dockerfile` (new)
- `frontend/Dockerfile` (new)
- `docker-compose.yml` (new)
- `docker-compose.prod.yml` (new)
- `backend/.dockerignore` (new)
- `frontend/.dockerignore` (new)

#### 3.2 Environment Configuration
- [ ] Create environment-specific config files
- [ ] Implement secrets management
- [ ] Add environment validation at startup
- [ ] Document all environment variables

**Files to create/modify:**
- `.env.example` (new)
- `.env.development` (new template)
- `.env.production` (new template)
- `backend/app/core/config.py` (modify)

#### 3.3 Nginx Reverse Proxy
- [ ] Create Nginx configuration
- [ ] Set up SSL/TLS termination
- [ ] Configure static file serving
- [ ] Add gzip compression
- [ ] Set up request buffering

**Files to create:**
- `nginx/nginx.conf` (new)
- `nginx/ssl/` (new directory for certs)

---

### Phase 4: CI/CD Pipeline (Priority: MEDIUM)

**Objective:** Automate testing and deployment

#### 4.1 GitHub Actions Workflows
- [ ] Create lint and format check workflow
- [ ] Create test workflow (backend)
- [ ] Create test workflow (frontend)
- [ ] Create build workflow
- [ ] Create deployment workflow

**Files to create:**
- `.github/workflows/lint.yml` (new)
- `.github/workflows/test-backend.yml` (new)
- `.github/workflows/test-frontend.yml` (new)
- `.github/workflows/build.yml` (new)
- `.github/workflows/deploy.yml` (new)

#### 4.2 Code Quality Tools
- [ ] Add ruff for Python linting
- [ ] Add black for Python formatting
- [ ] Add ESLint for JavaScript
- [ ] Add Prettier for JS/CSS formatting
- [ ] Create pre-commit hooks

**Files to create/modify:**
- `backend/pyproject.toml` (new)
- `frontend/.eslintrc.js` (new)
- `frontend/.prettierrc` (new)
- `.pre-commit-config.yaml` (new)

---

### Phase 5: Testing (Priority: MEDIUM)

**Objective:** Achieve 80%+ test coverage

#### 5.1 Backend Unit Tests
- [ ] Test chatbot service
- [ ] Test SAV workflow engine
- [ ] Test problem detector
- [ ] Test priority scorer
- [ ] Test tone analyzer
- [ ] Test warranty service
- [ ] Test evidence collector

**Files to create:**
- `backend/tests/` (new directory)
- `backend/tests/conftest.py` (new)
- `backend/tests/test_chatbot.py` (new)
- `backend/tests/test_sav_workflow.py` (new)
- `backend/tests/test_problem_detector.py` (new)
- `backend/tests/test_priority_scorer.py` (new)
- `backend/tests/test_tone_analyzer.py` (new)
- `backend/tests/test_warranty.py` (new)

#### 5.2 Backend Integration Tests
- [ ] Test chat endpoint
- [ ] Test upload endpoint
- [ ] Test SAV endpoints
- [ ] Test product endpoints
- [ ] Test authentication flow

**Files to create:**
- `backend/tests/api/` (new directory)
- `backend/tests/api/test_chat.py` (new)
- `backend/tests/api/test_upload.py` (new)
- `backend/tests/api/test_sav.py` (new)
- `backend/tests/api/test_auth.py` (new)

#### 5.3 Frontend Tests
- [ ] Set up Vitest
- [ ] Test ChatInterface component
- [ ] Test Dashboard component
- [ ] Test API integration

**Files to create:**
- `frontend/src/__tests__/` (new directory)
- `frontend/vitest.config.js` (new)

---

### Phase 6: Monitoring & Observability (Priority: MEDIUM)

**Objective:** Implement comprehensive monitoring

#### 6.1 Health Checks
- [ ] Add /health endpoint
- [ ] Add /ready endpoint
- [ ] Check database connectivity
- [ ] Check Redis connectivity
- [ ] Check OpenAI API status

**Files to create/modify:**
- `backend/app/api/endpoints/health.py` (new)
- `backend/app/main.py` (modify)

#### 6.2 Logging Improvements
- [ ] Implement structured JSON logging
- [ ] Add request ID tracking
- [ ] Add log rotation
- [ ] Configure log levels per environment
- [ ] Add performance logging

**Files to modify:**
- `backend/app/core/logging.py`
- `backend/app/main.py`

#### 6.3 Metrics & Alerting
- [ ] Add Prometheus metrics endpoint
- [ ] Track request latency
- [ ] Track error rates
- [ ] Track AI API usage
- [ ] Create Grafana dashboard template

**Files to create:**
- `backend/app/core/metrics.py` (new)
- `monitoring/grafana/` (new directory)
- `monitoring/prometheus/` (new directory)

---

### Phase 7: Documentation & Cleanup (Priority: LOW)

**Objective:** Finalize documentation and clean up codebase

#### 7.1 API Documentation
- [ ] Add OpenAPI descriptions to all endpoints
- [ ] Document request/response schemas
- [ ] Add example requests/responses
- [ ] Create Postman collection

**Files to modify:**
- All endpoint files in `backend/app/api/endpoints/`

#### 7.2 Deployment Documentation
- [ ] Create deployment guide
- [ ] Document environment variables
- [ ] Create troubleshooting guide
- [ ] Document backup procedures

**Files to create:**
- `docs/DEPLOYMENT.md` (new)
- `docs/ENVIRONMENT.md` (new)
- `docs/TROUBLESHOOTING.md` (new)
- `docs/BACKUP.md` (new)

#### 7.3 Code Cleanup
- [ ] Remove unused imports
- [ ] Remove debug print statements
- [ ] Standardize error messages
- [ ] Add type hints throughout

---

## Detailed Task Breakdown

### Phase 1 Tasks (Security)

| Task ID | Task | Priority | Complexity | Dependencies |
|---------|------|----------|------------|--------------|
| 1.1.1 | Create security.py with JWT functions | Critical | Medium | None |
| 1.1.2 | Create User model | Critical | Low | 1.1.1 |
| 1.1.3 | Create auth endpoints | Critical | Medium | 1.1.1, 1.1.2 |
| 1.1.4 | Add auth middleware | Critical | Medium | 1.1.3 |
| 1.1.5 | Protect existing endpoints | Critical | Low | 1.1.4 |
| 1.2.1 | Install and configure slowapi | High | Low | None |
| 1.2.2 | Add rate limits to endpoints | High | Low | 1.2.1 |
| 1.3.1 | Add Pydantic validators | High | Medium | None |
| 1.3.2 | Add file validation | High | Medium | None |
| 1.4.1 | Create security middleware | High | Low | None |
| 1.4.2 | Configure production CORS | High | Low | None |

### Phase 2 Tasks (Database)

| Task ID | Task | Priority | Complexity | Dependencies |
|---------|------|----------|------------|--------------|
| 2.1.1 | Set up Alembic | High | Medium | None |
| 2.1.2 | Create initial migration | High | Medium | 2.1.1 |
| 2.1.3 | Add connection pooling | High | Low | 2.1.2 |
| 2.2.1 | Create Redis connection | High | Low | None |
| 2.2.2 | Create session manager | High | Medium | 2.2.1 |
| 2.2.3 | Migrate chat sessions | High | Medium | 2.2.2 |
| 2.3.1 | Create storage abstraction | Medium | Medium | None |
| 2.3.2 | Add file cleanup job | Medium | Low | 2.3.1 |

### Phase 3 Tasks (Infrastructure)

| Task ID | Task | Priority | Complexity | Dependencies |
|---------|------|----------|------------|--------------|
| 3.1.1 | Create backend Dockerfile | High | Low | None |
| 3.1.2 | Create frontend Dockerfile | High | Low | None |
| 3.1.3 | Create docker-compose.yml | High | Medium | 3.1.1, 3.1.2 |
| 3.2.1 | Create .env.example | High | Low | None |
| 3.2.2 | Add env validation | Medium | Low | 3.2.1 |
| 3.3.1 | Create Nginx config | Medium | Medium | 3.1.3 |

### Phase 4 Tasks (CI/CD)

| Task ID | Task | Priority | Complexity | Dependencies |
|---------|------|----------|------------|--------------|
| 4.1.1 | Create lint workflow | Medium | Low | None |
| 4.1.2 | Create test workflow | Medium | Medium | Phase 5 |
| 4.1.3 | Create build workflow | Medium | Low | 4.1.1 |
| 4.1.4 | Create deploy workflow | Medium | High | 4.1.3 |
| 4.2.1 | Configure ruff/black | Low | Low | None |
| 4.2.2 | Configure ESLint/Prettier | Low | Low | None |

### Phase 5 Tasks (Testing)

| Task ID | Task | Priority | Complexity | Dependencies |
|---------|------|----------|------------|--------------|
| 5.1.1 | Create test fixtures | Medium | Medium | None |
| 5.1.2 | Test chatbot service | Medium | High | 5.1.1 |
| 5.1.3 | Test SAV services | Medium | High | 5.1.1 |
| 5.2.1 | Test API endpoints | Medium | Medium | 5.1.1 |
| 5.3.1 | Set up Vitest | Low | Low | None |
| 5.3.2 | Test React components | Low | Medium | 5.3.1 |

### Phase 6 Tasks (Monitoring)

| Task ID | Task | Priority | Complexity | Dependencies |
|---------|------|----------|------------|--------------|
| 6.1.1 | Create health endpoints | Medium | Low | None |
| 6.2.1 | Add structured logging | Medium | Medium | None |
| 6.2.2 | Add log rotation | Low | Low | 6.2.1 |
| 6.3.1 | Add Prometheus metrics | Low | Medium | None |

---

## Risk Assessment

### High Risk Items

| Risk | Impact | Mitigation |
|------|--------|------------|
| Data loss during migration | Critical | Backup before migration, test in staging |
| Authentication bypass | Critical | Security audit, penetration testing |
| Performance degradation | High | Load testing before production |
| API key exposure | Critical | Use secrets management, rotate keys |

### Medium Risk Items

| Risk | Impact | Mitigation |
|------|--------|------------|
| Redis connection failures | Medium | Implement fallback, connection retry |
| Database connection pool exhaustion | Medium | Monitor connections, tune pool size |
| Rate limit too restrictive | Medium | Monitor usage, adjust limits |

### Low Risk Items

| Risk | Impact | Mitigation |
|------|--------|------------|
| Log storage full | Low | Implement rotation, monitoring |
| Test flakiness | Low | Isolate tests, use fixtures |

---

## Success Criteria

### Phase 1 Complete When:
- [ ] All endpoints require authentication
- [ ] Rate limiting active and tested
- [ ] Security headers present in responses
- [ ] No sensitive data in logs

### Phase 2 Complete When:
- [ ] PostgreSQL running with all data migrated
- [ ] Redis storing sessions correctly
- [ ] Sessions persist across server restarts
- [ ] Connection pooling verified under load

### Phase 3 Complete When:
- [ ] Application runs in Docker containers
- [ ] docker-compose up starts all services
- [ ] Environment variables properly separated
- [ ] SSL/TLS working with Nginx

### Phase 4 Complete When:
- [ ] All workflows pass on PR
- [ ] Automatic deployment working
- [ ] Code formatting enforced

### Phase 5 Complete When:
- [ ] 80%+ backend test coverage
- [ ] All critical paths tested
- [ ] Tests run in CI pipeline

### Phase 6 Complete When:
- [ ] Health endpoints return correct status
- [ ] Logs are structured JSON
- [ ] Metrics available in Prometheus format

---

## Maintenance Plan

### Regular Tasks

| Task | Frequency | Responsible |
|------|-----------|-------------|
| Dependency updates | Weekly | DevOps |
| Security patches | As needed | DevOps |
| Database backups | Daily | Automated |
| Log rotation | Daily | Automated |
| Performance review | Monthly | Dev Team |
| Security audit | Quarterly | Security Team |

### Monitoring Checklist

- [ ] API response times < 2s
- [ ] Error rate < 1%
- [ ] Database connections < 80% pool
- [ ] Redis memory < 80%
- [ ] Disk usage < 80%
- [ ] CPU usage < 70% average

### Incident Response

1. **P1 (Critical):** Site down, data breach
   - Response: Immediate
   - Escalation: All hands

2. **P2 (High):** Major feature broken
   - Response: < 1 hour
   - Escalation: On-call + Team lead

3. **P3 (Medium):** Minor feature issue
   - Response: < 4 hours
   - Escalation: On-call

4. **P4 (Low):** Cosmetic issues
   - Response: Next business day
   - Escalation: Backlog

---

## Appendix: File Structure After Implementation

```
SAV-BOT-Meuble-de-france/
├── .github/
│   └── workflows/
│       ├── lint.yml
│       ├── test-backend.yml
│       ├── test-frontend.yml
│       ├── build.yml
│       └── deploy.yml
├── backend/
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py (new)
│   │   │   └── endpoints/
│   │   │       ├── auth.py (new)
│   │   │       ├── health.py (new)
│   │   │       └── ... (existing)
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   ├── security.py (new)
│   │   │   ├── middleware.py (new)
│   │   │   ├── rate_limit.py (new)
│   │   │   ├── redis.py (new)
│   │   │   └── metrics.py (new)
│   │   ├── db/
│   │   │   ├── base.py (new)
│   │   │   └── session.py (new)
│   │   ├── models/
│   │   │   ├── user.py (new)
│   │   │   └── ... (existing)
│   │   ├── services/
│   │   │   ├── session_manager.py (new)
│   │   │   ├── storage.py (new)
│   │   │   └── ... (existing)
│   │   └── main.py
│   ├── tests/
│   │   ├── api/
│   │   ├── services/
│   │   └── conftest.py
│   ├── Dockerfile (new)
│   ├── alembic.ini (new)
│   ├── pyproject.toml (new)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── __tests__/ (new)
│   │   └── ... (existing)
│   ├── Dockerfile (new)
│   ├── vitest.config.js (new)
│   └── ... (existing)
├── nginx/
│   ├── nginx.conf (new)
│   └── ssl/ (new)
├── monitoring/
│   ├── grafana/ (new)
│   └── prometheus/ (new)
├── docs/
│   ├── DEPLOYMENT.md (new)
│   ├── ENVIRONMENT.md (new)
│   ├── TROUBLESHOOTING.md (new)
│   └── ... (existing)
├── docker-compose.yml (new)
├── docker-compose.prod.yml (new)
├── .env.example (new)
├── .pre-commit-config.yaml (new)
├── projectplan.md (this file)
└── ... (existing files)
```

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-08 | Claude | Initial plan created |

---

**Next Steps:** Review this plan and confirm which phase to begin implementing first.
