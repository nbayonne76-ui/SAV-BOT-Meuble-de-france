# 📊 RAPPORT D'ANALYSE DE SCALABILITÉ - CHATBOT SAV MEUBLE DE FRANCE

**Date:** 6 Décembre 2025
**Version:** 1.0
**Objectif:** Évaluer la capacité du chatbot à gérer 200 demandes/mois aujourd'hui et 400+ demandes/mois dans 2-3 ans

---

## 🎯 RÉSUMÉ EXÉCUTIF

### Capacité Actuelle
- ✅ **Fonctionnel** pour 200 demandes/mois (~6-7 demandes/jour)
- ⚠️ **Limitations critiques** identifiées pour la montée en charge
- 🔴 **Refonte nécessaire** pour atteindre 400 demandes/mois de manière fiable

### Verdict Global
**Le système actuel peut gérer 200 demandes/mois MAIS nécessite des améliorations MAJEURES pour passer à 400 demandes/mois de manière robuste et maintenable.**

---

## 1️⃣ ANALYSE DE CAPACITÉ ACTUELLE

### Architecture Actuelle

```
┌─────────────────┐
│   Frontend      │  React + Vite (Port 5173)
│   (Vite)        │  - Interface chat conversationnelle
└────────┬────────┘  - Communication vocale bidirectionnelle
         │           - Upload photos/vidéos
         │
         ▼
┌─────────────────┐
│   Backend       │  FastAPI + Uvicorn (Port 8000)
│   (FastAPI)     │  - API REST
└────────┬────────┘  - Gestion sessions en mémoire (dict)
         │           - Workflow SAV automatisé
         │
         ├──────────► OpenAI GPT-4 (API externe)
         │
         └──────────► Stockage EN MÉMOIRE (⚠️ CRITIQUE)
                     - Tickets SAV: sav_workflow_engine.active_tickets
                     - Sessions chat: chatbot_instances
                     - Aucune persistance
```

### Métriques de Performance Estimées

#### Volume Actuel (200 demandes/mois)
- **6-7 demandes par jour** en moyenne
- **~1 demande toutes les 2-3 heures** (8h-20h)
- **Pics possibles:** 15-20 demandes/jour (soldes, promotions)

#### Charge Serveur par Demande
1. **Conversation initiale:** ~3-5 messages
2. **Validation ticket:** 2 messages
3. **Total:** ~5-7 messages par demande SAV complète

**Calcul de charge mensuelle:**
- 200 demandes × 6 messages = **1 200 messages OpenAI/mois**
- Temps moyen par message: 2-4 secondes
- Temps total conversation: 30-60 secondes par client

#### Coûts OpenAI Estimés (GPT-4)

**Prix GPT-4 (2025):**
- Input: $0.03 / 1K tokens
- Output: $0.06 / 1K tokens

**Estimation par conversation SAV:**
- Prompt système: ~800 tokens
- Message utilisateur moyen: ~100 tokens
- Réponse chatbot moyenne: ~300 tokens
- Total par échange: ~1 200 tokens

**Coût par demande SAV (6 messages):**
- Input: (800 + 100×6) × $0.03/1000 = $0.042
- Output: (300×6) × $0.06/1000 = $0.108
- **Total: ~$0.15 par demande SAV**

**Coût mensuel actuel (200 demandes):**
- 200 demandes × $0.15 = **$30/mois**

**Coût mensuel projeté (400 demandes):**
- 400 demandes × $0.15 = **$60/mois**

### ✅ Points Forts de l'Architecture Actuelle

1. **Interface Utilisateur Excellente**
   - Chat conversationnel intuitif
   - Communication vocale bidirectionnelle (Speech-to-Text + Text-to-Speech)
   - Upload de photos/vidéos pour preuves
   - Navigation fluide Chat ↔ Dashboard

2. **Workflow SAV Automatisé Intelligent**
   - Détection automatique du problème (8 catégories)
   - Analyse de priorité multi-facteurs (P0-P3)
   - Vérification automatique de garantie
   - Collecte de preuves guidée
   - Décision automatique (résolution vs escalade)

