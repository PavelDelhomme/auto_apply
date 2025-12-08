# 🧪 Suite de Tests Complète - Auto Apply

## Vue d'ensemble

Cette suite de tests complète permet de vérifier que tous les composants du projet fonctionnent correctement.

## Structure des tests

```
tests/
├── __init__.py
├── conftest.py              # Configuration et fixtures pytest
├── test_database.py         # Tests pour database.py
├── test_persona_manager.py  # Tests pour persona_manager.py
├── test_search_manager.py   # Tests pour search_manager.py
├── test_api.py              # Tests d'intégration des APIs Flask
├── test_cv_generator.py     # Tests pour cv_generator.py
├── test_scraper.py          # Tests pour scraper.py
├── test_job_filter.py       # Tests pour job_filter.py
└── test_complete_suite.py   # Tests de complétude du projet
```

## Types de tests

### Tests unitaires
- Testent chaque module individuellement
- Utilisent des fixtures et mocks
- Rapides à exécuter

### Tests d'intégration
- Testent l'interaction entre plusieurs modules
- Nécessitent une configuration complète
- Marqués avec `@pytest.mark.integration`

### Tests de complétude
- Vérifient que tous les modules sont importables
- Vérifient que les fichiers nécessaires existent
- Vérifient que les fonctions principales existent

## Exécution des tests

### Avec Docker (Recommandé)

```bash
# Tous les tests
make test-all

# Tests unitaires uniquement
make test-unit

# Tests d'intégration uniquement
make test-integration
```

### En local

```bash
# Installer les dépendances de test
pip install -r requirements.txt

# Lancer tous les tests
./run_tests.sh

# Ou avec pytest directement
pytest tests/ -v

# Avec couverture de code
pytest tests/ -v --cov=src --cov-report=html
```

### Tests spécifiques

```bash
# Un seul fichier de test
pytest tests/test_database.py -v

# Une seule fonction de test
pytest tests/test_database.py::test_insert_job -v

# Exclure les tests d'intégration
pytest tests/ -v -m "not integration"
```

## Résultats attendus

### Tests unitaires
- ✅ Tous les modules peuvent être importés
- ✅ Toutes les fonctions principales existent
- ✅ Les opérations CRUD fonctionnent
- ✅ Les validations fonctionnent

### Tests d'intégration
- ✅ Les APIs Flask répondent correctement
- ✅ Les données sont persistées correctement
- ✅ Les managers fonctionnent ensemble

### Couverture de code
- Objectif: > 70% de couverture
- Rapport HTML généré dans `htmlcov/index.html`

## Fichiers de configuration

Les tests utilisent des fichiers temporaires pour éviter de modifier les fichiers de production :
- `temp_config_dir`: Répertoire temporaire pour les fichiers JSON
- `temp_db`: Base de données temporaire SQLite

## Notes importantes

1. **Tests réseau**: Certains tests (scraper) nécessitent une connexion réseau et sont marqués comme `@pytest.mark.skip` par défaut
2. **wkhtmltopdf**: Les tests de génération de CV peuvent échouer si wkhtmltopdf n'est pas installé (c'est normal)
3. **Base de données**: Les tests utilisent des bases de données temporaires pour ne pas affecter les données de production

## Dépannage

### Erreur: Module not found
```bash
# Vérifier que vous êtes dans le bon répertoire
cd /path/to/auto_apply/auto_apply

# Vérifier que src/ est dans le PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Erreur: Database locked
- Les tests utilisent des bases de données temporaires
- Si l'erreur persiste, vérifier qu'aucun autre processus n'utilise la DB

### Tests qui échouent
- Vérifier les logs pour plus de détails
- Certains tests peuvent nécessiter une configuration spécifique
- Les tests d'intégration nécessitent que l'application soit configurée

