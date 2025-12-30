# 📋 Guide d'Utilisation du Formulaire Client

## 🎯 Vue d'Ensemble

Ce système permet à votre client de remplir un simple formulaire texte, puis vous générez automatiquement toute la configuration du chatbot.

**Avantages:**
- ✅ Client n'a pas besoin de connaître YAML
- ✅ Formulaire en français, simple à remplir
- ✅ Génération automatique en 1 commande
- ✅ Backups automatiques des anciennes configurations
- ✅ Validation automatique

---

## 🔄 Workflow Complet

```
1. Client remplit FORMULAIRE_CLIENT.txt
   ↓
2. Client vous envoie le formulaire
   ↓
3. Vous lancez: python config/generer_config.py
   ↓
4. Configs générées automatiquement
   ↓
5. Vous appliquez: docker-compose restart
   ↓
6. Chatbot configuré selon les préférences du client !
```

---

## 📝 Étape 1: Client Remplit le Formulaire

### Fichier à Envoyer au Client

**`FORMULAIRE_CLIENT.txt`** - Un simple fichier texte avec 40 questions

Le client remplit des champs comme:
```
ENTREPRISE_NOM = Ma Super Entreprise
ENTREPRISE_EMAIL_SAV = sav@mon-entreprise.fr
COULEUR_PRINCIPALE = #0066CC
MESSAGE_ACCUEIL_FR = Bonjour ! Comment puis-je vous aider ?
MODELE_IA = gpt-3.5-turbo
SLA_P0_HEURES = 4
GARANTIE_STRUCTURE_ANNEES = 5
```

### Ce que Le Client Configure

- 🏢 **Informations entreprise** (nom, email, téléphone)
- 🎨 **Couleurs** (principale, secondaire, accent)
- 💬 **Messages d'accueil** (FR, EN, AR)
- 🧠 **IA** (modèle, budget, longueur réponses)
- 🎯 **Priorités & SLA** (délais P0 à P3)
- 🛡️ **Garanties** (durées par composant)
- 📤 **Upload** (taille max, nombre de fichiers)
- 🔔 **Notifications** (email, SMS)
- 📊 **Dashboard** (titre, colonnes, refresh)
- 🎤 **Voix** (synthèse, reconnaissance)

---

## ⚙️ Étape 2: Vous Générez la Configuration

### Commande Simple

```bash
cd config
python generer_config.py
```

### Sortie Attendue

```
============================================================
🔧 GÉNÉRATEUR DE CONFIGURATION DEPUIS FORMULAIRE
============================================================

ℹ️  Backup créé: backup/chatbot_config_20251210_164708.yaml
ℹ️  Backup créé: backup/dashboard_config_20251210_164708.yaml

============================================================
📝 Lecture du formulaire client
============================================================

✅ 40 paramètres lus depuis le formulaire

============================================================
🤖 Génération chatbot_config.yaml
============================================================

✅ Fichier généré: config/chatbot_config.yaml
ℹ️    - Entreprise: Ma Super Entreprise
ℹ️    - Modèle IA: gpt-3.5-turbo
ℹ️    - SLA P0: 4h

============================================================
📊 Génération dashboard_config.yaml
============================================================

✅ Fichier généré: config/dashboard_config.yaml
ℹ️    - Titre: Tableau de Bord SAV
ℹ️    - Couleur: #0066CC
ℹ️    - Colonnes: 7

============================================================
✅ GÉNÉRATION TERMINÉE
============================================================

✅ Les configurations ont été générées avec succès !

Prochaines étapes:
  1. Vérifier les fichiers générés
  2. Valider: python config/validate_config.py
  3. Appliquer: docker-compose restart

💾 Backups sauvegardés dans: config/backup
```

---

## ✅ Étape 3: Validation (Optionnelle mais Recommandée)

```bash
python config/validate_config.py
```

**Si tout est OK:**
```
✅ Toutes les configurations sont valides ! 🎉
ℹ️  Vous pouvez appliquer les changements avec:
    docker-compose restart
```

---

## 🚀 Étape 4: Application

```bash
cd ..  # Retour racine projet
docker-compose restart
```

**Résultat:** Le chatbot redémarre avec la nouvelle configuration ! 🎉

---

## 📦 Structure des Fichiers

```
config/
├── FORMULAIRE_CLIENT.txt          ← Client remplit celui-ci
├── generer_config.py              ← Vous lancez celui-ci
├── chatbot_config.yaml            ← Généré automatiquement
├── dashboard_config.yaml          ← Généré automatiquement
├── validate_config.py             ← Pour valider
└── backup/                        ← Backups automatiques
    ├── chatbot_config_20251210_164708.yaml
    └── dashboard_config_20251210_164708.yaml
```

---

## 🎓 Exemples de Personnalisation

### Exemple 1: Client veut un chatbot économique

**Formulaire:**
```
MODELE_IA = gpt-3.5-turbo
BUDGET_IA = faible
LONGUEUR_REPONSES = courte
MODE_ECONOMIE = oui
```

**Résultat généré:**
- Modèle: gpt-3.5-turbo (90% moins cher que GPT-4)
- max_tokens: 300 (réponses courtes)
- history_limit: 4 (peu de mémoire)