3. **Validation Client Robuste**
   - Récapitulatif avant création ticket
   - Confirmation "OUI" obligatoire
   - Option continuation/clôture après ticket

4. **Analyse Avancée**
   - Détection de ton et urgence (CALM, FRUSTRATED, ANGRY, CRITICAL)
   - Scoring de priorité basé sur multiples critères
   - Analyse de garantie automatique

### ⚠️ Capacité Maximale Actuelle

**Avec l'architecture EN MÉMOIRE actuelle:**

| Métrique | Valeur Estimée | Limite |
|----------|---------------|---------|
| Demandes simultanées | 5-10 | 20 max |
| Tickets stockés | 50-100 | 200 max |
| Sessions actives | 10-20 | 50 max |
| Uptime | 95% | Redémarrage = perte totale |

**Capacité mensuelle réaliste:** 150-250 demandes maximum

---

## 2️⃣ RISQUES ET LIMITATIONS CRITIQUES

### 🔴 CRITIQUE - Niveau 1 (Bloquants pour 400 demandes/mois)

#### 1. Stockage EN MÉMOIRE (RISQUE MAJEUR ⚠️⚠️⚠️)

**Problème:**
```python
# chat.py ligne 24
chatbot_instances = {}  # ❌ Dictionnaire en mémoire

# sav_workflow_engine.py
class SAVWorkflowEngine:
    def __init__(self):
        self.active_tickets = {}  # ❌ Dictionnaire en mémoire
```

**Conséquences:**
- ❌ **Redémarrage serveur = PERTE TOTALE** de tous les tickets
- ❌ **Crash Python = PERTE TOTALE** de toutes les conversations
- ❌ **Aucune traçabilité** après fermeture session
- ❌ **Impossible de générer des rapports** historiques
- ❌ **Pas de backup** automatique
- ❌ **Pas de reprise sur erreur**

**Impact à 400 demandes/mois:**
- 13-14 demandes/jour
- Risque de perte de 5-10 tickets lors d'un redémarrage
- Perte potentielle de données clients critiques

**Solution OBLIGATOIRE:** Migration vers base de données persistante (PostgreSQL/MySQL)

---

#### 2. Sessions Chatbot Non Persistantes

**Problème:**
```python
# Ligne 84-86 chat.py
if request.session_id not in chatbot_instances:
    chatbot_instances[request.session_id] = MeubledeFranceChatbot(api_key=api_key)
```

**Conséquences:**
- ❌ Client déconnecté = conversation perdue
- ❌ Refresh navigateur = session réinitialisée
- ❌ Load balancing impossible (session liée au serveur)
- ❌ Pas de reprise de conversation

**Solution:** Redis/Memcached pour sessions distribuées

---

#### 3. Absence de Gestion d'Erreurs Robuste

**Problèmes identifiés:**
- Pas de retry automatique sur échec OpenAI
- Pas de fallback si quota OpenAI épuisé
- Pas de file d'attente pour requêtes échouées
- Logging Unicode défaillant (erreurs emoji)

**Impact:** Perte de tickets SAV lors d'erreurs temporaires

---

#### 4. Coûts OpenAI Non Optimisés

**Problème:**
- Utilisation de GPT-4 pour TOUS les messages (même simples)
- Pas de cache pour réponses communes
- Aucune limitation de tokens

**Impact financier à 400 demandes/mois:**
- $60/mois avec GPT-4
- Potentiel $120-150/mois si conversations longues
- Pas de contrôle des coûts

**Solution:** Hybrid GPT-4 / GPT-3.5-turbo selon complexité

---

### 🟠 HAUTE PRIORITÉ - Niveau 2 (Limitations de performance)

#### 5. Architecture Monoserveur

**Problème:**
- Un seul processus FastAPI
- Pas de load balancing
- Pas de failover

**Capacité maximale:** 30-50 requêtes simultanées

**Impact à 400 demandes/mois:**
- Pics de trafic non gérés
- Temps de réponse dégradé
- Risque de timeout

---

#### 6. Aucune Mise en Cache

**Problème:**
- Données commandes récupérées à chaque fois
- Vérification garantie recalculée
- Catalogue produits non caché

