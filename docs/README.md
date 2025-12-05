# Auto Apply - Système de Candidature Automatique Multi-Profils

## 📋 Description

Auto Apply est un système automatisé de candidature aux offres d'emploi qui permet de postuler automatiquement avec plusieurs profils (personas) différents. Le système scrape des offres d'emploi, génère des CVs personnalisés pour chaque profil, et soumet les candidatures de manière automatisée.

## ✨ Fonctionnalités

- 🔍 **Scraping automatique** : Récupération d'offres d'emploi depuis Indeed
- 👥 **Multi-personas** : Gestion de plusieurs profils avec CVs et emails différents
- 📄 **Génération de CVs** : Création automatique de CVs PDF personnalisés pour chaque persona
- 📝 **Lettres de motivation** : Génération automatique de lettres de motivation personnalisées
- 🤖 **Candidature automatisée** : Soumission automatique via Selenium
- 📊 **Base de données** : Suivi des offres et candidatures dans SQLite
- 📈 **Statistiques** : Suivi détaillé des candidatures par persona
- 🔒 **Évite les doublons** : Chaque persona ne postule qu'une fois par offre

## 🚀 Installation

### Option 1 : Installation avec Docker (Recommandé) 🐳

C'est la méthode la plus simple et la plus propre !

#### Avec Makefile (Recommandé)

```bash
# Voir toutes les commandes disponibles
make help

# Construire et lancer le conteneur
make up

# L'interface sera disponible sur http://localhost:2020
```

Commandes principales :
```bash
make up          # Démarrer les conteneurs
make down        # Arrêter les conteneurs
make logs        # Voir les logs en temps réel
make restart     # Redémarrer les conteneurs
make rebuild     # Reconstruire depuis zéro
make shell       # Ouvrir un shell dans le conteneur
make stats       # Voir les statistiques d'utilisation
make open        # Ouvrir l'interface dans le navigateur
```

#### Avec Docker Compose directement

```bash
# Construire et lancer le conteneur
docker-compose up -d --build

# L'interface sera disponible sur http://localhost:2020
```

Pour arrêter :
```bash
docker-compose down
```

Pour voir les logs :
```bash
docker-compose logs -f
```

### Option 2 : Installation manuelle

#### Prérequis

