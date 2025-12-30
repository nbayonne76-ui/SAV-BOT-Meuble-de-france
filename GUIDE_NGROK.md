# 🌐 Guide d'utilisation de ngrok pour le Chatbot Mobilier de France

## 📋 Prérequis

1. ngrok installé ✅ (déjà fait)
2. Docker containers démarrés (`docker-compose up -d`)
3. Compte ngrok (gratuit sur https://ngrok.com)

## 🚀 Méthode 1 : Exposer uniquement le Frontend (Recommandé)

### Étape 1 : Démarrer ngrok pour le frontend

Double-cliquez sur `start-ngrok-frontend.bat` ou exécutez :

```bash
ngrok http 5173
```

### Étape 2 : Récupérer l'URL

Vous verrez quelque chose comme :
```
Forwarding   https://abcd-1234.ngrok-free.app -> http://localhost:5173
```

### Étape 3 : Partager l'URL

Envoyez l'URL `https://abcd-1234.ngrok-free.app` à vos testeurs !

⚠️ **Important** : Le backend reste en local (localhost:8000) et n'est accessible que depuis votre réseau.

---

## 🔧 Méthode 2 : Exposer Frontend + Backend (Pour tests externes complets)

### Option A : Utiliser 2 tunnels ngrok séparés

#### Terminal 1 - Frontend
```bash
ngrok http 5173
```

#### Terminal 2 - Backend
```bash
ngrok http 8000
```

### Option B : Configuration ngrok.yml (Avancé)

Créez un fichier `ngrok.yml` :

```yaml
version: "2"
authtoken: VOTRE_TOKEN_ICI
tunnels:
  frontend:
    proto: http
    addr: 5173
  backend:
    proto: http
    addr: 8000
```

Puis lancez :
```bash
ngrok start --all
```

### Étape importante : Configurer les variables d'environnement

Si vous exposez le backend, modifiez `.env.production` :

```env
VITE_API_URL=https://votre-backend-ngrok.ngrok-free.app
```

Puis reconstruisez le frontend :
```bash
docker-compose up -d --build frontend
```

---

## 📱 Méthode 3 : Utiliser votre hotspot mobile (Plus simple)

Si vous voulez juste tester depuis votre téléphone :

1. Connectez votre PC à votre hotspot mobile
2. Trouvez l'IP de votre PC : `ipconfig` → Cherchez "Adresse IPv4"
3. Sur votre téléphone, allez sur : `http://VOTRE_IP:5173`

Exemple : `http://192.168.43.100:5173`

---

## 🎯 Commandes utiles

### Vérifier que ngrok fonctionne
```bash
curl http://localhost:4040/api/tunnels
```

### Voir l'interface web ngrok
Ouvrez : http://localhost:4040

### Arrêter ngrok
Appuyez sur `Ctrl + C` dans le terminal ngrok

---

## ⚠️ Limitations de la version gratuite

- URL change à chaque redémarrage
- 1 connexion simultanée par tunnel
- Bannière ngrok sur la page (peut être gênante)

**Solution** : Compte payant ngrok ($8/mois) pour :
- URL fixe personnalisée
- Pas de bannière
- Plus de connexions simultanées

---

## 🔐 Sécurité

⚠️ **ATTENTION** : Avec ngrok, votre application est accessible publiquement sur Internet !

**Recommandations** :
1. Ne pas exposer pendant longtemps
2. Ne pas partager l'URL publiquement
3. Utiliser un mot de passe si possible (ngrok Pro)
4. Surveiller les logs : http://localhost:4040

---

## 📞 Support

Si vous avez des problèmes :
1. Vérifiez que Docker tourne : `docker-compose ps`
2. Vérifiez les logs ngrok : http://localhost:4040
3. Vérifiez les logs du chatbot : `docker-compose logs backend frontend`

Bon test ! 🚀
