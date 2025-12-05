# 🐳 Guide Docker - Auto Apply

## Démarrage rapide

### 1. Construire et lancer le conteneur

```bash
docker-compose up -d --build
```

### 2. Accéder à l'interface

Ouvrez votre navigateur à l'adresse : **http://localhost:2020**

### 3. Arrêter le conteneur

```bash
docker-compose down
```

## Commandes utiles

### Voir les logs en temps réel
```bash
docker-compose logs -f
```

### Redémarrer le conteneur
```bash
docker-compose restart
```

### Reconstruire l'image
```bash
docker-compose up -d --build
```

### Accéder au shell du conteneur
```bash
docker-compose exec auto-apply bash
```

### Voir les statistiques du conteneur
```bash
docker stats auto-apply-dashboard
```

## Configuration des ports

Le port par défaut est **2020**. Pour changer le port, modifiez `docker-compose.yml` :

```yaml
ports:
  - "2021:2020"  # Utilisez le port 2021 sur votre machine
```

## Volumes montés

Les fichiers suivants sont montés comme volumes pour persister les données :

- `personas.json` - Configuration des personas
- `cvs.json` - Modèles de CVs
- `cv_template.html` - Template de CV
- `cover_letter_template.txt` - Template de lettre de motivation
- `cvs/` - Dossier contenant les CVs générés
- `jobs.db` - Base de données SQLite

## Dépannage

### Le conteneur ne démarre pas

Vérifiez les logs :
```bash
docker-compose logs
```

### Port déjà utilisé

Si le port 2020 est déjà utilisé, changez-le dans `docker-compose.yml` :
```yaml
ports:
  - "2021:2020"  # Utilisez un autre port
```

### Problèmes de permissions

Si vous avez des problèmes de permissions avec les fichiers montés :
```bash
sudo chown -R $USER:$USER .
```

### Reconstruire depuis zéro

```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Architecture

Le conteneur inclut :
- Python 3.9
- Chrome/Chromium (pour Selenium)
- ChromeDriver
- wkhtmltopdf (pour la génération de PDFs)
- Toutes les dépendances Python

Tout est configuré et prêt à l'emploi !

