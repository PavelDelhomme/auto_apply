# 📧 Guide Complet: Solutions pour Créer des Emails de Personas

## 🎯 Objectif

Créer un système d'emails fonctionnel pour vos personas **sans dépendre de GMX/CaraMail** qui se font bloquer facilement.

---

## 🌟 Solution 1: Utiliser Votre Domaine OVH (maily.ovh) ⭐ RECOMMANDÉ

### Avantages
- ✅ **Contrôle total** : Vous possédez le domaine
- ✅ **Création illimitée** : Créez autant d'emails que vous voulez
- ✅ **Pas de blocage** : Votre propre infrastructure
- ✅ **IMAP/SMTP activés** : Par défaut avec OVH
- ✅ **Professionnel** : Domaine personnalisé

### Configuration OVH

#### Option A: Interface Web OVH (Manuel)

1. **Connectez-vous à OVH Manager:**
   - https://www.ovh.com/manager/web/
   - Allez dans "Emails" → Votre domaine `maily.ovh`

2. **Créer un email:**
   - Cliquez sur "Créer une adresse email"
   - Nom d'utilisateur: `persona1`, `persona2`, etc.
   - Mot de passe: Générez un mot de passe fort
   - Taille de la boîte: 5 GB (gratuit) ou plus (payant)

3. **Configuration IMAP/SMTP:**
   - Serveur IMAP: `ssl0.ovh.net` (port 993, SSL)
   - Serveur SMTP: `ssl0.ovh.net` (port 465, SSL)
   - Ou: `mail.maily.ovh` si configuré

#### Option B: API OVH (Automatique) ⭐ MEILLEURE OPTION

**Créer des emails automatiquement via l'API OVH:**

1. **Installer l'API OVH:**
```bash
pip install ovh
```

2. **Créer des clés API:**
   - https://eu.api.ovh.com/createApp/
   - Créez une application et récupérez:
     - `Application Key`
     - `Application Secret`
     - `Consumer Key`

3. **Script Python pour créer des emails automatiquement:**

```python
import ovh
import random
import string

# Configuration OVH
client = ovh.Client(
    endpoint='ovh-eu',
    application_key='VOTRE_APP_KEY',
    application_secret='VOTRE_APP_SECRET',
    consumer_key='VOTRE_CONSUMER_KEY'
)

def create_email_account(domain, username, password):
    """Crée un compte email sur OVH."""
    try:
        result = client.post(
            f'/email/domain/{domain}/account',
            accountName=username,
            password=password,
            size=5000000000  # 5 GB
        )
        return result
    except Exception as e:
        print(f"Erreur création {username}@{domain}: {e}")
        return None

# Exemple: Créer 10 emails
for i in range(1, 11):
    username = f"persona{i}"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    create_email_account('maily.ovh', username, password)
    print(f"✅ {username}@maily.ovh créé")
```

**Configuration dans personas.json:**
```json
{
    "personaXXX": {
        "name": "Nom du Persona",
        "email": "persona1@maily.ovh",
        "password": "mot_de_passe_genere",
        "alias": false,
        "parent": null,
        "email_config": {
            "imap_server": "ssl0.ovh.net",
            "imap_port": 993,
            "smtp_server": "ssl0.ovh.net",
            "smtp_port": 465
        }
    }
}
```

**Limites OVH:**
- Gratuit: 5 GB par email (suffisant pour les personas)
- Payant: Jusqu'à 50 GB par email
- Nombre d'emails: Illimité (selon votre offre)

---

## 🌟 Solution 2: Catch-All Email avec OVH

### Concept
Un seul compte email qui reçoit **TOUS** les emails envoyés à votre domaine, peu importe l'adresse.

### Avantages
- ✅ **Un seul compte à gérer**
- ✅ **Emails illimités** : `persona1@maily.ovh`, `persona2@maily.ovh`, etc.
- ✅ **Pas besoin de créer chaque compte**
- ✅ **Réception automatique** de tous les emails

### Configuration OVH

