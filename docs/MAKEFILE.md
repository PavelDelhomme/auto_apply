# 📋 Guide du Makefile

Le Makefile fournit des commandes simples pour gérer tous les aspects de l'application Docker.

## 🚀 Commandes principales

### Démarrage et arrêt

```bash
make up          # Démarre les conteneurs en arrière-plan
make down        # Arrête et supprime les conteneurs
make start       # Alias de 'up'
make stop        # Alias de 'down'
make restart     # Redémarre les conteneurs
```

### Construction

```bash
make build       # Construit l'image Docker
make rebuild     # Reconstruit l'image et redémarre (sans cache)
```

### Logs et monitoring

```bash
make logs        # Affiche les logs en temps réel (suivre avec -f)
make logs-tail   # Affiche les 100 dernières lignes
make stats       # Affiche les statistiques d'utilisation des ressources
make ps          # Affiche l'état des conteneurs
make status      # Alias de 'ps'
```

### Accès au conteneur

```bash
make shell       # Ouvre un shell bash dans le conteneur
make shell-root  # Ouvre un shell root dans le conteneur
make exec CMD="python --version"  # Exécute une commande
make run CMD="python --version"   # Exécute une commande dans un nouveau conteneur
```

### Nettoyage

```bash
make clean           # Supprime conteneurs, volumes et images (demande confirmation)
make clean-volumes   # Supprime uniquement les volumes
make clean-images    # Supprime uniquement les images
```

### Utilitaires

```bash
make help        # Affiche toutes les commandes disponibles
make open        # Ouvre l'interface dans le navigateur
make test        # Teste la connexion au conteneur
make backup-db    # Sauvegarde la base de données
make restore-db FILE=backups/jobs_20240101_120000.sql  # Restaure la base de données
```

### Développement

```bash
make install-deps  # Installe les dépendances localement (sans Docker)
make dev           # Lance l'application en mode développement (sans Docker)
```

## 📖 Exemples d'utilisation

### Démarrage complet

```bash
# 1. Construire et démarrer
make up

# 2. Vérifier que tout fonctionne
make status

# 3. Ouvrir l'interface
make open

# 4. Suivre les logs
make logs
```

### Débogage

```bash
# Voir les logs en temps réel
make logs

# Ouvrir un shell pour inspecter
make shell

# Vérifier les ressources utilisées
make stats

# Tester une commande Python
make exec CMD="python -c 'import sys; print(sys.version)'"
```

### Maintenance

```bash
# Sauvegarder la base de données
make backup-db

# Redémarrer après une modification
make restart

# Reconstruire complètement
make rebuild

# Nettoyer tout (attention!)
make clean
```

### Développement local (sans Docker)

```bash
# Installer les dépendances
make install-deps

# Lancer l'application
make dev
```

## 🔧 Personnalisation

Vous pouvez modifier les variables au début du Makefile :

```makefile
COMPOSE_FILE = docker-compose.yml
SERVICE_NAME = auto-apply
CONTAINER_NAME = auto-apply-dashboard
PORT = 2020
```

## 💡 Astuces

1. **Voir toutes les commandes** : `make help`
2. **Logs en continu** : `make logs` puis Ctrl+C pour quitter
3. **Shell interactif** : `make shell` puis tapez vos commandes
4. **Exécuter des scripts** : `make exec CMD="python script.py"`
5. **Sauvegardes régulières** : Ajoutez `make backup-db` dans un cron

## ⚠️ Notes importantes

- `make clean` demande confirmation avant de supprimer
- Les sauvegardes sont stockées dans `backups/`
- `make rebuild` reconstruit sans cache (plus long mais plus propre)
- `make open` fonctionne sur Linux (xdg-open) et macOS (open)

