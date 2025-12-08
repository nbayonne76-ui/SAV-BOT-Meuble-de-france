# 🚀 DÉMARRAGE RAPIDE - Meuble de France Chatbot

## ⚠️ PREMIÈRE FOIS: Installation Requise

**Si c'est la première fois**, double-cliquez d'abord sur: `INSTALLER.bat`

Ce script va:
1. ✅ Créer l'environnement virtuel Python (venv)
2. ✅ Installer les dépendances Python (FastAPI, OpenAI, etc.)
3. ✅ Installer les dépendances Node.js (React, Vite, etc.)

**⏱️ Durée: 2-5 minutes**

---

## 🎯 Démarrage (après installation)

**Double-cliquez sur:** `START_ALL.bat`

Ce script lance automatiquement:
1. ✅ Backend (FastAPI) sur port 8000
2. ✅ Frontend (React + Vite) sur port 5173
3. ✅ Ouvre 2 fenêtres de commande

**Attendez 15-30 secondes** que tout démarre, puis ouvrez:
- **Chatbot:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs

---

## ⚙️ Configuration Actuelle

| Service  | Port  | URL                          | Status |
|----------|-------|------------------------------|--------|
| Backend  | 8000  | http://localhost:8000        | ✅     |
| Frontend | 5173  | http://localhost:5173        | ✅     |
| CORS     | -     | Configuré pour 5173          | ✅     |
| OpenAI   | -     | API Key configurée           | ✅     |

---

## 🔧 MÉTHODE ALTERNATIVE: Démarrage Manuel

### Backend (Terminal 1):
```bash
cd backend
venv\Scripts\activate
python -m app.main
```

### Frontend (Terminal 2):
```bash
cd frontend
npm install  # Si première fois
npm run dev
```

---

## 🖥️ Si Première Installation

### Backend:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend:
```bash
cd frontend
npm install
```

Ensuite utilisez `START_ALL.bat`

---

## 🧪 ÉTAPE 4: Tester l'Application

### Test 1: Conversation Shopping
```
Vous: "Bonjour, je cherche un canapé pour mon salon"
Bot: [Pose des questions sur vos besoins]
Vous: "Un 3 places, style moderne, gris"
Bot: [Recommande des produits adaptés]
```

### Test 2: Service SAV
```
Vous: "J'ai un problème avec ma commande MDF-2025-12345"
Bot: [Demande des détails sur le problème]
```

### Test 3: Multilingue
```
Vous: "Hello, I'm looking for a sofa"
Bot: [Répond en anglais]
```

### Test 4: Upload Photo
1. Cliquez sur l'icône appareil photo 📷
2. Sélectionnez une image
3. Envoyez le message
4. Le bot devrait confirmer la réception

---

## ✅ VÉRIFICATIONS

### Backend ✓
- [ ] http://localhost:8000 → Affiche info API
- [ ] http://localhost:8000/docs → Documentation Swagger
- [ ] http://localhost:8000/health → Status "healthy"
- [ ] Aucune erreur dans le terminal

### Frontend ✓
- [ ] http://localhost:5173 → Interface chatbot
- [ ] Message d'accueil visible
- [ ] Input de texte fonctionnel
- [ ] Bouton photo visible
- [ ] Design orange/ambré (couleurs Meuble de France)

### Fonctionnalités ✓
- [ ] Le bot répond aux messages
- [ ] Détection de langue fonctionne
- [ ] Recommandations produits cohérentes
- [ ] Upload photo fonctionne
- [ ] Interface responsive (essayez de réduire la fenêtre)

---

## 🎨 PERSONNALISATION

### Changer les couleurs de la marque

Éditez `frontend/tailwind.config.js`:

```javascript
colors: {
  'brand': {
    500: '#VOTRE_COULEUR',  // Couleur principale
    600: '#VOTRE_COULEUR',  // Couleur foncée
  }
}
```

Puis dans `ChatInterface.jsx`, remplacez `amber` et `orange` par `brand`.

### Ajouter des produits

Éditez `backend/app/api/endpoints/products.py` pour ajouter vos produits.

### Modifier le message d'accueil

Éditez `frontend/src/components/ChatInterface.jsx` ligne ~20.

### Adapter le ton du chatbot

Éditez `backend/app/services/chatbot.py` dans la fonction `create_system_prompt()`.

---

## 📚 DOCUMENTATION COMPLÈTE

- **[Cahier des Charges](./MEUBLE_DE_FRANCE_CAHIER_CHARGES.md)** - Spécifications complètes
- **[Guide Installation](./GUIDE_INSTALLATION_VS_CODE.md)** - Installation détaillée
- **[README](./README.md)** - Vue d'ensemble du projet
- **[API Documentation](http://localhost:8000/docs)** - Documentation Swagger

---

## 🐛 PROBLÈMES COURANTS

### Erreur: "Module anthropic not found"
```bash
cd backend
pip install -r requirements.txt
```

### Erreur: "API key invalid"
Vérifiez que votre clé API OpenAI est correcte dans `backend/.env`

### Erreur: "Port 8000 already in use"
Un autre programme utilise le port. Changez le port dans `backend/.env`:
```env
PORT=8001
```

### Le bot ne répond pas
1. Vérifiez que le backend est démarré
2. Ouvrez la console du navigateur (F12) pour voir les erreurs
3. Vérifiez les logs: `backend/logs/app.log`

### Erreur npm install
```bash
# Essayez de supprimer node_modules et réinstaller
cd frontend
rm -rf node_modules
npm install
```

---

## 🚀 PROCHAINES ÉTAPES

1. ✅ **Testez toutes les fonctionnalités**
2. ✅ **Personnalisez les couleurs et le branding**
3. ✅ **Ajoutez votre catalogue de produits**
4. ✅ **Configurez l'intégration CRM/ERP** (si nécessaire)
5. ✅ **Testez avec de vrais clients** (beta testing)
6. 🚀 **Déployez en production!**

---

## 📞 BESOIN D'AIDE?

- **Logs Backend:** `backend/logs/app.log`
- **Documentation API:** http://localhost:8000/docs
- **Console Navigateur:** F12 dans le navigateur

---

## 🎉 FÉLICITATIONS!

Votre chatbot Meuble de France est prêt à l'emploi!

**Fonctionnalités incluses:**
✅ Conversation naturelle type Copilot
✅ Support multilingue (FR/EN/AR/IT/DE)
✅ Recommandations produits intelligentes
✅ Upload photos pour SAV
✅ Classification priorité automatique
✅ Interface moderne et responsive
✅ API REST complète

**Prêt pour:**
- Shopping assistance
- Service après-vente
- Support client 24/7
- Recommandations personnalisées

---

**Bon développement! 💪🛋️**

*Créé avec ❤️ par Claude Code*
*Date: 2025-12-03*