- Python 3.8 ou supérieur
- Chrome/Chromium installé
- ChromeDriver (sera installé automatiquement ou téléchargez-le depuis [ChromeDriver](https://chromedriver.chromium.org/))
- wkhtmltopdf (pour la génération de PDFs)

#### Installation des dépendances

```bash
# Installer les dépendances Python
pip install -r requirements.txt

# Installer wkhtmltopdf (Ubuntu/Debian)
sudo apt-get install wkhtmltopdf

# Installer wkhtmltopdf (macOS)
brew install wkhtmltopdf

# Installer wkhtmltopdf (Windows)
# Téléchargez depuis https://wkhtmltopdf.org/downloads.html
```

## 📁 Structure du Projet

```
auto_apply/
├── app.py                     # Application Flask avec interface temps réel (NOUVEAU)
├── main.py                    # Point d'entrée principal (CLI)
├── run.py                     # Script d'exécution simplifié
├── server.py                  # Ancien serveur web Flask (basique)
├── scraper.py                 # Scraping des offres d'emploi
├── database.py                # Gestion de la base de données
├── job_filter.py              # Filtrage des offres
├── cv_generator.py            # Génération de CVs PDF
├── auto_apply.py              # Automatisation des candidatures (Selenium)
├── application_generator.py   # Génération de lettres de motivation
├── stats.py                   # Statistiques des candidatures
├── mailing.py                 # Gestion des emails (forwarding)
├── templates/
│   └── dashboard.html         # Interface web moderne (NOUVEAU)
├── personas.json              # Configuration des personas
├── cvs.json                   # Modèles de CVs
├── cv_template.html           # Template HTML pour les CVs
├── cover_letter_template.txt   # Template de lettre de motivation
├── config.example.py          # Exemple de configuration
├── Dockerfile                 # Configuration Docker
├── docker-compose.yml         # Orchestration Docker
├── requirements.txt           # Dépendances Python
├── .gitignore                 # Fichiers à ignorer par Git
└── README.md                  # Ce fichier
```

## ⚙️ Configuration

### 1. Configuration des Personas

Éditez `personas.json` pour configurer vos personas. Chaque persona doit avoir :
- `name` : Nom du persona
- `email` : Email du persona
- `password` : Mot de passe (si nécessaire)
- `alias` : Indique si c'est un alias email
- `parent` : Email parent si c'est un alias

Exemple :
```json
{
    "persona1": {
        "name": "Jean Dupont",
        "email": "jean.dupont@example.com",
        "password": "motdepasse",
        "alias": false,
        "parent": null
    }
}
```

### 2. Configuration des CVs

Éditez `cvs.json` pour définir les modèles de CVs. Chaque CV contient :
- `title` : Titre du poste
- `skills` : Liste de compétences
- `experience` : Expériences professionnelles
- `education` : Formation
- `hobbies` : Centres d'intérêt
- `projects` : Projets

### 3. Personnalisation de la Recherche

Dans `main.py`, modifiez les paramètres de recherche :

```python
search_query = "développeur python"
search_location = "Rennes"
title_keywords = ["Python", "Développeur", "Developer"]
location_keywords = ["Rennes", "Bretagne", "Remote", "Télétravail"]
exclude_keywords = ["Senior", "Lead", "Manager"]
max_applications_per_persona = 3
```

**Alternative** : Créez un fichier `config.py` basé sur `config.example.py` pour centraliser toute la configuration.

## 🎯 Utilisation

### Interface Web en Temps Réel (Recommandé) 🌐

L'interface web moderne permet de tout gérer depuis votre navigateur avec des mises à jour en temps réel !

#### Avec Docker
```bash
docker-compose up -d
# Puis ouvrez http://localhost:2020 dans votre navigateur
```

#### Sans Docker
```bash
python app.py
# Puis ouvrez http://localhost:2020 dans votre navigateur
```

**Fonctionnalités de l'interface :**
- 📊 **Dashboard en temps réel** : Statistiques, progression, logs
- 🎮 **Contrôles** : Démarrer/arrêter, générer CVs, rechercher offres
- 📋 **Logs en direct** : Suivez toutes les actions en temps réel
- 📈 **Statistiques** : Suivi détaillé des candidatures

### Utilisation en ligne de commande

#### Méthode 1 : Script principal
```bash
python main.py
```

#### Méthode 2 : Script simplifié
```bash
python run.py
```

#### Méthode 3 : Ancienne interface web (basique)
```bash
python server.py
# Puis ouvrez http://localhost:5000 dans votre navigateur
```

Le système va :
1. Initialiser la base de données
2. Charger les personas
3. Générer les CVs pour chaque persona
4. Scraper les offres d'emploi
5. Filtrer les offres selon vos critères
6. Postuler automatiquement avec chaque persona

### Mode Headless

Pour exécuter en arrière-plan (sans interface graphique), modifiez dans `main.py` :

```python
success = apply_to_job(
    ...
    headless=True  # Mode headless
)
```

### Consultation des statistiques

```bash
python stats.py
```

## 📊 Base de Données

La base de données SQLite `jobs.db` contient deux tables :

### Table `jobs`
- `id` : Identifiant unique
- `title` : Titre de l'offre
- `company` : Nom de l'entreprise
- `location` : Localisation
- `url` : URL de l'offre
- `description` : Description
- `created_at` : Date de création

### Table `applications`
- `id` : Identifiant unique
- `job_id` : Référence à l'offre
- `persona_email` : Email du persona
- `persona_name` : Nom du persona
- `cv_path` : Chemin du CV utilisé
- `cover_letter` : Lettre de motivation
- `applied_at` : Date de candidature
- `status` : Statut (pending, sent, failed)

## 🔧 Personnalisation Avancée

### Modifier le template de CV

Éditez `cv_template.html` pour personnaliser le design des CVs générés.

### Modifier le template de lettre de motivation

Éditez `cover_letter_template.txt` pour personnaliser les lettres de motivation.

### Ajouter d'autres sites de recrutement

Modifiez `scraper.py` pour ajouter le support d'autres sites (LinkedIn, Welcome to the Jungle, etc.).

## ⚠️ Avertissements et Bonnes Pratiques

1. **Respect des conditions d'utilisation** : Assurez-vous de respecter les conditions d'utilisation des sites de recrutement.

2. **Limitation des candidatures** : Ne postulez pas trop rapidement pour éviter d'être détecté comme bot.

3. **Qualité des candidatures** : Vérifiez que vos CVs et lettres de motivation sont pertinents pour chaque offre.

4. **Sécurité** : Ne partagez pas vos fichiers `personas.json` contenant des mots de passe.

5. **Légalité** : L'utilisation de ce système doit être conforme aux lois en vigueur dans votre pays.

## 🐛 Dépannage

### Erreur ChromeDriver

Si vous rencontrez une erreur avec ChromeDriver :
```bash
# Installer ChromeDriver via webdriver-manager (ajoutez-le à requirements.txt)
pip install webdriver-manager
```

Puis modifiez `auto_apply.py` pour utiliser webdriver-manager.

### Erreur wkhtmltopdf

Assurez-vous que wkhtmltopdf est installé et dans votre PATH.

### Erreurs de scraping

Indeed peut changer sa structure HTML. Si le scraping ne fonctionne plus, vérifiez les sélecteurs CSS dans `scraper.py`.

## 📝 Licence

Ce projet est fourni à des fins éducatives. Utilisez-le de manière responsable et éthique.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📧 Support

Pour toute question ou problème, ouvrez une issue sur le dépôt du projet.

---

**Note importante** : Ce système est conçu pour automatiser le processus de candidature, mais il est essentiel de rester éthique et de respecter les conditions d'utilisation des plateformes de recrutement.

