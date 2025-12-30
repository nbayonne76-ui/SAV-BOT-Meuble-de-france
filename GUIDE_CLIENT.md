# 🎯 Guide Rapide pour le Client

## 📦 Bienvenue !

Vous avez reçu le **système de configuration** de votre chatbot SAV. Ce guide vous explique comment personnaliser facilement votre chatbot et tableau de bord.

---

## 📁 Fichiers Reçus

Vous devriez avoir le dossier `config/` contenant:

```
config/
├── chatbot_config.yaml      ← Configuration du chatbot
├── dashboard_config.yaml    ← Configuration du tableau de bord
├── README.md                ← Vue d'ensemble
├── README_CONFIG.md         ← Guide complet
├── EXAMPLES.md              ← 5 exemples prêts à l'emploi
└── validate_config.py       ← Outil de validation
```

---

## 🚀 Démarrage en 3 Étapes

### Étape 1: Installer Python et PyYAML

Si pas déjà installé:

**Windows:**
```bash
# Installer Python depuis https://www.python.org/downloads/
# Puis installer PyYAML:
pip install pyyaml
```

**Mac/Linux:**
```bash
pip3 install pyyaml
```

### Étape 2: Modifier les Configurations

Ouvrez les fichiers avec **Notepad**, **VS Code**, ou n'importe quel éditeur de texte:

```
📝 chatbot_config.yaml     → Messages, IA, priorités, garanties
📝 dashboard_config.yaml   → Apparence, colonnes, filtres
```

**⚠️ IMPORTANT:**
- Utilisez des **espaces** (pas de tabulations)
- Ne supprimez pas les **`:`** après les noms de champs
- Mettez les textes entre **guillemets** `"` si caractères spéciaux

### Étape 3: Valider et Appliquer

Après modification:

```bash
# 1. Valider vos modifications
cd config
python validate_config.py

# 2. Si validation OK, appliquer:
cd ..
docker-compose restart
```

---

## 💡 Modifications Courantes

### 1. Changer le Nom de l'Entreprise

**Fichier:** `chatbot_config.yaml`

```yaml
company:
  name: "Votre Entreprise"        # ← Modifier ici
  short_name: "VE"
  support_email: "sav@votre-entreprise.fr"
  support_phone: "+33 1 23 45 67 89"
```

### 2. Modifier le Message d'Accueil

**Fichier:** `chatbot_config.yaml`

```yaml
messages:
  welcome:
    fr: "👋 Bonjour ! Je suis votre assistant SAV..."  # ← Modifier
```

### 3. Changer les Couleurs

**Fichier:** `dashboard_config.yaml`

```yaml
appearance:
  theme:
    primary: "#0066CC"    # Bleu - Remplacer par votre couleur
    secondary: "#FF6600"  # Orange
```

### 4. Réduire les Coûts OpenAI

**Fichier:** `chatbot_config.yaml`

```yaml
ai:
  model: "gpt-3.5-turbo"  # Au lieu de "gpt-4"
  max_tokens: 300         # Au lieu de 500
```

**💰 Économies:** 90-95% des coûts

### 5. Modifier les SLA

**Fichier:** `chatbot_config.yaml`

```yaml
priorities:
  P0:
    sla_hours: 4  # ← Modifier (ex: 2 pour 2 heures)
  P1:
    sla_hours: 24
```

---

## 🎨 Utiliser les Exemples Prêts à l'Emploi

Le fichier **`EXAMPLES.md`** contient 5 configurations complètes:

1. **Startup** - Configuration minimaliste
2. **Premium** - Service haut de gamme
3. **Multilingue** - Support FR/EN/AR/ES/DE
4. **Économique** - Réduction 95% des coûts
5. **Support Rapide** - SLA ultra-courts

**Comment utiliser:**
1. Ouvrez `EXAMPLES.md`
2. Copiez la section qui vous intéresse
3. Collez dans votre fichier de config
4. Validez avec `python validate_config.py`
5. Appliquez avec `docker-compose restart`

---

## ✅ Validation des Modifications

**Toujours valider avant d'appliquer:**

```bash
cd config
python validate_config.py
```

**Sortie attendue:**
```
✅ Toutes les configurations sont valides ! 🎉
ℹ️  Vous pouvez appliquer les changements avec:
    docker-compose restart
```

**Si erreurs:**
```
❌ 2 erreur(s) trouvée(s):
  - Modèle IA invalide: gpt-5
  - Temperature invalide: 1.5
```

Corrigez les erreurs puis re-validez.

---

## 🔧 Dépannage

### Le chatbot ne démarre plus

```bash
# Vérifier les logs
docker-compose logs backend

# Valider la config
python config/validate_config.py

# Restaurer version précédente si nécessaire
git checkout config/chatbot_config.yaml
```

### Les changements ne s'affichent pas

```bash
# Redémarrer
docker-compose restart

# Vider cache navigateur: Ctrl+Shift+R
```

### Erreur "Invalid YAML syntax"

**Problèmes fréquents:**
- ❌ Tabulations → Utilisez des espaces
- ❌ Mauvaise indentation
- ❌ `:` manquant
- ❌ Guillemets manquants

**Exemple correct:**
```yaml
company:
  name: "Mon Entreprise"  # ← Correct
```

**Exemple incorrect:**
```yaml
company
    name Mon Entreprise  # ← Incorrect (manque : et ")
```

---

## 📚 Documentation Complète

| Fichier | Contenu |
|---------|---------|
| **README.md** | Vue d'ensemble et démarrage rapide |
| **README_CONFIG.md** | Guide complet avec tous les paramètres |
| **EXAMPLES.md** | 5 configurations complètes prêtes à l'emploi |

---

## 📞 Support

Pour toute question:

1. 📖 Consultez **README_CONFIG.md** (guide détaillé)
2. 💡 Inspirez-vous de **EXAMPLES.md**
3. 🔍 Validez avec `python validate_config.py`
4. 📧 Contactez votre développeur si problème

---

## 🎯 Checklist de Personnalisation

Avant de mettre en production:

- [ ] Nom de l'entreprise modifié
- [ ] Email et téléphone SAV mis à jour
- [ ] Messages d'accueil personnalisés
- [ ] Couleurs adaptées à votre charte graphique
- [ ] Modèle IA choisi (gpt-3.5-turbo ou gpt-4)
- [ ] SLA définis selon vos engagements
- [ ] Garanties configurées selon vos produits
- [ ] Mots-clés ajustés à votre vocabulaire
- [ ] Configuration validée ✅
- [ ] Tests effectués ✅

---

## 🚀 Workflow Recommandé

```
1. Éditer les fichiers .yaml
   ↓
2. Valider: python validate_config.py
   ↓
3. Appliquer: docker-compose restart
   ↓
4. Tester sur http://localhost:5173
   ↓
5. Ajuster si nécessaire
```

---

**Bonne configuration ! 🎉**

*Si vous avez des questions, consultez la documentation complète dans `config/README_CONFIG.md`*

---

**Date:** 10 décembre 2024
**Version:** 1.0.0
