"""
Tests d'intégration pour les APIs Flask
"""
import pytest
import sys
import os
import json
import tempfile

# Ajouter src au PYTHONPATH
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Importer app en gérant les imports relatifs
try:
    from src.app import app
except ImportError:
    # Si l'import échoue, essayer directement
    import importlib.util
    spec = importlib.util.spec_from_file_location("app", os.path.join(src_path, "app.py"))
    app_module = importlib.util.module_from_spec(spec)
    # Créer un module src factice pour les imports relatifs
    import types
    src_module = types.ModuleType('src')
    sys.modules['src'] = src_module
    spec.loader.exec_module(app_module)
    app = app_module.app

@pytest.fixture
def client():
    """Crée un client de test Flask."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client

def test_api_personas_list(client):
    """Test de l'API de liste des personas."""
    response = client.get('/api/personas')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)

def test_api_searches_list(client):
    """Test de l'API de liste des recherches."""
    response = client.get('/api/searches')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)

def test_api_stats(client):
    """Test de l'API de statistiques."""
    response = client.get('/api/stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)
    # Vérifier la structure des stats
    assert 'total_jobs' in data or 'total_applications' in data

def test_api_jobs(client):
    """Test de l'API de liste des offres."""
    response = client.get('/api/jobs')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_api_create_search(client):
    """Test de création d'une recherche via API."""
    search_data = {
        'name': 'Test Search API',
        'query': 'développeur python',
        'location': 'Rennes',
        'title_keywords': ['Python'],
        'location_keywords': ['Rennes'],
        'exclude_keywords': [],
        'max_results': 10,
        'enabled': True,
        'standalone': False
    }
    
    response = client.post('/api/searches',
                          data=json.dumps(search_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'search_key' in data

def test_api_create_persona(client):
    """Test de création d'un persona via API."""
    persona_data = {
        'name': 'Test Persona API',
        'email': 'testapi@example.com',
        'password': 'testpass',
        'alias': False
    }
    
    response = client.post('/api/personas',
                          data=json.dumps(persona_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'persona_key' in data

def test_api_dashboard_route(client):
    """Test de la route principale du dashboard."""
    response = client.get('/')
    assert response.status_code == 200
    # Vérifier que c'est du HTML
    assert b'<!DOCTYPE html' in response.data or b'<html' in response.data

def test_api_jobs_with_params(client):
    """Test de l'API jobs avec paramètres."""
    # Test avec all=true
    response = client.get('/api/jobs?all=true&limit=10')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    
    # Test avec persona_email
    response = client.get('/api/jobs?persona_email=test@example.com')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_api_searches_enabled(client):
    """Test de l'API des recherches activées."""
    response = client.get('/api/searches/enabled')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)

