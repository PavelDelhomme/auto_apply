# 📧 Configuration Email des Personas

## 🎯 Vue d'Ensemble

Chaque persona peut avoir une configuration email personnalisée pour se connecter à sa boîte email via IMAP. Si aucune configuration n'est fournie, le système utilise des serveurs IMAP par défaut selon le domaine de l'email.

## 🔧 Configuration par Défaut

Le système reconnaît automatiquement les domaines suivants :

| Domaine | Serveur IMAP | Port |
|---------|--------------|------|
| gmx.com, gmx.fr | imap.gmx.com | 993 |
| gmail.com | imap.gmail.com | 993 |
| outlook.com, hotmail.com, live.com | outlook.office365.com | 993 |
| yahoo.com, yahoo.fr | imap.mail.yahoo.com | 993 |
| **caramail.com, caramail.fr** | **imap.caramail.com** | **993** |
| orange.fr, wanadoo.fr | imap.orange.fr | 993 |
| free.fr | imap.free.fr | 993 |
| laposte.net | imap.laposte.net | 993 |
| sfr.fr | imap.sfr.fr | 993 |
| numericable.fr | imap.numericable.fr | 993 |

Pour les autres domaines, le système essaie automatiquement `imap.{domaine}`.

## ⚙️ Configuration Personnalisée

### Structure dans personas.json

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

### Champs de Configuration

- **`imap_server`** : Adresse du serveur IMAP (ex: `imap.caramail.com`)
- **`imap_port`** : Port IMAP (par défaut: 993 pour SSL, 143 pour non-SSL)
- **`smtp_server`** : Adresse du serveur SMTP (pour l'envoi d'emails)
- **`smtp_port`** : Port SMTP (par défaut: 465 pour SSL, 587 pour TLS)
- **`use_ssl`** : Utiliser SSL pour la connexion (par défaut: true)
- **`use_tls`** : Utiliser TLS pour la connexion (par défaut: false)

## 🔍 Test de Connexion

### Via l'Interface Web

1. Aller dans **Gestion Emails**
2. Sélectionner un persona
3. Cliquer sur **"Test Connexion"**
4. Vérifier le résultat

### Via l'API

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

## 🚨 Problèmes Courants

### Erreur : "Impossible de se connecter au serveur"

**Causes possibles** :
1. Le serveur IMAP est incorrect
2. Le port est incorrect
3. Le serveur n'accepte pas les connexions depuis votre IP
4. L'accès IMAP n'est pas activé pour ce compte

**Solutions** :
1. Vérifier la configuration email du persona
2. Vérifier que l'accès IMAP est activé dans les paramètres du compte email
3. Essayer avec un port différent (143 au lieu de 993)
4. Vérifier les paramètres de sécurité du compte (connexions moins sécurisées, etc.)

### Erreur : "Identifiants incorrects"

**Causes possibles** :
1. Le mot de passe est incorrect
2. Le compte nécessite un "mot de passe d'application" (Gmail, etc.)
3. L'authentification à deux facteurs est activée

**Solutions** :
1. Vérifier le mot de passe dans `personas.json`
2. Pour Gmail, créer un "mot de passe d'application" dans les paramètres de sécurité
3. Désactiver temporairement l'authentification à deux facteurs ou utiliser un mot de passe d'application

### Erreur : "Impossible de résoudre le nom du serveur"

**Causes possibles** :
1. Le nom du serveur IMAP est incorrect
2. Problème de connexion réseau

**Solutions** :
1. Vérifier que le serveur IMAP est correct (ex: `imap.caramail.com`)
2. Vérifier la connexion internet
3. Essayer de ping le serveur : `ping imap.caramail.com`

## 🔐 Sécurité

### Stockage des Mots de Passe

⚠️ **Important** : Les mots de passe sont actuellement stockés en clair dans `personas.json`.

**Recommandations** :
1. Ne pas commiter `personas.json` dans Git (déjà dans `.gitignore`)
2. Utiliser des permissions restrictives sur le fichier : `chmod 600 config/personas.json`
3. **Future amélioration** : Chiffrement des mots de passe avec une clé maître

### Configuration Sécurisée

Pour une configuration plus sécurisée :
1. Stocker les mots de passe dans une variable d'environnement
2. Utiliser un gestionnaire de secrets (Vault, etc.)
3. Chiffrer le fichier `personas.json`

## 📝 Exemples

### Caramail

```json
{
  "persona10": {
    "name": "Antoine Petit",
    "email": "antoine.petit@caramail.fr",
    "password": "mot_de_passe",
    "email_config": {
      "imap_server": "imap.caramail.com",
      "imap_port": 993
    }
  }
}
```

### Gmail avec Mot de Passe d'Application

```json
{
  "persona1": {
    "name": "John Doe",
    "email": "john.doe@gmail.com",
    "password": "xxxx xxxx xxxx xxxx",
    "email_config": {
      "imap_server": "imap.gmail.com",
      "imap_port": 993
    }
  }
}
```

### Configuration Personnalisée

```json
{
  "persona1": {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "password": "mot_de_passe",
    "email_config": {
      "imap_server": "mail.example.com",
      "imap_port": 143,
      "use_ssl": false,
      "smtp_server": "smtp.example.com",
      "smtp_port": 587,
      "use_tls": true
    }
  }
}
```

## 🔗 Ressources

- [Guide Complet des Personas](GUIDE_COMPLET_PERSONAS.md)
- [Documentation du Système](README_SYSTEME_COMPLET.md)

