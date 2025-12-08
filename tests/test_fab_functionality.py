"""
Tests pour les fonctionnalités du FAB (Floating Action Button)
"""
import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.app import app

@pytest.fixture
def client():
    """Client de test Flask."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_personas():
    """Mock des personas."""
    return {
        'persona1': {
            'name': 'Test Persona',
            'email': 'test@example.com',
            'phone': '0123456789'
        }
    }

class TestGenerateCVs:
    """Tests pour la génération de CVs."""
    
    @patch('src.app.generate_cvs_from_json')
    def test_generate_cvs_success(self, mock_generate, client):
        """Test de génération de CVs réussie."""
        mock_generate.return_value = ['/app/cvs/test1.pdf', '/app/cvs/test2.pdf']
        
        response = client.post('/api/generate_cvs')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['count'] == 2
    
    @patch('src.app.generate_cvs_from_json')
    def test_generate_cvs_error(self, mock_generate, client):
        """Test de génération de CVs avec erreur."""
        mock_generate.side_effect = Exception('Erreur de génération')
        
        response = client.post('/api/generate_cvs')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data

class TestScrapeJobs:
    """Tests pour le scraping d'offres."""
    
    @patch('src.app.scrape_indeed')
    @patch('src.app.insert_job')
    def test_scrape_jobs_success(self, mock_insert, mock_scrape, client):
        """Test de scraping réussi."""
        mock_jobs = [
            {'title': 'Dev Python', 'company': 'Test Co', 'location': 'Rennes'},
            {'title': 'Dev Java', 'company': 'Test Co 2', 'location': 'Paris'}
        ]
        mock_scrape.return_value = mock_jobs
        
        response = client.post('/api/scrape_jobs', 
                             json={'query': 'développeur', 'location': 'Rennes', 'max_results': 50})
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'message' in data
    
    def test_scrape_jobs_missing_params(self, client):
        """Test de scraping sans paramètres."""
        response = client.post('/api/scrape_jobs', json={})
        assert response.status_code == 200  # Utilise des valeurs par défaut

class TestAutoApply:
    """Tests pour Auto Apply."""
    
    @patch('src.app.load_personas')
    @patch('src.app.generate_cvs_from_json')
    @patch('src.app.scrape_indeed')
    @patch('src.app.get_unapplied_jobs')
    @patch('src.app.apply_to_job')
    def test_start_auto_apply_success(self, mock_apply, mock_get_jobs, mock_scrape, 
                                       mock_generate, mock_load, client, mock_personas):
        """Test de démarrage d'Auto Apply réussi."""
        mock_load.return_value = mock_personas
        mock_generate.return_value = ['/app/cvs/test.pdf']
        mock_scrape.return_value = []
        mock_get_jobs.return_value = []
        
        response = client.post('/api/start_auto_apply',
                             json={
                                 'query': 'développeur',
                                 'location': 'Rennes',
                                 'personas': ['test@example.com']
                             })
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_start_auto_apply_already_running(self, client):
        """Test de démarrage quand déjà en cours."""
        # Simuler un processus en cours
        from src.app import app_state
        app_state['is_running'] = True
        
        response = client.post('/api/start_auto_apply',
                             json={'query': 'test', 'location': 'test'})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        
        # Réinitialiser
        app_state['is_running'] = False
    
    def test_stop_auto_apply(self, client):
        """Test d'arrêt d'Auto Apply."""
        from src.app import app_state
        app_state['is_running'] = True
        
        response = client.post('/api/stop_auto_apply')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert app_state['is_running'] is False

class TestTestApplication:
    """Tests pour le test de candidature."""
    
    @patch('src.app.persona_manager')
    @patch('src.app.generate_cv_for_persona')
    @patch('src.app.apply_to_job')
    def test_test_application_success(self, mock_apply, mock_generate, mock_pm, client):
        """Test de candidature réussi."""
        mock_persona = {
            'name': 'Test Persona',
            'email': 'test@example.com'
        }
        mock_pm.get_persona_by_email.return_value = mock_persona
        mock_generate.return_value = '/app/cvs/test.pdf'
        mock_apply.return_value = True
        
        response = client.post('/api/test_application',
                             json={
                                 'platform': 'indeed',
                                 'job_url': 'https://example.com/job',
                                 'persona_email': 'test@example.com',
                                 'dry_run': True
                             })
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_test_application_missing_params(self, client):
        """Test de candidature sans paramètres."""
        response = client.post('/api/test_application', json={})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    @patch('src.app.persona_manager')
    def test_test_application_persona_not_found(self, mock_pm, client):
        """Test de candidature avec persona introuvable."""
        mock_pm.get_persona_by_email.return_value = None
        
        response = client.post('/api/test_application',
                             json={
                                 'platform': 'indeed',
                                 'job_url': 'https://example.com/job',
                                 'persona_email': 'notfound@example.com'
                             })
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['success'] is False

class TestFABIntegration:
    """Tests d'intégration pour le FAB."""
    
    def test_all_fab_endpoints_exist(self, client):
        """Vérifie que tous les endpoints du FAB existent."""
        endpoints = [
            ('/api/generate_cvs', 'POST'),
            ('/api/scrape_jobs', 'POST'),
            ('/api/start_auto_apply', 'POST'),
            ('/api/stop_auto_apply', 'POST'),
            ('/api/test_application', 'POST')
        ]
        
        for endpoint, method in endpoints:
            if method == 'POST':
                response = client.post(endpoint, json={})
            else:
                response = client.get(endpoint)
            
            # Ne doit pas retourner 404 (route existe)
            assert response.status_code != 404, f"Endpoint {endpoint} n'existe pas"
    
    def test_fab_endpoints_return_json(self, client):
        """Vérifie que tous les endpoints retournent du JSON."""
        endpoints = [
            ('/api/generate_cvs', 'POST'),
            ('/api/scrape_jobs', 'POST'),
            ('/api/stop_auto_apply', 'POST')
        ]
        
        for endpoint, method in endpoints:
            if method == 'POST':
                response = client.post(endpoint, json={})
            else:
                response = client.get(endpoint)
            
            assert response.content_type == 'application/json'