**Impact:**
- 3-5 secondes par vérification
- Charge inutile sur services externes

---

#### 7. Sécurité et Authentification Basiques

**Problèmes:**
- Pas d'authentification utilisateur
- Pas de rate limiting
- Pas de protection CSRF
- Clé API stockée en clair dans .env

**Risques:**
- Abus du système
- Dépassement quota OpenAI par attaque
- Vol de données clients

---

### 🟡 MOYENNE PRIORITÉ - Niveau 3 (Améliorations qualité)

#### 8. Monitoring et Observabilité Limités

**Manques:**
- Pas de métriques temps réel
- Pas d'alertes automatiques
- Logs basiques (erreurs Unicode)
- Pas de dashboards performance

---

#### 9. Tests Automatisés Absents

**Problème:** Aucun test unitaire/intégration

**Risque:** Régressions lors des évolutions

---

#### 10. Gestion Photos/Vidéos Non Optimisée

**Problème:**
- Stockage local uniquement
- Pas de compression
- Pas de CDN

**Impact:** Saturation disque avec 400 demandes/mois

---

## 3️⃣ PLAN D'AMÉLIORATION TECHNIQUE DÉTAILLÉ

### Phase 1 - CRITIQUE (0-3 mois) - OBLIGATOIRE pour 400 demandes/mois

#### 🎯 Objectif: Rendre le système robuste et persistant

#### Action 1.1: Migration Base de Données PostgreSQL

**Implémentation:**

1. **Créer le schéma de base de données:**

```sql
-- Tickets SAV
CREATE TABLE tickets (
    ticket_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(100) NOT NULL,
    customer_name VARCHAR(200),
    order_number VARCHAR(50) NOT NULL,
    product_sku VARCHAR(100),
    product_name VARCHAR(200),
    problem_description TEXT NOT NULL,
    problem_category VARCHAR(50),
    priority VARCHAR(10),
    priority_score INTEGER,
    status VARCHAR(50),
    warranty_covered BOOLEAN,
    auto_resolved BOOLEAN,
    resolution_type VARCHAR(50),
    resolution_description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_order (order_number),
    INDEX idx_customer (customer_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
);

-- Historique des actions
CREATE TABLE ticket_actions (
    action_id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(50) REFERENCES tickets(ticket_id),
    timestamp TIMESTAMP DEFAULT NOW(),
    actor VARCHAR(100),
    action_type VARCHAR(50),
    description TEXT,
    metadata JSONB
);

-- Sessions chat
CREATE TABLE chat_sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    conversation_history JSONB,
    client_data JSONB,
    ticket_data JSONB,
    conversation_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- Preuves (photos/vidéos)
CREATE TABLE evidences (
    evidence_id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(50) REFERENCES tickets(ticket_id),
    evidence_type VARCHAR(20),
    file_url VARCHAR(500),
    file_size BIGINT,
    quality_score FLOAT,
    uploaded_at TIMESTAMP DEFAULT NOW()
);
```

2. **Modifier sav_workflow_engine.py:**

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

class SAVWorkflowEngine:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        # ❌ SUPPRIMER: self.active_tickets = {}

    async def process_new_claim(self, ...):
        # Créer ticket en base de données
        ticket_db = TicketDB(
            ticket_id=ticket_id,
            customer_id=customer_id,
            # ... autres champs
        )
        self.db.add(ticket_db)
        await self.db.commit()
        return ticket_db

    async def get_ticket(self, ticket_id: str):
        result = await self.db.execute(
            select(TicketDB).where(TicketDB.ticket_id == ticket_id)
        )
        return result.scalar_one_or_none()
```

3. **Ajouter SQLAlchemy models:**

```python
# backend/app/models/database.py
from sqlalchemy import Column, String, Integer, Boolean, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TicketDB(Base):
    __tablename__ = 'tickets'

    ticket_id = Column(String(50), primary_key=True)
    customer_id = Column(String(100), nullable=False)
    # ... autres colonnes
