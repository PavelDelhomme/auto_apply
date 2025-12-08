"""
Configuration globale pour les tests pytest
"""
import pytest
import sys
import os
import tempfile
import shutil
import json

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def temp_config_dir():
    """Crée un répertoire temporaire pour les fichiers de configuration."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_personas(temp_config_dir):
    """Crée un fichier personas.json de test."""
    personas = {
        "persona1": {
            "name": "Test Persona",
            "email": "test@example.com",
            "password": "testpass123",
            "alias": False,
            "parent": None
        }
    }
    personas_file = os.path.join(temp_config_dir, "personas.json")
    with open(personas_file, 'w', encoding='utf-8') as f:
        json.dump(personas, f, indent=2)
    return personas_file

@pytest.fixture
def sample_cvs(temp_config_dir):
    """Crée un fichier cvs.json de test."""
    cvs = {
        "cv1": {
            "title": "Développeur Python",
            "skills": ["Python", "Django", "Flask"],
            "experience": [{"company": "Test Corp", "role": "Dev", "duration": "2 ans"}],
            "education": [{"school": "Test University", "degree": "Master"}],
            "hobbies": ["Code", "Sport"],
            "projects": [{"name": "Test Project", "description": "Un projet de test"}]
        }
    }
    cvs_file = os.path.join(temp_config_dir, "cvs.json")
    with open(cvs_file, 'w', encoding='utf-8') as f:
        json.dump(cvs, f, indent=2)
    return cvs_file

@pytest.fixture
def temp_db():
    """Crée une base de données temporaire pour les tests avec le schéma complet."""
    import sqlite3
    from src.database import create_database, get_db_path
    
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    # Sauvegarder le chemin original
    original_get_db_path = get_db_path
    
    # Remplacer temporairement get_db_path pour utiliser la base de données temporaire
    import src.database as database_module
    database_module.get_db_path = lambda: temp_db.name
    
    try:
        # Créer la base de données avec le schéma complet
        create_database()
    finally:
        # Restaurer le chemin original
        database_module.get_db_path = original_get_db_path
    
    yield temp_db.name
    
    # Nettoyer
    os.unlink(temp_db.name)

@pytest.fixture
def sample_search():
    """Retourne un exemple de recherche."""
    return {
        "name": "Test Search",
        "query": "développeur python",
        "location": "Rennes",
        "title_keywords": ["Python"],
        "location_keywords": ["Rennes"],
        "exclude_keywords": ["Senior"],
        "search_type": "développeur",
        "max_results": 10,
        "is_active": True,
        "standalone": False
    }

