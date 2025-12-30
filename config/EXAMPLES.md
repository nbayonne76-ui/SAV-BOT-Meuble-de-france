# 🎨 Exemples de Configurations

Ce fichier contient des exemples de configurations prêtes à l'emploi pour différents types d'entreprises et cas d'usage.

---

## 📋 Table des Matières

1. [Configuration Minimaliste (Startup)](#1-configuration-minimaliste-startup)
2. [Configuration Premium (Luxe)](#2-configuration-premium-luxe)
3. [Configuration Multilingue](#3-configuration-multilingue)
4. [Configuration Économique (Réduction Coûts)](#4-configuration-économique-réduction-coûts)
5. [Configuration Support Rapide (SLA Courts)](#5-configuration-support-rapide-sla-courts)

---

## 1. Configuration Minimaliste (Startup)

**Cas d'usage:** Petite entreprise, budget limité, besoin simple

### `chatbot_config.yaml`

```yaml
company:
  name: "Ma Startup"
  short_name: "MS"
  support_email: "contact@ma-startup.fr"

ai:
  model: "gpt-3.5-turbo"      # Le moins cher
  temperature: 0.5            # Factuel
  max_tokens: 300             # Réponses courtes
  history_limit: 4            # Mémoire limitée

priorities:
  P0:
    sla_hours: 8              # SLA relâché
  P1:
    sla_hours: 48
  P2:
    sla_hours: 72
  P3:
    sla_hours: 168            # 1 semaine

upload:
  max_file_size_mb: 5         # Limité pour économiser stockage
  max_files_per_request: 5

notifications:
  send_email_on_ticket_creation: false  # Pas d'emails auto
  send_sms_for_urgent_tickets: false
```

### `dashboard_config.yaml`

```yaml
appearance:
  theme:
    primary: "#3B82F6"        # Bleu simple

statistics:
  total_tickets:
    enabled: true
  critical_tickets:
    enabled: false            # Masquer pour simplifier
  urgent_tickets:
    enabled: false
  auto_resolved:
    enabled: true

columns:
  order:
    - "ticket_id"
    - "customer"
    - "problem"
    - "status"
    - "actions"             # Seulement 5 colonnes

actions:
  view_details:
    enabled: true
  edit:
    enabled: false          # Pas de modification
  delete:
    enabled: false

export:
  enabled: false            # Pas d'export
```

---

## 2. Configuration Premium (Luxe)

**Cas d'usage:** Marque haut de gamme, service client d'excellence, budget élevé

### `chatbot_config.yaml`

```yaml
company:
  name: "Prestige Mobilier"
  short_name: "PM"
  support_email: "conciergerie@prestige-mobilier.fr"
  support_phone: "+33 1 80 00 00 00"

branding:
  primary_color: "#1F2937"    # Noir élégant
  secondary_color: "#D4AF37"   # Or
  accent_color: "#8B4513"      # Marron luxe

messages:
  welcome:
    fr: "🌟 Bienvenue chez Prestige Mobilier.\n\nVotre satisfaction est notre priorité absolue. Notre équipe dédiée est à votre écoute 24/7.\n\nComment puis-je vous assister aujourd'hui ?"

ai:
  model: "gpt-4-turbo"        # Meilleur modèle
  temperature: 0.8            # Plus empathique
  max_tokens: 800             # Réponses détaillées
  history_limit: 10           # Excellente mémoire

priorities:
  P0:
    sla_hours: 2              # SLA très court
  P1:
    sla_hours: 12
  P2:
    sla_hours: 24
  P3:
    sla_hours: 48

warranty:
  structure:
    duration_years: 10        # Garantie généreuse
  fabric:
    duration_years: 5
  mechanisms:
    duration_years: 7

upload:
  max_file_size_mb: 50        # Fichiers haute résolution
  max_files_per_request: 20

notifications:
  send_email_on_ticket_creation: true
  send_sms_for_urgent_tickets: true  # SMS pour P0/P1
```

### `dashboard_config.yaml`

```yaml
appearance:
  theme:
    primary: "#1F2937"
    secondary: "#D4AF37"
    success: "#10B981"

statistics:
  total_tickets:
    enabled: true
  critical_tickets:
    enabled: true
  urgent_tickets:
    enabled: true
  auto_resolved:
    enabled: true
  average_resolution_time:
    enabled: true             # Statistiques avancées
  satisfaction_rate:
    enabled: true

actions:
  view_details:
    enabled: true
  edit:
    enabled: true
  delete:
    enabled: true
  mark_resolved:
    enabled: true
  assign:
    enabled: true             # Assignation agents

export:
  enabled: true
  formats:
    - "csv"
    - "excel"
    - "pdf"
```

---

## 3. Configuration Multilingue

**Cas d'usage:** Entreprise internationale, support en plusieurs langues

### `chatbot_config.yaml`

```yaml
messages:
  welcome:
    fr: "👋 Bonjour ! Je suis votre assistant SAV."
    en: "👋 Hello! I am your customer support assistant."
    ar: "👋 مرحباً! أنا مساعد خدمة العملاء."
    es: "👋 ¡Hola! Soy tu asistente de atención al cliente."
    de: "👋 Hallo! Ich bin Ihr Kundenservice-Assistent."

  request_photos:
    fr: "📸 Avez-vous des photos du problème ?"
    en: "📸 Do you have photos of the problem?"
    ar: "📸 هل لديك صور للمشكلة؟"
    es: "📸 ¿Tiene fotos del problema?"
    de: "📸 Haben Sie Fotos des Problems?"

detection:
  sav_keywords:
    # Français
    - "problème"
    - "défaut"
    - "cassé"
    # English
    - "problem"
    - "defect"
    - "broken"
    # العربية
    - "مشكلة"
    - "عيب"
    - "مكسور"
    # Español
    - "problema"
    - "defecto"
    - "roto"
    # Deutsch
    - "problem"
    - "fehler"
    - "kaputt"

voice:
  speech_enabled: true
  voice_input_enabled: true
  default_voice_language: "fr-FR"
  supported_languages:
    - "fr-FR"
    - "en-US"
    - "ar-SA"
    - "es-ES"
    - "de-DE"
```

---

## 4. Configuration Économique (Réduction Coûts)

**Cas d'usage:** Minimiser les coûts OpenAI tout en gardant un service acceptable

### `chatbot_config.yaml`

```yaml
ai:
  model: "gpt-3.5-turbo"      # 10x moins cher que GPT-4
  temperature: 0.5            # Moins créatif = plus prévisible
  max_tokens: 300             # Réponses courtes
  history_limit: 4            # Peu de mémoire

messages:
  welcome:
    fr: "👋 Bonjour ! Décrivez votre problème avec votre numéro de commande."
    # Message court pour économiser tokens

detection:
  # Mots-clés minimaux mais efficaces
  sav_keywords:
    - "probleme"              # Sans accent (économie)
    - "casse"
    - "cmd-"
    - "commande"

upload:
  max_file_size_mb: 3         # Petits fichiers
  max_files_per_request: 3

rate_limit:
  messages_per_minute: 10     # Limiter usage
  uploads_per_hour: 20

analytics:
  keep_conversation_history: true
  history_retention_days: 30  # Courte rétention
```

**💡 Économies estimées:**
- GPT-3.5 vs GPT-4: **90% d'économie**
- max_tokens 300 vs 800: **60% d'économie**
- history_limit 4 vs 10: **60% d'économie sur contexte**
- **Total: ~95% d'économie par conversation**

---

## 5. Configuration Support Rapide (SLA Courts)

**Cas d'usage:** Service client réactif, engagement fort sur les délais

### `chatbot_config.yaml`

```yaml
priorities:
  P0:
    label: "🔴 URGENT"
    sla_hours: 1              # 1 heure !
    keywords:
      - "urgent"
      - "immédiat"
      - "danger"
      - "cassé"

  P1:
    label: "🟠 PRIORITAIRE"
    sla_hours: 4
    keywords:
      - "rapidement"
      - "important"
      - "ne fonctionne pas"

  P2:
    label: "🟡 NORMAL"
    sla_hours: 12

  P3:
    label: "🟢 FAIBLE"
    sla_hours: 24

notifications:
  send_email_on_ticket_creation: true
  send_sms_for_urgent_tickets: true   # SMS immédiat pour P0

  browser_notifications:
    enabled: true
    for_priorities: ["P0", "P1"]      # Alertes navigateur
```

### `dashboard_config.yaml`

```yaml
notifications:
  auto_refresh:
    enabled: true
    interval_seconds: 10      # Refresh très fréquent

  sound_alerts:
    enabled: true             # Son pour nouveaux tickets

  browser_notifications:
    enabled: true
    for_priorities: ["P0"]

  tab_badge:
    enabled: true             # Badge sur onglet

columns:
  order:
    - "priority"              # Priorité en premier
    - "ticket_id"
    - "customer"
    - "problem"
    - "sla_remaining"         # Temps restant SLA
    - "status"
    - "actions"
```

---

## 🚀 Comment Appliquer un Exemple

1. **Copier** les sections pertinentes d'un exemple
2. **Coller** dans vos fichiers `chatbot_config.yaml` et `dashboard_config.yaml`
3. **Adapter** selon vos besoins spécifiques
4. **Valider** avec `python config/validate_config.py`
5. **Appliquer** avec `docker-compose restart`

---

## 💡 Conseils de Personnalisation

### Mix & Match
Vous pouvez combiner des éléments de plusieurs exemples:
- SLA de l'exemple Premium + Économie de coûts
- Messages multilingues + Configuration minimaliste

### Test en Deux Phases
1. **Phase 1**: Commencez avec une config économique
2. **Phase 2**: Améliorez progressivement selon les retours

### Priorités Business
Choisissez vos paramètres selon vos priorités:
- **Budget limité** → Exemple Économique
- **Image de marque** → Exemple Premium
- **International** → Exemple Multilingue
- **Réactivité** → Exemple Support Rapide

---

**Dernière mise à jour:** 10 décembre 2024
