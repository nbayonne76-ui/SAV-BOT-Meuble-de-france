# 📞 Mode Vocal - Communication Bidirectionnelle en Temps Réel

## 🎯 Vue d'Ensemble

Le chatbot SAV Mobilier de France supporte désormais la **communication vocale bidirectionnelle en temps réel** grâce à l'OpenAI Realtime API.

### Différence avec le Mode Texte

| Fonctionnalité | Mode Texte | Mode Vocal |
|----------------|-----------|------------|
| **Interface** | Clavier + bouton micro (transcription) | Appel téléphonique virtuel |
| **Interaction** | Client tape ou parle → transcrit → envoie → réponse texte | Client parle naturellement → Bot répond en voix |
| **Latence** | ~2-3 secondes | **< 200ms** (temps réel) |
| **Envoi message** | Bouton "Envoyer" requis | **Automatique** (détection de fin de parole) |
| **Réponse bot** | Texte affiché (+ lecture optionnelle) | **Voix naturelle en direct** |
| **Expérience** | Chat écrit | **Conversation téléphonique** |

## ✨ Fonctionnalités

### 🎤 Conversation Naturelle
- Parlez naturellement comme au téléphone
- Pas besoin de cliquer sur des boutons
- Le bot détecte automatiquement quand vous avez fini de parler
- Latence ultra-faible (< 200ms)

### 🗣️ Voix Naturelle
- Le bot répond avec une voix naturelle et fluide
- Pas de synthèse vocale robotique
- Ton conversationnel et empathique

### 📊 Indicateurs Visuels
- 🎤 **Écoute...** : Le bot vous écoute
- 🔊 **Parle...** : Le bot répond
- Transcription en temps réel affichée

### 📝 Historique Complet
- Tous les messages sont sauvegardés
- Transcription automatique de vos paroles
- Affichage de la conversation complète

## 🚀 Comment Utiliser

### 1. Accès au Mode Vocal

1. Ouvrez le chatbot SAV Mobilier de France
2. Cliquez sur l'onglet **"Mode Vocal (Nouveau !)"** 📞
3. Cliquez sur **"Démarrer l'Appel Vocal"**

### 2. Autoriser le Microphone

- Votre navigateur demandera l'accès au microphone
- Cliquez sur **"Autoriser"**
- Le micro est requis pour parler au bot

### 3. Parlez Naturellement

```
Vous: "Bonjour"
Bot 🔊: "Bonjour ! Je suis votre assistant SAV Mobilier de France. Quel est votre nom ?"

Vous: "Marie Dupont"
Bot 🔊: "Enchanté Marie. Quel est votre problème ?"

Vous: "Mon canapé a un pied cassé"
Bot 🔊: "Je comprends, c'est embêtant. Quel est votre numéro de commande ?"

Vous: "CMD-2024-12345"
Bot 🔊: "Parfait. Je récapitule : Marie Dupont, canapé avec pied cassé,
       commande CMD-2024-12345. Je crée votre ticket ?"

Vous: "Oui"
Bot 🔊: "✅ Ticket créé avec succès ! Numéro de ticket : TKT-2024-001"
```

### 4. Raccrocher

- Cliquez sur **"Raccrocher"** 📵 quand vous avez terminé
- L'appel se termine automatiquement après 10 minutes d'inactivité

## 🏗️ Architecture Technique

```
Frontend (React)
    ↓
    WebSocket
    ↓
Backend Proxy (FastAPI)
    ↓
    WebSocket + Headers Auth
    ↓
OpenAI Realtime API (GPT-4)
```

### Pourquoi un Proxy Backend ?

Les navigateurs ne peuvent pas envoyer de headers personnalisés avec WebSocket.
Le backend agit comme proxy sécurisé et gère l'authentification OpenAI.

## 💰 Coûts

### OpenAI Realtime API Pricing

| Modèle | Prix par minute | Utilisation recommandée |
|--------|----------------|-------------------------|
| gpt-4o-realtime-preview | **$0.18/min** | Production (meilleure qualité) |
| gpt-realtime-mini | $0.16/min | Tests & développement |

**Exemple de coûts** :
- 1 conversation de 3 minutes = **~$0.54**
- 10 conversations/jour (30 min total) = **~$5.40/jour**
- 300 conversations/mois (900 min) = **~$162/mois**

### Optimisations de Coûts

1. **Limiter la longueur des réponses** : `max_response_output_tokens: 300`
2. **Déconnexion automatique** : Timeout après 10 min d'inactivité
3. **Mode économique** : Utilisez `gpt-realtime-mini` pour tests

