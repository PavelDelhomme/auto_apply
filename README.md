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
├── config/            # Fichiers de configuration
│   ├── personas.json  # Configuration des personas
│   ├── cvs.json       # Modèles de CVs
│   └── searches.json  # Recherches sauvegardées
├── templates/         # Templates
│   ├── dashboard.html # Interface web principale
│   ├── index.html     # Page de statistiques
│   ├── cv/            # Templates de CV
│   │   └── cv_template.html
│   └── letters/       # Templates de lettres
│       └── cover_letter_template.txt
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

- **[Guide Complet des Personas](docs/GUIDE_COMPLET_PERSONAS.md)** - Tout sur les personas, variantes, CVs multiples
- `docs/AMELIORATIONS_LOGS_STATS.md` - Système de logs et statistiques historiques
- `docs/AMELIORATIONS_RECHERCHES_PERSONAS.md` - Recherches avec personas assignés
- `docs/GUIDE_COMPLET.md` - Guide d'utilisation complet
- `docs/AMELIORATIONS.md` - Liste des améliorations
- `docs/QUICKSTART.md` - Guide de démarrage rapide
- `docs/MAKEFILE.md` - Documentation du Makefile
- `docs/DOCKER.md` - Guide Docker

### 🎓 Concepts Importants

#### Variantes de Personas

Une **variante** (ou **alias**) est un persona qui hérite des caractéristiques d'un persona de base, mais avec un nom et email différents. Cela permet de :
- Multiplier les candidatures à la même offre
- Tester différentes approches
- Éviter la détection

**Exemple** :
- Persona de base : `Christian Gaillard` (christian.gaillard@gmx.com)
- Variante 1 : `Georges Fabre` (george.fabre@gmx.com) - alias: true, parent: christian.gaillard@gmx.com
- Variante 2 : `Hugo Germain` (hugo.germain@gmx.com) - alias: true, parent: christian.gaillard@gmx.com

#### CVs Multiples

Un persona peut avoir plusieurs CVs :
- **CV par défaut** : Utilisé si aucun CV spécifique n'est trouvé
- **CV par recherche** : CV spécialisé pour une recherche (`search_key`)
- **CVs avec ID** : Plusieurs CVs avec des IDs différents (`cv_id`)

**Exemple** :
- CV par défaut : `christian.gaillard_cv.pdf`
- CV pour recherche Python : `christian.gaillard_python_senior_python_cv.pdf`
- CV pour recherche Django : `christian.gaillard_django_dev_django_cv.pdf`

#### Structure Complète d'un Persona

```json
{
  "name": "Christian Gaillard",
  "email": "christian.gaillard@gmx.com",
  "password": "mot_de_passe",
  "alias": false,
  "parent": null,
  "skills": ["Python", "JavaScript", "Django", "React"],
  "experience_years": 5,
  "education": [
    {
      "degree": "Master Informatique",
      "school": "Université de Rennes",
      "dates": "2015-2020"
    }
  ],
  "languages": ["Français", "Anglais"],
  "location": "Rennes, France",
  "phone": "+33 6 12 34 56 78",
  "linkedin": "https://linkedin.com/in/christian-gaillard",
  "github": "https://github.com/christian-gaillard",
  "portfolio": "https://christian-gaillard.dev",
  "notes": "Spécialisé en développement web full-stack"
}
```

## ✨ Fonctionnalités

### 🎯 Gestion des Personas
- Créer, modifier, supprimer des personas avec détails complets
- **Variantes** : Créer des alias qui héritent d'un persona de base
- **CVs multiples** : Un CV par défaut + CVs spécifiques par recherche
- Tester les personas et leurs emails
- Sélection multiple pour les candidatures
- Gestion complète des informations (compétences, expérience, éducation, etc.)

### 🔍 Recherches Multiples
- Créer plusieurs recherches d'emploi avec critères détaillés
- **Assignation de personas** : Spécifier quels personas utiliser pour chaque recherche
- Types de postes variés (développeur, devops, data, etc.)
- Lancer plusieurs recherches simultanément depuis les paramètres
- Paramètres personnalisés par recherche (salaire, contrat, télétravail, etc.)
- Mode standalone (scraper uniquement, sans personas)

### 📄 Système de CVs Avancé
- **CV par défaut** : CV généraliste pour chaque persona
- **CVs par recherche** : CV spécialisé pour une recherche spécifique
- **CVs multiples** : Plusieurs CVs avec IDs différents
- Génération automatique avec photos uniques
- Stockage dans la base de données pour traçabilité

### 📧 Gestion des Emails
- Récupération automatique depuis IMAP
- Test de connexion pour chaque persona
- Stockage des emails en base de données
- Marquage comme lu/non lu
- Interface de visualisation complète

### 📊 Interface Web
- Dashboard en temps réel avec WebSocket
- Statistiques détaillées et historiques
- Logs persistants avec filtres
- Mode sombre/clair
- Drawer avec onglets organisés
- Gestion complète des personas, recherches, offres, emails

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

