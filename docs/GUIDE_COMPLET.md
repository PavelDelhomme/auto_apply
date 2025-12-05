# 📚 Guide Complet - Auto Apply

## 🎯 Vue d'ensemble

Auto Apply est un système complet de candidature automatique avec gestion multi-personas, interface web moderne et ligne de commande.

## 🌐 Interface Web (Dashboard)

### Accès
```bash
make up
# Puis ouvrez http://localhost:2020
```

### Fonctionnalités de l'interface

#### 📊 Dashboard
- Statistiques en temps réel
- Progression des candidatures
- Contrôles rapides

#### 👥 Personas
- **Sélection de personas** : Choisissez quels personas utiliser
- Vue de tous les personas disponibles
- Compteur de sélection
- Boutons "Tout sélectionner" / "Tout désélectionner"

#### 💼 Offres
- Recherche d'offres d'emploi
- Liste des offres disponibles
- Filtrage et visualisation

#### 📈 Résultats
- Statistiques détaillées par persona
- Top des offres les plus candidatées
- Tableaux de résultats complets

#### ⚙️ Paramètres
- **Recherche** : Mots-clés, localisation, exclusions
- **Candidatures** : Max par persona, délais, lettres de motivation
- **Mode** : Headless, avec/sans lettre de motivation
- **Sauvegarde** : Paramètres sauvegardés dans le navigateur

### Utilisation du Dashboard

1. **Sélectionner les personas**
   - Onglet "Personas"
   - Cocher les personas à utiliser
   - Voir le compteur de sélection

2. **Configurer les paramètres**
   - Onglet "Paramètres"
   - Ajuster tous les paramètres
   - Cliquer sur "Sauvegarder"

3. **Lancer la candidature**
   - Cliquer sur "🚀 Lancer Auto Apply"
   - Vérifier les personas sélectionnés dans la modal
   - Configurer la recherche
   - Cliquer sur "Démarrer"

4. **Suivre en temps réel**
   - Logs en direct
   - Statistiques mises à jour
   - Progression visible

## 💻 Ligne de Commande (CLI)

### Installation
```bash
# Le script CLI est déjà disponible
python cli.py --help
```

### Commandes principales

#### Afficher les statistiques
```bash
python cli.py --stats
```

#### Générer les CVs uniquement
```bash
python cli.py --generate-cvs
```

#### Scraper les offres uniquement
```bash
python cli.py --scrape-only --query "développeur python" --location "Rennes"
```

#### Candidater avec tous les personas
```bash
python cli.py \
  --query "développeur python" \
  --location "Rennes" \
  --title-keywords Python Développeur \
  --exclude-keywords Senior Lead \
  --max-per-persona 3
```

#### Candidater avec des personas spécifiques
```bash
python cli.py \
  --personas persona1@email.com persona2@email.com \
  --query "développeur python" \
  --location "Rennes"
```

#### Mode simulation (dry-run)
```bash
python cli.py --dry-run --query "développeur python"
```

### Options avancées CLI

```bash
python cli.py \
  --query "développeur python" \
  --location "Rennes" \
  --max-results 100 \
  --title-keywords Python Développeur Backend \
  --location-keywords Rennes Remote Télétravail \
  --exclude-keywords Senior Lead Manager \
  --max-per-persona 5 \
  --delay-min 3 \
  --delay-max 15 \
  --headless \
  --no-cover-letter \
  --personas email1@example.com email2@example.com
```

## 🔧 Configuration

### Fichiers de configuration

1. **personas.json** - Définition des personas
2. **cvs.json** - Modèles de CVs
3. **cv_template.html** - Template HTML pour CVs
4. **cover_letter_template.txt** - Template de lettre de motivation

### Paramètres sauvegardés

Les paramètres du dashboard sont sauvegardés dans le localStorage du navigateur.

## 📊 Résultats et Statistiques

### Via l'interface web
- Onglet "Résultats" pour voir les statistiques détaillées
- Statistiques par persona
- Top des offres candidatées

### Via la ligne de commande
```bash
python cli.py --stats
```

### Via l'API
```bash
curl http://localhost:2020/api/stats | python3 -m json.tool
```

## 🎨 Mode Sombre/Clair

Cliquez sur le bouton 🌙/☀️ en haut à droite pour changer de thème.
Le choix est sauvegardé automatiquement.

## 🚀 Workflow Recommandé

### 1. Préparation
```bash
# Générer les CVs
make up
# Puis dans l'interface: "Générer les CVs"
# Ou en CLI:
python cli.py --generate-cvs
```

### 2. Recherche d'offres
```bash
# Via l'interface: Onglet "Offres" > Rechercher
# Ou en CLI:
python cli.py --scrape-only --query "développeur python" --location "Rennes"
```

### 3. Candidature automatique

**Via l'interface (recommandé)** :
1. Onglet "Personas" > Sélectionner les personas
2. Onglet "Paramètres" > Configurer
3. Dashboard > "🚀 Lancer Auto Apply"

**Via CLI** :
```bash
python cli.py \
  --query "développeur python" \
  --location "Rennes" \
  --personas email1@example.com email2@example.com \
  --max-per-persona 3
```

### 4. Suivi
- Interface web : Logs en temps réel
- CLI : Statistiques après exécution
- API : `/api/stats` pour les statistiques

## 🔍 Dépannage

### Le conteneur ne démarre pas
```bash
make logs
make ps
```

### Erreurs de génération de CVs
```bash
make shell
python -c "from cv_generator import generate_cvs_from_json; generate_cvs_from_json()"
```

### Vérifier les personas
```bash
curl http://localhost:2020/api/personas | python3 -m json.tool | head -20
```

## 📝 Exemples d'utilisation

### Exemple 1 : Candidature rapide avec 5 personas
```bash
python cli.py \
  --personas $(python -c "import json; p=json.load(open('personas.json')); print(' '.join([v['email'] for k,v in list(p.items())[:5]]))") \
  --query "développeur python" \
  --max-per-persona 2
```

### Exemple 2 : Candidature ciblée
```bash
python cli.py \
  --query "développeur backend python" \
  --location "Paris" \
  --title-keywords Python Django FastAPI \
  --exclude-keywords Senior Lead Architecte \
  --max-per-persona 5 \
  --delay-min 10 \
  --delay-max 20
```

### Exemple 3 : Test sans candidater
```bash
python cli.py --dry-run --query "développeur python"
```

## 🎯 Bonnes Pratiques

1. **Testez d'abord** : Utilisez `--dry-run` pour tester
2. **Limitez les candidatures** : Ne dépassez pas 5 par persona
3. **Délais raisonnables** : Minimum 5-10 secondes entre candidatures
4. **Sélectionnez les personas** : Ne pas utiliser tous les personas à chaque fois
5. **Surveillez les logs** : Vérifiez les erreurs dans l'interface

## 📞 Support

Pour plus d'informations :
- `README.md` - Documentation générale
- `QUICKSTART.md` - Guide de démarrage rapide
- `MAKEFILE.md` - Commandes Makefile
- `DOCKER.md` - Guide Docker

