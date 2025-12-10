# 📧 Guide de Création de Boîtes Mail pour Personas

## 🎯 Objectif

Ce guide vous aide à créer des boîtes mail pour vos personas **sans numéro de téléphone** et **sans utiliser GMX** (qui nécessite maintenant l'activation manuelle d'IMAP).

---

## 🚨 Problème Actuel avec GMX/CaraMail

**IMPORTANT:** GMX et CaraMail ont désactivé IMAP par défaut pour des raisons de sécurité. Même avec le bon mot de passe, la connexion échouera tant que IMAP n'est pas activé manuellement dans les paramètres de la boîte mail.

**Solution temporaire:** Activez IMAP dans les paramètres de chaque compte GMX/CaraMail.

**Solution recommandée:** Utilisez des fournisseurs alternatifs qui n'ont pas cette restriction.

---

## 🌐 Fournisseurs Recommandés (Sans Numéro de Téléphone)

### 1. **Mail.com** ⭐⭐⭐ MEILLEUR CHOIX
- **Avantages:**
  - ✅ Pas de numéro de téléphone requis
  - ✅ IMAP/SMTP disponibles gratuitement et activés par défaut
  - ✅ Nombreux domaines disponibles (@mail.com, @email.com, @inbox.com, @gmx.com, @yahoo.com, etc.)
  - ✅ 2 GB gratuits
  - ✅ Interface simple
  - ✅ Pas de limite stricte sur le nombre de comptes
  
- **Inconvénients:**
  - Interface moins moderne que Gmail
  - Publicités dans la version gratuite (mais pas gênantes)

- **Création:**
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

- **Configuration IMAP (déjà activé par défaut):**
  - Serveur IMAP: `imap.mail.com` (port 993, SSL)
  - Serveur SMTP: `smtp.mail.com` (port 587, STARTTLS)
  - Utilisez votre adresse email complète comme nom d'utilisateur
  - Utilisez votre mot de passe

- **Ajout dans personas.json:**
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

### 2. **Zoho Mail** ⭐⭐ Recommandé
- **Avantages:**
  - ✅ Pas de numéro de téléphone requis
  - ✅ IMAP/SMTP disponibles gratuitement
  - ✅ 5 GB gratuits
  - ✅ Interface professionnelle
  - ✅ Pas de publicités
  
