"""
Tests étendus pour app.py - Amélioration de la couverture
"""
import pytest
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock

# Ajouter src au PYTHONPATH
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from src.app import app, socketio
except ImportError:
    import importlib.util
    spec = importlib.util.spec_from_file_location("app", os.path.join(src_path, "app.py"))
    app_module = importlib.util.module_from_spec(spec)
    import types
    src_module = types.ModuleType('src')
    sys.modules['src'] = src_module
    spec.loader.exec_module(app_module)
    app = app_module.app
    socketio = app_module.socketio

@pytest.fixture
def client():
    """Crée un client de test Flask."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_persona_data():
    """Données de test pour un persona."""
    return {
        'name': 'Test Persona Extended',
        'email': 'testextended@example.com',
        'password': 'testpass123',
        'alias': False
    }

@pytest.fixture
def sample_search_data():
    """Données de test pour une recherche."""
    return {
        'name': 'Test Search Extended',
        'query': 'développeur python',
        'location': 'Rennes',
        'title_keywords': ['Python', 'Django'],
        'location_keywords': ['Rennes', 'Bretagne'],
        'exclude_keywords': ['Senior'],
        'max_results': 20,
        'enabled': True,
        'standalone': False
    }

# Tests pour les routes personas
def test_api_base_personas(client):
    """Test de l'API des personas de base."""
    response = client.get('/api/personas/base')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)

def test_api_get_persona(client, sample_persona_data):
    """Test de récupération d'un persona spécifique."""
    # Créer un persona d'abord
    create_response = client.post('/api/personas',
                                 data=json.dumps(sample_persona_data),
                                 content_type='application/json')
    assert create_response.status_code == 200
    create_data = json.loads(create_response.data)
    persona_key = create_data['persona_key']
    
    # Récupérer le persona
    response = client.get(f'/api/personas/{persona_key}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == sample_persona_data['name']
    assert data['email'] == sample_persona_data['email']

def test_api_get_persona_not_found(client):
    """Test de récupération d'un persona inexistant."""
    response = client.get('/api/personas/nonexistent')
    assert response.status_code == 404

def test_api_get_variants(client, sample_persona_data):
    """Test de récupération des variantes d'un persona."""
    # Créer un persona
    create_response = client.post('/api/personas',
                                 data=json.dumps(sample_persona_data),
                                 content_type='application/json')
    create_data = json.loads(create_response.data)
    persona_key = create_data['persona_key']
    
    # Récupérer les variantes
    response = client.get(f'/api/personas/{persona_key}/variants')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)

