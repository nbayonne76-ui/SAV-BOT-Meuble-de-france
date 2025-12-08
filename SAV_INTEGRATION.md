# 🎯 INTÉGRATION SAV COMPLÈTE - Meuble de France Chatbot

## ✅ CE QUI A ÉTÉ INTÉGRÉ

Votre chatbot dispose maintenant d'un système SAV complet avec **9 scénarios détaillés** et une **FAQ évolutive** !

---

## 📋 FICHIERS CRÉÉS

### 1. Base de Connaissances SAV

**[backend/data/sav_scenarios.json](backend/data/sav_scenarios.json)**
- 9 scénarios SAV complets
- Classification par priorité (P0 à P3)
- Questions de diagnostic
- Solutions étape par étape
- Instructions pour photos
- Guidelines pour le chatbot

### 2. FAQ Évolutive

**[backend/data/faq.json](backend/data/faq.json)**
- 15 questions fréquentes
- 5 catégories : Garanties SAV, Livraison, Retour/Échange, Entretien, Paiement
- Structure pour votes (utile/pas utile)
- Statistiques de popularité
- Prêt à être enrichi avec vos vraies données

### 3. Services Backend

**[backend/app/services/sav_knowledge.py](backend/app/services/sav_knowledge.py)**
- Chargement et recherche dans scénarios SAV
- Recherche dans FAQ
- Génération contexte pour l'IA
- Ajout/modification FAQ
- Statistiques

**[backend/app/services/chatbot.py](backend/app/services/chatbot.py)** - MIS À JOUR
- Intégration automatique base SAV
- Contexte dynamique selon message client
- Catalogue produits + SAV dans chaque réponse

### 4. API REST

**[backend/app/api/endpoints/faq.py](backend/app/api/endpoints/faq.py)**
- GET `/api/faq` - Rechercher dans FAQ
- GET `/api/faq/categories` - Liste catégories
- GET `/api/faq/category/{id}` - Questions par catégorie
- POST `/api/faq/vote` - Voter utile/pas utile
- POST `/api/faq/add` - Ajouter question
- GET `/api/faq/stats` - Statistiques

---

## 🎬 LES 9 SCÉNARIOS SAV INTÉGRÉS

### 🔴 PRIORITÉ CRITIQUE (P0) - Réponse <4h

#### SAV-005: Lit coffre - Vérin à gaz défaillant
- **Danger:** Risque de blessure
- **Symptômes:** Sommier retombe brutalement
- **Solution:** Remplacement vérins <24h
- **Mots-clés:** lit, coffre, vérin, retombe, dangereux

---

### 🟠 PRIORITÉ HAUTE (P1) - Réponse <24h

#### SAV-002: Canapé Relax - Mécanisme électrique en panne
- **Produit:** Canapé 3 places Relax (SAL-CAP-002)
- **Symptômes:** Mécanisme ne fonctionne plus
- **Solution:** Technicien domicile 24-48h
- **Garantie:** 5 ans mécanisme
- **Mots-clés:** relax, électrique, mécanisme, moteur, panne

#### SAV-004: Table extensible - Mécanisme bloqué
- **Produit:** Table extensible Moderne (SAM-TAB-001)
- **Symptômes:** Extension papillon ne s'ouvre plus
- **Solution:** Déblocage ou technicien 48-72h
- **Garantie:** 3 ans structure
- **Mots-clés:** table, extension, bloqué, papillon

#### SAV-007: Livraison - Meuble endommagé
- **Urgent:** Procédure immédiate lors livraison
- **Actions:** Ne pas signer, prendre photos, refuser ou réserves
- **Solution:** Nouvelle livraison ou remplacement pièces
- **Mots-clés:** livraison, endommagé, rayé, cassé

---

### 🟡 PRIORITÉ MOYENNE (P2) - Réponse <5 jours

#### SAV-001: Canapé d'angle - Affaissement coussins
- **Produit:** Canapé d'angle Confort Plus (SAL-CAP-001)
- **Symptômes:** Coussins s'affaissent prématurément
- **Solution:** Retournement coussins ou remplacement
- **Garantie:** 2 ans structure, 1 an tissus
- **Mots-clés:** affaissement, coussin, s'affaisse