1. **Activer le catch-all:**
   - OVH Manager → Emails → Votre domaine
   - Activez "Redirection catch-all"
   - Redirigez vers: `catchall@maily.ovh` (ou votre email principal)

2. **Créer le compte catch-all:**
   - Créez un seul compte: `catchall@maily.ovh`
   - Tous les emails à `*@maily.ovh` arriveront ici

3. **Dans personas.json:**
```json
{
    "personaXXX": {
        "name": "Nom du Persona",
        "email": "persona1@maily.ovh",  // N'importe quelle adresse
        "password": "mot_de_passe_du_catchall",
        "alias": false,
        "parent": null,
        "email_config": {
            "imap_server": "ssl0.ovh.net",
            "imap_port": 993,
            "smtp_server": "ssl0.ovh.net",
            "smtp_port": 465
        }
    }
}
```

**⚠️ Limitation:** Pour **envoyer** des emails, vous devrez configurer SMTP avec authentification. Tous les personas utiliseront le même compte SMTP mais avec des adresses "From" différentes.

---

## 🌟 Solution 3: Zoho Mail (Gratuit pour 5 comptes)

### Avantages
- ✅ 5 comptes gratuits par organisation
- ✅ IMAP/SMTP activés
- ✅ Pas de blocage
- ✅ Interface professionnelle

### Limitation
- ⚠️ Maximum 5 comptes gratuits par organisation

### Solution: Créer Plusieurs Organisations

1. **Créer plusieurs organisations Zoho:**
   - Organisation 1: `entreprise1.zoho.com` → 5 comptes
   - Organisation 2: `entreprise2.zoho.com` → 5 comptes
   - Organisation 3: `entreprise3.zoho.com` → 5 comptes
   - etc.

2. **Total:** 5 comptes × N organisations = 5N comptes gratuits

**Configuration:**
```json
{
    "email_config": {
        "imap_server": "imap.zoho.com",
        "imap_port": 993,
        "smtp_server": "smtp.zoho.com",
        "smtp_port": 587
    }
}
```

---

## 🌟 Solution 4: Mail.com (Illimité mais Manuel)

### Avantages
- ✅ Création illimitée (pas de limite stricte)
- ✅ IMAP activé par défaut
- ✅ Pas de SMS requis
- ✅ Plusieurs domaines disponibles

