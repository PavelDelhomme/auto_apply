# 📖 Documentation Complète du Système Auto Apply

## 🎯 Vue d'Ensemble

Auto Apply est un système complet de candidature automatique qui permet de :
- Créer et gérer plusieurs personas (identités virtuelles)
- Scraper des offres d'emploi depuis plusieurs sources
- Postuler automatiquement avec des CVs et lettres de motivation personnalisés
- Suivre les candidatures et les réponses par email
- Analyser les statistiques et performances

## 🏗️ Architecture du Système

### Composants Principaux

1. **Backend Flask** (`src/app.py`)
   - API REST pour toutes les opérations
   - WebSocket pour les mises à jour en temps réel
   - Gestion des candidatures automatiques

2. **Base de Données SQLite** (`src/database.py`)
   - Offres d'emploi (`jobs`)
   - Candidatures (`applications`)
   - Emails des personas (`persona_emails`)
   - Logs (`logs`)
   - Statistiques historiques (`historical_stats`)
   - CVs des personas (`persona_cvs`)

3. **Gestionnaires**
   - `PersonaManager` : CRUD des personas et variantes
   - `SearchManager` : CRUD des recherches et historique

4. **Générateurs**
   - `CVGenerator` : Génération de CVs PDF/HTML
   - `ApplicationGenerator` : Génération de lettres de motivation

5. **Scrapers**
   - `Scraper` : Scraping d'offres depuis Indeed et autres sources

6. **Interface Web** (`templates/dashboard.html`)
   - Dashboard en temps réel
   - Gestion complète des personas, recherches, offres
   - Visualisation des statistiques et logs

## 👤 Système de Personas

### Qu'est-ce qu'un Persona ?

Un **persona** est une identité virtuelle complète avec :
- Nom et email uniques
- Mot de passe pour la boîte email
- Compétences, expérience, éducation
- CVs personnalisés
- Boîte email pour recevoir les réponses

### Structure Complète

```json
{
  "persona1": {
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
}
```

### Variantes (Alias)

Une **variante** est un persona qui hérite des caractéristiques d'un persona de base mais avec un nom et email différents.

**Caractéristiques** :
- `alias: true` : Indique que c'est une variante
- `parent` : Email du persona de base
- Hérite automatiquement des données du parent

**Utilisation** :
- Multiplier les candidatures à la même offre
- Tester différentes approches
- Éviter la détection

**Exemple** :
```json
{
  "persona2": {
    "name": "Georges Fabre",
    "email": "george.fabre@gmx.com",
    "password": "mot_de_passe",
    "alias": true,
    "parent": "christian.gaillard@gmx.com"
  }
}
```

### Création de Variantes

#### Via l'Interface
1. Gestion des Personas → Sélectionner un persona de base
2. Cliquer sur "🔄 Variantes"
3. Choisir le nombre de variantes
4. Optionnel : Modifier le modèle de nom

#### Via l'API
```python
# Une variante
persona_key = persona_manager.create_variant(
    base_persona_key="persona1",
    variant_name="Georges Fabre",
    email_suffix="george.fabre@gmx.com"
)

# Plusieurs variantes
persona_keys = persona_manager.create_multiple_variants(
    base_persona_key="persona1",
    count=5
)
```

## 📄 Système de CVs Multiples

### Concept

Un persona peut avoir **plusieurs CVs** :
1. **CV par défaut** : CV généraliste utilisé par défaut
2. **CV par recherche** : CV spécialisé pour une recherche spécifique
3. **CVs avec ID** : Plusieurs CVs avec des IDs différents

### Structure de Stockage

**Fichiers** :
- CV par défaut : `/app/cvs/{email}_cv.pdf`
- CV par recherche : `/app/cvs/{email}_{search_key}_{cv_id}_cv.pdf`
- CV avec ID : `/app/cvs/{email}_{cv_id}_cv.pdf`

**Base de données** :
- Table `persona_cvs` : Stocke les métadonnées (cv_id, search_key, cv_path, cv_data)

### Création de CVs

#### CV par Défaut
```python
generate_cv_for_persona(
    persona_email="christian.gaillard@gmx.com",
    persona_name="Christian Gaillard",
    cv_data={"title": "Développeur Full Stack", ...},
    cv_id="default"
)
```

#### CV pour une Recherche
```python
generate_cv_for_persona(
    persona_email="christian.gaillard@gmx.com",
    persona_name="Christian Gaillard",
    cv_data={"title": "Développeur Python Senior", ...},
    search_key="python_senior",
    cv_id="python_cv"
)
```

### Utilisation Automatique

Lors d'une candidature :
1. Le système cherche un CV pour `search_key` spécifique
2. Si non trouvé, utilise le CV par défaut (`cv_id='default'`)
3. Si aucun CV, génère un nouveau CV automatiquement

### API

```bash
# Lister tous les CVs d'un persona
GET /api/personas/{email}/cvs

# Récupérer un CV spécifique
GET /api/personas/{email}/cv?search_key=search1&cv_id=cv1

# Générer un nouveau CV
POST /api/personas/{email}/cv/generate
{
  "search_key": "search1",
  "cv_id": "cv1",
  "cv_data": { ... }
}
```

## 🔍 Système de Recherches

### Structure d'une Recherche

```json
{
  "search1": {
    "name": "Développeur Python Rennes",
    "query": "développeur python",
    "location": "Rennes",
    "is_active": true,
    "standalone": false,
    "personas_assigned": ["christian.gaillard@gmx.com"],
    "personas_excluded": [],
    "salary_min": 40000,
    "salary_max": 60000,
    "contract_type": ["CDI"],
    "remote": true,
    "full_time": true,
    "priority": 3
  }
}
```

