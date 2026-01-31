# 🛋️ Meuble de France - Complete API Reference

**Last Updated:** January 31, 2026  
**Version:** 2.0  
**Base URL:** `http://localhost:8000` (dev) | `https://api.meuble-de-france.com` (prod)

---

## 📋 Table of Contents

1. [Root & Health](#root--health)
2. [Authentication](#authentication)
3. [Chat](#chat)
4. [Upload](#upload)
5. [Products](#products)
6. [Tickets](#tickets)
7. [FAQ](#faq)
8. [SAV (Service After Sale)](#sav-service-after-sale)
9. [Voice](#voice)
10. [Realtime](#realtime)

---

## Root & Health

### GET `/`

**Description:** Root endpoint with basic app info  
**Authentication:** None  
**Rate Limit:** No limit

**Response (200 OK):**

```json
{
  "app": "Meuble de France",
  "version": "2.0",
  "status": "running",
  "docs": "/docs"
}
```

---

### GET `/health`

**Description:** Basic health check for load balancers  
**Authentication:** None  
**Rate Limit:** No limit

**Response (200 OK):**

```json
{
  "status": "healthy",
  "app": "Meuble de France",
  "version": "2.0",
  "uptime_seconds": 3600.25,
  "memory_mb": 256.5,
  "memory_status": "ok",
  "cpu_percent": 15.2,
  "threads": 8
}
```

---

### GET `/ready`

**Description:** Comprehensive readiness check with dependency status  
**Authentication:** None  
**Rate Limit:** No limit

**Response (200 OK):**

```json
{
  "status": "ready",
  "checks": {
    "database": {
      "healthy": true,
      "response_time_ms": 12.5,
      "error": null
    },
    "cache": {
      "healthy": true,
      "type": "redis",
      "response_time_ms": 5.2,
      "error": null
    },
    "openai": {
      "healthy": true,
      "response_time_ms": 450.0,
      "error": null
    },
    "circuit_breakers": {
      "all_healthy": true
    }
  }
}
```

---

## Authentication

### POST `/api/auth/register`

**Description:** Register a new user account  
**Authentication:** None  
**Rate Limit:** 5 requests/minute

**Request Body:**

```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "password": "SecurePass123!"
}
```

**Response (201 Created):**

```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "user",
  "status": "active",
  "created_at": "2026-01-31T10:00:00Z",
  "updated_at": "2026-01-31T10:00:00Z"
}
```

**Error Responses:**

- `400 Bad Request` - Email already registered
- `400 Bad Request` - Username already taken

---

### POST `/api/auth/login`

**Description:** Login user with email/username and password  
**Authentication:** None  
**Rate Limit:** 10 requests/minute

**Request Body (form-data):**

```
username: user@example.com or johndoe
password: SecurePass123!
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Error Responses:**

- `401 Unauthorized` - Incorrect username or password
- `403 Forbidden` - Account locked (too many failed attempts)
- `403 Forbidden` - Account is inactive

---

### POST `/api/auth/refresh`

**Description:** Refresh access token using a valid refresh token  
**Authentication:** None  
**Rate Limit:** 10 requests/minute

**Request Body:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Error Responses:**

- `401 Unauthorized` - Invalid or expired refresh token

---

### POST `/api/auth/logout`

**Description:** Logout current user and blacklist their access token  
**Authentication:** Required (Bearer token)  
**Rate Limit:** No specific limit

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "message": "Successfully logged out",
  "success": true
}
```

---

### GET `/api/auth/me`

**Description:** Get current authenticated user information  
**Authentication:** Required (Bearer token)  
**Rate Limit:** No specific limit

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "user",
  "status": "active",
  "created_at": "2026-01-31T10:00:00Z",
  "updated_at": "2026-01-31T10:00:00Z"
}
```

---

### PUT `/api/auth/me`

**Description:** Update current user information  
**Authentication:** Required (Bearer token)  
**Rate Limit:** No specific limit

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "full_name": "John Updated Doe",
  "email": "newemail@example.com"
}
```

**Response (200 OK):** Updated user object

---

## Chat

### POST `/api/chat/`

**Description:** Send a message to the chatbot  
**Authentication:** Optional (Bearer token improves session management)  
**Rate Limit:** 30 requests/minute

**Headers:**

```
Authorization: Bearer <access_token> (optional)
Content-Type: application/json
```

**Request Body:**

```json
{
  "message": "Mon canapé a un problème",
  "session_id": "session-123",
  "order_number": "CMD-2025-30301",
  "photos": ["https://example.com/photo1.jpg"],
  "language": "fr"
}
```

**Response (200 OK):**

```json
{
  "response": "Je comprends votre problème avec votre canapé. Pouvez-vous me donner plus de détails?",
  "language": "fr",
  "conversation_type": "sav",
  "session_id": "session-123",
  "requires_validation": false,
  "ticket_id": "SAV-MDF-00001",
  "should_close_session": false
}
```

**Error Responses:**

- `400 Bad Request` - Invalid session ID or order number format
- `500 Internal Server Error` - Server error

---

### DELETE `/api/chat/{session_id}`

**Description:** Clear a chat session  
**Authentication:** Optional (Bearer token to clear only user's own sessions)  
**Rate Limit:** Standard API write limit

**Headers:**

```
Authorization: Bearer <access_token> (optional)
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Session cleared"
}
```

**Error Responses:**

- `400 Bad Request` - Invalid session ID format
- `404 Not Found` - Session not found

---

## Upload

### POST `/api/upload/`

**Description:** Upload photos or videos for SAV claims  
**Authentication:** Optional (Bearer token recommended)  
**Rate Limit:** 10 requests/minute

**Headers:**

```
Authorization: Bearer <access_token> (optional)
Content-Type: multipart/form-data
```

**Request Body (form-data):**

```
files: [file1.jpg, file2.mp4, ...]
```

**Constraints:**

- Maximum 10 files per request
- Maximum 10 MB per file
- Allowed formats: jpg, jpeg, png, gif, bmp, mp4, mov, avi, webm

**Response (200 OK):**

```json
{
  "success": true,
  "files": [
    {
      "original_name": "photo1.jpg",
      "saved_name": "sav-uploads/abc123def456",
      "url": "https://cdn.example.com/sav-uploads/abc123def456.jpg",
      "size": 2048576,
      "type": "jpg",
      "storage": "cloudinary"
    }
  ],
  "count": 1
}
```

**Error Responses:**

- `400 Bad Request` - No files provided or too many files
- `400 Bad Request` - Unsupported file type
- `400 Bad Request` - File too large

---

### GET `/api/upload/health`

**Description:** Check upload service health  
**Authentication:** None  
**Rate Limit:** No limit

**Response (200 OK):**

```json
{
  "success": true,
  "storage": "cloudinary",
  "configured": true,
  "max_file_size_mb": 10,
  "max_files_per_request": 10,
  "allowed_extensions": ["jpg", "jpeg", "png", "gif", "mp4", "mov"]
}
```

---

## Products

### GET `/api/products/`

**Description:** List all products with optional filtering  
**Authentication:** None  
**Rate Limit:** No specific limit

**Query Parameters:**

- `category` (optional): Filter by category (salon, salle_a_manger, chambre, decoration)
- `search` (optional): Search by keywords
- `limit` (optional): Maximum results (default: 50)

**Request:**

```
GET /api/products/?category=salon&limit=20
```

**Response (200 OK):**

```json
{
  "success": true,
  "category": "salon",
  "products": [
    {
      "id": "SAL-CAP-001",
      "name": "Canapé Premium",
      "category": "salon",
      "price": 1299.99,
      "description": "Canapé confortable...",
      "stock": 5
    }
  ],
  "total": 42
}
```

---

### GET `/api/products/categories`

**Description:** List all available product categories  
**Authentication:** None  
**Rate Limit:** No specific limit

**Response (200 OK):**

```json
{
  "success": true,
  "categories": [
    {
      "id": "salon",
      "name": "Salon",
      "product_count": 42
    },
    {
      "id": "chambre",
      "name": "Chambre",
      "product_count": 38
    }
  ],
  "total": 4
}
```

---

### GET `/api/products/{product_id}`

**Description:** Get detailed information about a specific product  
**Authentication:** None  
**Rate Limit:** No specific limit

**Request:**

```
GET /api/products/SAL-CAP-001
```

**Response (200 OK):**

```json
{
  "success": true,
  "product": {
    "id": "SAL-CAP-001",
    "name": "Canapé Premium",
    "category": "salon",
    "price": 1299.99,
    "description": "Canapé confortable avec garantie 5 ans",
    "dimensions": "200cm x 90cm x 85cm",
    "weight_kg": 45,
    "colors": ["Gris", "Bleu", "Noir"],
    "materials": ["Tissu", "Bois massif"],
    "warranty_years": 5,
    "stock": 5,
    "images": ["url1", "url2"]
  }
}
```

**Error Responses:**

- `404 Not Found` - Product not found

---

### GET `/api/products/catalog/summary`

**Description:** Get a summary of the entire product catalog  
**Authentication:** None  
**Rate Limit:** No specific limit

**Response (200 OK):**

```json
{
  "success": true,
  "catalog_version": "2.1",
  "last_updated": "2026-01-31T10:00:00Z",
  "summary": "AI-friendly catalog summary for chatbot context",
  "total_products": 180
}
```

---

## Tickets

### POST `/api/tickets/`

**Description:** Create a new SAV ticket  
**Authentication:** None  
**Rate Limit:** Standard

**Request Body:**

```json
{
  "order_number": "CMD-2025-30301",
  "problem_description": "Le canapé a un ressort cassé",
  "priority": "P1",
  "photos": ["https://example.com/photo1.jpg"]
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "ticket": {
    "ticket_id": "SAV-MDF-00001",
    "order_number": "CMD-2025-30301",
    "problem_description": "Le canapé a un ressort cassé",
    "priority": "P1",
    "photos": ["https://example.com/photo1.jpg"],
    "status": "nouveau",
    "created_at": "2026-01-31T10:00:00Z"
  }
}
```

---

### GET `/api/tickets/`

**Description:** List all tickets with pagination  
**Authentication:** None  
**Rate Limit:** Standard

**Query Parameters:**

- `limit` (optional): Maximum results (default: 10)

**Response (200 OK):**

```json
{
  "success": true,
  "tickets": [
    {
      "ticket_id": "SAV-MDF-00001",
      "order_number": "CMD-2025-30301",
      "status": "nouveau",
      "priority": "P1",
      "created_at": "2026-01-31T10:00:00Z"
    }
  ],
  "total": 127
}
```

---

### GET `/api/tickets/{ticket_id}`

**Description:** Get detailed information about a specific ticket  
**Authentication:** None  
**Rate Limit:** Standard

**Response (200 OK):**

```json
{
  "success": true,
  "ticket": {
    "ticket_id": "SAV-MDF-00001",
    "order_number": "CMD-2025-30301",
    "problem_description": "Le canapé a un ressort cassé",
    "priority": "P1",
    "status": "nouveau",
    "photos": ["https://example.com/photo1.jpg"],
    "created_at": "2026-01-31T10:00:00Z",
    "updated_at": "2026-01-31T10:30:00Z"
  }
}
```

**Error Responses:**

- `404 Not Found` - Ticket not found

---

## FAQ

### GET `/api/faq/`

**Description:** Search FAQ or get all questions  
**Authentication:** None  
**Rate Limit:** Standard

**Query Parameters:**

- `query` (optional): Search query
- `category` (optional): Filter by category ID

**Response (200 OK):**

```json
[
  {
    "id": "faq-001",
    "question": "Comment nettoyer mon canapé?",
    "answer": "Utilisez un chiffon humide avec de l'eau tiède...",
    "category": "Entretien",
    "category_icon": "🧹",
    "keywords": ["nettoyage", "canapé", "tissu"],
    "popularity": 150,
    "helpful_count": 120,
    "not_helpful_count": 5
  }
]
```

---

### GET `/api/faq/categories`

**Description:** Get all FAQ categories  
**Authentication:** None  
**Rate Limit:** Standard

**Response (200 OK):**

```json
[
  {
    "id": "entretien",
    "name": "Entretien",
    "icon": "🧹",
    "question_count": 25
  },
  {
    "id": "garantie",
    "name": "Garantie",
    "icon": "🛡️",
    "question_count": 18
  }
]
```

---

### GET `/api/faq/category/{category_id}`

**Description:** Get all FAQ questions for a specific category  
**Authentication:** None  
**Rate Limit:** Standard

**Response (200 OK):** Array of FAQ questions for the category

---

### POST `/api/faq/vote`

**Description:** Vote on FAQ question helpfulness  
**Authentication:** None  
**Rate Limit:** Standard

**Request Body:**

```json
{
  "question_id": "faq-001",
  "helpful": true
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Vote recorded",
  "question_id": "faq-001",
  "helpful": true
}
```

---

### POST `/api/faq/add`

**Description:** Add a new FAQ question (admin only in production)  
**Authentication:** None  
**Rate Limit:** Standard

**Request Body:**

```json
{
  "category_id": "entretien",
  "question": "Comment réparer une rayure?",
  "answer": "Les rayures mineures peuvent être...",
  "keywords": ["rayure", "réparation", "bois"]
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "message": "FAQ question added successfully",
  "category_id": "entretien"
}
```

---

### GET `/api/faq/stats`

**Description:** Get FAQ statistics  
**Authentication:** None  
**Rate Limit:** Standard

**Response (200 OK):**

```json
{
  "metadata": {
    "last_updated": "2026-01-31T10:00:00Z",
    "version": "2.1"
  },
  "statistics": {
    "total_questions": 120,
    "total_votes": 5400,
    "avg_helpfulness": 95.2
  },
  "total_categories": 8
}
```

---

## SAV (Service After Sale)

### POST `/api/sav/create-claim`

**Description:** Create a new SAV claim with automated workflow  
**Authentication:** None  
**Rate Limit:** Standard

**Request Body:**

```json
{
  "customer_id": "CUST-12345",
  "order_number": "CMD-2025-30301",
  "product_sku": "SAL-CAP-001",
  "product_name": "Canapé Premium",
  "problem_description": "Le canapé a un ressort cassé après 2 mois",
  "purchase_date": "2025-11-15T10:00:00Z",
  "delivery_date": "2025-11-20T10:00:00Z",
  "customer_tier": "premium",
  "product_value": 1299.99
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "ticket": {
    "ticket_id": "SAV-MDF-00001",
    "status": "en_attente_preuves",
    "priority": "P1",
    "priority_score": 95,
    "problem_category": "Defaut_structural",
    "problem_severity": "Haute",
    "problem_confidence": 0.92,
    "warranty_covered": true,
    "warranty_component": "Structural",
    "auto_resolved": false,
    "resolution_type": null,
    "sla_response_deadline": "2026-02-01T10:00:00Z",
    "sla_intervention_deadline": "2026-02-05T10:00:00Z",
    "created_at": "2026-01-31T10:00:00Z"
  },
  "evidence_requirements": "Pour accélérer le traitement, veuillez fournir: 1. Photos des dégâts...",
  "next_steps": ["Envoyer photos", "Fournir reçu de garantie"]
}
```

---

### POST `/api/sav/add-evidence`

**Description:** Add evidence (photos/videos) to a SAV ticket  
**Authentication:** None  
**Rate Limit:** Standard

**Request Body:**

```json
{
  "ticket_id": "SAV-MDF-00001",
  "evidence_type": "photo",
  "evidence_url": "https://cdn.example.com/evidence1.jpg",
  "file_size_bytes": 2048576,
  "description": "Photo du ressort cassé",
  "metadata": {
    "taken_at": "2026-01-31T09:00:00Z",
    "camera": "iPhone 13"
  }
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "evidence_analysis": {
    "quality": "good",
    "quality_score": 0.85,
    "issues": [],
    "strengths": ["Clear visibility", "Good lighting"],
    "recommendations": [],
    "verified": true
  },
  "completeness": {
    "is_complete": true,
    "completeness_score": 1.0,
    "missing_items": [],
    "additional_requests": [],
    "can_proceed": true
  },
  "ticket_status": "en_analyse",
  "evidence_count": 2
}
```

---

### GET `/api/sav/ticket/{ticket_id}`

**Description:** Get complete status of a SAV ticket  
**Authentication:** None  
**Rate Limit:** Standard

**Response (200 OK):**

```json
{
  "success": true,
  "ticket": {
    "ticket_id": "SAV-MDF-00001",
    "status": "en_analyse",
    "priority": "P1",
    "problem_category": "Defaut_structural",
    "warranty_covered": true,
    "completion_percentage": 65,
    "actions_count": 8,
    "evidence_count": 2,
    "next_milestone": "Analyse complète"
  }
}
```

---

### GET `/api/sav/ticket/{ticket_id}/history`

**Description:** Get complete history of all actions on a ticket  
**Authentication:** None  
**Rate Limit:** Standard

**Response (200 OK):**

```json
{
  "success": true,
  "ticket_id": "SAV-MDF-00001",
  "actions": [
    {
      "action_id": "ACT-001",
      "timestamp": "2026-01-31T10:00:00Z",
      "actor": "system",
      "action_type": "ticket_created",
      "description": "SAV ticket created",
      "metadata": {}
    },
    {
      "action_id": "ACT-002",
      "timestamp": "2026-01-31T10:05:00Z",
      "actor": "customer",
      "action_type": "evidence_added",
      "description": "Customer added photo evidence",
      "metadata": { "evidence_type": "photo" }
    }
  ]
}
```

---

### GET `/api/sav/evidence-requirements/{problem_category}`

**Description:** Get evidence requirements for a problem category  
**Authentication:** None  
**Rate Limit:** Standard

**Query Parameters:**

- `priority` (optional): Priority level (P1, P2, P3) - default: P2

**Response (200 OK):**

```json
{
  "category": "Defaut_structural",
  "requirements": "Pour ce type de défaut, nous recommandons: 1. Au moins 3 photos...",
  "required_evidence": [
    {
      "type": "photo",
      "minimum_count": 3,
      "description": "Dégâts visibles"
    }
  ]
}
```

---

## Voice

### POST `/api/voice/transcribe`

**Description:** Transcribe audio file to text using Whisper  
**Authentication:** None  
**Rate Limit:** Standard

**Headers:**

```
Content-Type: multipart/form-data
```

**Request Body (form-data):**

```
audio_file: <audio file (mp3, wav, webm, m4a, etc.)>
```

**Response (200 OK):**

```json
{
  "text": "Mon canapé a un problème, le ressort est cassé",
  "language": "fr",
  "duration": 4.5
}
```

**Error Responses:**

- `400 Bad Request` - No file provided
- `503 Service Unavailable` - Whisper service temporarily unavailable

---

### POST `/api/voice/chat`

**Description:** Send a message with conversation history to voice chatbot  
**Authentication:** Optional  
**Rate Limit:** 30 requests/minute

**Request Body:**

```json
{
  "message": "Mon canapé a un problème, le ressort est cassé",
  "conversation_history": [
    { "role": "assistant", "content": "Bonjour! Comment puis-je vous aider?" },
    { "role": "user", "content": "J'ai un problème avec mon canapé" }
  ],
  "session_id": "voice-session-123",
  "photos": ["https://example.com/photo1.jpg"]
}
```

**Response (200 OK):**

```json
{
  "response": "Je comprends. Pouvez-vous me donner le numéro de commande? Cela m'aidera à vérifier la garantie.",
  "session_id": "voice-session-123",
  "action": null,
  "ticket_data": null,
  "emotion_analysis": {
    "detected_emotion": "frustrated",
    "confidence": 0.85
  }
}
```

---

### POST `/api/voice/generate-speech`

**Description:** Generate speech from text using TTS  
**Authentication:** None  
**Rate Limit:** Standard

**Request Body:**

```json
{
  "text": "Votre réclamation a été créée avec succès",
  "language": "fr",
  "voice": "nova"
}
```

**Response (200 OK):**

```
Audio file stream (audio/mpeg)
```

**Headers in Response:**

```
Content-Type: audio/mpeg
Content-Length: 12345
```

---

## Realtime

### POST `/api/realtime/token`

**Description:** Get OpenAI Realtime API token (secure proxy)  
**Authentication:** None  
**Rate Limit:** Standard

**Response (200 OK):**

```json
{
  "token": "sk-proj-xxxxxxxxxxxxxxxxxxxxx"
}
```

**Error Responses:**

- `500 Internal Server Error` - API key not configured

---

### GET `/api/realtime/health`

**Description:** Check Realtime API service health  
**Authentication:** None  
**Rate Limit:** No limit

**Response (200 OK):**

```json
{
  "status": "ok",
  "realtime_configured": true,
  "message": "Service Realtime API prêt"
}
```

---

## Response Status Codes

| Code | Meaning                                        |
| ---- | ---------------------------------------------- |
| 200  | OK - Request successful                        |
| 201  | Created - Resource created                     |
| 400  | Bad Request - Invalid input                    |
| 401  | Unauthorized - Authentication required         |
| 403  | Forbidden - Access denied                      |
| 404  | Not Found - Resource not found                 |
| 409  | Conflict - Resource conflict                   |
| 429  | Too Many Requests - Rate limit exceeded        |
| 500  | Internal Server Error - Server error           |
| 503  | Service Unavailable - Temporary unavailability |

---

## Rate Limiting

**Current Limits:**

- Chat messages: 30/minute
- Auth (login/refresh): 10/minute
- Auth (register): 5/minute
- File upload: 10/minute
- Standard API operations: 60/minute

**Rate Limit Headers:**

```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 28
X-RateLimit-Reset: 1643641200
```

When rate limited, you'll receive:

```
HTTP 429 Too Many Requests
Retry-After: 60
```

---

## Authentication

All protected endpoints require:

```
Authorization: Bearer <access_token>
```

Token expires in 30 minutes. Use the `/api/auth/refresh` endpoint to get a new token.

---

## Error Response Format

```json
{
  "detail": "Error message here",
  "status_code": 400
}
```

---

## Testing the API

### Using cURL

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "SecurePass123!"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=SecurePass123!"

# Chat (with token)
curl -X POST http://localhost:8000/api/chat/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Bonjour",
    "session_id": "test-session"
  }'
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
response = requests.post(f"{BASE_URL}/api/auth/register", json={
    "email": "test@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "SecurePass123!"
})
print(response.json())

# Login
response = requests.post(f"{BASE_URL}/api/auth/login", data={
    "username": "testuser",
    "password": "SecurePass123!"
})
token = response.json()["access_token"]

# Chat
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(f"{BASE_URL}/api/chat/",
    headers=headers,
    json={"message": "Bonjour", "session_id": "test"}
)
print(response.json())
```

---

## Documentation

- **Swagger UI:** `/docs` (development only)
- **ReDoc:** `/redoc` (development only)
- **OpenAPI Schema:** `/openapi.json` (development only)

---

**Last Updated:** January 31, 2026
