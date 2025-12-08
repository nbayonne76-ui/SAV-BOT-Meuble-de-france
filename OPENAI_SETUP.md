# 🤖 Configuration OpenAI - Meuble de France Chatbot

## ✅ Modifications Effectuées

Votre projet a été configuré pour utiliser **OpenAI GPT-4** au lieu d'Anthropic Claude.

### Fichiers Modifiés:

1. ✅ `backend/.env` - Clé API changée pour OpenAI
2. ✅ `backend/requirements.txt` - Dépendance `openai` au lieu d'`anthropic`
3. ✅ `backend/app/core/config.py` - Configuration OpenAI
4. ✅ `backend/app/services/chatbot.py` - Service chatbot utilisant OpenAI GPT-4
5. ✅ `backend/app/api/endpoints/chat.py` - Endpoint utilisant OpenAI
6. ✅ `DEMARRAGE_RAPIDE.md` - Documentation mise à jour

---

## 🔑 ÉTAPE 1: Obtenir une Clé API OpenAI

### Si vous n'avez pas encore de clé API:

1. Allez sur: https://platform.openai.com/api-keys
2. Créez un compte ou connectez-vous
3. Cliquez sur "Create new secret key"
4. Copiez la clé (elle commence par `sk-...`)
5. **IMPORTANT:** Sauvegardez-la immédiatement (vous ne pourrez plus la revoir)

### Coût estimé:
- GPT-4: ~$0.03 par 1K tokens (input) + $0.06 par 1K tokens (output)
- Une conversation moyenne (10 messages) coûte environ $0.20-0.50

---

## ⚙️ ÉTAPE 2: Configurer la Clé API

Éditez le fichier: `backend\.env`

```env
# Remplacez VOTRE_CLE_OPENAI_ICI par votre vraie clé API
OPENAI_API_KEY=sk-VOTRE_VRAIE_CLE_OPENAI_ICI
```

**Exemple:**
```env
OPENAI_API_KEY=sk-proj-1234567890abcdefghijklmnopqrstuvwxyz
```

---

## 🚀 ÉTAPE 3: Installation et Démarrage

### Backend:

```bash
cd backend

# Créer environnement virtuel
python -m venv venv

# Activer (Windows)
venv\Scripts\activate

# Installer les dépendances (inclut openai)
pip install -r requirements.txt

# Démarrer le serveur
python -m app.main
```

✅ Backend: http://localhost:8000

### Frontend (nouveau terminal):

```bash
cd frontend
npm install
npm run dev
```

✅ Frontend: http://localhost:5173

---

## 🧪 ÉTAPE 4: Tester l'Application

### Test 1: Conversation Simple
```
Vous: "Bonjour"
Bot: [Répond en utilisant GPT-4]
```

### Test 2: Shopping
```
Vous: "Je cherche un canapé 3 places moderne"
Bot: [Recommande des produits]
```

### Test 3: Multilingue
```
Vous: "Hello, I'm looking for a sofa"
Bot: [Répond en anglais avec GPT-4]
```

---

## 🔍 Vérifications

### Backend fonctionne?
- [ ] http://localhost:8000 → Affiche info API
- [ ] http://localhost:8000/docs → Documentation Swagger
- [ ] Aucune erreur dans le terminal backend

### Frontend fonctionne?
- [ ] http://localhost:5173 → Interface chatbot
- [ ] Message d'accueil visible
- [ ] Peut envoyer des messages

### ChatGPT-4 répond?
- [ ] Le bot répond à vos messages
- [ ] Les réponses sont cohérentes et naturelles
- [ ] Détection de langue fonctionne
- [ ] Recommandations produits correctes

---

## ⚠️ Dépannage

### Erreur: "Invalid API key"
```
✅ Vérifiez que votre clé commence par sk-
✅ Vérifiez qu'il n'y a pas d'espaces avant/après
✅ Vérifiez que vous avez des crédits sur votre compte OpenAI
```

### Erreur: "Model 'gpt-4' not found"
```
✅ Vérifiez que vous avez accès à GPT-4
✅ Si non, modifiez chatbot.py ligne 322:
   model="gpt-4"  →  model="gpt-3.5-turbo"
```

### Erreur: "Rate limit exceeded"
```
✅ Vous avez atteint la limite de requêtes
✅ Attendez quelques minutes
✅ Ou augmentez votre quota sur platform.openai.com
```

### Le bot répond en anglais alors que je parle français
```
✅ C'est normal au début
✅ Continuez en français, il va s'adapter
✅ Ou spécifiez: "Parle-moi en français"
```

---

## 💰 Gestion des Coûts

### Estimation Mensuelle:
```
100 conversations/jour × 10 messages/conversation × $0.30/conversation
= ~$900/mois pour usage intensif

10 conversations/jour = ~$90/mois
1 conversation/jour = ~$9/mois
```

### Limiter les Coûts:

1. **Utilisez GPT-3.5-Turbo** (20x moins cher):
   ```python
   # Dans chatbot.py ligne 322
   model="gpt-3.5-turbo"  # Au lieu de "gpt-4"
   ```

2. **Définissez une limite de dépenses**:
   - Allez sur: https://platform.openai.com/account/billing/limits
   - Définissez un "Hard limit" (ex: $50/mois)

3. **Utilisez des tokens limités**:
   ```python
   # Dans chatbot.py ligne 324
   max_tokens=500  # Au lieu de 1000
   ```

---

## 📊 Modèles Disponibles

### GPT-4 (Recommandé pour qualité):
```python
model="gpt-4"
- Coût: $$$
- Qualité: ⭐⭐⭐⭐⭐
- Vitesse: Moyen
```

### GPT-4-Turbo (Recommandé pour performance):
```python
model="gpt-4-turbo"
- Coût: $$
- Qualité: ⭐⭐⭐⭐⭐
- Vitesse: Rapide
```

### GPT-3.5-Turbo (Recommandé pour dev/test):
```python
model="gpt-3.5-turbo"
- Coût: $
- Qualité: ⭐⭐⭐⭐
- Vitesse: Très rapide
```

Pour changer de modèle, éditez: `backend/app/services/chatbot.py` ligne 322

---

## 🔄 Passer de GPT-4 à GPT-3.5-Turbo

Si vous voulez économiser, utilisez GPT-3.5-Turbo:

1. Ouvrez: `backend/app/services/chatbot.py`
2. Ligne 322, changez:
   ```python
   model="gpt-4",  # Ancien
   ```
   en:
   ```python
   model="gpt-3.5-turbo",  # Nouveau (20x moins cher)
   ```
3. Redémarrez le backend

---

## 📞 Support OpenAI

- **Documentation:** https://platform.openai.com/docs
- **Statut API:** https://status.openai.com
- **Pricing:** https://openai.com/pricing
- **Community:** https://community.openai.com

---

## ✅ C'est Tout!

Votre chatbot Meuble de France est maintenant configuré avec OpenAI GPT-4!

**Avantages:**
✅ Qualité conversationnelle excellente
✅ Multilingue natif
✅ Compréhension contextuelle avancée
✅ Recommandations intelligentes
✅ API stable et bien documentée

**Prochaines étapes:**
1. Testez toutes les fonctionnalités
2. Personnalisez le contenu (produits, ton, etc.)
3. Ajustez le modèle selon vos besoins (GPT-4 vs GPT-3.5)
4. Configurez les limites de dépenses
5. Déployez en production!

---

**Bon développement! 🚀**

*Document créé le 2025-12-03*