- **Inconvénients:**
  - Limite de 5 comptes gratuits par organisation
  - Nécessite de créer une "organisation" (mais c'est gratuit)

- **Création:**
  1. Allez sur https://www.zoho.com/mail/
  2. Cliquez sur "Créer un compte"
  3. Choisissez "Pour usage personnel"
  4. Créez votre organisation (nom fictif OK, ex: "MonEntreprise")
  5. Créez votre compte email
  6. **PAS de vérification par SMS nécessaire**

- **Configuration IMAP:**
  - Serveur IMAP: `imap.zoho.com` (port 993, SSL)
  - Serveur SMTP: `smtp.zoho.com` (port 587, STARTTLS)

---

### 3. **ProtonMail** ⭐ Recommandé (pour la sécurité)
- **Avantages:**
  - Pas de numéro de téléphone requis (sauf pour certaines fonctionnalités)
  - Chiffrement end-to-end
  - IMAP disponible via ProtonMail Bridge (gratuit)
  - Interface moderne
  - 500 MB gratuits (1 GB avec compte payant)
  
- **Inconvénients:**
  - Nécessite ProtonMail Bridge pour IMAP (application à installer)
  - Limite de 1 compte gratuit par IP
  
- **Création:**
  1. Allez sur https://proton.me/mail
  2. Cliquez sur "Créer un compte gratuit"
  3. Choisissez un nom d'utilisateur et un mot de passe
  4. Pas de vérification par SMS nécessaire pour le compte de base
  5. Pour IMAP: Installez ProtonMail Bridge depuis https://proton.me/mail/bridge

- **Configuration IMAP (via Bridge):**
  - Serveur IMAP: `127.0.0.1:1143`
  - Serveur SMTP: `127.0.0.1:1025`
  - Utilisez les identifiants du Bridge (différents de votre compte)

---

### 2. **Tutanota** ⭐ Recommandé
- **Avantages:**
  - Pas de numéro de téléphone requis
  - Chiffrement automatique
  - Interface simple
  - 1 GB gratuit
  
- **Inconvénients:**
  - IMAP nécessite un abonnement payant (12€/an)
  - Interface moins flexible que ProtonMail

- **Création:**
  1. Allez sur https://tutanota.com
  2. Cliquez sur "Créer un compte gratuit"
  3. Choisissez un nom d'utilisateur et un mot de passe
  4. Pas de vérification par SMS

---

### 3. **Mail.com**
- **Avantages:**
  - Pas de numéro de téléphone requis
  - Nombreux domaines disponibles (@mail.com, @email.com, @inbox.com, etc.)
  - IMAP/SMTP disponibles gratuitement
  - 2 GB gratuits
  
- **Inconvénients:**
  - Interface moins moderne
  - Publicités dans la version gratuite

- **Création:**
  1. Allez sur https://www.mail.com
  2. Cliquez sur "Créer un compte"
  3. Choisissez un domaine et un nom d'utilisateur
  4. Remplissez le formulaire (pas de SMS requis)
  5. Activez IMAP dans les paramètres

- **Configuration IMAP:**
  - Serveur IMAP: `imap.mail.com` (port 993)
  - Serveur SMTP: `smtp.mail.com` (port 587)

---

### 4. **Zoho Mail**
- **Avantages:**
  - Pas de numéro de téléphone requis
  - IMAP/SMTP disponibles gratuitement
  - 5 GB gratuits
  - Interface professionnelle
  
- **Inconvénients:**
  - Limite de 5 comptes gratuits par organisation
  - Nécessite de créer une "organisation"

- **Création:**
  1. Allez sur https://www.zoho.com/mail/
  2. Cliquez sur "Créer un compte"
  3. Choisissez un nom d'organisation
  4. Créez votre compte (pas de SMS requis)

- **Configuration IMAP:**
  - Serveur IMAP: `imap.zoho.com` (port 993)
  - Serveur SMTP: `smtp.zoho.com` (port 587)

---

### 5. **Yandex Mail**
- **Avantages:**
  - Pas de numéro de téléphone requis
  - IMAP/SMTP disponibles gratuitement
  - 10 GB gratuits
  - Domaine @yandex.com
  
- **Inconvénients:**
  - Service russe (peut poser problème selon votre localisation)
  - Interface en russe par défaut (peut être changée)

- **Création:**
  1. Allez sur https://mail.yandex.com
  2. Cliquez sur "Créer un compte"
  3. Remplissez le formulaire (pas de SMS requis)

- **Configuration IMAP:**
  - Serveur IMAP: `imap.yandex.com` (port 993)
  - Serveur SMTP: `smtp.yandex.com` (port 465)

---

### 6. **Temp-Mail Services** (Temporaires)
- **Services:** 10minutemail.com, guerrillamail.com, tempmail.com
- **Avantages:**
  - Création instantanée
  - Pas de vérification
  - Parfait pour les tests
  
- **Inconvénients:**
  - Emails temporaires (expirent après quelques minutes/heures)
  - Pas adapté pour un usage permanent

---

## 🔧 Configuration dans personas.json

Une fois votre boîte mail créée, ajoutez-la dans `config/personas.json`:

### Exemple pour Mail.com:

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

### Exemple pour Zoho Mail:

```json
{
    "personaXXX": {
        "name": "Marie Martin",
        "email": "marie.martin@votre-organisation.zoho.com",
        "password": "votre_mot_de_passe",
        "alias": false,
        "parent": null,
        "email_config": {
            "imap_server": "imap.zoho.com",
            "imap_port": 993,
            "smtp_server": "smtp.zoho.com",
            "smtp_port": 587
        }
    }
}
```

> 💡 **Note:** Le champ `email_config` est optionnel. Si vous ne le spécifiez pas, le système utilisera les serveurs par défaut selon le domaine.

---

## 📋 Checklist de Création

Pour chaque nouvelle boîte mail:

- [ ] Choisir un fournisseur (recommandé: **Mail.com** - le plus simple)
- [ ] Créer le compte (sans numéro de téléphone)
- [ ] Vérifier l'email de confirmation
- [ ] Activer IMAP dans les paramètres (si nécessaire - Mail.com l'a activé par défaut)
- [ ] Tester la connexion IMAP avec un client email (Thunderbird, Outlook) pour vérifier
- [ ] Ajouter le persona dans `personas.json` avec la configuration `email_config`
- [ ] Tester la connexion depuis l'interface Auto Apply (bouton "Tester connexion")
- [ ] Vérifier la réception d'emails (bouton "Récupérer les emails")

## 🎯 Stratégie Recommandée

### Pour créer plusieurs boîtes mail rapidement:

1. **Utilisez Mail.com** (le plus simple):
   - Créez plusieurs comptes avec différents domaines (@mail.com, @email.com, @inbox.com)
   - Chaque compte peut avoir plusieurs alias (gratuit)
   - IMAP activé par défaut

2. **Répartissez les fournisseurs:**
   - 50% Mail.com
   - 30% Zoho Mail
   - 20% Autres (ProtonMail, Tutanota, etc.)

3. **Organisez par groupes:**
   - Créez des personas principaux sur différents fournisseurs
   - Créez des alias pour chaque persona principal
   - Cela évite de dépendre d'un seul fournisseur

---

## 🚫 Fournisseurs à Éviter

- **GMX/CaraMail**: Nécessite activation manuelle d'IMAP (désactivé par défaut)
- **Gmail**: Nécessite numéro de téléphone pour la vérification
- **Outlook/Hotmail**: Nécessite numéro de téléphone pour la vérification
- **Yahoo**: Nécessite numéro de téléphone pour la vérification

---

## 💡 Conseils

1. **Rotation des fournisseurs**: Utilisez différents fournisseurs pour éviter les limites
2. **Mots de passe forts**: Utilisez des mots de passe uniques et sécurisés
3. **Vérification régulière**: Testez régulièrement les connexions avec le script `scripts/test_all_personas_email.py`
4. **Sauvegarde**: Gardez une liste de tous les comptes créés avec leurs mots de passe dans un gestionnaire de mots de passe

---

## 🔄 Mise à Jour du Rapport

Après avoir créé de nouvelles boîtes mail, exécutez:

```bash
python3 scripts/test_all_personas_email.py
```

Cela générera un nouveau rapport dans `EMAIL_STATUS_REPORT.md` avec le statut de tous les personas.

---

## 📞 Support

Si vous rencontrez des problèmes:
1. Vérifiez le rapport `EMAIL_STATUS_REPORT.md`
2. Consultez les logs dans l'interface Auto Apply
3. Testez la connexion manuellement avec un client email (Thunderbird, Outlook, etc.)

