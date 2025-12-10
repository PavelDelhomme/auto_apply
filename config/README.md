# 📁 Configuration

Ce dossier contient les fichiers de configuration de l'application.

## ⚠️ Fichiers Sensibles

Les fichiers suivants contiennent des informations sensibles et **NE SONT PAS** versionnés dans Git :

- `personas.json` - Contient les personas avec leurs mots de passe email
- `ovh_config.json` - Contient les clés API OVH

## 📋 Fichiers d'Exemple

- `personas.json.example` - Exemple de structure pour personas.json
- `ovh_config.json.example` - Exemple de configuration OVH

## 🔧 Création des Fichiers

### Créer personas.json

Si le fichier n'existe pas, créez-le en copiant l'exemple :

```bash
cp config/personas.json.example config/personas.json
```

Puis modifiez-le avec vos personas réels.

### Créer ovh_config.json

Si vous utilisez l'API OVH :

```bash
cp config/ovh_config.json.example config/ovh_config.json
```

Puis remplissez vos clés API OVH.

## 🔒 Sécurité

Ces fichiers sont exclus de Git via `.gitignore` pour protéger vos informations sensibles.

**⚠️ IMPORTANT:** Ne committez jamais ces fichiers dans Git !

