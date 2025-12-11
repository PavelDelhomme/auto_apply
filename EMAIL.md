# 📧 Guide Complet : Emails pour Personas

> **Document centralisé** regroupant toutes les informations sur la configuration et la gestion des emails pour les personas.

---

## 📑 Table des Matières

1. [Plan d'Action](#-plan-daction-mise-en-place-des-emails-personas)
2. [Solutions Disponibles](#-solutions-disponibles)
3. [Création de Boîtes Mail](#-création-de-boîtes-mail)
4. [Résolution de Problèmes](#-résolution-de-problèmes)
5. [Configuration Technique](#-configuration-technique)
6. [Commandes Utiles](#-commandes-utiles)

---

## 🎯 Plan d'Action : Mise en Place des Emails Personas

### 📊 État Actuel

✅ **Sécurité Git** : `config/personas.json` a été supprimé de tout l'historique Git  
❌ **Fichier personas.json** : N'existe pas localement (à recréer)  
❌ **Emails GMX/CaraMail** : 309 personas, 0 fonctionnels (blocages, IMAP désactivé)

---

### 🚀 Plan d'Action Recommandé

#### **Étape 1 : Recréer personas.json** ⚠️ PRIORITÉ

Le fichier `config/personas.json` n'existe plus localement. Vous devez le recréer.

```bash
# Copier l'exemple
cp config/personas.json.example config/personas.json

# Puis éditer avec vos personas réels
# (gardez vos données sensibles en local, ne commitez jamais ce fichier)
```

**💡 Important** : Si vous avez une sauvegarde de `personas.json`, restaurez-la maintenant.

---

#### **Étape 2 : Choisir une Solution Email** 🎯

Vous avez **3 options principales** :

##### **Option A : OVH avec Catch-All** ⭐ **RECOMMANDÉ**

**Pourquoi ?**
- Vous possédez déjà `maily.ovh`
- Création illimitée d'emails
- Pas de blocage comme GMX
- Configuration automatique possible

**Actions :**
1. Obtenir vos clés API OVH : https://eu.api.ovh.com/createApp/
2. Créer `config/ovh_config.json` avec vos clés
3. Configurer le catch-all : `make setup-ovh-catchall`
4. Créer vos personas avec `personaX@maily.ovh`

**Temps estimé** : 30-60 minutes

##### **Option B : Mail.com / Zoho Mail** (Alternative)

**Pourquoi ?**
- Gratuit
- Pas besoin de domaine
- IMAP activé par défaut

**Actions :**
1. Créer manuellement des comptes Mail.com
2. Ajouter les emails dans `personas.json`

**Temps estimé** : 2-3 heures (création manuelle)

##### **Option C : Réparer GMX/CaraMail** (Temporaire)

**Pourquoi ?**
- Si vous voulez garder vos emails existants
- Nécessite activation manuelle IMAP pour chaque compte

**Actions :**
1. Activer IMAP manuellement pour chaque compte GMX/CaraMail
2. Tester : `make test-email`

**Temps estimé** : 1-2 heures (par compte)

---

#### **Étape 3 : Mettre en Place la Solution Choisie** 🔧

##### Si vous choisissez OVH (Recommandé) :

```bash
# 1. Créer le fichier de configuration OVH
cp config/ovh_config.json.example config/ovh_config.json
# Puis éditer avec vos clés API

# 2. Configurer le catch-all (reçoit tous les emails @maily.ovh)
make setup-ovh-catchall

# 3. Créer des emails individuels si nécessaire
make create-ovh-emails
```

##### Si vous choisissez Mail.com :

1. Créer manuellement des comptes sur https://www.mail.com
2. Ajouter les emails dans `personas.json`
3. Tester : `make test-email`

---

#### **Étape 4 : Tester et Valider** ✅

```bash
# Tester toutes les connexions email
make test-email

# Vérifier le rapport généré
cat EMAIL_STATUS_REPORT.md

# Tester une connexion spécifique via l'interface
# http://localhost:2020/mailbox
```

---

#### **Étape 5 : Nettoyer les Personas de Test** 🧹

```bash
# Supprimer les personas de test
make clean-test-personas

# Vérifier le résultat
make check-file FILE=config/personas.json
```

---

## 🌟 Solutions Disponibles

### Solution 1: Utiliser Votre Domaine OVH (maily.ovh) ⭐ RECOMMANDÉ

#### Avantages
- ✅ **Contrôle total** : Vous possédez le domaine
- ✅ **Création illimitée** : Créez autant d'emails que vous voulez
- ✅ **Pas de blocage** : Votre propre infrastructure
- ✅ **IMAP/SMTP activés** : Par défaut avec OVH
- ✅ **Professionnel** : Domaine personnalisé

#### Configuration OVH

##### Option A: Interface Web OVH (Manuel)

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

##### Option B: API OVH (Automatique) ⭐ MEILLEURE OPTION

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

3. **Utiliser les scripts fournis:**
```bash
# Configurer le catch-all
make setup-ovh-catchall

# Créer des emails individuels
make create-ovh-emails
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

### Solution 2: Catch-All Email avec OVH

#### Concept
Un seul compte email qui reçoit **TOUS** les emails envoyés à votre domaine, peu importe l'adresse.

#### Avantages
- ✅ **Un seul compte à gérer**
- ✅ **Emails illimités** : `persona1@maily.ovh`, `persona2@maily.ovh`, etc.
- ✅ **Pas besoin de créer chaque compte**
- ✅ **Réception automatique** de tous les emails

#### Configuration OVH

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

### Solution 3: Mail.com ⭐⭐⭐ MEILLEUR CHOIX (Alternative)

#### Avantages
- ✅ Pas de numéro de téléphone requis
- ✅ IMAP/SMTP disponibles gratuitement et activés par défaut
- ✅ Nombreux domaines disponibles (@mail.com, @email.com, @inbox.com, etc.)
- ✅ 2 GB gratuits
- ✅ Interface simple
- ✅ Pas de limite stricte sur le nombre de comptes

#### Inconvénients
- Interface moins moderne que Gmail
- Publicités dans la version gratuite (mais pas gênantes)

#### Création

1. Allez sur https://www.mail.com
2. Cliquez sur "Créer un compte gratuit"
3. Choisissez un domaine (recommandé: @mail.com, @email.com, @inbox.com)
4. Remplissez le formulaire:
   - Nom d'utilisateur (ex: `jean.dupont`)
   - Mot de passe fort
   - Date de naissance (peut être fictive)
   - Question de sécurité
5. **PAS de vérification par SMS nécessaire**
6. Activez votre compte via l'email de confirmation

#### Configuration IMAP (déjà activé par défaut)
- Serveur IMAP: `imap.mail.com` (port 993, SSL)
- Serveur SMTP: `smtp.mail.com` (port 587, STARTTLS)
- Utilisez votre adresse email complète comme nom d'utilisateur
- Utilisez votre mot de passe

#### Ajout dans personas.json
```json
{
    "personaXXX": {
        "name": "Jean Dupont",
        "email": "jean.dupont@mail.com",
        "password": "votre_mot_de_passe",
        "alias": false,
        "parent": null,
        "email_config": {
            "imap_server": "imap.mail.com",
            "imap_port": 993,
            "smtp_server": "smtp.mail.com",
            "smtp_port": 587
        }
    }
}
```

---

### Solution 4: Zoho Mail (Gratuit pour 5 comptes)

#### Avantages
- ✅ 5 comptes gratuits par organisation
- ✅ IMAP/SMTP activés
- ✅ Pas de blocage
- ✅ Interface professionnelle

#### Limitation
- ⚠️ Maximum 5 comptes gratuits par organisation

#### Solution: Créer Plusieurs Organisations

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

### Solution 5: Solution Self-Hosted (Mailcow, Mail-in-a-Box)

#### Avantages
- ✅ **Contrôle total**
- ✅ **Création illimitée** via API
- ✅ **Pas de limites**
- ✅ **Votre propre infrastructure**

#### Inconvénients
- ⚠️ Nécessite un serveur VPS
- ⚠️ Configuration plus complexe
- ⚠️ Maintenance requise

#### Options

##### Mailcow
- Interface web moderne
- API complète
- Création d'emails via API
- Documentation: https://mailcow.github.io/mailcow-dockerized-docs/

##### Mail-in-a-Box
- Configuration simple
- Interface web
- Création d'emails via interface ou API

---

## 📧 Création de Boîtes Mail

### Fournisseurs Recommandés (Sans Numéro de Téléphone)

#### 1. **Mail.com** ⭐⭐⭐ MEILLEUR CHOIX
Voir [Solution 3](#solution-3-mailcom--meilleur-choix-alternative) ci-dessus.

#### 2. **Zoho Mail** ⭐⭐ Recommandé
Voir [Solution 4](#solution-4-zoho-mail-gratuit-pour-5-comptes) ci-dessus.

#### 3. **ProtonMail** ⭐ Recommandé (pour la sécurité)
- Avantages: Chiffrement end-to-end, IMAP via Bridge
- Inconvénients: Nécessite ProtonMail Bridge, limite de 1 compte gratuit par IP

#### 4. **Tutanota** ⭐ Recommandé
- Avantages: Chiffrement automatique, interface simple
- Inconvénients: IMAP nécessite un abonnement payant (12€/an)

#### 5. **Yandex Mail**
- Avantages: 10 GB gratuits, pas de SMS requis
- Inconvénients: Service russe, interface en russe par défaut

---

### 🚫 Fournisseurs à Éviter

- **GMX/CaraMail**: Nécessite activation manuelle d'IMAP (désactivé par défaut), se fait bloquer facilement
- **Gmail**: Nécessite numéro de téléphone pour la vérification
- **Outlook/Hotmail**: Nécessite numéro de téléphone pour la vérification
- **Yahoo**: Nécessite numéro de téléphone pour la vérification

---

## 🔧 Résolution de Problèmes

### ⚠️ ATTENTION: Blocage de Comptes GMX

**Problème critique:** GMX bloque les comptes après trop de tentatives de connexion.

**Message d'erreur typique:**
> "Dear GMX member, our system has detected irregular activity related to your account. As a precautionary measure, we have blocked your account."

**Causes:**
- Trop de tentatives de connexion IMAP en peu de temps
- Connexions depuis plusieurs IP différentes
- Activité suspecte détectée par GMX

**Solutions:**
1. **Contacter le support GMX** pour débloquer le compte
   - Allez sur https://support.gmx.fr
   - Expliquez que vous testez des connexions IMAP
   - Demandez le déblocage du compte
2. **Attendre 24-48 heures** avant de réessayer
3. **Réduire le nombre de tests simultanés** (réduit à 3 en parallèle au lieu de 10)
4. **Utiliser un délai entre les connexions** (déjà implémenté: 0.1-0.5s entre chaque connexion)

**💡 Recommandation:** Évitez GMX/CaraMail pour les tests en masse. Utilisez Mail.com ou Zoho Mail à la place.

---

### Problèmes Courants

#### 1. **IMAP Désactivé (GMX/CaraMail)**

**Problème:** GMX et CaraMail désactivent IMAP par défaut pour des raisons de sécurité.

**Solution:**
1. Connectez-vous à https://www.gmx.fr ou https://www.caramail.com
2. Allez dans **Paramètres** → **Réglages** → **Accès par programme**
3. Activez **IMAP** et **SMTP**
4. Réessayez la connexion

**⚠️ Important:** GMX désactive automatiquement IMAP après une période d'inactivité. Il faudra réactiver régulièrement.

**💡 Alternative recommandée:** Migrer vers Mail.com ou Zoho Mail

---

#### 2. **Mot de Passe Manquant**

**Solution:**
1. Ajoutez le mot de passe dans `config/personas.json`
2. Ou utilisez le bouton "Mettre à jour mot de passe" dans l'interface

---

#### 3. **Identifiants Incorrects**

**Problème:** Le mot de passe configuré est incorrect ou a changé.

**Solutions:**
1. Vérifiez le mot de passe dans `config/personas.json`
2. Utilisez le bouton "Mettre à jour mot de passe" dans l'interface
3. Pour les alias GMX/CaraMail, utilisez le mot de passe du compte principal

---

#### 4. **Timeout (>10 secondes)**

**Cause:** Le serveur IMAP ne répond pas ou est trop lent

**Solution:** 
- Vérifiez votre connexion internet
- Le serveur peut être surchargé, réessayez plus tard
- Certains serveurs peuvent bloquer les connexions depuis Docker

---

#### 5. **Impossible de se connecter au serveur**

**Cause:** Serveur IMAP incorrect ou inaccessible

**Solution:**
- Vérifiez que le serveur IMAP est correct dans `email_config`
- Testez la connexion manuellement avec un client email (Thunderbird, Outlook)

---

#### 6. **Impossible de résoudre le nom du serveur**

**Cause:** Nom de domaine incorrect ou DNS non résolu

**Solution:**
- Vérifiez que le domaine email est correct
- Vérifiez la configuration DNS

---

## ⚙️ Configuration Technique

### Configuration par Défaut

Le système reconnaît automatiquement les domaines suivants :

| Domaine | Serveur IMAP | Port |
|---------|--------------|------|
| gmx.com, gmx.fr | imap.gmx.com | 993 |
| gmail.com | imap.gmail.com | 993 |
| outlook.com, hotmail.com, live.com | outlook.office365.com | 993 |
| yahoo.com, yahoo.fr | imap.mail.yahoo.com | 993 |
| caramail.com, caramail.fr | imap.caramail.com | 993 |
| orange.fr, wanadoo.fr | imap.orange.fr | 993 |
| free.fr | imap.free.fr | 993 |
| laposte.net | imap.laposte.net | 993 |
| sfr.fr | imap.sfr.fr | 993 |
| numericable.fr | imap.numericable.fr | 993 |

Pour les autres domaines, le système essaie automatiquement `imap.{domaine}`.

---

### Configuration Personnalisée

#### Structure dans personas.json

```json
{
  "persona1": {
    "name": "Antoine Petit",
    "email": "antoine.petit@caramail.fr",
    "password": "mot_de_passe",
    "email_config": {
      "imap_server": "imap.caramail.com",
      "imap_port": 993,
      "smtp_server": "smtp.caramail.com",
      "smtp_port": 465,
      "use_ssl": true,
      "use_tls": false
    }
  }
}
```

#### Champs de Configuration

- **`imap_server`** : Adresse du serveur IMAP (ex: `imap.caramail.com`)
- **`imap_port`** : Port IMAP (par défaut: 993 pour SSL, 143 pour non-SSL)
- **`smtp_server`** : Adresse du serveur SMTP (pour l'envoi d'emails)
- **`smtp_port`** : Port SMTP (par défaut: 465 pour SSL, 587 pour TLS)
- **`use_ssl`** : Utiliser SSL pour la connexion (par défaut: true)
- **`use_tls`** : Utiliser TLS pour la connexion (par défaut: false)

---

### Test de Connexion

#### Via l'Interface Web

1. Aller dans **Gestion Emails**
2. Sélectionner un persona
3. Cliquer sur **"Test Connexion"**
4. Vérifier le résultat

#### Via l'API

```bash
POST /api/personas/{email}/emails/test-connection
```

**Réponse en cas de succès** :
```json
{
  "success": true,
  "message": "Connexion réussie au serveur imap.caramail.com:993",
  "server": "imap.caramail.com",
  "port": 993
}
```

**Réponse en cas d'erreur** :
```json
{
  "success": false,
  "error": "Identifiants incorrects. Vérifiez le mot de passe.",
  "server": "imap.caramail.com",
  "port": 993,
  "hint": "Vérifiez que l'accès IMAP est activé pour ce compte."
}
```

---

### 🔐 Sécurité

#### Stockage des Mots de Passe

⚠️ **Important** : Les mots de passe sont actuellement stockés en clair dans `personas.json`.

**Recommandations :**
1. Ne pas commiter `personas.json` dans Git (déjà dans `.gitignore`)
2. Utiliser des permissions restrictives sur le fichier : `chmod 600 config/personas.json`
3. **Future amélioration** : Chiffrement des mots de passe avec une clé maître

---

## 🛠️ Commandes Utiles

### Tester les Connexions Email

```bash
# Tester toutes les connexions email
make test-email

# Le rapport est généré dans EMAIL_STATUS_REPORT.md
cat EMAIL_STATUS_REPORT.md
```

### Configuration OVH

```bash
# Configurer le catch-all OVH
make setup-ovh-catchall

# Créer des emails OVH automatiquement
make create-ovh-emails
```

### Nettoyage

```bash
# Supprimer les personas de test
make clean-test-personas

# Vérifier qu'un fichier n'est pas dans Git
make check-file FILE=config/personas.json
```

---

## 📋 Checklist de Vérification

Pour chaque persona qui échoue:

- [ ] Le persona a-t-il un email configuré ?
- [ ] Le persona a-t-il un mot de passe configuré ?
- [ ] Le mot de passe est-il correct ?
- [ ] Pour les alias, le parent a-t-il le bon mot de passe ?
- [ ] Pour GMX/CaraMail, IMAP est-il activé ?
- [ ] Le serveur IMAP est-il correct dans `email_config` ?
- [ ] La connexion internet fonctionne-t-elle ?

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

## ❓ Questions Fréquentes

### Q: Je n'ai pas de sauvegarde de personas.json, que faire ?
**R:** Recréez-le à partir de `config/personas.json.example` et ajoutez vos personas un par un.

### Q: Comment obtenir les clés API OVH ?
**R:** 
1. Allez sur https://eu.api.ovh.com/createApp/
2. Créez une application
3. Récupérez les 3 clés (Application Key, Application Secret, Consumer Key)
4. Mettez-les dans `config/ovh_config.json`

### Q: Le catch-all OVH, c'est quoi ?
**R:** C'est une configuration qui fait que **tous les emails** envoyés à `*@maily.ovh` arrivent dans une seule boîte. Vous pouvez créer autant de personas que vous voulez sans créer de comptes individuels.

### Q: Je veux garder mes emails GMX, c'est possible ?
**R:** Oui, mais vous devrez activer IMAP manuellement pour chaque compte. Voir la section [Résolution de Problèmes](#-résolution-de-problèmes).

---

## 📞 Support

Si vous rencontrez toujours des problèmes:

1. Consultez `EMAIL_STATUS_REPORT.md` pour les détails (généré par `make test-email`)
2. Vérifiez les logs dans l'interface Auto Apply
3. Testez la connexion manuellement avec un client email (Thunderbird, Outlook)

---

## 🔄 Prochaines Étapes

1. **Recréer `config/personas.json`** (si vous avez une sauvegarde)
2. **Choisir votre solution** (OVH recommandé)
3. **Configurer** selon la solution choisie
4. **Tester** avec `make test-email`
5. **Vérifier le rapport** `EMAIL_STATUS_REPORT.md`

---

**💡 Besoin d'aide ?** Consultez ce guide dans l'ordre des sections pour une progression logique.

