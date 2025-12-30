# 🧪 PHASE 4 : Tests & Couverture de code

**Date de début:** 28 décembre 2025
**Statut:** En cours
**Objectif:** Atteindre 80%+ coverage backend, 70%+ frontend

---

## 📊 État actuel (Baseline)

### Coverage Backend: **39.88%** → Objectif: **80%+**

**Tests actuels:**
- ✅ 11 tests passed
- ❌ 6 tests failed
- ⚠️ 1 error

**Fichiers prioritaires** (les moins couverts):

| Fichier | Coverage | Lignes testées | Lignes manquantes | Priorité |
|---------|----------|----------------|-------------------|----------|
| **chatbot.py** | 12.13% | 37/305 | 268 | 🔴 URGENT |
| **evidence_collector.py** | 22.37% | 51/228 | 177 | 🔴 URGENT |
| **warranty_service.py** | 22.58% | 14/62 | 48 | 🔴 URGENT |
| **sav_knowledge.py** | 20.47% | 35/171 | 136 | 🔴 URGENT |
| **product_catalog.py** | 22.88% | 35/153 | 118 | 🔴 URGENT |
| **tone_analyzer.py** | 33.87% | 42/124 | 82 | 🟠 HAUTE |
| **session_manager.py** | 36.99% | 54/146 | 92 | 🟠 HAUTE |
| **problem_detector.py** | 35.71% | 25/70 | 45 | 🟠 HAUTE |
| **sav_workflow_engine.py** | 45.45% | 110/242 | 132 | 🟠 HAUTE |

**Fichiers bien couverts** (>80%):
- ✅ constants.py: 86.90%
- ✅ models/user.py: 87.39%
- ✅ priority_scorer.py: 82.42%
- ✅ rate_limit.py: 84.09%
- ✅ main.py: 83.33%
- ✅ models/warranty.py: 80.49%

---

## 🎯 Objectifs Phase 4

### Objectifs quantitatifs
- [ ] **Backend coverage:** 39.88% → 80%+ (+40 points)
- [ ] **Frontend coverage:** 0% → 70%+ (nouveau)
- [ ] **Tests passing:** 11/18 → 100% (0 failures)
- [ ] **Fichiers critiques:** 8 fichiers <40% → tous >80%

### Objectifs qualitatifs
- [ ] Tous les flux critiques testés (création ticket SAV, chat, upload)
- [ ] Tests unitaires pour toute la logique métier
- [ ] Tests d'intégration pour les API endpoints
- [ ] Tests E2E pour les parcours utilisateur critiques
- [ ] Coverage reporting automatisé (HTML + badge)

---

## 📋 Tâches Phase 4

### **Partie 1: Correction tests existants** (🔥 Immédiat)

#### Tâche 1.1: Corriger les 6 tests failants
- [ ] Analyser les erreurs des tests auth
- [ ] Corriger test_register_new_user
- [ ] Corriger test_register_duplicate_email
- [ ] Corriger test_login_valid_credentials
- [ ] Corriger test_login_invalid_password
- [ ] Corriger test_login_nonexistent_user
- [ ] Corriger test_low_priority_information_request

**Temps estimé:** 1h

---

### **Partie 2: Tests Backend - Fichiers critiques** (🔴 Priorité HAUTE)

#### Tâche 2.1: Tests chatbot.py (12% → 80%)
**Fichier:** `backend/tests/services/test_chatbot.py` (à créer)

**Tests à ajouter:**
```python
# Tests unitaires
- test_detect_language_french()
- test_detect_language_english()
- test_detect_product_mention()
- test_detect_conversation_type_sav()
- test_detect_conversation_type_shopping()
- test_classify_priority()
- test_generate_ticket_id()
- test_is_user_confirming()
- test_is_user_rejecting()
- test_is_user_wanting_to_continue()
- test_is_user_wanting_to_close()

# Tests d'intégration
- test_chat_general_conversation()
- test_chat_with_order_number()
- test_chat_with_photo_upload()
- test_chat_sav_workflow_full()
- test_fetch_order_data()
- test_prepare_ticket_validation()
- test_generate_validation_summary()
- test_create_ticket_after_validation()
```

**Coverage attendu:** 80%+
**Temps estimé:** 4h

---

#### Tâche 2.2: Tests sav_workflow_engine.py (45% → 80%)
**Fichier:** `backend/tests/services/test_sav_workflow_engine.py` (à créer)

**Tests à ajouter:**
```python
- test_analyze_problem()
- test_check_warranty()
- test_assess_priority()
- test_collect_evidence()
- test_determine_resolution()
- test_create_ticket_complete()
- test_set_sla_deadlines()
- test_workflow_p0_critical()
- test_workflow_p3_low()
- test_auto_resolution_threshold()
```

**Coverage attendu:** 80%+
**Temps estimé:** 3h

---

#### Tâche 2.3: Tests evidence_collector.py (22% → 80%)
**Fichier:** `backend/tests/services/test_evidence_collector.py` (à créer)