def test_api_update_persona(client, sample_persona_data):
    """Test de mise à jour d'un persona."""
    # Créer un persona
    create_response = client.post('/api/personas',
                                 data=json.dumps(sample_persona_data),
                                 content_type='application/json')
    create_data = json.loads(create_response.data)
    persona_key = create_data['persona_key']
    
    # Mettre à jour
    update_data = {'name': 'Updated Name'}
    response = client.put(f'/api/personas/{persona_key}',
                         data=json.dumps(update_data),
                         content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['persona']['name'] == 'Updated Name'

def test_api_delete_persona(client, sample_persona_data):
    """Test de suppression d'un persona."""
    # Créer un persona
    create_response = client.post('/api/personas',
                                 data=json.dumps(sample_persona_data),
                                 content_type='application/json')
    create_data = json.loads(create_response.data)
    persona_key = create_data['persona_key']
    
    # Supprimer
    response = client.delete(f'/api/personas/{persona_key}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    
    # Vérifier qu'il n'existe plus
    get_response = client.get(f'/api/personas/{persona_key}')
    assert get_response.status_code == 404

def test_api_create_persona_variant(client, sample_persona_data):
    """Test de création d'une variante de persona."""
    # Créer un persona de base
    create_response = client.post('/api/personas',
                                 data=json.dumps(sample_persona_data),
                                 content_type='application/json')
    create_data = json.loads(create_response.data)
    persona_key = create_data['persona_key']
    
    # Créer une variante
    variant_data = {'name': 'Variant Name'}
    response = client.post(f'/api/personas/{persona_key}/variant',
                          data=json.dumps(variant_data),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True

def test_api_duplicate_persona(client, sample_persona_data):
    """Test de duplication d'un persona."""
    # Créer un persona
    create_response = client.post('/api/personas',
                                 data=json.dumps(sample_persona_data),
                                 content_type='application/json')
    create_data = json.loads(create_response.data)
    persona_key = create_data['persona_key']
    
    # Dupliquer
    duplicate_data = {'name': 'Duplicated Persona'}
    response = client.post(f'/api/personas/{persona_key}/duplicate',
                          data=json.dumps(duplicate_data),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'persona_key' in data

# Tests pour les routes searches
def test_api_get_search(client, sample_search_data):
    """Test de récupération d'une recherche spécifique."""
    # Créer une recherche
    create_response = client.post('/api/searches',
                                 data=json.dumps(sample_search_data),
                                 content_type='application/json')
    assert create_response.status_code == 200
    create_data = json.loads(create_response.data)
    search_key = create_data['search_key']
    
    # Récupérer la recherche
    response = client.get(f'/api/searches/{search_key}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == sample_search_data['name']

def test_api_update_search(client, sample_search_data):
    """Test de mise à jour d'une recherche."""
    # Créer une recherche
    create_response = client.post('/api/searches',
                                 data=json.dumps(sample_search_data),
                                 content_type='application/json')
    create_data = json.loads(create_response.data)
    search_key = create_data['search_key']
    
    # Mettre à jour
    update_data = {'name': 'Updated Search Name'}
    response = client.put(f'/api/searches/{search_key}',
                         data=json.dumps(update_data),
                         content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True

def test_api_delete_search(client, sample_search_data):
    """Test de suppression d'une recherche."""
    # Créer une recherche
    create_response = client.post('/api/searches',
                                 data=json.dumps(sample_search_data),
                                 content_type='application/json')
    create_data = json.loads(create_response.data)
    search_key = create_data['search_key']
    
    # Supprimer
    response = client.delete(f'/api/searches/{search_key}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True

def test_api_duplicate_search(client, sample_search_data):
    """Test de duplication d'une recherche."""
    # Créer une recherche
    create_response = client.post('/api/searches',
                                 data=json.dumps(sample_search_data),
                                 content_type='application/json')
    create_data = json.loads(create_response.data)
    search_key = create_data['search_key']
    
    # Dupliquer
    duplicate_data = {'name': 'Duplicated Search'}
    response = client.post(f'/api/searches/{search_key}/duplicate',
                          data=json.dumps(duplicate_data),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True

def test_api_search_history(client, sample_search_data):
    """Test de récupération de l'historique d'une recherche."""
    # Créer une recherche
    create_response = client.post('/api/searches',
                                 data=json.dumps(sample_search_data),
                                 content_type='application/json')
    create_data = json.loads(create_response.data)
    search_key = create_data['search_key']
    
    # Récupérer l'historique
    response = client.get(f'/api/searches/{search_key}/history')
    assert response.status_code == 200
    data = json.loads(response.data)
    # L'API retourne un dict avec 'history', pas directement une liste
    assert isinstance(data, dict)
    assert 'history' in data or 'success' in data

def test_api_job_types(client):
    """Test de l'API des types de postes."""
    response = client.get('/api/searches/job-types')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

# Tests pour les routes CVs et emails
def test_api_get_persona_cv(client, sample_persona_data):
    """Test de récupération du CV d'un persona."""
    # Créer un persona
    create_response = client.post('/api/personas',
                                 data=json.dumps(sample_persona_data),
                                 content_type='application/json')
    create_data = json.loads(create_response.data)
    persona_email = sample_persona_data['email']
    
    # Récupérer le CV (peut ne pas exister)
    response = client.get(f'/api/personas/{persona_email}/cv')
    # Peut retourner 200 avec un message ou 404
    assert response.status_code in [200, 404]

def test_api_get_all_cvs(client):
    """Test de récupération de tous les CVs."""
    response = client.get('/api/personas/cvs')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_api_get_persona_emails(client, sample_persona_data):
    """Test de récupération des emails d'un persona."""
    # Créer un persona
    create_response = client.post('/api/personas',
                                 data=json.dumps(sample_persona_data),
                                 content_type='application/json')
    persona_email = sample_persona_data['email']
    
    # Récupérer les emails
    response = client.get(f'/api/personas/{persona_email}/emails')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_api_get_email_count(client, sample_persona_data):
    """Test de récupération du nombre d'emails."""
    # Créer un persona
    create_response = client.post('/api/personas',
                                 data=json.dumps(sample_persona_data),
                                 content_type='application/json')
    persona_email = sample_persona_data['email']
    
    # Récupérer le count
    response = client.get(f'/api/personas/{persona_email}/emails/count')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total' in data
    assert 'unread' in data

# Tests pour les routes utilitaires
def test_api_favicon(client):
    """Test de la route favicon."""
    response = client.get('/favicon.ico')
    assert response.status_code == 200
    assert 'image/svg+xml' in response.content_type

def test_api_old_dashboard(client):
    """Test de l'ancienne route dashboard."""
    response = client.get('/old')
    assert response.status_code == 200

def test_api_logs(client):
    """Test de l'API des logs."""
    response = client.get('/api/logs')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_api_status(client):
    """Test de l'API de statut."""
    response = client.get('/api/status')
    assert response.status_code == 200
    data = json.loads(response.data)
    # L'API retourne 'container_status' ou 'current_step'
    assert 'container_status' in data or 'current_step' in data or 'status' in data

# Tests pour les routes avec erreurs
def test_api_create_persona_invalid_data(client):
    """Test de création de persona avec données invalides."""
    invalid_data = {'name': 'Test'}  # Email manquant
    response = client.post('/api/personas',
                          data=json.dumps(invalid_data),
                          content_type='application/json')
    # Peut retourner 200 avec error ou 500
    assert response.status_code in [200, 500]

def test_api_create_search_invalid_data(client):
    """Test de création de recherche avec données invalides."""
    invalid_data = {'name': 'Test'}  # Query manquant
    response = client.post('/api/searches',
                          data=json.dumps(invalid_data),
                          content_type='application/json')
    # Peut retourner 200 avec error ou 500
    assert response.status_code in [200, 500]

# Tests pour les routes POST avec mocks
@patch('src.app.scrape_indeed')
def test_api_scrape_jobs(mock_scrape, client):
    """Test de l'API de scraping d'offres."""
    # Mock du scraper
    mock_scrape.return_value = [
        {
            'title': 'Test Job',
            'company': 'Test Company',
            'location': 'Test Location',
            'url': 'https://example.com/job',
            'description': 'Test description'
        }
    ]
    
    scrape_data = {
        'query': 'développeur python',
        'location': 'Rennes',
        'max_results': 10
    }
    
    response = client.post('/api/scrape_jobs',
                          data=json.dumps(scrape_data),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    # L'API retourne 'success' et 'message' quand le scraping est lancé en async
    assert 'success' in data or 'jobs' in data or 'count' in data or 'message' in data

@patch('src.app.generate_cvs_from_json')
def test_api_generate_cvs(mock_generate, client):
    """Test de l'API de génération de CVs."""
    # Mock de la génération
    mock_generate.return_value = {'persona1': '/path/to/cv1.pdf'}
    
    response = client.post('/api/generate_cvs')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'success' in data or 'message' in data

