# 🧪 PHASE 4 PARTIE 7 : Tests Frontend React & E2E

**Date:** 28 décembre 2025
**Objectif:** Tests frontend React (0% → 70%+) + 3 scénarios E2E Playwright
**Scope:** 4 composants principaux + tests E2E

---

## 📊 Baseline Coverage

**Coverage actuel:** 0% sur tous les fichiers

| Fichier | Lignes | Coverage | Priorité |
|---------|--------|----------|----------|
| **ChatInterface.jsx** | 959 | 0% | 🔴 CRITIQUE (composant principal) |
| **Dashboard.jsx** | 707 | 0% | 🔴 CRITIQUE |
| **RealtimeVoiceChat.jsx** | 512 | 0% | 🟡 MOYENNE |
| **VoiceChatWhisper.jsx** | 848 | 0% | 🟡 MOYENNE |
| **App.jsx** | 72 | 0% | 🟢 BASSE |
| **main.jsx** | 10 | 0% | 🟢 BASSE |
| **TOTAL** | **3108 lignes** | **0%** | **Objectif: 70%+** |

---

## 🎯 Objectifs Partie 7

### Tests unitaires React (70%+ coverage)
- ✅ ChatInterface.jsx → 70%+ (composant principal)
- ✅ Dashboard.jsx → 70%+
- ✅ App.jsx → 90%+ (simple)
- ⏳ VoiceChatWhisper.jsx → 50%+ (complexe, vocal)
- ⏳ RealtimeVoiceChat.jsx → 50%+ (WebSocket, complexe)

### Tests E2E Playwright (3+ scénarios)
- ✅ Scénario 1: Flux complet création ticket SAV
- ✅ Scénario 2: Upload photos et validation
- ✅ Scénario 3: Dashboard - visualisation tickets

---

## 📋 PARTIE 7A : Tests React Testing Library

### 1. ChatInterface.jsx (959 lignes) - PRIORITÉ 1

**Fonctionnalités à tester:**

#### État et Lifecycle
- [ ] Initialisation correcte du composant
- [ ] Message de bienvenue affiché au montage
- [ ] Génération session ID unique (crypto.randomUUID)
- [ ] Nettoyage au démontage (cleanup recognition, speech synthesis)

#### Messaging
- [ ] Affichage liste messages (user/assistant)
- [ ] Envoi message texte
- [ ] Validation message vide (disabled)
- [ ] Indicateur typing pendant chargement
- [ ] Scroll auto vers bas quand nouveau message
- [ ] Sanitization HTML avec DOMPurify
- [ ] Formatage timestamp (HH:mm)

#### Upload Fichiers
- [ ] Bouton upload ouvre sélecteur
- [ ] Upload 1 fichier image (jpg, png)
- [ ] Upload multiple fichiers
- [ ] Validation types fichiers (images, vidéos)
- [ ] Validation taille max (10MB)
- [ ] Preview fichiers uploadés
- [ ] Suppression fichier individuel
- [ ] Envoi fichiers avec message

#### Reconnaissance Vocale (Web Speech API)
- [ ] Détection support navigateur
- [ ] Bouton microphone visible si supporté
- [ ] Démarrage reconnaissance vocale
- [ ] Affichage transcription en temps réel
- [ ] Ajout transcript au champ texte
- [ ] Arrêt reconnaissance
- [ ] Gestion erreurs (no-speech, not-allowed, network)
- [ ] Redémarrage automatique si arrêt inattendu

#### Synthèse Vocale (Text-to-Speech)
- [ ] Détection support speechSynthesis
- [ ] Toggle activation/désactivation voix
- [ ] Lecture automatique réponses bot
- [ ] Nettoyage texte (markdown, emojis)
- [ ] Configuration voix française (fr-FR)
- [ ] Indicateur "bot en train de parler"
- [ ] Arrêt parole si désactivé

#### Workflow Ticket SAV
- [ ] Affichage boutons validation ticket
- [ ] Confirmation création ticket
- [ ] Annulation et recommence
- [ ] Appel API `/api/chat/create-ticket`
- [ ] Message confirmation après création
- [ ] Données ticket stockées dans pendingTicket