**Tests à ajouter:**
```python
- test_analyze_photo_quality()
- test_extract_photo_metadata()
- test_detect_problem_in_photo()
- test_analyze_video()
- test_verify_evidence_authenticity()
- test_generate_evidence_report()
```

**Coverage attendu:** 80%+
**Temps estimé:** 2h

---

#### Tâche 2.4: Tests session_manager.py (37% → 80%)
**Fichier:** `backend/tests/services/test_session_manager.py` (à créer)

**Tests à ajouter:**
```python
- test_create_session()
- test_get_session()
- test_save_session()
- test_get_or_create_session()
- test_delete_session()
- test_add_message()
- test_update_session()
- test_list_sessions()
- test_get_session_count()
- test_cleanup_expired_sessions()
- test_session_ttl_expiration()
```

**Coverage attendu:** 80%+
**Temps estimé:** 2h

---

#### Tâche 2.5: Tests warranty_service.py (23% → 80%)
**Fichier:** `backend/tests/services/test_warranty_service.py` (à créer)

**Tests à ajouter:**
```python
- test_check_warranty_valid()
- test_check_warranty_expired()
- test_check_warranty_no_order()
- test_calculate_remaining_days()
- test_warranty_type_detection()
- test_extended_warranty()
```

**Coverage attendu:** 80%+
**Temps estimé:** 1.5h

---

### **Partie 3: Tests Backend - API Endpoints** (🟠 Priorité MOYENNE)

#### Tâche 3.1: Tests API chat.py
**Fichier:** `backend/tests/api/test_chat.py` (à créer)

**Tests à ajouter:**
```python
- test_chat_endpoint_success()
- test_chat_endpoint_with_session()
- test_chat_endpoint_with_photos()
- test_chat_endpoint_rate_limit()
- test_chat_endpoint_invalid_input()
- test_delete_session_endpoint()
- test_session_count_endpoint()
```

**Coverage attendu:** 80%+
**Temps estimé:** 2h

---

#### Tâche 3.2: Tests API sav.py
**Fichier:** `backend/tests/api/test_sav.py` (à créer)

**Tests à ajouter:**
```python
- test_create_ticket_endpoint()
- test_get_tickets_endpoint()
- test_get_ticket_by_id()
- test_update_ticket_status()
- test_add_ticket_note()
- test_assign_ticket()
```

**Coverage attendu:** 80%+
**Temps estimé:** 2h

---

#### Tâche 3.3: Tests API upload.py
**Fichier:** `backend/tests/api/test_upload.py` (à créer)

**Tests à ajouter:**
```python
- test_upload_photo_valid()
- test_upload_photo_invalid_type()
- test_upload_photo_too_large()
- test_upload_multiple_photos()
- test_upload_video()
- test_upload_malicious_file()
```

**Coverage attendu:** 80%+
**Temps estimé:** 1.5h

---

### **Partie 4: Configuration Coverage Reporting** (🔧 Infrastructure)

#### Tâche 4.1: Configuration pytest-cov avancée
**Fichier:** `backend/pyproject.toml`

```toml
[tool.pytest.ini_options]
addopts = [
    "--cov=app",
    "--cov-report=html",
    "--cov-report=xml",
    "--cov-report=term-missing:skip-covered",
    "--cov-fail-under=80",  # ✅ Fail if < 80%
    "--verbose",
]
```

**Temps estimé:** 30min

---

#### Tâche 4.2: GitHub Actions CI/CD
**Fichier:** `.github/workflows/tests.yml` (à créer)

```yaml
name: Tests & Coverage

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Backend Tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
```

**Temps estimé:** 1h

---

#### Tâche 4.3: Badge Coverage README
**Fichier:** `README.md`

Ajouter:
```markdown
![Backend Coverage](https://img.shields.io/codecov/c/github/username/repo/main?flag=backend&label=Backend%20Coverage)
![Frontend Coverage](https://img.shields.io/codecov/c/github/username/repo/main?flag=frontend&label=Frontend%20Coverage)
```

**Temps estimé:** 15min

---

### **Partie 5: Tests Frontend** (🎨 React)

#### Tâche 5.1: Configuration Vitest
**Fichier:** `frontend/vitest.config.js`

```javascript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      lines: 70,
      branches: 70,
      functions: 70,
      statements: 70
    }
  }
})
```

**Temps estimé:** 1h

---

#### Tâche 5.2: Tests ChatInterface.jsx
**Fichier:** `frontend/src/components/__tests__/ChatInterface.test.jsx`

**Tests à ajouter:**
```javascript
- test('renders chat interface')
- test('sends message on submit')
- test('handles photo upload')
- test('displays message history')
- test('handles voice recording')
- test('handles session reset')
- test('displays loading state')
- test('handles error state')
```

**Coverage attendu:** 70%+
**Temps estimé:** 3h

---

#### Tâche 5.3: Tests Dashboard.jsx
**Fichier:** `frontend/src/components/__tests__/Dashboard.test.jsx`

**Tests à ajouter:**
```javascript
- test('renders dashboard')
- test('fetches and displays tickets')
- test('filters tickets by status')
- test('sorts tickets by priority')
- test('shows ticket details')
```

