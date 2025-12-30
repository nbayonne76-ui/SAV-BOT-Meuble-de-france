# 🛋️ Mobilier de France - SAV-BOT

Production-ready AI-powered chatbot for customer service and after-sales support.

## 📊 Status & Badges

[![CI/CD Pipeline](https://github.com/nbayonne76-ui/meuble-de-france-chatbot/actions/workflows/ci.yml/badge.svg)](https://github.com/nbayonne76-ui/meuble-de-france-chatbot/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/nbayonne76-ui/meuble-de-france-chatbot/branch/main/graph/badge.svg)](https://codecov.io/gh/nbayonne76-ui/meuble-de-france-chatbot)
[![Backend Coverage](https://img.shields.io/badge/backend%20coverage-62%25-yellow)](.)
[![Frontend Coverage](https://img.shields.io/badge/frontend%20coverage-53%25-yellow)](.)
[![Tests](https://img.shields.io/badge/tests-351%2B%20created-brightgreen)](.)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://hub.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![Node](https://img.shields.io/badge/node-20+-green)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB)](https://react.dev/)

## 🎯 Key Features

- 💬 **Natural Conversations:** Copilot-style intelligent dialogue
- 🌍 **Multilingual Support:** FR, EN, AR, IT, DE
- 🛋️ **Smart Product Recommendations:** AI-powered suggestions
- 📷 **Photo Upload & Analysis:** Visual defect detection
- 🎫 **Automated Ticketing:** Smart priority scoring (P0-P3)
- 🔒 **Production-Ready Security:** JWT auth, rate limiting, CORS
- 🐳 **Containerized:** Full Docker deployment
- 🧪 **Comprehensive Testing:** 351+ tests, CI/CD pipeline
- 📊 **Monitoring:** Health checks, metrics, and logging
- 🎙️ **Voice Support:** Speech recognition & synthesis

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/meuble-de-france-chatbot.git
cd meuble-de-france-chatbot

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access:
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## 📚 Documentation

### Getting Started
- [📖 Deployment Guide](./docs/DEPLOYMENT.md) - Complete deployment instructions
- [⚙️ Environment Variables](./docs/ENVIRONMENT.md) - All configuration options
- [🔧 Troubleshooting](./docs/TROUBLESHOOTING.md) - Common issues and solutions
- [📋 Project Plan](./projectplan.md) - Production readiness roadmap

### Business Documentation
- [📄 Specifications (FR)](./MEUBLE_DE_FRANCE_CAHIER_CHARGES.md) - Full requirements
- [🚀 Quick Start (FR)](./DEMARRAGE_RAPIDE.md) - Fast setup guide
- [💼 Installation Guide](./GUIDE_INSTALLATION_VS_CODE.md) - VS Code setup

### API Documentation
- **Development:** http://localhost:8000/docs (Swagger)
- **Alternative:** http://localhost:8000/redoc (ReDoc)

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React Frontend│────▶│  FastAPI Backend│────▶│   OpenAI API    │
│   (Port 5173)   │     │   (Port 8000)   │     │    (GPT-4)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                        ┌──────┴──────┐
                        │             │
                   ┌────▼────┐  ┌─────▼─────┐
                   │PostgreSQL│  │   Redis   │
                   │   DB     │  │  Cache    │
                   └──────────┘  └───────────┘
```

## 🛠️ Technology Stack

### Backend
- **Framework:** FastAPI 0.115+
- **Language:** Python 3.11+
- **AI:** OpenAI GPT-4
- **Database:** PostgreSQL 16 / SQLite (dev)
- **Cache:** Redis 7
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Auth:** JWT (python-jose)
- **Testing:** Pytest, pytest-asyncio

### Frontend
- **Framework:** React 18
- **Build Tool:** Vite 5
- **Styling:** TailwindCSS 3
- **Icons:** Lucide React
- **HTTP Client:** Fetch API
- **Testing:** Vitest, React Testing Library

### DevOps
- **Containerization:** Docker, Docker Compose
- **Reverse Proxy:** Nginx
- **CI/CD:** GitHub Actions
- **Code Quality:** Ruff, Black, ESLint, Prettier
- **Pre-commit:** Git hooks

## 🧪 Testing & CI/CD

### Test Suite Overview

**351+ tests** across backend and frontend with **~60% average coverage**

| Component | Tests | Coverage | Status |
|-----------|-------|----------|--------|
| Backend Services | 245 | 62% | ✅ |
| Backend APIs | 77 | ~70% | ✅ |
| Frontend Components | 89 | 53% | 🟡 |
| E2E Playwright | 30+ | N/A | ✅ |

### Running Tests Locally

```bash
# Backend tests
cd backend
pytest                           # Run all tests
pytest --cov=app                 # With coverage
pytest --cov-report=html         # HTML coverage report
pytest -v tests/api/             # API tests only
pytest -k "test_chatbot"         # Specific test pattern

# Frontend tests
cd frontend
npm test                         # Run in watch mode
npm test -- --run                # Run once
npm run test:ui                  # Interactive UI
npm run test:coverage            # With coverage report

# E2E tests (requires backend + frontend running)
cd frontend
npm run test:e2e                 # Run all E2E tests
npm run test:e2e:ui              # Interactive mode
npm run test:e2e:debug           # Debug mode
npm run test:e2e:report          # View last report
```

### CI/CD Pipeline

**Automated on every push and pull request:**

1. **Backend Tests** - Pytest with coverage upload to Codecov
2. **Frontend Tests** - Vitest with coverage upload to Codecov
3. **E2E Tests** - Playwright tests with video/screenshot capture
4. **Code Quality** - ESLint, Prettier, Ruff, Black
5. **Security Scan** - Trivy vulnerability scanning
6. **Docker Build** - Multi-stage builds for production

**GitHub Actions Workflow:** [.github/workflows/ci.yml](.github/workflows/ci.yml)

**View CI/CD Status:** [Actions Tab](https://github.com/nbayonne76-ui/meuble-de-france-chatbot/actions)

## 🔒 Security Features

- ✅ JWT Authentication with refresh tokens
- ✅ Password hashing (bcrypt)
- ✅ Rate limiting (slowapi)
- ✅ CORS protection
- ✅ Security headers (X-Frame-Options, CSP, etc.)
- ✅ Input validation (Pydantic)
- ✅ SQL injection prevention (SQLAlchemy)
- ✅ File upload validation (magic bytes)
- ✅ Environment variable validation
- ✅ Secrets management

## 📊 Project Status

### ✅ Completed Phases

- **Phase 1:** Security Hardening (JWT, rate limiting, validation)
- **Phase 2:** Database & Storage (PostgreSQL, Redis, file storage)
- **Phase 3:** Containerization (Docker, Nginx, environment config)
- **Phase 4:** Testing & CI/CD (351+ tests, 60% coverage, GitHub Actions)
  - ✅ Backend unit tests (245 tests, 62% coverage)
  - ✅ Backend API tests (77 tests)
  - ✅ Frontend tests (89 tests, 53% coverage)
  - ✅ E2E Playwright tests (30+ scenarios)
  - ✅ CI/CD pipeline with Codecov integration
- **Phase 5:** Health Checks & Monitoring
- **Phase 6:** Documentation (Deployment, environment, troubleshooting)

### 🔄 In Progress

- Improving test coverage to 70%+
- Enhanced JSON logging
- Prometheus metrics
- OpenAPI documentation improvements

See [projectplan.md](./projectplan.md) for detailed roadmap.

## 🚢 Deployment

### Production Deployment

```bash
# Configure production environment
cp .env.production .env
# Edit with production values

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose exec backend alembic upgrade head

# Check health
curl https://yourdomain.com/health
```

See [DEPLOYMENT.md](./docs/DEPLOYMENT.md) for complete production deployment guide.

## 📈 Performance

- **Response Time:** < 2s (excluding AI processing)
- **Concurrent Users:** 100+ supported
- **Rate Limits:** 100 req/min (configurable)
- **Uptime Target:** 99.9%

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support & Contact

**Project Lead:** Nicolas Bayonne
**Email:** nicolas.bayonne@contact.fr
**Role:** Digital Transformation & AI Consultant

### Getting Help

- 📖 Check [Documentation](./docs/)
- 🐛 [Open an Issue](https://github.com/yourusername/meuble-de-france-chatbot/issues)
- 💬 Email support

## 📄 License

This project is proprietary software. All rights reserved.

Copyright © 2025 Mobilier de France

---

⭐ **Version:** 1.0.0
📅 **Last Updated:** 2025-12-09
🏗️ **Status:** Production Ready
