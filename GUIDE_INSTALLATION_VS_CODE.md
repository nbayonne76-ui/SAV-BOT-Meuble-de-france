# 🎯 GUIDE COMPLET - INSTALLATION MEUBLE DE FRANCE CHATBOT

## ✅ BIENVENUE!

Ce guide vous permet d'installer le chatbot Meuble de France en quelques minutes.

---

## 📂 STRUCTURE DU PROJET

```
meuble-de-france-chatbot/
├── backend/
│   ├── app/
│   │   ├── __init__.py ✅
│   │   ├── main.py ✅
│   │   ├── core/
│   │   │   ├── __init__.py ✅
│   │   │   ├── config.py ✅
│   │   │   └── logging.py ✅
│   │   ├── services/
│   │   │   ├── __init__.py ✅
│   │   │   └── chatbot.py ✅
│   │   └── api/
│   │       ├── __init__.py ✅
│   │       └── endpoints/
│   │           ├── __init__.py ✅
│   │           ├── chat.py ✅
│   │           ├── upload.py ✅
│   │           ├── products.py ✅
│   │           └── tickets.py ✅
│   ├── .env ✅
│   └── requirements.txt ✅
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatInterface.jsx ✅
│   │   ├── App.jsx ✅
│   │   ├── main.jsx ✅
│   │   └── index.css ✅
│   ├── .env ✅
│   ├── package.json ✅
│   ├── vite.config.js ✅
│   ├── tailwind.config.js ✅
│   ├── postcss.config.js ✅
│   └── index.html ✅
│
├── uploads/
│   ├── photos/
│   └── videos/
│
├── MEUBLE_DE_FRANCE_CAHIER_CHARGES.md ✅
└── README.md ✅
```

---

## 🚀 INSTALLATION RAPIDE

### **Prérequis:**
- ✅ Python 3.11+ installé
- ✅ Node.js 18+ installé
- ✅ Clé API Anthropic (Claude)
- ✅ VS Code installé
- ✅ Git installé (optionnel)

---

## ÉTAPE 1: BACKEND - Installation

### 1.1 Créer l'environnement virtuel

Ouvrez un terminal dans VS Code et tapez:

```bash
cd backend
python -m venv venv
```

### 1.2 Activer l'environnement

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 1.3 Installer les dépendances

```bash
pip install -r requirements.txt
```

### 1.4 Configurer les variables d'environnement

Éditez le fichier `backend/.env` et remplacez `VOTRE_CLE_API` par votre vraie clé Anthropic:

```env
ANTHROPIC_API_KEY=sk-ant-api03-VOTRE_VRAIE_CLE_ICI
```

### 1.5 Démarrer le backend

```bash
python -m app.main
```

✅ **Le backend devrait démarrer sur http://localhost:8000**

Testez en ouvrant: http://localhost:8000/docs

---

## ÉTAPE 2: FRONTEND - Installation

### 2.1 Ouvrir un nouveau terminal

Dans VS Code, ouvrez un nouveau terminal (le backend doit rester actif).

### 2.2 Installer les dépendances

```bash
cd frontend
npm install
```

### 2.3 Démarrer le frontend

```bash
npm run dev
```

✅ **Le frontend devrait démarrer sur http://localhost:5173**

Le navigateur devrait s'ouvrir automatiquement.

---

## 🧪 TESTER L'APPLICATION

### Test 1: Conversation Shopping
```
Vous: "Bonjour, je cherche un canapé"
Bot: [Répond et pose des questions sur vos besoins]
```

### Test 2: Demande SAV
```
Vous: "J'ai un problème avec ma commande"
Bot: [Demande votre numéro de commande]
```

### Test 3: Multilingue
```
Vous: "Hello, I'm looking for a sofa"
Bot: [Répond en anglais]
```

### Test 4: Upload Photo
1. Cliquez sur l'icône appareil photo
2. Sélectionnez une image
3. Le bot devrait confirmer l'upload

---

## ✅ VÉRIFICATION FINALE

### Backend ✓
- [ ] http://localhost:8000 fonctionne
- [ ] http://localhost:8000/docs affiche Swagger
- [ ] http://localhost:8000/health retourne OK

### Frontend ✓
- [ ] http://localhost:5173 affiche l'interface
- [ ] Message d'accueil visible
- [ ] Input de texte fonctionnel
- [ ] Bouton photo visible

### Fonctionnalités ✓
- [ ] Le bot répond aux messages
- [ ] Détection de langue fonctionne
- [ ] Upload photo fonctionne
- [ ] Pas d'erreurs dans la console

---

## 🎨 PERSONNALISATION

### Changer le nom de la marque

Éditez `frontend/src/components/ChatInterface.jsx`:

```jsx
// Ligne ~50
<h1 className="text-2xl font-bold">Meuble de France</h1>
```

### Changer les couleurs

Éditez `frontend/src/components/ChatInterface.jsx`:

```jsx
// Ligne ~48 - Header
className="bg-gradient-to-r from-amber-600 to-amber-800"

// Ligne ~120 - Messages utilisateur
className="bg-amber-600 text-white"
```

### Ajouter des produits

Éditez `backend/app/services/chatbot.py` pour ajouter votre catalogue produits.

---

## 🐛 RÉSOLUTION PROBLÈMES

### Erreur: "Module not found"
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Erreur: "API key invalid"
Vérifiez que votre clé API Anthropic est correcte dans `backend/.env`

### Erreur: "Port already in use"
```bash
# Trouver et arrêter le processus
# Windows
netstat -ano | findstr :8000
taskkill /PID [PID_NUMBER] /F

# Mac/Linux
lsof -i :8000
kill -9 [PID]
```

### Le bot ne répond pas
1. Vérifiez que le backend est démarré
2. Vérifiez la console du navigateur (F12)
3. Vérifiez les logs: `backend/logs/app.log`

---

## 📚 DOCUMENTATION COMPLÈTE

- [Cahier des charges](./MEUBLE_DE_FRANCE_CAHIER_CHARGES.md)
- [Documentation API](http://localhost:8000/docs)
- [Guide développeur](./DEVELOPER_GUIDE.md)

---

## 🚀 DÉPLOIEMENT PRODUCTION

Pour déployer en production, consultez le guide de déploiement.

Options recommandées:
- **Backend:** Heroku, AWS, Azure, DigitalOcean
- **Frontend:** Vercel, Netlify, AWS S3
- **Database:** PostgreSQL (remplace SQLite)

---

## 📞 SUPPORT

En cas de problème:
1. Consultez les logs: `backend/logs/app.log`
2. Vérifiez la documentation API
3. Contactez Nicolas Bayonne

---

## 🎉 FÉLICITATIONS!

Votre chatbot Meuble de France est prêt!

**Prochaines étapes:**
1. ✅ Personnaliser les couleurs/branding
2. ✅ Ajouter votre catalogue produits
3. ✅ Configurer les intégrations CRM/ERP
4. ✅ Tester avec de vrais clients
5. 🚀 Déployer en production!

---

**Bon développement! 💪**

*Document créé le 2025-12-03*