#### Clôture Conversation
- [ ] Détection should_close_session
- [ ] Message au revoir affiché
- [ ] Effacement messages après 3s
- [ ] Appel DELETE `/api/chat/{session_id}`
- [ ] Réaffichage message bienvenue

#### Intégration API
- [ ] Appel POST `/api/chat`
- [ ] Headers Content-Type: application/json
- [ ] Body: message, session_id, photos
- [ ] Gestion erreurs réseau (try/catch)
- [ ] Message d'erreur utilisateur si échec

#### Accessibilité & UX
- [ ] Envoi message avec Enter
- [ ] Shift+Enter pour nouvelle ligne
- [ ] Bouton send disabled si vide
- [ ] Placeholders informatifs
- [ ] Indicateurs visuels (recording, speaking)

**Tests estimés:** ~40-50 tests
**Coverage cible:** 70%+

---

### 2. Dashboard.jsx (707 lignes) - PRIORITÉ 2

**Fonctionnalités à tester:**

#### État et Chargement
- [ ] Initialisation composant
- [ ] Chargement tickets au montage (useEffect)
- [ ] Indicateur loading pendant fetch
- [ ] Gestion erreurs fetch
- [ ] Refresh auto toutes les X secondes

#### Affichage Tickets
- [ ] Liste tickets vide (message "Aucun ticket")
- [ ] Affichage carte ticket (N°, client, priorité, statut)
- [ ] Couleurs selon priorité (P0 rouge, P1 orange, P2 jaune, P3 vert)
- [ ] Couleurs selon statut (created, in_progress, resolved)
- [ ] Formatage dates relatives (il y a X heures)
- [ ] Icônes selon type problème

#### Filtrage & Tri
- [ ] Filtre par priorité (P0, P1, P2, P3, Tous)
- [ ] Filtre par statut (created, in_progress, resolved, Tous)
- [ ] Recherche par texte (nom client, N° ticket)
- [ ] Tri par date (plus récents en premier)
- [ ] Tri par priorité
- [ ] Compteurs par filtre

#### Détails Ticket
- [ ] Clic ticket ouvre modal détails
- [ ] Affichage toutes infos ticket
- [ ] Historique actions
- [ ] Preuves (photos/vidéos)
- [ ] Fermeture modal (X, ESC, clic extérieur)

#### Actions Tickets
- [ ] Mise à jour statut
- [ ] Ajout commentaire
- [ ] Ajout preuves supplémentaires
- [ ] Assignation technicien
- [ ] Clôture ticket

#### Statistiques
- [ ] Compteur total tickets
- [ ] Compteur par priorité
- [ ] Compteur par statut
- [ ] SLA dépassé (indicateur rouge)

**Tests estimés:** ~30-35 tests
**Coverage cible:** 70%+

---

### 3. App.jsx (72 lignes) - PRIORITÉ 3

**Fonctionnalités à tester:**

#### Routing & Navigation
- [ ] Affichage onglet Chat par défaut
- [ ] Clic onglet Dashboard affiche Dashboard
- [ ] Clic onglet Chat affiche ChatInterface
- [ ] État actif tab (CSS active)

#### Layout
- [ ] Header toujours visible
- [ ] Titre application
- [ ] Navigation responsive
- [ ] Footer / info

**Tests estimés:** ~5-8 tests
**Coverage cible:** 90%+

---

### 4. VoiceChatWhisper.jsx & RealtimeVoiceChat.jsx (Optional)

**Fonctionnalités critiques:**

#### VoiceChatWhisper
- [ ] Initialisation MediaRecorder
- [ ] Démarrage/arrêt enregistrement
- [ ] Envoi audio à l'API Whisper
- [ ] Affichage transcription
- [ ] Gestion erreurs microphone

#### RealtimeVoiceChat
- [ ] Connexion WebSocket
- [ ] Envoi/réception audio temps réel
- [ ] Gestion déconnexion
- [ ] Indicateurs visuels

**Tests estimés:** ~20 tests combinés
**Coverage cible:** 50%+

---

## 📋 PARTIE 7B : Tests E2E Playwright