### Assignation de Personas

- **`personas_assigned`** : Liste des emails de personas à utiliser (si vide, tous les personas)
- **`personas_excluded`** : Liste des emails de personas à exclure

### Mode Standalone

Une recherche `standalone` :
- Scrape uniquement les offres
- Ne postule pas avec des personas
- Utile pour collecter des offres sans candidater

## 📧 Gestion des Emails

### Récupération

Les emails sont récupérés depuis la boîte IMAP du persona et stockés en base de données.

### Types d'Emails

- `application` : Réponses aux candidatures
- `notification` : Notifications diverses
- `other` : Autres emails

### Tests

L'interface permet de :
- Tester la connexion IMAP
- Récupérer les emails depuis IMAP
- Visualiser les emails reçus
- Marquer comme lu/non lu

### API

```bash
# Récupérer les emails
GET /api/personas/{email}/emails

# Compter les emails
GET /api/personas/{email}/emails/count

# Tester la connexion
POST /api/personas/{email}/emails/test-connection

# Récupérer depuis IMAP
POST /api/personas/{email}/emails/fetch
```

## 📊 Statistiques et Logs

### Logs

Tous les logs sont stockés en base de données avec :
- Timestamp
- Niveau (info, success, warning, error)
- Catégorie (general, scraping, application, etc.)
- Marquage test/production

### Statistiques Historiques

Les statistiques sont enregistrées chaque heure avec :
- Nombre d'offres trouvées
- Nombre de candidatures
- Candidatures envoyées/échouées
- Recherches exécutées
- Personas utilisés

### Données de Test

Toutes les données peuvent être marquées comme "test" :
- Jobs de test
- Applications de test
- Emails de test
- Logs de test
- Statistiques de test

Permet de nettoyer facilement les données de test.

## 🚀 Flux de Candidature Automatique

### 1. Lancement

```python
POST /api/searches/run-multiple
{
  "search_keys": ["search1", "search2"],
  "selected_personas": ["persona1@example.com"],
  "max_per_persona": 3,
  "delay_min": 5,
  "delay_max": 10
}
```

### 2. Pour Chaque Recherche

1. **Scraping** : Récupération des offres depuis Indeed
2. **Filtrage** : Filtrage selon les critères de la recherche
3. **Pour chaque persona assigné** :
   - Sélection du CV (spécifique à la recherche ou par défaut)
   - Génération de la lettre de motivation
   - Candidature automatique
   - Enregistrement en base de données

### 3. Suivi

- Logs en temps réel via WebSocket
- Statistiques mises à jour
- Emails récupérés automatiquement

## 🧪 Tests

### Tests Disponibles

```bash
# Tous les tests
make test-all

# Tests unitaires
make test-unit

# Tests d'intégration
make test-integration

# Tests spécifiques
pytest tests/test_persona_emails.py -v
pytest tests/test_persona_manager.py -v
```

### Tests des Emails

Les tests vérifient :
- Insertion d'emails
- Récupération des emails
- Comptage des emails
- Marquage comme lu
- Test de connexion IMAP

## 📁 Structure des Fichiers

```
auto_apply/
├── src/                    # Code source
│   ├── app.py             # Application Flask
│   ├── database.py        # Base de données
│   ├── persona_manager.py # Gestion personas
│   ├── search_manager.py  # Gestion recherches
│   ├── cv_generator.py    # Génération CVs
│   └── ...
├── config/                 # Configuration
│   ├── personas.json      # Personas
│   ├── cvs.json           # Modèles de CVs
│   └── searches.json       # Recherches
├── templates/             # Templates HTML
│   ├── dashboard.html     # Interface principale
│   ├── cv/                # Templates CV
│   └── letters/           # Templates lettres
├── static/                # Fichiers statiques
│   ├── css/               # Styles
│   └── js/                # JavaScript
├── data/                  # Base de données
├── cvs/                   # CVs générés
├── photos/                # Photos des personas
└── docs/                  # Documentation
```

## 🔗 Liens Utiles

- [Guide Complet des Personas](GUIDE_COMPLET_PERSONAS.md)
- [Guide des Recherches](AMELIORATIONS_RECHERCHES_PERSONAS.md)
- [Guide des Logs et Statistiques](AMELIORATIONS_LOGS_STATS.md)

## ❓ Questions Fréquentes

### Q: Qu'est-ce qu'une variante de persona ?
R: Une variante est un persona qui hérite des caractéristiques d'un persona de base mais avec un nom et email différents. Cela permet de multiplier les candidatures.

### Q: Comment avoir plusieurs CVs pour un persona ?
R: Utilisez l'API `/api/personas/{email}/cv/generate` avec `search_key` et `cv_id` différents. Le système utilisera automatiquement le bon CV selon la recherche.

### Q: Comment tester les emails d'un persona ?
R: Dans l'interface, allez dans "Gestion Emails", sélectionnez un persona et cliquez sur "Test Connexion" ou "Récupérer depuis IMAP".

### Q: Comment assigner des personas à une recherche ?
R: Lors de la création/édition d'une recherche, utilisez la section "Personas pour cette recherche" pour assigner ou exclure des personas.

### Q: Qu'est-ce qu'une recherche standalone ?
R: Une recherche standalone scrape uniquement les offres sans postuler avec des personas. Utile pour collecter des offres.