```

**Durée:** 2-3 semaines
**Priorité:** 🔴 CRITIQUE
**Coût:** Migration simple, pas de coût supplémentaire

---

#### Action 1.2: Implémenter Redis pour Sessions

**Implémentation:**

```python
# backend/app/services/session_manager.py
import redis.asyncio as redis
import json

class SessionManager:
    def __init__(self):
        self.redis = redis.from_url("redis://localhost:6379")

    async def save_session(self, session_id: str, chatbot_state: dict):
        await self.redis.setex(
            f"session:{session_id}",
            3600,  # 1 heure TTL
            json.dumps(chatbot_state)
        )

    async def load_session(self, session_id: str) -> dict:
        data = await self.redis.get(f"session:{session_id}")
        return json.loads(data) if data else None
```

**Modifier chat.py:**

```python
session_manager = SessionManager()

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Charger session depuis Redis
    session_data = await session_manager.load_session(request.session_id)

    if session_data:
        chatbot = MeubledeFranceChatbot.from_dict(session_data, api_key)
    else:
        chatbot = MeubledeFranceChatbot(api_key=api_key)

    result = await chatbot.chat(...)

    # Sauvegarder session dans Redis
    await session_manager.save_session(request.session_id, chatbot.to_dict())
```

**Durée:** 1 semaine
**Priorité:** 🔴 CRITIQUE
**Coût:** Redis gratuit (local) ou $10-20/mois (cloud)

---

#### Action 1.3: Gestion d'Erreurs et Retry Automatique

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class MeubledeFranceChatbot:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _call_openai(self, messages):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=1500  # Limite pour contrôler coûts
            )
            return response
        except openai.RateLimitError:
            logger.warning("Quota OpenAI dépassé, retry dans 10s...")
            raise
        except openai.APIError as e:
            logger.error(f"Erreur API OpenAI: {e}")
            # Fallback vers réponse générique
            return self._generate_fallback_response()
```

**Durée:** 3-4 jours
**Priorité:** 🔴 CRITIQUE

---

#### Action 1.4: Optimisation Coûts OpenAI

**Stratégie Hybrid GPT-4 / GPT-3.5:**

```python
def select_model(self, user_message: str, conversation_type: str) -> str:
    """Choisir le modèle selon la complexité"""

    # Messages simples → GPT-3.5 ($0.002/1K tokens)
    simple_patterns = [
        "oui", "non", "merci", "bonjour",
        "continuer", "clôturer"
    ]
    if any(p in user_message.lower() for p in simple_patterns):
        return "gpt-3.5-turbo"

    # Analyse SAV complexe → GPT-4
    if conversation_type == "sav" and self.pending_ticket_validation:
        return "gpt-4"

    # Par défaut → GPT-3.5
    return "gpt-3.5-turbo"
```

**Économie estimée:** 40-50% des coûts
**$60/mois → $30-35/mois** pour 400 demandes

---

### Phase 2 - HAUTE PRIORITÉ (3-6 mois) - Performance et Scale

#### Action 2.1: Load Balancing avec Nginx

```nginx
upstream fastapi_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;

    location /api/ {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
    }
}
```

**Déploiement:** 3 instances FastAPI
**Capacité:** 150 requêtes simultanées
**Durée:** 1 semaine

---

#### Action 2.2: Mise en Cache avec Redis

```python
from functools import lru_cache

class OrderDataService:
    @cache_with_ttl(ttl=300)  # 5 minutes
    async def fetch_order_data(self, order_number: str):
        # Vérifier cache Redis
        cached = await redis.get(f"order:{order_number}")
        if cached:
            return json.loads(cached)

        # Sinon, fetch depuis source
        data = await self._fetch_from_source(order_number)

        # Mettre en cache
        await redis.setex(
            f"order:{order_number}",
            300,
            json.dumps(data)
        )
        return data
```

**Gain:** Réduction de 70% des appels externes
**Durée:** 1 semaine

---

#### Action 2.3: Sécurité et Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/")
@limiter.limit("10/minute")  # Max 10 requêtes/minute par IP
async def chat(request: ChatRequest):
    # ... code existant