## 🔧 Configuration

### Backend: Installer les Dépendances

```bash
cd backend
pip install websockets>=12.0
```

### Variables d'Environnement

```bash
# .env
OPENAI_API_KEY=sk-...your-key-here
```

### Démarrer les Services

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

## 📱 Navigateurs Supportés

| Navigateur | Support Vocal | Qualité |
|-----------|---------------|---------|
| Chrome | ✅ Excellent | ⭐⭐⭐⭐⭐ |
| Edge | ✅ Excellent | ⭐⭐⭐⭐⭐ |
| Firefox | ✅ Bon | ⭐⭐⭐⭐ |
| Safari | ✅ Bon | ⭐⭐⭐⭐ |
| Mobile Chrome | ✅ Bon | ⭐⭐⭐ |
| Mobile Safari | ⚠️ Limité | ⭐⭐ |

**Recommandation** : Chrome Desktop pour la meilleure expérience

## 🐛 Dépannage

### Problème: "Microphone non disponible"

**Solution** :
1. Vérifiez que votre navigateur a l'autorisation d'accéder au micro
2. Chrome → Paramètres → Confidentialité → Autorisations du site → Microphone
3. Ajoutez votre site à la liste autorisée

### Problème: "Erreur de connexion OpenAI"

**Solution** :
1. Vérifiez que la clé API OpenAI est configurée :
   ```bash
   echo $OPENAI_API_KEY
   ```
2. Vérifiez que le backend est démarré
3. Vérifiez les logs backend :
   ```bash
   tail -f backend/logs/app.log
   ```

### Problème: "Pas de son / Bot ne parle pas"

**Solution** :
1. Vérifiez le volume de votre ordinateur
2. Testez avec un autre navigateur (Chrome recommandé)
3. Vérifiez la console JavaScript (F12) pour les erreurs

### Problème: "Latence élevée (> 1 seconde)"

**Solution** :
1. Vérifiez votre connexion Internet (débit minimum: 1 Mbps)
2. Fermez les autres applications consommant de la bande passante
3. Testez à un moment avec moins de charge réseau

## 🔐 Sécurité

### Protection de la Clé API

- ✅ La clé OpenAI est stockée **uniquement** dans le backend
- ✅ Le frontend ne voit **jamais** la clé API
- ✅ Le proxy backend gère toute l'authentification

### Permissions Microphone

- Le micro est activé **uniquement** pendant l'appel
- Désactivation automatique à la fin de l'appel
- Aucun enregistrement permanent

## 📊 Monitoring

### Logs Backend

```bash
tail -f backend/logs/app.log | grep "realtime"
```

**Événements à surveiller** :
- `✅ Frontend connecté au proxy WebSocket`
- `✅ Connecté à OpenAI Realtime API`
- `📤 Frontend → OpenAI`
- `📥 OpenAI → Frontend`
- `🔌 Connexion fermée`

### Métriques

- Nombre de sessions actives
- Durée moyenne des conversations
- Coût total par jour/mois
- Taux d'erreurs

## 🎓 Bonnes Pratiques

### Pour les Utilisateurs

1. **Parlez clairement** : Articulez bien pour une meilleure transcription
2. **Environnement calme** : Évitez les bruits de fond
3. **Pause après chaque phrase** : Laissez le bot répondre
4. **Soyez concis** : Le bot pose UNE question à la fois

### Pour les Développeurs

1. **Optimiser les prompts système** : Garder les instructions courtes
2. **Limiter max_tokens** : Réduire les coûts
3. **Timeout approprié** : Déconnexion auto après inactivité
4. **Monitoring des coûts** : Suivre l'utilisation quotidienne
5. **Rate limiting** : Limiter le nombre de sessions simultanées

## 🔮 Roadmap Future

- [ ] Multilingue (FR, EN, AR) avec détection automatique
- [ ] Analyse émotionnelle en temps réel
- [ ] Création de ticket SAV directement en vocal
- [ ] Envoi de photos pendant l'appel vocal
- [ ] Transfert vers agent humain en cours d'appel

## 📚 Ressources

### Documentation

- [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime)
- [WebSocket MDN](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)

### Support

- 📧 Email: support@mobilierdefrance.fr
- 💬 GitHub Issues: [Créer un ticket](https://github.com/votre-repo/issues)

---

**Version** : 1.0.0
**Dernière mise à jour** : Décembre 2024
**Auteur** : Équipe Mobilier de France
