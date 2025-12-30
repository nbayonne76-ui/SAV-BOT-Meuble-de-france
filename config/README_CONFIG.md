# 📖 Guide de Configuration du SAV Bot

Ce dossier contient les fichiers de configuration permettant de personnaliser entièrement le chatbot SAV et le tableau de bord **sans modifier le code source**.

---

## 📁 Fichiers de Configuration

### 1. `chatbot_config.yaml` - Configuration du Chatbot
Personnalise le comportement, les messages, et l'intelligence du chatbot.

**Sections principales:**
- 🏢 **Informations entreprise** - Nom, contact, branding
- 💬 **Messages** - Accueil, erreurs, confirmations (multilingue)
- 🧠 **Paramètres IA** - Modèle OpenAI, créativité, longueur réponses
- 🔍 **Détection** - Mots-clés pour SAV vs Shopping
- 🎯 **Priorités** - P0 à P3, SLA, mots-clés
- 🛡️ **Garanties** - Durées par composant, exclusions
- 📤 **Upload** - Taille max, formats autorisés
- 🎤 **Voix** - Synthèse vocale, reconnaissance vocale

### 2. `dashboard_config.yaml` - Configuration du Tableau de Bord
Personnalise l'apparence et les fonctionnalités du dashboard SAV.

**Sections principales:**
- 🎨 **Apparence** - Thème, couleurs, logo
- 📈 **Statistiques** - Cartes affichées en haut
- 🔽 **Filtres** - Priorité, statut, date
- 📋 **Colonnes** - Ordre, largeur, tri
- 🔘 **Actions** - Boutons disponibles (voir, éditer, supprimer)
- 📄 **Modal** - Sections du popup détails
- 🎯 **Statuts** - Labels, couleurs, icônes
- 🔔 **Notifications** - Auto-refresh, alertes
- 📤 **Export** - CSV, Excel, PDF

---

## 🚀 Comment Utiliser

### Étape 1: Modifier les fichiers YAML

Ouvrez les fichiers `.yaml` avec n'importe quel éditeur de texte:
- **Windows**: Notepad++, VS Code
- **Mac**: TextEdit, VS Code
- **Linux**: nano, vim, gedit

**⚠️ IMPORTANT:**
- Respectez l'indentation (utilisez des espaces, PAS de tabulations)
- Ne supprimez pas les `:` après les noms de champs
- Les textes avec caractères spéciaux doivent être entre guillemets `"`

### Étape 2: Valider la syntaxe YAML

Avant d'appliquer, vérifiez que votre YAML est valide:
- En ligne: https://www.yamllint.com/
- Ou utilisez l'outil de validation fourni (voir ci-dessous)

### Étape 3: Appliquer les changements

Après modification des fichiers:

```bash
# Redémarrer le backend (pour chatbot_config.yaml)
docker-compose restart backend

# Redémarrer le frontend (pour dashboard_config.yaml)
docker-compose restart frontend

# Ou redémarrer tout
docker-compose restart
```

---

## 📝 Exemples de Personnalisation Courante

### Exemple 1: Changer le nom de l'entreprise

**Fichier:** `chatbot_config.yaml`

```yaml
company:
  name: "Votre Entreprise"  # ← Modifiez ici
  short_name: "VE"
  support_email: "sav@votreentreprise.fr"
```

### Exemple 2: Modifier le message d'accueil

**Fichier:** `chatbot_config.yaml`

```yaml
messages:
  welcome:
    fr: "👋 Bonjour ! Je suis l'assistant SAV de Votre Entreprise..."
```

### Exemple 3: Changer le modèle IA (réduire les coûts)

**Fichier:** `chatbot_config.yaml`

```yaml
ai:
  model: "gpt-3.5-turbo"  # Moins cher
  # model: "gpt-4"        # Plus cher mais meilleur
```

### Exemple 4: Ajouter un mot-clé de détection SAV

**Fichier:** `chatbot_config.yaml`

```yaml
detection:
  sav_keywords:
    - "problème"
    - "défaut"
    - "mon_nouveau_mot_cle"  # ← Ajoutez ici
```

### Exemple 5: Modifier les couleurs du dashboard

**Fichier:** `dashboard_config.yaml`

```yaml
appearance:
  theme:
    primary: "#DC2626"    # Rouge → Changez en #0066CC pour bleu
    secondary: "#F97316"  # Orange → Changez selon votre charte
```

### Exemple 6: Changer le SLA pour tickets P0

**Fichier:** `chatbot_config.yaml`

```yaml
priorities:
  P0:
    label: "Critique"
    sla_hours: 4  # ← Modifiez (ex: 2 pour 2 heures)
```

### Exemple 7: Activer l'export de données

**Fichier:** `dashboard_config.yaml`

```yaml
export:
  enabled: true  # ← Passez de false à true
  formats:
    - "csv"
    - "excel"
```

### Exemple 8: Désactiver une colonne du tableau

**Fichier:** `dashboard_config.yaml`

```yaml
columns:
  tone:
    enabled: false  # ← Passe de true à false pour cacher
```

---

## 🛠️ Outil de Validation

Pour vérifier que vos modifications sont correctes:

```bash
# Depuis le dossier racine du projet
python config/validate_config.py
```

Cet outil vérifiera:
- ✅ Syntaxe YAML valide
- ✅ Tous les champs requis présents
- ✅ Types de données corrects
- ✅ Valeurs dans les plages autorisées

---

## 🔧 Dépannage

### Problème: Le bot ne démarre plus après modification

**Solution:**
1. Vérifiez la syntaxe YAML (indentation, guillemets)
2. Vérifiez les logs: `docker-compose logs backend`
3. Restaurez la version précédente du fichier
4. Validez avec l'outil de validation

### Problème: Les changements ne s'appliquent pas

**Solution:**
1. Vérifiez que vous avez bien redémarré les services
2. Videz le cache du navigateur (Ctrl+Shift+R)
3. Vérifiez les logs pour erreurs

### Problème: Erreur "Invalid YAML syntax"

**Solution:**
- Utilisez des espaces, pas des tabulations
- Vérifiez que les `:` sont bien présents
- Mettez les valeurs avec caractères spéciaux entre guillemets

---

## 📚 Ressources

- **Documentation YAML**: https://yaml.org/
- **Validateur YAML en ligne**: https://www.yamllint.com/
- **Guide OpenAI Models**: https://platform.openai.com/docs/models
- **Tailwind Colors** (pour personnaliser couleurs): https://tailwindcss.com/docs/customizing-colors

---

## 🆘 Support

Pour toute question sur la configuration:
1. Consultez les commentaires dans les fichiers YAML
2. Vérifiez les exemples ci-dessus
3. Contactez le développeur: v-nbayonne@example.com

---

## 📋 Checklist de Mise en Production

Avant de déployer en production, vérifiez:

- [ ] Nom et coordonnées de l'entreprise modifiés
- [ ] Messages d'accueil personnalisés
- [ ] Modèle IA choisi (gpt-3.5-turbo pour économie)
- [ ] Mots-clés de détection adaptés à votre activité
- [ ] SLA définis selon vos engagements clients
- [ ] Garanties configurées selon vos produits
- [ ] Couleurs du dashboard selon votre charte graphique
- [ ] Colonnes du tableau adaptées à vos besoins
- [ ] Notifications configurées
- [ ] Configuration validée avec l'outil
- [ ] Tests effectués sur environnement de dev
- [ ] Backup des fichiers de config

---

**Dernière mise à jour:** 10 décembre 2024
**Version:** 1.0.0
