# 🚀 Auto Apply - Système de Candidature Automatique

Système complet de candidature automatique avec gestion multi-personas, recherches multiples, interface web moderne et ligne de commande.

## 📁 Structure du Projet

```
auto_apply/
├── src/                    # Code source Python
│   ├── __init__.py
│   ├── app.py             # Application Flask principale
│   ├── database.py        # Gestion de la base de données
│   ├── scraper.py         # Scraping d'offres d'emploi
│   ├── job_filter.py      # Filtrage des offres
│   ├── auto_apply.py      # Automatisation des candidatures
│   ├── cv_generator.py    # Génération de CVs
│   ├── application_generator.py  # Génération de lettres de motivation
│   ├── stats.py           # Statistiques
│   ├── persona_manager.py # Gestion des personas
│   ├── search_manager.py  # Gestion des recherches
│   └── cli.py            # Interface ligne de commande
├── templates/             # Templates HTML
│   └── dashboard.html    # Interface web principale
├── docs/                 # Documentation
│   ├── GUIDE_COMPLET.md
│   ├── AMELIORATIONS.md
│   └── ...
├── data/                 # Base de données (créé automatiquement)
├── cvs/                  # CVs générés (créé automatiquement)
├── docker-compose.yml    # Configuration Docker Compose
├── Dockerfile           # Image Docker
├── requirements.txt     # Dépendances Python
├── Makefile            # Commandes utiles
├── personas.json       # Configuration des personas
├── cvs.json           # Modèles de CVs
├── cv_template.html   # Template HTML pour CVs
├── cover_letter_template.txt  # Template de lettre de motivation
└── README.md          # Ce fichier
```

## 🚀 Démarrage Rapide

### Avec Docker (Recommandé)

```bash
# Construire et démarrer
make build
make up

# Ou en une commande
make rebuild

# Accéder à l'interface
make open
```

L'interface sera disponible sur http://localhost:2020

### Commandes Makefile

```bash
make help          # Afficher toutes les commandes
make build         # Construire l'image Docker
make up            # Démarrer les conteneurs
make down          # Arrêter les conteneurs
make restart       # Redémarrer les conteneurs
make logs          # Voir les logs
make shell         # Ouvrir un shell dans le conteneur
make test          # Tester la connexion
```

## 📚 Documentation

Toute la documentation est disponible dans le dossier `docs/` :

- `docs/GUIDE_COMPLET.md` - Guide d'utilisation complet
- `docs/AMELIORATIONS.md` - Liste des améliorations
- `docs/QUICKSTART.md` - Guide de démarrage rapide
- `docs/MAKEFILE.md` - Documentation du Makefile
- `docs/DOCKER.md` - Guide Docker

## ✨ Fonctionnalités

### 🎯 Gestion des Personas
- Créer, modifier, supprimer des personas
- Créer des variantes automatiquement
- Tester les personas
- Sélection multiple pour les candidatures

### 🔍 Recherches Multiples
- Créer plusieurs recherches d'emploi
- Types de postes variés (développeur, devops, data, etc.)
- Lancer plusieurs recherches simultanément
- Paramètres personnalisés par recherche

### 📊 Interface Web
- Dashboard en temps réel
- Statistiques détaillées
- Logs en direct
- Mode sombre/clair
- Drawer avec onglets organisés

### 💻 Ligne de Commande
- Interface CLI complète
- Mode dry-run pour tester
- Statistiques et actions individuelles

## ⚙️ Configuration

### Personas
Éditez `personas.json` pour configurer vos personas.

### CVs
Éditez `cvs.json` pour définir les modèles de CVs.

### Recherches
Créez vos recherches via l'interface web ou directement dans le code.

## 🛠️ Développement

### Structure du Code

Tous les fichiers Python sont dans `src/` :
- `app.py` : Application Flask principale avec API et WebSocket
- `persona_manager.py` : Gestion CRUD des personas
- `search_manager.py` : Gestion CRUD des recherches
- Autres modules : fonctionnalités spécifiques

### Variables d'Environnement

- `DATABASE_DIR` : Répertoire de la base de données (défaut: `/app/data`)
- `FLASK_ENV` : Environnement Flask (production/development)

## 📝 Licence

Ce projet est à usage personnel.

## 🤝 Contribution

Pour améliorer le projet, n'hésitez pas à proposer des modifications !

---

**Note** : Ce système est conçu pour automatiser les candidatures. Utilisez-le de manière responsable et respectez les conditions d'utilisation des sites d'emploi.