### Installation Playwright

```bash
npm install --save-dev @playwright/test
npx playwright install
```

### Configuration Playwright

**playwright.config.js:**
```javascript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

### Scénario E2E 1: Création Ticket SAV (Flux Complet)

**Fichier:** `e2e/create-ticket-flow.spec.js`

**Étapes:**
1. Ouvrir application
2. Vérifier message bienvenue affiché
3. Saisir message: "Bonjour, je m'appelle Jean Dupont. Mon canapé OSLO a un pied cassé, commande CMD-2024-12345"
4. Cliquer bouton Send
5. Attendre réponse bot (indicateur typing)
6. Vérifier réponse bot contient récapitulatif
7. Vérifier boutons validation visibles
8. Cliquer "Valider le ticket"
9. Attendre confirmation
10. Vérifier message "Ticket créé avec succès"
11. Vérifier N° ticket affiché (SAV-YYYY-XXXXX)

**Assertions:**
- Message d'accueil présent
- Champ input fonctionnel
- Réponse bot reçue en <5s
- Boutons validation apparaissent
- Ticket créé avec succès
- N° ticket valide (format SAV-2025-XXXXX)

---

### Scénario E2E 2: Upload Photos

**Fichier:** `e2e/photo-upload-flow.spec.js`

**Étapes:**
1. Ouvrir application
2. Cliquer bouton camera (upload)
3. Sélectionner fichier image test (fixtures/test-photo.jpg)
4. Vérifier preview image affichée
5. Saisir message: "Voici la photo du pied cassé"
6. Envoyer message
7. Vérifier message utilisateur avec image
8. Vérifier réponse bot

**Assertions:**
- Bouton upload fonctionnel
- Preview image correcte
- Upload réussi
- Message envoyé avec photo
- API reçoit URL photo

---

### Scénario E2E 3: Dashboard Tickets

**Fichier:** `e2e/dashboard-tickets.spec.js`

**Étapes:**
1. Créer tickets via seed data
2. Ouvrir application
3. Cliquer onglet "Dashboard"
4. Vérifier liste tickets affichée
5. Vérifier compteurs (total, par priorité)
6. Filtrer par priorité P0
7. Vérifier seuls tickets P0 visibles
8. Cliquer ticket pour détails
9. Vérifier modal détails ouverte
10. Vérifier toutes infos ticket présentes
11. Fermer modal (X)

**Assertions:**
- Dashboard charge correctement
- Tickets affichés (≥1)
- Compteurs corrects
- Filtres fonctionnels
- Modal détails complète
- Fermeture modal OK

---

## 🛠️ Outils & Configuration

### Dépendances déjà installées ✅
- ✅ Vitest
- ✅ @testing-library/react
- ✅ @testing-library/jest-dom
- ✅ @vitest/coverage-v8
- ✅ jsdom
- ✅ @vitest/ui

### À installer
- [ ] @playwright/test
- [ ] @testing-library/user-event (interactions)

### Mocks nécessaires

#### API Mock (MSW - Mock Service Worker)
```bash
npm install --save-dev msw
```

**Configuration MSW:**
```javascript
// src/test/mocks/handlers.js
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.post('/api/chat', () => {
    return HttpResponse.json({
      response: 'Test response',
      language: 'fr',
      conversation_type: 'sav'
    });
  }),

  http.post('/api/upload', () => {
    return HttpResponse.json({
      files: [{
        url: '/uploads/photos/test.jpg',
        original_name: 'test.jpg',
        type: 'jpg'
      }]
    });
  }),

  http.post('/api/chat/create-ticket', () => {
    return HttpResponse.json({
      ticket_id: 'SAV-2025-12345',
      status: 'created',
      priority: 'high'
    });
  })
];
```

#### Browser APIs Mock
```javascript
// src/test/setup.js
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

global.crypto = {
  randomUUID: () => 'test-uuid-12345'
};

// Mock Web Speech API
window.SpeechRecognition = class SpeechRecognition {
  constructor() {
    this.lang = '';
    this.continuous = false;
    this.interimResults = false;
  }
  start() {}
  stop() {}
  addEventListener() {}
};

