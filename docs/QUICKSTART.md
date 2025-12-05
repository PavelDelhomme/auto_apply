# 🚀 Guide de Démarrage Rapide

## Installation et Lancement avec Docker

### Méthode 1 : Avec Makefile (Recommandé) ⚡

```bash
# 1. Voir toutes les commandes disponibles
make help

# 2. Lancer l'application
make up

# 3. Ouvrir l'interface dans le navigateur
make open
```

### Méthode 2 : Avec Docker Compose

```bash
# 1. Lancer l'application
docker-compose up -d --build

# 2. Accéder à l'interface
# Ouvrez votre navigateur et allez sur : http://localhost:2020
```

## Commandes Makefile utiles

```bash
make help        # Affiche toutes les commandes disponibles
make up          # Démarre les conteneurs
make down        # Arrête les conteneurs
make logs        # Affiche les logs en temps réel
make restart     # Redémarre les conteneurs
make rebuild     # Reconstruit tout depuis zéro
make shell       # Ouvre un shell dans le conteneur
make stats       # Affiche les statistiques d'utilisation
make status      # Affiche l'état des conteneurs
make open        # Ouvre l'interface dans le navigateur
make clean       # Nettoie tout (conteneurs, volumes, images)
```

### 3. Utiliser l'interface

L'interface web vous permet de :

1. **📄 Générer les CVs** : Cliquez sur "Générer les CVs" pour créer les CVs PDF pour tous vos personas
2. **🔍 Rechercher des offres** : Entrez vos critères et cliquez sur "Rechercher des offres"
3. **🚀 Démarrer Auto Apply** : Configurez vos paramètres et lancez le processus automatique
4. **📊 Suivre en temps réel** : Regardez les logs et statistiques se mettre à jour en direct

## Fonctionnalités de l'interface

### Dashboard en temps réel
- Statistiques globales (offres trouvées, candidatures envoyées, etc.)
- Activité de la session en cours
- Barre de progression

### Contrôles
- Génération de CVs
- Recherche d'offres
- Démarrage/Arrêt du processus automatique
- Configuration des paramètres de recherche

### Logs en direct
- Tous les événements s'affichent en temps réel
- Codes couleur pour les différents types de messages
- Scroll automatique vers les nouveaux logs

## Configuration

### Personas
Éditez `personas.json` pour configurer vos personas avant de lancer.

### CVs
Éditez `cvs.json` pour personnaliser les modèles de CVs.

### Paramètres de recherche
Configurez directement dans l'interface web :
- Mots-clés de recherche
- Localisation
- Mots-clés à inclure/exclure
- Nombre maximum de candidatures par persona

## Arrêter l'application

```bash
docker-compose down
```

## Voir les logs du conteneur

```bash
docker-compose logs -f
```

## Dépannage

### Le port 2020 est déjà utilisé
Modifiez `docker-compose.yml` et changez le port :
```yaml
ports:
  - "2021:2020"  # Utilisez le port 2021
```

### L'interface ne se charge pas
Vérifiez que le conteneur est bien démarré :
```bash
docker-compose ps
```

### Erreurs de Chrome/Selenium
Le conteneur inclut déjà Chrome et ChromeDriver. Si vous avez des problèmes, vérifiez les logs :
```bash
docker-compose logs auto-apply
```

## Support

Pour plus d'informations, consultez :
- `README.md` - Documentation complète
- `DOCKER.md` - Guide Docker détaillé