#### SAV-003: Fauteuil - Velours usagé prématurément
- **Produit:** Fauteuil Pétale (SAL-FAU-001)
- **Symptômes:** Velours brillant/usé après 3 mois
- **Solution:** Échange, avoir 30%, ou remboursement
- **Garantie:** 1 an tissus
- **Mots-clés:** velours, brillant, usé, tissu

#### SAV-006: Matelas - Affaissement prématuré
- **Produit:** Matelas Confort Optimal (CHA-MAT-001)
- **Symptômes:** Creux >2,5cm au centre
- **Solution:** Échange ou avoir 50%
- **Garantie:** 10 ans affaissement >2,5cm
- **Mots-clés:** matelas, affaissement, creux, dos

---

### 🟢 PRIORITÉ BASSE (P3) - Réponse <7 jours

#### INFO-001: Entretien - Canapé cuir
- **Type:** Information entretien
- **Contenu:** Guide complet entretien cuir (quotidien, mensuel, trimestriel)
- **Inclut:** Réparation petites rayures
- **Produit:** Kit entretien cuir 45€
- **Mots-clés:** entretien, cuir, nettoyage

#### RETURN-001: Retour/Échange - Changement d'avis
- **Type:** Rétractation 14 jours
- **Options:** Retour (49€), Échange gratuit, Avoir 100%
- **Conditions:** Produit intact, emballage conservé
- **Mots-clés:** retour, échange, rétractation, changer

---

## 📚 FAQ - 15 QUESTIONS INITIALES

### 🛡️ Garanties et SAV (3 questions)
1. Quelle est la durée de garantie de mes meubles ?
2. Comment faire une réclamation SAV ?
3. Que faire si mon meuble arrive endommagé ?

### 🚚 Livraison (2 questions)
4. Quels sont les délais de livraison ?
5. La livraison en étage est-elle incluse ?

### 🔄 Retour et Échange (2 questions)
6. Puis-je retourner un meuble si je change d'avis ?
7. Comment échanger un produit contre une autre couleur ?

### 🧽 Entretien et Maintenance (3 questions)
8. Comment entretenir mon canapé en cuir ?
9. Comment nettoyer un canapé en tissu/velours ?
10. Mon matelas s'affaisse, que faire ?

### 💳 Paiement et Financement (2 questions)
11. Quels moyens de paiement acceptez-vous ?
12. Proposez-vous un paiement en plusieurs fois ?

---

## 🤖 COMMENT ÇA FONCTIONNE

### Flux de Conversation SAV

```
Client: "Mon canapé relax ne marche plus"
   ↓
Chatbot analyse le message
   ↓
Recherche dans sav_scenarios.json
   ↓
Trouve: SAV-002 (Mécanisme électrique)
   ↓
Charge: Questions diagnostic + Solutions
   ↓
Répond avec contexte SAV adapté
```

### Intelligence Contextuelle

