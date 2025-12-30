# 🚀 Guide de Déploiement Railway - Meuble de France Chatbot

Ce guide vous accompagne pour déployer votre chatbot SAV sur Railway en moins de 30 minutes.

## ✅ Prérequis

- Compte GitHub (votre code doit être sur GitHub)
- Compte Railway.app (gratuit)
- Clé API OpenAI valide

## 📋 Plan de Déploiement

Vous allez déployer **3 services** sur Railway:
1. **PostgreSQL** - Base de données
2. **Redis** - Cache
3. **Backend + Frontend** - Application complète (monorepo)

---

## 🎯 Étape 1: Préparer votre Repository GitHub

### 1.1 Vérifier que votre code est sur GitHub

```bash
# Vérifier le remote
git remote -v

# Si pas encore de remote GitHub, créer un repo sur github.com puis:
git remote add origin https://github.com/VOTRE-USERNAME/meuble-de-france-chatbot.git
git push -u origin main
```

### 1.2 S'assurer que les fichiers sensibles sont ignorés

Vérifiez que `.env` est dans `.gitignore` et qu'aucune clé API n'est committée.

```bash
# Vérifier
cat .gitignore | grep .env

# Si .env n'est pas listé, l'ajouter
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
git push
```

---

## 🎯 Étape 2: Créer un Projet Railway

### 2.1 Inscription

1. Allez sur https://railway.app
2. Cliquez sur "Start a New Project"
3. Connectez-vous avec GitHub (recommandé)

### 2.2 Créer le Projet

1. Cliquez sur "+ New Project"
2. Choisissez "Deploy from GitHub repo"
3. Sélectionnez votre repository `meuble-de-france-chatbot`
4. Railway va détecter automatiquement votre `railway.json`

---

## 🎯 Étape 3: Configurer PostgreSQL

### 3.1 Ajouter PostgreSQL

1. Dans votre projet Railway, cliquez sur "+ New"
2. Sélectionnez "Database" → "Add PostgreSQL"
3. Railway va créer la base de données automatiquement

### 3.2 Noter les Informations de Connexion

Railway génère automatiquement une variable `DATABASE_URL`. Vous n'avez rien à faire, elle sera disponible pour votre backend.

---

## 🎯 Étape 4: Configurer Redis

### 4.1 Ajouter Redis

1. Dans votre projet Railway, cliquez sur "+ New"
2. Sélectionnez "Database" → "Add Redis"
3. Railway va créer Redis automatiquement

### 4.2 Variable d'Environnement

Railway génère automatiquement `REDIS_URL`.

---

## 🎯 Étape 5: Configurer le Backend

### 5.1 Accéder aux Variables d'Environnement

1. Cliquez sur votre service Backend dans Railway
2. Allez dans l'onglet "Variables"

### 5.2 Ajouter les Variables Requises

Cliquez sur "+ New Variable" et ajoutez:

```bash
# OBLIGATOIRE - Votre clé OpenAI
OPENAI_API_KEY=sk-proj-VOTRE_CLE_ICI

# OBLIGATOIRE - Clé secrète (générer une nouvelle)
SECRET_KEY=GENERER_UNE_CLE_SECRETE_ICI

# Base de données (automatique depuis PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (automatique)
REDIS_URL=${{Redis.REDIS_URL}}

# Configuration App
DEBUG=False
APP_NAME=Meuble de France Chatbot
PORT=8000

# CORS - Sera mis à jour après déploiement
CORS_ORIGINS=*

# Sécurité
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_AUTH=5/minute

# Upload
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,heic,mp4,mov,avi,webm
```

### 5.3 Générer une SECRET_KEY

Pour générer une clé secrète sécurisée:

```bash
# Option 1: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: OpenSSL
openssl rand -base64 32

# Option 3: En ligne
# https://randomkeygen.com/ (Fort Knox Passwords)
```

Copiez le résultat et utilisez-le pour `SECRET_KEY`.

---

## 🎯 Étape 6: Configurer le Frontend

### 6.1 Variables d'Environnement Frontend

Dans le service Frontend, ajoutez:

```bash
# URL du backend (sera l'URL Railway de votre backend)
VITE_API_URL=${{Backend.RAILWAY_PUBLIC_DOMAIN}}
```

**Note**: Railway remplace automatiquement `${{Backend.RAILWAY_PUBLIC_DOMAIN}}` par l'URL publique de votre backend.

---

## 🎯 Étape 7: Déployer

### 7.1 Déclencher le Déploiement

Railway déploie automatiquement à chaque push sur votre branche principale.

Pour forcer un redéploiement:
1. Allez dans l'onglet "Deployments"
2. Cliquez sur "Deploy" ou "Redeploy"

### 7.2 Surveiller les Logs

1. Cliquez sur votre service Backend
2. Allez dans l'onglet "Logs"
3. Surveillez le déploiement en temps réel

**Signes de succès**:
```
✓ Building...
✓ Starting server...
✓ Application startup complete
```

