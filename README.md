# Application "Envoi de Factures"

> Documentation complète — rédigée le 23 mai 2026  
> À lire si vous reprenez ce projet après plusieurs mois, ou si vous l'expliquez à quelqu'un qui ne connaît rien.

---

## À quoi ça sert — en une phrase

Cette application permet d'**envoyer un fichier PDF (facture) vers un traitement automatique**, en appuyant simplement sur un bouton depuis un téléphone ou un ordinateur.

---

## Le problème que ça résout

Avant cette application, pour traiter une facture reçue par mail, il fallait :
1. Ouvrir n8n (outil d'automatisation)
2. Trouver le bon workflow (MALAIKA, NV Diffusion, etc.)
3. Cliquer sur "Exécuter"
4. Remplir manuellement un formulaire pour uploader le fichier
5. Soumettre

**Maintenant**, il suffit de :
1. Ouvrir l'application sur son téléphone
2. Choisir le fichier PDF
3. Appuyer sur le bouton de la bonne société

---

## Ce qui se passe dans les coulisses

```
Votre téléphone
      ↓  (upload du PDF)
Application web (factures-app)
      ↓  (envoie le fichier à n8n)
n8n — Workflow automatique
      ↓
  ┌───────────────────────────────┐
  │  1. Renomme le fichier        │
  │  2. OCR via Mistral AI        │  ← lit et comprend le PDF
  │  3. Stockage Google Drive     │  ← sauvegarde le fichier
  │  4. Traitement Airtable       │  ← enregistre les données
  └───────────────────────────────┘
```

---

## Les 4 sociétés / workflows

| Bouton | Société | Webhook ID n8n |
|--------|---------|----------------|
| 🔴 M | **MALAIKA** | `3cae1a91-9841-4150-910e-e7bcd7d9523c` |
| 🔵 N | **NV Diffusion** | `3f72f3f3-a6b9-4df0-829c-be7d4ae6f2b8` |
| 🟣 J | **JOVITYS** | ⚠️ Temporaire = NV Diffusion |
| 🟢 V | **VALSYONE** | ⚠️ Temporaire = NV Diffusion |

> ⚠️ JOVITYS et VALSYONE utilisent provisoirement le même workflow que NV Diffusion.
> Quand leurs propres workflows seront créés dans n8n, mettre à jour `app.py` (voir section "Modifier").

---

## Comment utiliser l'application au quotidien

### Depuis n'importe où (téléphone, ordinateur, hors WiFi)

1. Ouvrez le navigateur
2. Allez sur : **`https://factures-app.onrender.com`**
3. Appuyez sur la zone "Choisir un fichier" → sélectionnez votre PDF
4. Appuyez sur le bouton de la société concernée
5. Attendez le message ✅ "Facture envoyée avec succès"

### Depuis le bureau (même WiFi que le Mac)

L'application peut aussi tourner localement sur le Mac (voir section "Lancer en local").  
URL locale : **`http://192.168.1.26:5555`**

---

## Où sont hébergées les différentes briques

| Brique | Où | URL / Accès |
|--------|----|-------------|
| **Code source** | GitHub | `github.com/nvdiffusionrun/factures-app` |
| **Application web** | Render.com | `https://factures-app.onrender.com` |
| **Workflows automatiques** | n8n (serveur OVH) | `n8n.srv867860.hstgr.cloud` |
| **Stockage fichiers** | Google Drive | Compte lié à n8n |

---

## Structure des fichiers du projet

```
factures-app/
│
├── app.py            ← Le cœur de l'application (serveur + interface web)
├── requirements.txt  ← Liste des bibliothèques Python nécessaires
├── start.sh          ← Script pour lancer l'app en local
├── Procfile          ← Instruction pour Render (comment démarrer l'app)
├── .gitignore        ← Fichiers à ne pas envoyer sur GitHub
└── README.md         ← Ce fichier de documentation
```

---

## Modifier les URLs des workflows n8n

Quand JOVITYS et VALSYONE auront leurs propres triggers, ou si un webhook change :

**1.** Ouvrez `app.py` dans un éditeur de texte

**2.** Trouvez la section `WORKFLOWS` en haut du fichier (lignes ~8 à 41)

**3.** Modifiez le champ `"url"` de la société concernée :

```python
"jovitys": {
    "name": "JOVITYS",
    "url": "https://n8n.srv867860.hstgr.cloud/form/COLLER-LE-NOUVEAU-WEBHOOK-ID-ICI",
    "file_field": "attachment_0",
    ...
},
```

**4.** Sauvegardez, puis dans le Terminal :

```bash
cd "/Users/thierry/Pictures/Factures a traiter"
git add app.py
git commit -m "mise à jour webhook JOVITYS"
git push
```

→ Render redéploie automatiquement en 2 minutes. C'est tout.

---

## Lancer l'application en local (sur le Mac)

Si Render est indisponible ou pour tester une modification en cours :

```bash
# Ouvrir le Terminal, puis :
cd "/Users/thierry/Pictures/Factures a traiter"
python3 app.py
```

L'app est alors accessible sur :
- **Mac** : http://localhost:5555
- **Téléphone (même WiFi)** : http://192.168.1.26:5555

Pour arrêter : appuyez sur `Ctrl + C` dans le terminal.

---

## Dépannage — problèmes courants

### ❌ Le chargement est très lent au premier accès
→ Normal. Render "endort" l'app gratuite après 15 min d'inactivité.
Le premier accès la réveille (30 secondes d'attente). Les suivants sont instantanés.

### ❌ "n8n a répondu avec le code 404"
→ Le workflow n'est pas **activé** dans n8n.  
Ouvrez n8n → trouvez le workflow → activez le toggle en haut à droite.

### ❌ "n8n a répondu avec le code 5xx"
→ Erreur interne dans n8n. Ouvrez n8n → onglet **"Exécutions"** → regardez quelle étape a échoué (OCR Mistral, Google Drive, etc.)

### ❌ "Le workflow n8n met trop de temps à répondre"
→ n8n est surchargé. Réessayez dans 1–2 minutes.

### ❌ Port 5555 déjà utilisé (en local uniquement)
```bash
lsof -ti :5555 | xargs kill -9
python3 app.py
```

---

## Glossaire pour les non-initiés

| Terme | Explication simple |
|-------|--------------------|
| **n8n** | Outil d'automatisation — un robot qui exécute des tâches à votre place |
| **Workflow** | Un scénario automatique dans n8n (ex : "quand je reçois un fichier, fais ceci puis cela") |
| **Webhook** | Une adresse URL secrète que n8n surveille pour recevoir des données |
| **Flask** | Le framework Python utilisé pour créer le serveur de l'application |
| **Render** | Service cloud qui fait tourner l'application 24h/24 sur internet |
| **GitHub** | Plateforme de sauvegarde du code — comme un Google Drive pour développeurs |
| **OCR** | Technologie qui "lit" le texte dans une image ou un PDF scanné |
| **Mistral AI** | Intelligence artificielle utilisée pour lire les factures dans ce projet |
| **`git push`** | Commande pour envoyer les modifications locales vers GitHub |

---

## Comptes & accès

| Ressource | Identifiant |
|-----------|-------------|
| GitHub | `nvdiffusionrun` |
| Email associé | `nvdiffusionrun@gmail.com` |
| Render | Connecté via GitHub (`nvdiffusionrun`) |
| n8n | `n8n.srv867860.hstgr.cloud` |

---

*Document rédigé le 23 mai 2026 — Application développée avec Claude (Anthropic)*
