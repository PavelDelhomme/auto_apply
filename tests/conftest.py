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
    """Crée une base de données temporaire pour les tests."""
    import sqlite3
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    conn = sqlite3.connect(temp_db.name)
    c = conn.cursor()
    
    # Créer les tables
    c.execute('''CREATE TABLE IF NOT EXISTS jobs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  company TEXT,
                  location TEXT,
                  url TEXT,
                  description TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  UNIQUE(title, company, location))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS applications
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  job_id INTEGER,
                  persona_email TEXT,
                  persona_name TEXT,
                  cv_path TEXT,
                  cover_letter TEXT,
                  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  status TEXT DEFAULT 'pending',
                  FOREIGN KEY (job_id) REFERENCES jobs(id),
                  UNIQUE(job_id, persona_email))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS persona_emails
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  persona_email TEXT,
                  sender TEXT,
                  subject TEXT,
                  body TEXT,
                  received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  is_read INTEGER DEFAULT 0,
                  email_type TEXT DEFAULT 'application')''')
    
    conn.commit()
    conn.close()
    
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