```

**Protection contre:**
- Abus du système
- Attaques DDoS
- Épuisement quota OpenAI

**Durée:** 3-4 jours

---

#### Action 2.4: Stockage Photos sur S3/Cloud

```python
import boto3

class FileStorage:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.bucket = 'meuble-de-france-sav'

    async def upload_evidence(self, file, ticket_id):
        # Compresser l'image
        compressed = await self.compress_image(file)

        # Upload vers S3
        key = f"evidences/{ticket_id}/{file.filename}"
        self.s3.upload_fileobj(compressed, self.bucket, key)

        # Retourner URL CDN
        return f"https://cdn.meuble-de-france.fr/{key}"
```

**Coût:** ~$5-10/mois pour 400 demandes
**Durée:** 1 semaine

---

### Phase 3 - MOYENNE PRIORITÉ (6-12 mois) - Monitoring et Tests

#### Action 3.1: Monitoring avec Prometheus + Grafana

```python
from prometheus_client import Counter, Histogram

chat_requests = Counter('chat_requests_total', 'Total chat requests')
chat_duration = Histogram('chat_duration_seconds', 'Chat processing time')

@router.post("/")
async def chat(request: ChatRequest):
    chat_requests.inc()

    with chat_duration.time():
        result = await chatbot.chat(...)

    return result
```

**Métriques surveillées:**
- Nombre de demandes/heure
- Temps de réponse moyen
- Taux d'erreur OpenAI
- Coûts OpenAI en temps réel

**Durée:** 1 semaine

---

#### Action 3.2: Tests Automatisés

```python
# tests/test_sav_workflow.py
import pytest

@pytest.mark.asyncio
async def test_ticket_creation():
    engine = SAVWorkflowEngine(db_session)

    ticket = await engine.process_new_claim(
        customer_id="test@example.com",
        order_number="CMD-2024-12345",
        problem_description="Pied cassé",
        # ...
    )

    assert ticket.ticket_id is not None
    assert ticket.priority in ["P0", "P1", "P2", "P3"]
```

**Couverture cible:** 80%
**Durée:** 2-3 semaines

---

## 4️⃣ STRATÉGIE D'ÉVOLUTIVITÉ 2-3 ANS

### Roadmap d'Évolution

```
ANNÉE 1 (2025-2026): Consolidation
├─ Q1: Phase 1 CRITIQUE (DB + Redis + Retry)
├─ Q2: Phase 2 PERFORMANCE (Load Balancing + Cache)
├─ Q3: Phase 3 MONITORING (Prometheus + Tests)
└─ Q4: Optimisation continue
        Capacité: 400-500 demandes/mois ✅

ANNÉE 2 (2026-2027): Expansion
├─ Q1: Multi-canal (SMS, Email, WhatsApp)
├─ Q2: IA prédictive (anticiper problèmes)
├─ Q3: Intégration CRM/ERP
└─ Q4: Analytics avancés
        Capacité: 800-1000 demandes/mois ✅

ANNÉE 3 (2027-2028): Intelligence
├─ Q1: ML pour détection automatique
├─ Q2: Recommandations personnalisées
├─ Q3: Self-service avancé
└─ Q4: Automatisation 90%+
        Capacité: 1500+ demandes/mois ✅
```

### Architecture Cible (2-3 ans)

```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    │    (Nginx)      │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │  FastAPI #1  │ │  FastAPI #2  │ │  FastAPI #3  │
    │   (8001)     │ │   (8002)     │ │   (8003)     │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           └────────────────┼────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │    Redis     │    │   OpenAI     │
│  (Primary)   │    │  (Sessions   │    │   GPT-4/3.5  │
│              │    │   + Cache)   │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
        │
        │ Réplication
        ▼
┌──────────────┐
│  PostgreSQL  │
│  (Replica)   │
│  (Read-only) │
└──────────────┘

        │
        ▼
┌──────────────┐
│  Prometheus  │───► Grafana (Dashboards)
│  (Metrics)   │
└──────────────┘
```

### Évolution des Canaux

**Phase 1 (Actuel):** Web uniquement

**Phase 2 (An 2):**
```python
class MultiChannelBot:
    async def handle_message(self, message, channel):
        if channel == "web":
            return await self.web_handler(message)
        elif channel == "sms":
            return await self.sms_handler(message)
        elif channel == "whatsapp":
            return await self.whatsapp_handler(message)
        elif channel == "email":
            return await self.email_handler(message)