// Mock Speech Synthesis
window.speechSynthesis = {
  speak: vi.fn(),
  cancel: vi.fn(),
  getVoices: () => [{ lang: 'fr-FR', name: 'French' }]
};

// Mock File API
global.FormData = class FormData {
  append() {}
};
```

---

## 📊 Stratégie de Tests

### Priorité des tests

**Phase 1 - Critique (70% du temps):**
1. ChatInterface.jsx - Messaging core
2. ChatInterface.jsx - API integration
3. Dashboard.jsx - Display tickets
4. App.jsx - Navigation

**Phase 2 - Important (20% du temps):**
5. ChatInterface.jsx - File upload
6. Dashboard.jsx - Filters
7. E2E Scénario 1 (création ticket)

**Phase 3 - Nice to have (10% du temps):**
8. Voice components (basic tests)
9. E2E Scénarios 2 & 3
10. Edge cases

### Patterns de test React

#### Pattern 1: Render & Display
```javascript
it('should display welcome message', () => {
  render(<ChatInterface />);
  expect(screen.getByText(/Bonjour/i)).toBeInTheDocument();
});
```

#### Pattern 2: User Interactions
```javascript
it('should send message on button click', async () => {
  render(<ChatInterface />);
  const input = screen.getByPlaceholderText(/Nom complet/i);
  const button = screen.getByRole('button', { name: /send/i });

  await user.type(input, 'Test message');
  await user.click(button);

  expect(screen.getByText('Test message')).toBeInTheDocument();
});
```

#### Pattern 3: API Mocking
```javascript
it('should fetch and display bot response', async () => {
  server.use(
    http.post('/api/chat', () => {
      return HttpResponse.json({ response: 'Bot response' });
    })
  );

  render(<ChatInterface />);
  // ... interact

  await waitFor(() => {
    expect(screen.getByText('Bot response')).toBeInTheDocument();
  });
});
```

#### Pattern 4: Async State
```javascript
it('should show loading indicator', async () => {
  render(<ChatInterface />);

  const button = screen.getByRole('button', { name: /send/i });
  await user.click(button);

  expect(screen.getByText(/typing/i)).toBeInTheDocument();
});
```

---

## 📝 Checklist Completion

### Tests React ✅
- [ ] ChatInterface.jsx (40+ tests, 70%+)
- [ ] Dashboard.jsx (30+ tests, 70%+)
- [ ] App.jsx (8+ tests, 90%+)
- [ ] VoiceChatWhisper.jsx (10+ tests, 50%+)
- [ ] Configuration MSW
- [ ] Mocks APIs complètes
- [ ] Coverage rapport HTML généré

### Tests E2E Playwright ✅
- [ ] Playwright installé et configuré
- [ ] Scénario 1: Création ticket (complet)
- [ ] Scénario 2: Upload photos
- [ ] Scénario 3: Dashboard
- [ ] Screenshots failures
- [ ] Videos retries
- [ ] Rapport HTML E2E

### Documentation ✅
- [ ] Mise à jour PHASE_4_PROGRESS.md
- [ ] Coverage screenshots
- [ ] Instructions lancer tests
- [ ] README tests frontend

---

## 🎯 Critères de Succès

✅ **Coverage global frontend:** 70%+
✅ **ChatInterface coverage:** 70%+
✅ **Dashboard coverage:** 70%+
✅ **App coverage:** 90%+
✅ **Tests passants:** 100% (0 failures)
✅ **Tests E2E:** 3 scénarios passants
✅ **Temps exécution:** <30s (unit), <2min (E2E)
✅ **CI-ready:** Tests peuvent tourner en CI

---

## 📈 Estimation

**Temps estimé:** 6-8 heures
- Tests ChatInterface: 3h
- Tests Dashboard: 2h
- Tests App: 30min
- Tests E2E Playwright: 2h
- Configuration & mocks: 1h
- Documentation: 30min

**Tests créés:** ~90-100 tests
- Unit tests: 85-95
- E2E tests: 3-5

**Lignes code tests:** ~2000-2500 lignes

---

**🚀 Prêt à démarrer!**
