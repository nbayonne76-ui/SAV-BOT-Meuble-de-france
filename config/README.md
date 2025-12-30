# 🎛️ Système de Configuration du SAV Bot

Bienvenue dans le système de configuration centralisé du SAV Bot ! Ce dossier contient tous les fichiers nécessaires pour personnaliser votre chatbot et tableau de bord **sans toucher au code source**.

---

## 📚 Fichiers Disponibles

### 📄 Fichiers de Configuration (YAML)

| Fichier | Description | Que configure-t-il ? |
|---------|-------------|---------------------|
| **`chatbot_config.yaml`** | Configuration du chatbot | Messages, IA, détection, priorités, garanties |
| **`dashboard_config.yaml`** | Configuration du tableau de bord | Apparence, colonnes, filtres, actions, statuts |

### 📖 Documentation

| Fichier | Contenu |
|---------|---------|
| **`README_CONFIG.md`** | Guide complet d'utilisation des configurations |
| **`EXAMPLES.md`** | Exemples prêts à l'emploi (Startup, Premium, Multilingue, etc.) |
| **`README.md`** | Ce fichier - Vue d'ensemble |

### 🛠️ Outils

| Fichier | Usage |
|---------|-------|
| **`validate_config.py`** | Script Python pour valider vos configurations avant application |

---

## 🚀 Démarrage Rapide

### 1️⃣ Première Utilisation

```bash
# 1. Installez PyYAML (nécessaire pour la validation)
pip install pyyaml

# 2. Explorez les fichiers de configuration
notepad config/chatbot_config.yaml
notepad config/dashboard_config.yaml

# 3. Lisez les exemples pour vous inspirer
notepad config/EXAMPLES.md

# 4. Modifiez selon vos besoins
# ... éditez les fichiers YAML ...

# 5. Validez vos modifications
python config/validate_config.py

# 6. Appliquez les changements
docker-compose restart
```

### 2️⃣ Workflow Recommandé

```
📝 Éditer → 🔍 Valider → ✅ Appliquer → 🧪 Tester
```

1. **Éditer** les fichiers `.yaml` avec votre éditeur préféré
2. **Valider** avec `python config/validate_config.py`
3. **Appliquer** avec `docker-compose restart`
4. **Tester** en ouvrant le chatbot et le dashboard

---

## 💡 Cas d'Usage Fréquents

### Changer le nom de l'entreprise
```yaml
# Fichier: chatbot_config.yaml
company:
  name: "Mon Entreprise"
  short_name: "ME"
```

### Réduire les coûts OpenAI
```yaml
# Fichier: chatbot_config.yaml
ai:
  model: "gpt-3.5-turbo"  # Au lieu de gpt-4
  max_tokens: 300         # Au lieu de 500
```

### Personnaliser les couleurs
```yaml
# Fichier: dashboard_config.yaml
appearance:
  theme:
    primary: "#0066CC"    # Votre couleur principale
    secondary: "#FF6600"  # Votre couleur secondaire
```

### Modifier les SLA
```yaml
# Fichier: chatbot_config.yaml
priorities:
  P0:
    sla_hours: 2  # Modifier ici
  P1:
    sla_hours: 12
```

---

## 📊 Structure des Configurations

### chatbot_config.yaml
```
🏢 company          - Infos entreprise
🎨 branding         - Couleurs, logo
💬 messages         - Textes du bot (multilingue)
🧠 ai               - Paramètres OpenAI
🔍 detection        - Mots-clés SAV/Shopping
🎯 priorities       - P0-P3, SLA
🛡️ warranty         - Garanties par composant
📤 upload           - Fichiers autorisés
⏱️ rate_limit       - Protection abus
🎤 voice            - Synthèse/reconnaissance vocale
🔔 notifications    - Emails, SMS
📊 analytics        - Logs, historique
```

### dashboard_config.yaml
```
🎨 appearance       - Thème, couleurs
📈 statistics       - Cartes stats
🔽 filters          - Filtres dispo
📋 columns          - Colonnes tableau
🔘 actions          - Boutons actions
📄 modal            - Popup détails
🎯 statuses         - Statuts tickets
🔔 notifications    - Auto-refresh, alertes
📤 export           - CSV, Excel, PDF
🔐 permissions      - Droits utilisateurs
📱 responsive       - Mobile, tablette
```

---

## ✅ Validation des Configurations

### Pourquoi valider ?
- ✅ Détecte les erreurs de syntaxe YAML
- ✅ Vérifie que tous les champs requis sont présents
- ✅ Valide les types de données
- ✅ Contrôle les plages de valeurs
- ✅ Vérifie la cohérence entre chatbot et dashboard

