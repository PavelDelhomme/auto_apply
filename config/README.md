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

Le fichier `personas.json` peut être placé à plusieurs endroits :

#### Option 1: Dans le projet (développement)
```bash
cp config/personas.json.example config/personas.json
# Puis modifiez-le avec vos personas réels
```

#### Option 2: En dehors du projet (production) ⭐ RECOMMANDÉ
Si vous placez `personas.json` en dehors du projet (ex: `../../personas.json`), le système le détectera automatiquement.

Le fichier est configuré dans `docker-compose.yml` pour être monté depuis `../../personas.json`.

**Avantage:** Le fichier n'est jamais dans le projet, donc aucun risque de commit accidentel.

#### Option 3: Variable d'environnement
Vous pouvez spécifier un chemin personnalisé via `PERSONAS_FILE` dans `docker-compose.yml`:

```yaml
environment:
  - PERSONAS_FILE=/chemin/absolu/vers/personas.json
```

### Vérifier que personas.json est chargé

Consultez les logs pour vérifier :
```bash
make logs
```

Vous devriez voir :
```
[HH:MM:SS] [INFO] ✅ X persona(s) chargé(s) depuis: /chemin/vers/personas.json
```

### Créer ovh_config.json

Si vous utilisez l'API OVH :

```bash
cp config/ovh_config.json.example config/ovh_config.json
```

Puis remplissez vos clés API OVH.

## 🔒 Sécurité

Ces fichiers sont exclus de Git via `.gitignore` pour protéger vos informations sensibles.

**⚠️ IMPORTANT:** Ne committez jamais ces fichiers dans Git !

