# 🧪 Guide de Test du Système SAV

## ✅ Fichiers créés aujourd'hui

Vérifiez que ces fichiers existent :
- ✅ `backend/app/services/tone_analyzer.py`
- ✅ `backend/app/services/client_summary_generator.py`
- ✅ `backend/app/services/sav_workflow_engine.py` (modifié)
- ✅ `backend/app/services/chatbot.py` (modifié)
- ✅ `backend/app/main.py` (modifié)
- ✅ `backend/app/api/endpoints/sav.py`

---

## 🚀 ÉTAPE 1 : Démarrer le Backend

### Option A : Avec le script de démarrage
```bash
cd c:\Users\v-nbayonne\meuble-de-france-chatbot\backend
.\start-backend.bat
```

### Option B : Manuellement
```bash
cd c:\Users\v-nbayonne\meuble-de-france-chatbot\backend
python -m app.main
```

**✅ Vérification :** Vous devriez voir :
```
🚀 Starting Meuble de France Chatbot v1.0.0
📝 API Documentation: http://127.0.0.1:8000/docs
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## 🚀 ÉTAPE 2 : Démarrer le Frontend

Dans un nouveau terminal :

```bash
cd c:\Users\v-nbayonne\meuble-de-france-chatbot\frontend
npm start
```

**✅ Vérification :** Le navigateur devrait s'ouvrir sur `http://localhost:5173`

---

## 🧪 ÉTAPE 3 : Tester l'API SAV

### Test 1 : Créer une réclamation SAV (Problème critique)

Ouvrez un nouveau terminal et testez :

```bash
curl -X POST http://localhost:8000/api/sav/create-claim ^
  -H "Content-Type: application/json" ^
  -d "{\"customer_id\":\"test@example.fr\",\"order_number\":\"CMD-2024-TEST01\",\"product_sku\":\"OSLO-3P\",\"product_name\":\"Canapé OSLO 3 places\",\"problem_description\":\"Mon canapé a un pied cassé net, il va tomber sur mon enfant, c'est vraiment dangereux!!!\",\"purchase_date\":\"2024-06-01T00:00:00Z\",\"delivery_date\":\"2024-07-15T00:00:00Z\",\"customer_tier\":\"standard\",\"product_value\":1890.0}"
```

**✅ Résultat attendu :**
```json
{
  "success": true,
  "ticket": {
    "ticket_id": "SAV-20251204-...",
    "priority": "P0",
    "priority_score": 85+,
    "problem_category": "structural",
    "warranty_covered": true,
    "auto_resolved": false,
    "status": "escalated_to_human"
  }
}
```

**🎯 Ce qui se passe automatiquement :**
1. ✅ Analyse NLP → Catégorie : `structural`
2. ✅ Analyse TON → Ton : `URGENT`, Urgence : `CRITICAL`
3. ✅ Vérification garantie → Couvert (6 mois < 5 ans)
4. ✅ Calcul priorité → P0 (score ≥ 85)
5. ✅ Décision → Escalade humaine (P0 toujours escaladé)
6. ✅ Récapitulatif généré avec email/SMS

---

### Test 2 : Problème modéré sous garantie

```bash
curl -X POST http://localhost:8000/api/sav/create-claim ^
  -H "Content-Type: application/json" ^
  -d "{\"customer_id\":\"client@example.fr\",\"order_number\":\"CMD-2024-TEST02\",\"product_sku\":\"OSLO-3P\",\"product_name\":\"Canapé OSLO 3 places\",\"problem_description\":\"Les coussins de mon canapé s'affaissent un peu après 8 mois, c'est un peu décevant\",\"purchase_date\":\"2024-04-01T00:00:00Z\",\"delivery_date\":\"2024-05-15T00:00:00Z\",\"customer_tier\":\"standard\",\"product_value\":1890.0}"
```

**✅ Résultat attendu :**
```json
{
  "ticket": {
    "priority": "P1" ou "P2",
    "problem_category": "cushions",
    "warranty_covered": true,
    "auto_resolved": false,
    "status": "awaiting_technician"
  }
}
```