```

**Canaux prévus:**
- ✅ Web (actuel)
- 📱 SMS (Twilio API)
- 💬 WhatsApp Business API
- 📧 Email (IMAP/SMTP)
- 📞 Téléphone (IVR avec Twilio)

---

## 5️⃣ RECOMMANDATIONS HAUTE DISPONIBILITÉ

### Objectif: 99.9% Uptime (8.76 heures downtime/an max)

#### 1. Infrastructure Redondante

**Configuration recommandée:**

```yaml
# docker-compose.yml
version: '3.8'

services:
  fastapi-1:
    image: meuble-sav-backend
    environment:
      - INSTANCE_ID=1
    depends_on:
      - postgres
      - redis

  fastapi-2:
    image: meuble-sav-backend
    environment:
      - INSTANCE_ID=2
    depends_on:
      - postgres
      - redis

  fastapi-3:
    image: meuble-sav-backend
    environment:
      - INSTANCE_ID=3
    depends_on:
      - postgres
      - redis

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - fastapi-1
      - fastapi-2
      - fastapi-3

  postgres:
    image: postgres:15
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: meuble_sav
      POSTGRES_USER: sav_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
```

---

#### 2. Backup Automatisé

```bash
# backup-script.sh
#!/bin/bash

# Backup PostgreSQL
pg_dump -h localhost -U sav_user meuble_sav | gzip > \
  backups/meuble_sav_$(date +%Y%m%d_%H%M%S).sql.gz

# Backup Redis
redis-cli --rdb backups/redis_$(date +%Y%m%d_%H%M%S).rdb

# Upload vers S3
aws s3 sync backups/ s3://meuble-backups/sav/

# Garder 30 jours de backups
find backups/ -mtime +30 -delete
```

**Fréquence:** Toutes les 6 heures
**Rétention:** 30 jours

---

#### 3. Health Checks et Auto-Recovery

```python
# backend/app/main.py

@app.get("/health")
async def health_check():
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "openai": await check_openai_quota()
    }

    all_healthy = all(checks.values())

    return JSONResponse(
        status_code=200 if all_healthy else 503,
        content={
            "status": "healthy" if all_healthy else "unhealthy",
            "checks": checks,
            "timestamp": datetime.now().isoformat()
        }
    )
```

**Monitoring externe:** UptimeRobot ou StatusCake
**Auto-restart:** Docker avec `restart: always`

---

#### 4. Alertes Automatiques

```python
# alerts.py
import smtplib

class AlertManager:
    def alert_critical(self, message):
        # Email
        self.send_email("admin@meuble-de-france.fr", message)

        # SMS (Twilio)
        self.send_sms("+33612345678", message)

        # Slack
        self.send_slack_notification(message)

    def trigger_conditions(self):
        if error_rate > 10%:
            self.alert_critical("Taux d'erreur élevé!")

        if response_time_avg > 5s:
            self.alert_critical("Temps de réponse dégradé!")

        if openai_quota < 10%:
            self.alert_critical("Quota OpenAI presque épuisé!")