### Comment valider ?

```bash
cd config
python validate_config.py
```

**Sortie en cas de succès:**
```
✅ Toutes les configurations sont valides ! 🎉
ℹ️  Vous pouvez appliquer les changements avec:
    docker-compose restart
```

**Sortie en cas d'erreur:**
```
❌ 3 erreur(s) trouvée(s):
  - Section manquante: company
  - Modèle IA invalide: gpt-5
  - Temperature invalide: 1.5
```

---

## 🎨 Exemples Prêts à l'Emploi

Le fichier `EXAMPLES.md` contient 5 configurations complètes:

1. **Configuration Minimaliste** - Pour startups avec budget limité
2. **Configuration Premium** - Pour marques luxe avec service d'excellence
3. **Configuration Multilingue** - Support en plusieurs langues
4. **Configuration Économique** - Minimiser les coûts OpenAI (95% d'économie)
5. **Configuration Support Rapide** - SLA très courts, alertes en temps réel

**Comment utiliser:**
1. Ouvrez `EXAMPLES.md`
2. Copiez la section qui vous intéresse
3. Collez dans votre fichier de config
4. Adaptez selon vos besoins

---

## 🔧 Dépannage

### Le bot ne démarre plus après modification

**Cause probable:** Erreur de syntaxe YAML

**Solution:**
```bash
# 1. Vérifier les logs
docker-compose logs backend

# 2. Valider la config
python config/validate_config.py

# 3. Si nécessaire, restaurer la version précédente
git checkout config/chatbot_config.yaml
```

### Les changements ne s'appliquent pas

**Solutions:**
```bash
# 1. Redémarrer les services
docker-compose restart

# 2. Vider cache navigateur
# Ctrl+Shift+R (Chrome/Firefox)

# 3. Reconstruire les containers (si nécessaire)
docker-compose down
docker-compose up -d --build
```

### Erreur "Invalid YAML syntax"

**Problèmes fréquents:**
- ❌ Utilisation de tabulations (utilisez des espaces)
- ❌ Mauvaise indentation
- ❌ `:` manquant après un nom de champ
- ❌ Guillemets manquants pour texte avec caractères spéciaux

**Exemple correct:**
```yaml
company:
  name: "Mon Entreprise"  # ← guillemets + deux-points
  support_email: "sav@example.fr"
```

**Exemple incorrect:**
```yaml
company
    name Mon Entreprise  # ← Manque : et guillemets
```

---

## 📦 Fichiers Requis

Pour que le système fonctionne, vous devez avoir:

- ✅ `config/chatbot_config.yaml` - Configuration chatbot
- ✅ `config/dashboard_config.yaml` - Configuration dashboard
- ✅ PyYAML installé (`pip install pyyaml`)

**Fichiers optionnels:**
- 📖 Documentation (README, EXAMPLES)
- 🛠️ Script de validation

---

## 🔐 Bonnes Pratiques

### Avant de Modifier

1. ✅ **Backup** - Sauvegardez les fichiers originaux
2. ✅ **Git** - Commitez vos changements
3. ✅ **Test** - Testez d'abord en développement

### Pendant la Modification

1. ✅ **Indentation** - Utilisez 2 espaces (pas de tabulations)
2. ✅ **Commentaires** - Les fichiers sont commentés, lisez-les
3. ✅ **Validation** - Validez après chaque modification importante

### Après Modification

1. ✅ **Validation** - `python config/validate_config.py`
2. ✅ **Application** - `docker-compose restart`
3. ✅ **Vérification** - Testez le chatbot et dashboard
4. ✅ **Commit** - Sauvegardez dans git

---

## 📞 Support

Pour toute question:

1. 📖 **Consultez** `README_CONFIG.md` (guide détaillé)
2. 💡 **Inspirez-vous** de `EXAMPLES.md`
3. 🔍 **Validez** avec `validate_config.py`
4. 📧 **Contactez** le développeur si problème persistant

---

## 🎯 Prochaines Étapes

1. ✅ Lisez `README_CONFIG.md` pour le guide complet
2. ✅ Explorez `EXAMPLES.md` pour vous inspirer
3. ✅ Modifiez les fichiers selon vos besoins
4. ✅ Validez avec `python config/validate_config.py`
5. ✅ Appliquez avec `docker-compose restart`
6. ✅ Testez et ajustez

---

**Bonne configuration ! 🚀**

*Dernière mise à jour: 10 décembre 2024*