### Exemple 2: Client veut service premium

**Formulaire:**
```
MODELE_IA = gpt-4
BUDGET_IA = élevé
LONGUEUR_REPONSES = longue
SLA_P0_HEURES = 2
GARANTIE_STRUCTURE_ANNEES = 10
```

**Résultat généré:**
- Modèle: gpt-4 (meilleur mais cher)
- max_tokens: 800 (réponses détaillées)
- SLA P0: 2 heures
- Garantie structure: 10 ans

### Exemple 3: Client veut personnaliser les couleurs

**Formulaire:**
```
COULEUR_PRINCIPALE = #0066CC
COULEUR_SECONDAIRE = #FF6600
COULEUR_ACCENT = #00CC66
```

**Résultat généré:**
- Chatbot et Dashboard utilisent ces couleurs
- Branding cohérent partout

---

## 🛠️ Fonctionnalités Avancées

### Backups Automatiques

Chaque génération sauvegarde les anciennes configs dans `config/backup/`:
```
backup/chatbot_config_YYYYMMDD_HHMMSS.yaml
backup/dashboard_config_YYYYMMDD_HHMMSS.yaml
```

**Pour restaurer un backup:**
```bash
cd config
cp backup/chatbot_config_20251210_164708.yaml chatbot_config.yaml
cp backup/dashboard_config_20251210_164708.yaml dashboard_config.yaml
docker-compose restart
```

### Mots-Clés Personnalisés

Le client peut ajouter ses propres mots-clés:
```
MOTS_CLES_SAV_SUPPLEMENTAIRES = réclamation,insatisfait,remboursement
MOTS_CLES_SHOPPING_SUPPLEMENTAIRES = devis,catalogue,promotion
```

Ils seront automatiquement ajoutés à la détection.

---

## 📧 Email à Envoyer au Client

```
Objet: Configuration de Votre Chatbot SAV

Bonjour,

Pour personnaliser votre chatbot SAV, veuillez:

1. Télécharger le fichier joint: FORMULAIRE_CLIENT.txt
2. Ouvrir avec Notepad/Word/n'importe quel éditeur texte
3. Remplir les champs (les champs [OBLIGATOIRE] sont requis)
4. Me renvoyer le fichier rempli

Le formulaire contient 40 questions simples sur:
- Nom de votre entreprise et coordonnées
- Couleurs de votre charte graphique
- Messages d'accueil personnalisés
- Délais de réponse (SLA)
- Garanties produits
- Et plus encore...

Je générerai ensuite la configuration automatiquement et vous livrerai
le chatbot configuré selon vos préférences !

⏱️ Temps de remplissage: 15-20 minutes
📝 Format: Simple fichier texte

Questions ? N'hésitez pas !

Cordialement,
[Votre nom]
```

---

## 🔧 Dépannage

### Erreur: "Fichier formulaire introuvable"

**Cause:** Le fichier FORMULAIRE_CLIENT.txt n'est pas au bon endroit

**Solution:**
```bash
# Vérifier qu'il est dans config/
ls config/FORMULAIRE_CLIENT.txt

# S'il manque, le créer depuis le template
cp FORMULAIRE_CLIENT_TEMPLATE.txt config/FORMULAIRE_CLIENT.txt
```

### Erreur lors de la génération

**Cause:** Valeur invalide dans le formulaire

**Solution:**
- Vérifier que les nombres sont bien des nombres
- Vérifier que les couleurs commencent par `#`
- Vérifier que oui/non est bien écrit

### Config générée mais chatbot ne démarre pas

**Solution:**
```bash
# 1. Valider la config
python config/validate_config.py

# 2. Vérifier les logs
docker-compose logs backend

# 3. Si nécessaire, restaurer backup
cp config/backup/chatbot_config_[DATE].yaml config/chatbot_config.yaml
docker-compose restart
```

---

## ✅ Checklist de Livraison au Client

Avant d'envoyer le formulaire:

- [ ] `FORMULAIRE_CLIENT.txt` prêt
- [ ] Instructions claires jointes
- [ ] Email d'accompagnement préparé
- [ ] Script `generer_config.py` testé
- [ ] Système de backup vérifié

Après réception du formulaire:

- [ ] Formulaire reçu et complet
- [ ] Génération: `python generer_config.py`
- [ ] Validation: `python validate_config.py`
- [ ] Application: `docker-compose restart`
- [ ] Tests: Vérifier chatbot + dashboard
- [ ] Confirmation client: "Configuration appliquée ✅"

---

## 💡 Conseils

### Pour le Client
- Prenez votre temps pour remplir le formulaire
- Les champs [OPTIONNEL] peuvent rester vides
- Consultez votre charte graphique pour les couleurs
- Définissez des SLA réalistes selon vos ressources

### Pour Vous (Développeur)
- Toujours faire un backup avant génération (automatique ✅)
- Valider avant d'appliquer
- Tester sur environnement de dev d'abord
- Garder les backups pendant 30 jours minimum

---

**Bonne configuration ! 🚀**

*Dernière mise à jour: 10 décembre 2024*