```

---

#### 5. Plan de Reprise d'Activité (DRP)

**RTO (Recovery Time Objective):** 30 minutes
**RPO (Recovery Point Objective):** 6 heures

**Procédure de restauration:**

1. **Détecter la panne** (< 5 min)
   - Alertes automatiques
   - Health checks

2. **Analyser la cause** (< 10 min)
   - Vérifier logs Grafana
   - Identifier composant défaillant

3. **Restaurer le service** (< 15 min)
   - Redémarrer conteneurs Docker
   - Basculer sur instance de backup
   - Restaurer DB depuis backup si nécessaire

---

## 6️⃣ ESTIMATION BUDGÉTAIRE

### Coûts Mensuels Actuels (200 demandes/mois)

| Poste | Coût |
|-------|------|
| Serveur (1 instance) | $10-20 |
| OpenAI GPT-4 | $30 |
| **TOTAL** | **$40-50/mois** |

### Coûts Mensuels Projetés (400 demandes/mois) - Après Optimisations

| Poste | Coût |
|-------|------|
| Serveur (3 instances) | $30-50 |
| PostgreSQL (managed) | $20-30 |
| Redis (managed) | $10-20 |
| OpenAI Hybrid GPT-4/3.5 | $35-40 |
| S3 Stockage Photos | $5-10 |
| Monitoring (Grafana Cloud) | $15 |
| Backups | $5 |
| **TOTAL** | **$120-165/mois** |

### Coûts de Développement (Phase 1-3)

| Phase | Durée | Coût Estimé |
|-------|-------|-------------|
| Phase 1 - CRITIQUE | 3 mois | 40-60h dev |
| Phase 2 - PERFORMANCE | 3 mois | 30-40h dev |
| Phase 3 - MONITORING | 3 mois | 20-30h dev |
| **TOTAL** | **9 mois** | **90-130h dev** |

---

## 7️⃣ PLAN D'ACTION IMMÉDIAT (Next Steps)

### Priorité Immédiate (Semaine 1-2)

✅ **Étape 1:** Mettre en place PostgreSQL
- Créer schéma de base de données
- Migrer `sav_workflow_engine` vers DB
- Tester création/lecture tickets

✅ **Étape 2:** Implémenter Redis pour sessions
- Configurer Redis
- Adapter `chatbot_instances` vers Redis
- Tester persistance sessions

✅ **Étape 3:** Ajouter retry automatique OpenAI
- Implémenter `tenacity`
- Tester gestion d'erreurs

### Court Terme (Mois 1)

✅ **Étape 4:** Optimiser coûts OpenAI
- Implémenter hybrid GPT-4/3.5
- Limiter tokens par requête

✅ **Étape 5:** Backups automatisés
- Script backup PostgreSQL
- Cron job quotidien

### Moyen Terme (Mois 2-3)

✅ **Étape 6:** Load balancing
- Configurer Nginx
- Déployer 3 instances FastAPI

✅ **Étape 7:** Monitoring
- Prometheus + Grafana
- Alertes critiques

---

## 8️⃣ INDICATEURS DE SUCCÈS (KPIs)

### Métriques Techniques

| Métrique | Valeur Actuelle | Objectif 400 demandes/mois |
|----------|-----------------|----------------------------|
| **Uptime** | ~95% | 99.9% |
| **Temps réponse moyen** | 3-5s | < 2s |
| **Taux d'erreur** | ~5% | < 1% |
| **Sessions simultanées** | 5-10 | 50+ |
| **Tickets stockés** | 50-100 | Illimité (DB) |
| **Coût par demande** | $0.20 | $0.10 |

### Métriques Business

| Métrique | Objectif |
|----------|----------|
| **Taux de résolution automatique** | > 60% |
| **Satisfaction client** | > 85% |
| **Temps moyen de traitement** | < 48h |
| **Tickets escaladés** | < 30% |

---

## 📌 CONCLUSION

### Résumé des Actions Critiques

🔴 **URGENT - À faire IMMÉDIATEMENT:**
1. Migration PostgreSQL (tickets persistants)
2. Redis pour sessions
3. Retry automatique OpenAI

🟠 **IMPORTANT - 1-3 mois:**
4. Load balancing (3 instances)
5. Cache Redis pour données
6. Optimisation coûts OpenAI

🟡 **SOUHAITABLE - 3-6 mois:**
7. Monitoring Prometheus/Grafana
8. Tests automatisés
9. Stockage S3

### Verdict Final

**Le chatbot SAV Meuble de France peut gérer 400 demandes/mois SEULEMENT si les 3 actions critiques (PostgreSQL, Redis, Retry) sont implémentées dans les 2-3 prochains mois.**

**Sans ces améliorations, le système restera limité à 150-250 demandes/mois avec un risque élevé de perte de données.**

---

**Document généré le:** 6 Décembre 2025
**Validité:** 12 mois
**Prochaine révision:** Juin 2026