### Inconvénients
- ⚠️ Création manuelle (pas d'API publique)
- ⚠️ Peut prendre du temps pour créer beaucoup de comptes

### Stratégie
- Créez 10-20 comptes Mail.com par jour
- Utilisez différents domaines (@mail.com, @email.com, @inbox.com)
- Stockez les identifiants dans un gestionnaire de mots de passe

---

## 🌟 Solution 5: Solution Self-Hosted (Mailcow, Mail-in-a-Box)

### Avantages
- ✅ **Contrôle total**
- ✅ **Création illimitée** via API
- ✅ **Pas de limites**
- ✅ **Votre propre infrastructure**

### Inconvénients
- ⚠️ Nécessite un serveur VPS
- ⚠️ Configuration plus complexe
- ⚠️ Maintenance requise

### Options

#### Mailcow
- Interface web moderne
- API complète
- Création d'emails via API
- Documentation: https://mailcow.github.io/mailcow-dockerized-docs/

#### Mail-in-a-Box
- Configuration simple
- Interface web
- Création d'emails via interface ou API

**Exemple avec Mailcow API:**
```python
import requests

def create_mailbox(domain, username, password):
    """Crée un mailbox via l'API Mailcow."""
    url = "https://votre-mailcow.example.com/api/v1/add/mailbox"
    headers = {"X-API-Key": "VOTRE_API_KEY"}
    data = {
        "local_part": username,
        "domain": domain,
        "password": password,
        "quota": 5000000000  # 5 GB
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

---

## 🌟 Solution 6: Services d'Email Temporaires avec API

### ImprovMX
- Service de redirection d'emails
- API pour créer des alias
- Gratuit jusqu'à 10 domaines
- Redirige vers votre email principal

### Mailgun
- Service d'email transactionnel
- API complète
- Payant mais puissant
- Création d'emails via API

---

## 🎯 Recommandation Finale

### Pour Votre Cas (maily.ovh)

**Option 1: Catch-All OVH (Le Plus Simple)**
1. Activez le catch-all sur `maily.ovh`
2. Créez un seul compte `catchall@maily.ovh`
3. Tous vos personas utilisent `personaX@maily.ovh`
4. Tous les emails arrivent dans le même compte IMAP
5. **Avantage:** Un seul compte à gérer, emails illimités

**Option 2: API OVH (Le Plus Flexible)**
1. Utilisez l'API OVH pour créer des emails automatiquement
2. Créez un script Python pour générer N personas
3. Chaque persona a son propre compte email
4. **Avantage:** Comptes séparés, plus professionnel

**Option 3: Mix OVH + Mail.com**
1. Utilisez OVH pour 50-100 personas principaux
2. Utilisez Mail.com pour les alias/variantes
3. **Avantage:** Diversification, moins de risque

---

## 📋 Plan d'Action Recommandé

### Étape 1: Obtenir les Clés API OVH

1. **Allez sur:** https://eu.api.ovh.com/createApp/
2. **Connectez-vous** avec votre compte OVH
3. **Créez une application:**
   - Nom: "Auto Apply Email Manager"
   - Description: "Gestion des emails pour personas"
4. **Récupérez les clés:**
   - Application Key
   - Application Secret
   - Consumer Key (généré après validation)

### Étape 2: Configurer les Clés API

1. **Créez le fichier:** `config/ovh_config.json`
2. **Copiez le contenu:**
```json
{
    "application_key": "VOTRE_APP_KEY",
    "application_secret": "VOTRE_APP_SECRET",
    "consumer_key": "VOTRE_CONSUMER_KEY",
    "domain": "maily.ovh",
    "endpoint": "ovh-eu"
}
```
3. **Remplacez** les valeurs par vos clés réelles

### Étape 3: Configurer le Catch-All (Recommandé)

1. **Exécutez:** `make setup-ovh-catchall`
2. Le script va:
   - Créer le compte `catchall@maily.ovh`
   - Configurer la redirection catch-all
   - Ajouter le persona dans `personas.json`
3. **Récupérez le mot de passe** affiché et sauvegardez-le

### Étape 4: Créer vos Personas

**Option A: Avec Catch-All (Simple)**
- Créez vos personas avec `personaX@maily.ovh` dans l'interface
- Tous utiliseront le même mot de passe (celui du catch-all)
- Tous les emails arriveront dans `catchall@maily.ovh`

**Option B: Comptes Séparés (Avancé)**
- Exécutez: `make create-ovh-emails`
- Entrez le nombre d'emails à créer
- Le script crée automatiquement les emails et les personas

### Étape 5: Tester

1. **Testez la connexion:** `make test-email`
2. **Vérifiez** que les emails OVH fonctionnent
3. **Ajustez** si nécessaire

---

## 🔧 Script d'Intégration OVH

Je peux créer un script Python qui:
1. Se connecte à l'API OVH
2. Crée automatiquement N emails
3. Génère les mots de passe
4. Ajoute les personas dans `personas.json`
5. Teste les connexions IMAP

**Souhaitez-vous que je crée ce script ?**

---

## 💡 Conseils

1. **Commencez petit:** Testez avec 5-10 personas d'abord
2. **Diversifiez:** Utilisez plusieurs solutions (OVH + Mail.com)
3. **Automatisez:** Utilisez des scripts pour créer les comptes
4. **Surveillez:** Testez régulièrement avec `make test-email`
5. **Sauvegardez:** Gardez une liste de tous les comptes créés

---

## 📞 Support

Si vous avez besoin d'aide pour:
- Configurer l'API OVH
- Créer le script d'automatisation
- Configurer le catch-all
- Intégrer avec Auto Apply

N'hésitez pas à demander !