---

## 🎯 Étape 8: Configurer le Domaine et CORS

### 8.1 Obtenir votre URL

Une fois déployé, Railway génère des URLs automatiques:
- Backend: `https://votre-backend.up.railway.app`
- Frontend: `https://votre-frontend.up.railway.app`

Trouvez-les dans l'onglet "Settings" → "Domains" de chaque service.

### 8.2 Mettre à jour CORS

1. Retournez dans les variables du Backend
2. Modifiez `CORS_ORIGINS`:

```bash
CORS_ORIGINS=https://votre-frontend.up.railway.app,https://votre-domaine-perso.com
```

3. Redéployez le backend

### 8.3 (Optionnel) Ajouter un Domaine Personnalisé

1. Dans "Settings" → "Domains" → "Custom Domain"
2. Ajoutez votre domaine (ex: `chatbot.monentreprise.com`)
3. Configurez le DNS selon les instructions Railway

---

## 🎯 Étape 9: Initialiser la Base de Données

### 9.1 Exécuter les Migrations

Dans Railway, accédez au terminal du Backend:

1. Cliquez sur Backend → Onglet "Settings"
2. Trouvez "Service" → "Command" ou utilisez le bouton "Shell" si disponible
3. Exécutez:

```bash
alembic upgrade head
```

**Alternative**: Vous pouvez exécuter les migrations automatiquement au démarrage.

Modifiez `backend/Dockerfile`, ligne 56:

```dockerfile
# Ajouter avant la commande uvicorn
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips "*"
```

---

## 🎯 Étape 10: Tester l'Application

### 10.1 Vérifier les Endpoints

```bash
# Health check backend
curl https://votre-backend.up.railway.app/health

# Documentation API
https://votre-backend.up.railway.app/docs

# Frontend
https://votre-frontend.up.railway.app
```

### 10.2 Tester le Chatbot

1. Ouvrez l'URL du frontend
2. Envoyez un message test
3. Vérifiez l'upload de photos
4. Testez la création de ticket

---

## 📊 Monitoring et Maintenance

### Voir les Logs

```
Railway Dashboard → Service → Logs
```

### Voir les Métriques

```
Railway Dashboard → Service → Metrics
```

### Redéployer

```bash
# Via Git
git push origin main

# Via Railway UI
Dashboard → Deployments → Redeploy
```

### Arrêter Temporairement

```
Service → Settings → Sleep Service
```

---

## 💰 Limites du Plan Gratuit Railway

- **500 heures/mois** de compute time
- **512 MB RAM** par service
- **1 GB** de stockage base de données
- **100 GB** de bandwidth

**Estimation**: Avec une utilisation modérée, le plan gratuit suffit largement pour commencer.

Pour augmenter les ressources: Railway Pro à $5/mois + pay-as-you-go.

---

## 🔧 Troubleshooting

### Erreur "Application failed to respond"

```bash
# Vérifier les logs
Railway → Service → Logs

# Causes communes:
# 1. Variable d'environnement manquante
# 2. Port incorrect (doit être PORT=8000)
# 3. Base de données non accessible
```

### Erreur CORS

```bash
# Vérifier CORS_ORIGINS dans les variables
# Doit inclure l'URL exacte du frontend
CORS_ORIGINS=https://exact-frontend-url.up.railway.app
```

### Build Failed

```bash
# Vérifier Dockerfile
# Railway utilise automatiquement le Dockerfile s'il existe
# Sinon, il utilise Nixpacks
```

### Database Connection Error

```bash
# Vérifier que DATABASE_URL est bien configurée
# Railway l'injecte automatiquement depuis PostgreSQL
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

---

## 🎉 Checklist Finale

- [ ] PostgreSQL déployé et connecté
- [ ] Redis déployé et connecté
- [ ] Backend déployé et répond sur `/health`
- [ ] Frontend déployé et accessible
- [ ] Variables d'environnement configurées
- [ ] CORS configuré avec la bonne URL
- [ ] Migrations de base de données exécutées
- [ ] Tests manuels réussis (chat, upload, tickets)
- [ ] Logs vérifiés (pas d'erreurs)

---

## 📞 Support

**Issues?**
- Logs Railway: Dashboard → Logs
- Documentation Railway: https://docs.railway.app
- Support Railway: Discord (https://discord.gg/railway)

**Questions sur l'app?**
- Voir `TROUBLESHOOTING.md`
- GitHub Issues

---

## 🔄 Prochaines Étapes

Une fois déployé avec succès:

1. **Surveiller les performances** (Railway Metrics)
2. **Configurer des alertes** (Railway Integrations)
3. **Sauvegardes base de données** (Scripts automatisés)
4. **Domaine personnalisé** (Settings → Domains)
5. **CI/CD amélioré** (GitHub Actions + Railway Webhooks)

---

**Déployé par**: Railway
**Date de création**: 2025-12-29
**Version**: 1.0.0