**Coverage attendu:** 70%+
**Temps estimé:** 2h

---

### **Partie 6: Tests E2E** (🎭 End-to-End)

#### Tâche 6.1: Configuration Playwright
**Fichier:** `playwright.config.js` (racine projet)

```javascript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:5173',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] }},
  ],
});
```

**Temps estimé:** 1h

---

#### Tâche 6.2: Tests E2E critiques
**Fichier:** `e2e/sav-ticket-creation.spec.js`

**Tests à ajouter:**
```javascript
test('complete SAV ticket creation flow', async ({ page }) => {
  // 1. Ouvrir chatbot
  // 2. Envoyer message SAV
  // 3. Uploader photos
  // 4. Valider récapitulatif
  // 5. Vérifier ticket créé
})

test('chat conversation general', async ({ page }) => {
  // Test conversation basique
})

test('product search and display', async ({ page }) => {
  // Test recherche produit
})
```

**Temps estimé:** 4h

---

## 📊 Métriques de succès

### Coverage Targets

| Catégorie | Baseline | Objectif | Status |
|-----------|----------|----------|--------|
| **Backend Global** | 39.88% | 80%+ | ⏳ |
| chatbot.py | 12.13% | 80%+ | ⏳ |
| sav_workflow_engine.py | 45.45% | 80%+ | ⏳ |
| session_manager.py | 36.99% | 80%+ | ⏳ |
| evidence_collector.py | 22.37% | 80%+ | ⏳ |
| **Frontend Global** | 0% | 70%+ | ⏳ |
| ChatInterface.jsx | 0% | 70%+ | ⏳ |
| Dashboard.jsx | 0% | 70%+ | ⏳ |
| **Tests E2E** | 0 | 3+ scenarios | ⏳ |

### Tests Targets

| Type de test | Actuel | Objectif | Status |
|--------------|--------|----------|--------|
| Tests unitaires backend | 18 | 100+ | ⏳ |
| Tests intégration API | 5 | 30+ | ⏳ |
| Tests unitaires frontend | 0 | 50+ | ⏳ |
| Tests E2E | 0 | 3+ | ⏳ |
| **Total tests** | **23** | **183+** | ⏳ |

---

## 🗓️ Planning Phase 4

### Semaine 1 (Jours 1-3)
- ✅ Jour 1: Analyse baseline + correction tests existants
- ⏳ Jour 2-3: Tests chatbot.py + sav_workflow_engine.py

### Semaine 2 (Jours 4-7)
- ⏳ Jour 4: Tests session_manager.py + evidence_collector.py
- ⏳ Jour 5: Tests warranty_service.py + problem_detector.py
- ⏳ Jour 6-7: Tests API endpoints (chat, sav, upload)

### Semaine 3 (Jours 8-11)
- ⏳ Jour 8-9: Configuration frontend + tests ChatInterface
- ⏳ Jour 10: Tests Dashboard + autres composants
- ⏳ Jour 11: Tests E2E Playwright

### Semaine 4 (Jours 12-14)
- ⏳ Jour 12: Configuration CI/CD + badges
- ⏳ Jour 13: Atteindre targets 80%/70%
- ⏳ Jour 14: Documentation + rapport final

---

## 🛠️ Outils & Dépendances

### Backend (Python)
```bash
pip install pytest pytest-cov pytest-asyncio httpx pytest-mock
```

### Frontend (JavaScript)
```bash
npm install -D vitest @vitest/ui jsdom @testing-library/react @testing-library/jest-dom
npm install -D @playwright/test
```

---

## 📝 Templates de tests

### Template test unitaire backend
```python
# backend/tests/services/test_example.py
import pytest
from app.services.example import ExampleService

@pytest.mark.asyncio
async def test_example_function():
    # Arrange
    service = ExampleService()

    # Act
    result = await service.do_something()

    # Assert
    assert result is not None
    assert result.status == "success"
```

### Template test API endpoint
```python
# backend/tests/api/test_example.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_endpoint_success():
    response = client.get("/api/example")
    assert response.status_code == 200
    assert "data" in response.json()
```

### Template test React
```javascript
// frontend/src/components/__tests__/Example.test.jsx
import { render, screen, fireEvent } from '@testing-library/react'
import Example from '../Example'

test('renders component', () => {
  render(<Example />)
  expect(screen.getByText('Hello')).toBeInTheDocument()
})
```

---

## ✅ Critères d'achèvement Phase 4

La Phase 4 sera considérée comme **TERMINÉE** quand:

- [ ] Backend coverage ≥ 80%
- [ ] Frontend coverage ≥ 70%
- [ ] 0 tests failants (100% passing)
- [ ] Tous les fichiers critiques >80% coverage
- [ ] 3+ scénarios E2E critiques testés
- [ ] CI/CD configuré et fonctionnel
- [ ] Badges coverage ajoutés au README
- [ ] Rapport de coverage généré automatiquement

---

**🚀 Phase 4 démarrée le 28 décembre 2025**
**⏱️ Durée estimée totale: 3-4 semaines**
**👤 Assigné à: Claude Sonnet 4.5**
