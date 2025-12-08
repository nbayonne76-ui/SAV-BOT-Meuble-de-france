# 📦 Import des Produits Réels - Meuble de France

## 🎯 Objectif

Remplacer le catalogue fictif par les **vrais produits** du site mobilierdefrance.com

---

## 🚀 Méthode 1: Import Automatique (RECOMMANDÉ)

### Étapes:

**1. Double-cliquez sur:** `IMPORTER_PRODUITS.bat`

Le script va:
- ✅ Installer BeautifulSoup4 et lxml
- ✅ Scraper le site mobilierdefrance.com
- ✅ Extraire les 139 canapés d'angle
- ✅ Générer le nouveau `catalog.json`

**2. Attendez 1-2 minutes**

Vous verrez:
```
🔍 Scraping: https://www.mobilierdefrance.com/canapes-d-angle
✅ Trouvé 139 produits
  [1/139] ✅ Canapé d'angle Modèle X
  [2/139] ✅ Canapé d'angle Modèle Y
  ...
✅ Catalogue sauvegardé: backend/data/catalog.json
```

**3. Relancez le chatbot**
```
START_ALL.bat
```

---

## 🔧 Méthode 2: Import Manuel (Si scraping échoue)

### Format CSV Requis:

Créez un fichier `produits.csv` avec ces colonnes:

```csv
nom,reference,prix,categorie,lien,image
"Canapé d'angle Harmonie","MDF-CAP-001","1899€","Canapés d'angle","https://...","https://..."
"Canapé d'angle Élégance","MDF-CAP-002","2299€","Canapés d'angle","https://...","https://..."
```

### Étapes:

1. Exportez vos produits en CSV
2. Placez le fichier dans: `backend/data/produits.csv`
3. Lancez le script d'import manuel:

```bash
cd backend
venv\Scripts\activate
python scripts\import_csv.py
```

---

## 🔍 Vérification du Catalogue

### Vérifier le fichier:

```bash
# Windows
type backend\data\catalog.json

# Ou ouvrir dans VS Code
code backend\data\catalog.json
```

### Structure attendue:

```json
{
  "catalog_version": "2.0.0",
  "last_updated": "2025-12-04",
  "source": "mobilierdefrance.com",
  "categories": {
    "salon": {
      "name": "Salon",
      "products": [
        {
          "id": "MDF-CAP-001",
          "name": "Canapé d'angle Harmonie",
          "price_range": "1899€",
          "link": "https://www.mobilierdefrance.com/...",
          "category": "Canapés d'angle"
        }
      ]
    }
  }
}
```

---

## 🧪 Tester le Chatbot avec Vrais Produits

### Test 1: Demande générale

**User:** "Je cherche un canapé d'angle"

**Chatbot devrait:**
- Poser des questions sur style, budget, dimensions
- Recommander des produits réels du catalogue
- Fournir des liens directs vers mobilierdefrance.com

### Test 2: Référence spécifique

**User:** "Parlez-moi du canapé [REFERENCE_REELLE]"

**Chatbot devrait:**
- Reconnaître la référence
- Donner les détails du produit
- Fournir le lien direct

---

## ⚠️ Problèmes Courants

### 1. "Aucun produit trouvé avec les sélecteurs standards"

**Cause:** Structure HTML du site a changé

**Solution:**
1. Le script a généré `mobilierdefrance_html.txt`
2. Ouvrez ce fichier
3. Identifiez les classes CSS des produits
4. Mettez à jour `scripts/scraper_mobilier_france.py` ligne 51:

```python
product_selectors = [
    '.votre-classe-css',  # Ajoutez vos sélecteurs ici
    '.product-item',
    ...
]
```

### 2. "HTTP 403 Forbidden"

**Cause:** Le site bloque le scraping

**Solutions:**
- Utilisez l'import manuel (CSV)
- Demandez accès à l'API interne
- Contactez l'équipe e-commerce pour export

### 3. "Produits sans prix"

**Cause:** Prix dynamiques (JavaScript)

**Solution:**
- Ajoutez "Prix sur demande" pour ces produits
- Le chatbot redirigera vers le site pour voir le prix

---

## 📊 Données Extraites par le Scraper

Pour chaque produit:

| Donnée | Source | Exemple |
|--------|--------|---------|
| Nom | Titre produit | "Canapé d'angle Harmonie" |
| Référence | SKU/data-sku | "MDF-CAP-001" |
| Prix | Classe .price | "1899€" |
| Lien | href du produit | https://... |
| Image | src de l'image | https://.../image.jpg |
| Catégorie | Page source | "Canapés d'angle" |

---

## 🔄 Mise à Jour Régulière

### Automatiser l'import hebdomadaire:

**Windows Task Scheduler:**

1. Ouvrir "Planificateur de tâches"
2. Créer une tâche:
   - Déclencheur: Tous les lundis à 2h
   - Action: `C:\...\IMPORTER_PRODUITS.bat`
3. Le catalogue sera mis à jour automatiquement

---

## 🆘 Support

### Si le scraping ne fonctionne pas:

**Option A: Import Manuel**
- Exportez votre catalogue en CSV
- Utilisez la méthode 2 ci-dessus

**Option B: API Integration**
- Si vous avez une API interne
- Créez un endpoint `/api/products`
- Le chatbot l'interrogera directement

**Option C: Base de Données Directe**
- Connectez le chatbot à votre BDD produits
- Configurez `backend/.env`:
```env
DATABASE_URL=postgresql://user:pass@host/db
```

---

## 📈 Résultats Attendus

### Avant (Catalogue Fictif):
```
User: "Référence SAL-CAP-001"
Bot: "Je suis désolé, je ne trouve pas cette référence..."
```

### Après (Catalogue Réel):
```
User: "Référence MDF-CAP-001"
Bot: "Le Canapé d'angle Harmonie est disponible à partir de 1899€.
Voir les détails: https://www.mobilierdefrance.com/..."
```

---

## ✅ Checklist de Vérification

- [ ] IMPORTER_PRODUITS.bat exécuté sans erreur
- [ ] backend/data/catalog.json contient les vrais produits
- [ ] Les références commencent par "MDF-" (ou vos vraies références)
- [ ] Les prix sont réels
- [ ] Les liens pointent vers mobilierdefrance.com
- [ ] START_ALL.bat relancé
- [ ] Test avec une vraie référence réussie

---

**Créé le:** 2025-12-04
**Version:** 1.0
**Auteur:** Claude Code
