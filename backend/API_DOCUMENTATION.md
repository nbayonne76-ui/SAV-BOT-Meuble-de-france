# 🛋️ Meuble de France - API Documentation

## Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Authentification](#authentification)
3. [Endpoints Principaux](#endpoints-principaux)
4. [Monitoring et Santé](#monitoring-et-santé)
5. [Gestion des Erreurs](#gestion-des-erreurs)
6. [Limites et Rate Limiting](#limites-et-rate-limiting)
7. [Exemples d'Utilisation](#exemples-dutilisation)

---

## Vue d'ensemble

L'API Meuble de France est une API REST complète pour le chatbot intelligent de service client et SAV.

### URLs de Base

- **Développement**: `http://localhost:8000`
- **Production**: `https://api.meuble-de-france.com`

### Documentation Interactive

- **Swagger UI**: `/docs` (disponible en mode développement uniquement)
- **ReDoc**: `/redoc` (disponible en mode développement uniquement)
- **OpenAPI Schema**: `/openapi.json` (disponible en mode développement uniquement)

### Formats de Données

- **Request**: JSON (`application/json`)
- **Response**: JSON (`application/json`)
- **Charset**: UTF-8

---

## Authentification

L'API supporte deux méthodes d'authentification:

### 1. JWT Tokens (Utilisateurs)

#### Login

```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Réponse:**
```json
{
  "success": true,
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Utilisation du Token

```bash
GET /api/chat/history
Authorization: Bearer eyJhbGci...
```

#### Refresh Token

```bash
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGci..."
}
```

### 2. API Keys (Applications)

#### Création d'une API Key

```bash
POST /api/auth/api-keys
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Application Mobile",
  "expires_in_days": 365
}
```

**Réponse:**
```json
{
  "success": true,
  "api_key": "mdf_live_abc123...",
  "key_id": "api_key_123",
  "name": "Application Mobile",
  "expires_at": "2025-01-09T12:00:00Z"
}
```

#### Utilisation de l'API Key

```bash
GET /api/products
X-API-Key: mdf_live_abc123...
```

---

## Endpoints Principaux

### Chat

#### Envoyer un message

```bash
POST /api/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Bonjour, j'ai un problème avec mon canapé",
  "language": "fr",
  "session_id": "session_123"
}
```

**Réponse:**
```json
{
  "success": true,
  "response": "Bonjour ! Je suis désolé d'apprendre que vous rencontrez un problème...",
  "language": "fr",
  "session_id": "session_123",
  "intent": "support_request",
  "confidence": 0.95
}
```

#### Historique de conversation

```bash
GET /api/chat/history?limit=20&offset=0
Authorization: Bearer <token>
```

### Upload de Fichiers

#### Upload d'image ou vidéo

```bash
POST /api/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary_data>
description: "Photo du défaut sur le canapé"
```

**Réponse:**
```json
{
  "success": true,
  "file_url": "https://cloudinary.com/.../image.jpg",
  "file_id": "upload_123",
  "file_type": "image/jpeg",
  "size_bytes": 245760
}
```

### Tickets SAV

#### Créer un ticket

```bash
POST /api/tickets
Authorization: Bearer <token>
Content-Type: application/json

{
  "customer_id": "CUST123",
  "product_sku": "CANAPÉ-OSLO-3P",
  "problem_category": "défaut_fabrication",
  "problem_severity": "moyen",
  "description": "Déchirure sur l'accoudoir gauche",
  "attachments": ["upload_123"]
}
```

**Réponse:**
```json
{
  "success": true,
  "ticket": {
    "ticket_id": "TKT-2025-001234",
    "status": "open",
    "priority": "medium",
    "created_at": "2025-01-09T10:30:00Z",
    "sla_response_deadline": "2025-01-10T10:30:00Z"
  }
}
```

#### Consulter un ticket

```bash
GET /api/tickets/TKT-2025-001234
Authorization: Bearer <token>
```

### Produits

#### Rechercher des produits

```bash
GET /api/products?query=canapé&category=salon&limit=10
Authorization: Bearer <token>
```

**Réponse:**
```json
{
  "success": true,
  "products": [
    {
      "sku": "CANAPÉ-OSLO-3P",
      "name": "Canapé Oslo 3 places",
      "category": "salon",
      "price": 1299.00,
      "in_stock": true,
      "images": ["https://..."]
    }
  ],
  "total": 15,
  "page": 1,
  "limit": 10
}
```

### Services Vocaux

#### Transcription audio (Whisper)

```bash
POST /api/voice/transcribe
Authorization: Bearer <token>
Content-Type: multipart/form-data

audio_file: <binary_audio_data>
language: fr
```

**Réponse:**
```json
{
  "success": true,
  "text": "Bonjour, j'ai un problème avec mon canapé",
  "language": "fr",
  "duration": 3.5
}
```

#### Synthèse vocale (TTS)

```bash
POST /api/voice/tts
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "Votre ticket a été créé avec succès",
  "language": "fr",
  "voice": "alloy"
}
```

**Réponse:** Audio file (audio/mpeg)

---

## Monitoring et Santé

### Health Check (Liveness)

Simple vérification que l'application fonctionne:

```bash
GET /health
```

**Réponse:**
```json
{
  "status": "healthy",
  "app": "Mobilier de France Chatbot",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "memory_mb": 245.67,
  "memory_status": "ok",
  "cpu_percent": 15.3,
  "threads": 12
}
```

### Readiness Check

Vérification complète des dépendances:

```bash
GET /ready
```

**Réponse:**
```json
{
  "ready": true,
  "critical_ready": true,
  "checks": {
    "database": {
      "healthy": true,
      "response_time_ms": 5.2
    },
    "cache": {
      "healthy": true,
      "type": "redis"
    },
    "openai_api": {
      "healthy": true,
      "breakers": {
        "openai": {"state": "closed", "success_rate": 99.5}
      }
    },
    "memory": {
      "healthy": true,
      "status": "ok",
      "rss_mb": 245.67
    }
  }
}
```

### Query Performance Stats

```bash
GET /query-stats
```

**Réponse:**
```json
{
  "performance_status": "good",
  "stats": {
    "total_queries": 1250,
    "slow_queries": 12,
    "slow_query_percentage": 0.96,
    "average_query_time_ms": 45.3,
    "threshold_ms": 1000
  },
  "timestamp": "2025-01-09T12:00:00Z"
}
```

### Memory Monitoring

```bash
GET /memory
```

**Réponse:**
```json
{
  "status": "ok",
  "alert_level": null,
  "messages": [],
  "usage": {
    "process": {
      "rss_mb": 245.67,
      "vms_mb": 512.34,
      "percent_of_system": 3.2
    },
    "system": {
      "total_mb": 8192.0,
      "available_mb": 4096.0,
      "used_percent": 50.0
    }
  }
}
```

### Circuit Breakers Status

```bash
GET /circuit-breakers
```

**Réponse:**
```json
{
  "healthy": true,
  "breakers": {
    "openai": {
      "state": "closed",
      "failure_count": 0,
      "success_rate": 99.8,
      "total_calls": 1500
    },
    "cloudinary": {
      "state": "closed",
      "failure_count": 0,
      "success_rate": 100.0,
      "total_calls": 250
    }
  },
  "summary": {
    "total": 5,
    "closed": 5,
    "open": 0,
    "half_open": 0
  }
}
```

### Environment Validation

```bash
GET /env-status
```

---

## Gestion des Erreurs

### Format d'Erreur Standard

```json
{
  "success": false,
  "error": "error_code",
  "detail": "Description détaillée de l'erreur",
  "request_id": "req_abc123"
}
```

### Codes d'Erreur HTTP

| Code | Signification | Description |
|------|---------------|-------------|
| 200 | OK | Requête réussie |
| 201 | Created | Ressource créée avec succès |
| 400 | Bad Request | Requête invalide (données manquantes/incorrectes) |
| 401 | Unauthorized | Authentification requise ou invalide |
| 403 | Forbidden | Accès refusé (permissions insuffisantes) |
| 404 | Not Found | Ressource introuvable |
| 413 | Payload Too Large | Requête trop volumineuse (> 5MB) |
| 429 | Too Many Requests | Rate limit dépassé |
| 500 | Internal Server Error | Erreur serveur |
| 503 | Service Unavailable | Service temporairement indisponible |
| 504 | Gateway Timeout | Timeout (> 30s) |

### Erreurs Spécifiques

#### Rate Limit Exceeded

```json
{
  "success": false,
  "error": "rate_limit_exceeded",
  "detail": "Too many requests. Please try again later.",
  "retry_after": 60
}
```

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
Retry-After: 60
```

#### Payload Too Large

```json
{
  "success": false,
  "error": "payload_too_large",
  "detail": "Request body exceeds maximum size of 5.0MB"
}
```

#### Request Timeout

```json
{
  "success": false,
  "error": "gateway_timeout",
  "detail": "Request exceeded maximum processing time of 30s"
}
```

---

## Limites et Rate Limiting

### Limites par Type d'Endpoint

| Endpoint | Rate Limit | Taille Max | Timeout |
|----------|-----------|------------|---------|
| `/api/auth/login` | 5/minute | 5MB | 30s |
| `/api/chat` | 100/minute | 5MB | 30s |
| `/api/upload` | 10/minute | 10MB | 60s |
| `/api/*` (autres) | 100/minute | 5MB | 30s |

### Headers de Rate Limit

Chaque réponse inclut des headers de rate limiting:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704801600
```

### Gestion du Rate Limiting

Lorsque vous atteignez la limite:

1. Attendez la période indiquée dans `Retry-After`
2. Vérifiez `X-RateLimit-Reset` pour le timestamp de réinitialisation
3. Implémentez un backoff exponentiel pour les retries

---

## Exemples d'Utilisation

### Workflow Complet: Création de Ticket SAV

#### 1. Authentification

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "password123"
  }'
```

#### 2. Upload d'une Photo du Problème

```bash
curl -X POST http://localhost:8000/api/upload \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@/path/to/photo.jpg" \
  -F "description=Photo du défaut"
```

#### 3. Création du Ticket

```bash
curl -X POST http://localhost:8000/api/tickets \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST123",
    "product_sku": "CANAPÉ-OSLO-3P",
    "problem_category": "défaut_fabrication",
    "problem_severity": "moyen",
    "description": "Déchirure sur l'accoudoir gauche",
    "attachments": ["upload_123"]
  }'
```

#### 4. Suivi du Ticket

```bash
curl -X GET http://localhost:8000/api/tickets/TKT-2025-001234 \
  -H "Authorization: Bearer <access_token>"
```

### Workflow: Conversation Vocale

#### 1. Upload Audio

```bash
curl -X POST http://localhost:8000/api/voice/transcribe \
  -H "Authorization: Bearer <access_token>" \
  -F "audio_file=@/path/to/audio.mp3" \
  -F "language=fr"
```

#### 2. Traitement du Message

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Bonjour, j'ai un problème avec mon canapé",
    "language": "fr",
    "session_id": "session_123"
  }'
```

#### 3. Synthèse Vocale de la Réponse

```bash
curl -X POST http://localhost:8000/api/voice/tts \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Votre ticket a été créé avec succès",
    "language": "fr",
    "voice": "alloy"
  }' \
  --output response.mp3
```

---

## Support et Contact

Pour toute question technique ou problème avec l'API:

- **Email**: support@meuble-de-france.com
- **Documentation**: `/docs` (mode développement)
- **Status Page**: `/health`, `/ready`

---

*Documentation générée automatiquement - Dernière mise à jour: 2025-01-09*