Le chatbot reçoit automatiquement :
1. **Catalogue produits complet** (catalog.json)
2. **Scénarios SAV pertinents** (basés sur mots-clés)
3. **FAQ pertinentes** (basées sur requête)
4. **Guidelines SAV** (12 règles d'or)

---

## 🧪 TESTER LE SYSTÈME SAV

### Test 1: Scénario Critique (P0)

**Dans le chatbot, écrivez:**
```
"Le sommier de mon lit coffre ne tient plus, il retombe tout le temps"
```

**Le chatbot devrait:**
- ✅ Détecter priorité CRITIQUE
- ✅ Alerter sur danger sécurité
- ✅ Poser questions diagnostic (combien de vérins, etc.)
- ✅ Proposer intervention <24h
- ✅ Mentionner garantie 2 ans mécanisme

---

### Test 2: Scénario SAV Standard (P2)

**Dans le chatbot, écrivez:**
```
"Les coussins de mon canapé d'angle s'affaissent déjà"
```

**Le chatbot devrait:**
- ✅ Poser questions (quelle partie, depuis quand, etc.)
- ✅ Suggérer solution rapide (retourner coussins)
- ✅ Proposer remplacement sous garantie
- ✅ Demander photos
- ✅ Créer dossier SAV

---

### Test 3: Information Entretien (P3)

**Dans le chatbot, écrivez:**
```
"Comment entretenir mon canapé en cuir ?"
```

**Le chatbot devrait:**
- ✅ Donner guide entretien complet
- ✅ Quotidien / Mensuel / Trimestriel
- ✅ Produits à éviter
- ✅ Proposer kit entretien 45€

---

### Test 4: Livraison Endommagée (P1)

**Dans le chatbot, écrivez:**
```
"Mon buffet vient d'être livré et il est rayé !"
```

**Le chatbot devrait:**
- ✅ Donner procédure URGENTE
- ✅ Ne pas signer / Prendre photos
- ✅ Proposer refus ou acceptation avec réserves
- ✅ Expliquer conséquences de chaque choix

---

## 🔌 API FAQ - EXEMPLES D'UTILISATION

### Rechercher dans la FAQ

**GET** `http://localhost:8000/api/faq?query=garantie`

```json
{
  "results": [
    {
      "id": "faq-garanties-001",
      "question": "Quelle est la durée de garantie ?",
      "answer": "...",
      "category": "Garanties et SAV",
      "relevance_score": 5
    }
  ]
}
```

---

### Lister les Catégories

**GET** `http://localhost:8000/api/faq/categories`

```json
{
  "categories": [
    {
      "id": "garanties",
      "name": "Garanties et SAV",
      "icon": "🛡️",
      "question_count": 3
    },
    ...
  ]
}
```

---

### Voter sur une Question

**POST** `http://localhost:8000/api/faq/vote`

```json
{
  "question_id": "faq-garanties-001",
  "helpful": true
}
```

---

### Ajouter une Question

**POST** `http://localhost:8000/api/faq/add`

```json
{
  "category_id": "garanties",
  "question": "Puis-je étendre ma garantie ?",
  "answer": "Oui, nous proposons une extension de garantie...",
  "keywords": ["garantie", "extension", "prolongation"]
}
```

---

## 📈 ENRICHIR LA FAQ AU FIL DU TEMPS

### Méthode Recommandée

1. **Analyser les conversations réelles**
   - Identifier questions fréquentes
   - Repérer points de confusion

2. **Ajouter les nouvelles questions**
   ```bash
   POST /api/faq/add
   ```

3. **Suivre les votes**
   - Voir quelles réponses sont utiles
   - Améliorer celles qui ne le sont pas

4. **Mettre à jour régulièrement**
   - Éditez [backend/data/faq.json](backend/data/faq.json)
   - Ou utilisez l'API
   - Redémarrez le backend

---

## 🎯 CLASSIFICATION PRIORITÉS SAV

### P0 - CRITIQUE 🔴
- **Délai:** <4h
- **Intervention:** <24h
- **Exemples:** Danger, blessure, produit dangereux
- **Action:** Appel équipe immédiat

### P1 - HAUTE 🟠
- **Délai:** <24h
- **Intervention:** 24-72h
- **Exemples:** Produit inutilisable, fonction principale HS
- **Action:** Technicien domicile rapide

### P2 - MOYENNE 🟡
- **Délai:** <5 jours
- **Intervention:** 5-7 jours
- **Exemples:** Défaut qualité, inconfort, sous garantie
- **Action:** Remplacement ou réparation standard

### P3 - BASSE 🟢
- **Délai:** <7 jours
- **Intervention:** Variable
- **Exemples:** Info, entretien, retour standard
- **Action:** Réponse informative

---

## 💡 GUIDELINES CHATBOT SAV (12 RÈGLES)

Le chatbot suit automatiquement ces règles :

1. ✅ Toujours demander numéro de commande si disponible
2. ✅ Poser questions précises pour diagnostic avant solution
3. ✅ Proposer solutions adaptées selon garantie
4. ✅ Créer ticket SAV systématiquement pour problèmes techniques
5. ✅ Classer priorité correctement (P0-P3)
6. ✅ Rassurer le client avec empathie
7. ✅ Donner timeline précise
8. ✅ Mentionner coûts clairement (gratuit/payant)
9. ✅ Proposer alternatives quand possible
10. ✅ Confirmer par email récapitulatif
11. ✅ Pour photos : Vue ensemble + zooms zones problématiques
12. ✅ Sécurité : Alerter immédiatement sur dangers

---

## 📊 STATISTIQUES & SUIVI

### Accéder aux Stats

**GET** `http://localhost:8000/api/faq/stats`

Retourne :
- Nombre total de questions
- Questions par catégorie
- Votes utiles/pas utiles
- Dernière mise à jour

---

## 🔧 PERSONNALISATION

### Ajouter un Scénario SAV

1. Éditez [backend/data/sav_scenarios.json](backend/data/sav_scenarios.json)
2. Copiez structure d'un scénario existant
3. Modifiez : id, title, keywords, solutions
4. Redémarrez le backend

### Modifier une FAQ

1. Éditez [backend/data/faq.json](backend/data/faq.json)
2. Trouvez la question par ID
3. Modifiez question/réponse
4. Redémarrez le backend

### Ajouter une Catégorie FAQ

```json
{
  "id": "nouvelle-categorie",
  "name": "Nom de la Catégorie",
  "icon": "🎨",
  "questions": [...]
}
```

---

## 🚀 DÉMARRAGE COMPLET

### 1. Backend

```bash
cd c:\Users\v-nbayonne\meuble-de-france-chatbot\backend
venv\Scripts\activate
python -m app.main
```

✅ Serveur : http://localhost:8000
✅ Docs API : http://localhost:8000/docs

### 2. Frontend

```bash
cd c:\Users\v-nbayonne\meuble-de-france-chatbot\frontend
npm run dev
```

✅ Interface : http://localhost:5173

### 3. Tester

Ouvrez le chatbot et testez les scénarios ci-dessus !

---

## 📝 EXEMPLE CONVERSATION COMPLÈTE

### Scénario : Affaissement Matelas

```
Client: "Bonjour, mon matelas s'est affaissé au milieu"

Bot: "Bonjour ! Je comprends, les problèmes de dos liés à un matelas
affaissé sont vraiment pénibles. Je vais vérifier si c'est couvert
par votre garantie 10 ans.

Pour mieux vous aider :
1. Quelle est la taille du matelas ? (140, 160 ou 180cm)
2. Est-ce en mousse mémoire, ressorts ou latex ?
3. Depuis combien de temps avez-vous remarqué l'affaissement ?
4. Retournez-vous régulièrement le matelas ?
5. Utilisez-vous un protège-matelas ?"

Client: "C'est un 160x200 en mousse mémoire, remarqué il y a 2 mois,
je ne l'ai jamais retourné en 2 ans"

Bot: "D'accord, merci ! Votre matelas est sous garantie 10 ans pour
affaissement >2,5cm.

🔍 Procédure de mesure :
1. Placez une règle droite sur la longueur
2. Mesurez la profondeur du creux au centre
3. Prenez une photo de la règle posée

Pouvez-vous faire cette mesure et me donner le résultat ?"

Client: "J'ai mesuré, il y a 4cm de creux" [+ photo]

Bot: "✅ Photo reçue et mesure validée : 4cm d'affaissement

C'est supérieur à la norme de 2,5cm = ✅ COUVERT par garantie 10 ans

🎫 Dossier SAV créé : SAV-20241203-161
🟡 Priorité : MOYENNE

🔄 Options :

**Option 1 (Recommandée) :** Échange standard
- Nouveau matelas identique
- Livraison : 2-3 semaines
- Gratuit (sous garantie)

**Option 2 :** Avoir commercial 50%
- Sur matelas gamme supérieure
- Utilisable immédiatement

Quelle option préférez-vous ?

💡 Conseil pour le nouveau : Retournez-le tous les 3 mois la 1ère année !"
```

---

## ✅ RÉCAPITULATIF

Votre chatbot Meuble de France dispose maintenant de :

- ✅ **9 scénarios SAV complets** (P0 à P3)
- ✅ **15 questions FAQ** (5 catégories)
- ✅ **Recherche intelligente** dans scénarios et FAQ
- ✅ **API REST complète** pour gérer la FAQ
- ✅ **Contexte dynamique** selon message client
- ✅ **Guidelines SAV** intégrées
- ✅ **Classification priorités** automatique
- ✅ **Système de votes** pour amélioration continue
- ✅ **Prêt à être enrichi** avec vos données réelles

---

## 🎉 LE CHATBOT EST PRÊT POUR LE SAV !

Testez tous les scénarios et commencez à enrichir la FAQ au fil des vraies conversations avec vos clients.

**Endpoints disponibles :**
- http://localhost:8000/docs - Documentation API complète
- http://localhost:8000/api/faq - Toutes les FAQs
- http://localhost:8000/api/chat - Chatbot avec SAV intégré
- http://localhost:8000/api/products - Catalogue produits

---

*Document créé le 2025-12-03*
*Système SAV + FAQ fully operational! 🚀*