**🎯 Ce qui se passe :**
1. ✅ Analyse TON → Ton : `CONCERNED`, Urgence : `MEDIUM`
2. ✅ Catégorie : `cushions`
3. ✅ Garantie → Couvert (8 mois < 2 ans)
4. ✅ Priorité → P1 ou P2
5. ✅ Décision → Assignation technicien
6. ✅ Délai → Réponse < 48h

---

### Test 3 : Problème hors garantie

```bash
curl -X POST http://localhost:8000/api/sav/create-claim ^
  -H "Content-Type: application/json" ^
  -d "{\"customer_id\":\"ancien@example.fr\",\"order_number\":\"CMD-2021-TEST03\",\"product_sku\":\"OSLO-3P\",\"product_name\":\"Canapé OSLO 3 places\",\"problem_description\":\"Le tissu de mon canapé est déchiré\",\"purchase_date\":\"2021-01-01T00:00:00Z\",\"delivery_date\":\"2021-02-15T00:00:00Z\",\"customer_tier\":\"standard\",\"product_value\":1890.0}"
```

**✅ Résultat attendu :**
```json
{
  "ticket": {
    "warranty_covered": false,
    "status": "escalated_to_human",
    "priority": "P2" ou "P3"
  }
}
```

**🎯 Ce qui se passe :**
1. ✅ Garantie → ❌ Expirée (4 ans > 2 ans tissu)
2. ✅ Escalade humaine (hors garantie)
3. ✅ Proposition solutions alternatives

---

### Test 4 : Vérifier les exigences de preuves

```bash
curl http://localhost:8000/api/sav/evidence-requirements/structural?priority=P0
```

**✅ Résultat attendu :**
```json
{
  "message": "🔴 URGENT\n\n📸 Preuves nécessaires:\n✅ 3 photo(s) minimum\n✅ 1 vidéo(s)\n...",
  "requirements": {
    "min_photos": 3,
    "min_videos": 1,
    "required_angles": ["vue_ensemble", "zoom_probleme", "contexte"]
  }
}
```

---

## 🧪 ÉTAPE 4 : Tester via le Chatbot

### Test dans l'interface web :

1. **Ouvrez** : http://localhost:5173
2. **Message test 1 (Urgent) :**
   ```
   Message: "Mon canapé a un pied cassé, mon enfant risque de se blesser!!!"
   Numéro de commande: CMD-2024-12345
   ```

   **Résultat attendu :**
   - ✅ Détection ton : URGENT
   - ✅ Ticket créé automatiquement
   - ✅ Priorité P0
   - ✅ Escalade humaine

3. **Message test 2 (Modéré) :**
   ```
   Message: "Bonjour, les coussins de mon canapé OSLO s'affaissent un peu après 8 mois"
   Numéro de commande: CMD-2024-12345
   ```

   **Résultat attendu :**
   - ✅ Ton : CONCERNED ou FRUSTRATED
   - ✅ Catégorie : cushions
   - ✅ Sous garantie
   - ✅ Assignation technicien

4. **Message test 3 (Calme) :**
   ```
   Message: "Bonjour, j'aimerais avoir des informations sur l'entretien de mon canapé"
   Numéro de commande: CMD-2024-12345
   ```

   **Résultat attendu :**
   - ✅ Ton : CALM
   - ✅ Pas de ticket SAV (information uniquement)
   - ✅ Conseils d'entretien

---

## 📊 ÉTAPE 5 : Vérifier les Logs

Dans le terminal du backend, vous devriez voir :

```
🎫 Nouvelle réclamation SAV: CMD-2024-TEST01
🔍 Problème analysé pour SAV-20251204-001: structural | P0
🎭 Ton analysé pour SAV-20251204-001: URGENT | Urgence: CRITICAL | Empathie requise: True
🔒 Garantie vérifiée pour SAV-20251204-001: ✅ Couvert
📊 Priorité calculée pour SAV-20251204-001: P0 (score: 95)
⚠️  Escalade humaine pour SAV-20251204-001: Priorité P0 | Score 95
📧 Récapitulatif généré pour SAV-20251204-001: SUM-20251204-120000 | Validation requise: True
✅ Ticket SAV-20251204-001 traité: escalated_to_human | Priorité: P0 | Auto-résolu: False | Validation requise: True
```

---

## 🔍 ÉTAPE 6 : Vérifier la Documentation API

Ouvrez : http://localhost:8000/docs

Vous devriez voir les nouveaux endpoints SAV :
- ✅ `POST /api/sav/create-claim`
- ✅ `POST /api/sav/add-evidence`
- ✅ `GET /api/sav/ticket/{ticket_id}`
- ✅ `GET /api/sav/ticket/{ticket_id}/history`
- ✅ `GET /api/sav/evidence-requirements/{problem_category}`

---

## ✅ Checklist de Vérification

### Fonctionnalités Core :

- [ ] **Vérification garantie instantanée** : Garantie vérifiée automatiquement
- [ ] **Analyse du ton** : Ton et urgence détectés (CALM, CONCERNED, FRUSTRATED, ANGRY, URGENT)
- [ ] **Collecte preuves** : Exigences générées selon catégorie
- [ ] **Pré-qualification** : Problème classifié en 8 catégories
- [ ] **Calcul priorité** : Score 0-100 calculé, P0-P3 assigné
- [ ] **Décision automatique** : Auto-résolution / Escalade / Technicien
- [ ] **Récapitulatif client** : Email et SMS générés
- [ ] **Validation requise** : Lien de validation créé
- [ ] **Historique complet** : Toutes actions tracées

### Tests par scénario :

- [ ] **Problème critique (P0)** : Escalade humaine immédiate
- [ ] **Problème urgent (P1)** : Assignation technicien < 24h
- [ ] **Problème modéré (P2)** : Traitement standard < 5j
- [ ] **Problème léger (P3)** : Réponse < 7j
- [ ] **Hors garantie** : Alternatives proposées
- [ ] **Ton urgent détecté** : SLA ajusté à 4h

---

## 🐛 En cas de problème

### Erreur : "Module not found"
```bash
cd c:\Users\v-nbayonne\meuble-de-france-chatbot\backend
pip install -r requirements.txt
```

### Erreur : "Port already in use"
```bash
# Trouver et tuer le processus
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Erreur : "Cannot connect to backend"
Vérifiez que :
1. Backend tourne sur http://localhost:8000
2. Frontend configuré avec la bonne URL dans `.env`

---

## 📧 Exemple de Récapitulatif Email Généré

Voici ce que le client recevrait par email :

```
Bonjour Client,

═══════════════════════════════════════════════════════
📋 RÉCAPITULATIF DE VOTRE DEMANDE SAV
═══════════════════════════════════════════════════════

🎫 Numéro de ticket : SAV-20251204-001
📦 Commande : CMD-2024-TEST01
🛋️ Produit : Canapé OSLO 3 places

⚠️ Problème signalé :
Problème de structure: Mon canapé a un pied cassé net, mon enf...

🛡️ Garantie : ✅ Sous garantie
🎯 Priorité : 🔴 CRITIQUE

───────────────────────────────────────────────────────
📍 PROCHAINES ÉTAPES
───────────────────────────────────────────────────────

👤 Un conseiller SAV vous contactera rapidement pour étudier votre cas.

⏰ Délai de réponse : Avant le 04/12/2025 à 16h00

───────────────────────────────────────────────────────
✅ VALIDATION REQUISE
───────────────────────────────────────────────────────

Pour traiter votre demande, merci de valider les informations ci-dessus :

👉 https://mobilierdefrance.com/sav/validate/SAV-20251204-001

Cette validation nous permet de :
• Confirmer que vous êtes bien à l'origine de la demande
• Éviter tout malentendu sur les éléments fournis
• Accélérer le traitement de votre dossier

⚠️ Sans validation sous 72h, votre demande sera automatiquement annulée.
```

---

## 🎉 Succès !

Si tous les tests passent, le système SAV est **100% opérationnel** !

Vous avez maintenant :
- ✅ Analyse automatique du ton et urgence
- ✅ Vérification garantie instantanée
- ✅ Classification intelligente (8 catégories)
- ✅ Calcul de priorité (8 facteurs)
- ✅ Décisions automatiques
- ✅ Récapitulatifs clients avec validation
- ✅ Traçabilité complète

**Le noyau du bot SAV fonctionne ! 🚀**
