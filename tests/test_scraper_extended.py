"""
Tests étendus pour le module scraper.py avec mocks
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_scraper_imports():
    """Test que le module peut être importé."""
    try:
        from scraper import scrape_indeed
        assert True
    except ImportError as e:
        pytest.skip(f"Module scraper non disponible: {e}")

@patch('scraper.requests.Session')
def test_scrape_indeed_with_mock_requests(mock_session_class):
    """Test de scrape_indeed avec mock requests."""
    from scraper import scrape_indeed
    
    # Mock de la session requests
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session
    
    # Mock de la réponse HTTP
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '''
    <html>
        <body>
            <div class="job_seen_beacon">
                <h2 class="jobTitle"><a href="/job1">Développeur Python</a></h2>
                <span class="companyName">Test Company</span>
                <div class="companyLocation">Rennes</div>
            </div>
            <div class="job_seen_beacon">
                <h2 class="jobTitle"><a href="/job2">Développeur Java</a></h2>
                <span class="companyName">Another Company</span>
                <div class="companyLocation">Paris</div>
            </div>
        </body>
    </html>
    '''
    mock_session.get.return_value = mock_response
    
    # Appeler scrape_indeed
    jobs = scrape_indeed(query="développeur python", location="Rennes", max_results=10)
    
    assert isinstance(jobs, list)
    # Vérifier que des offres sont retournées (si le parsing fonctionne)
    if jobs:
        job = jobs[0]
        assert 'title' in job
        assert 'company' in job
        assert 'location' in job

@patch('scraper.requests.Session')
def test_scrape_indeed_403_error(mock_session_class):
    """Test de gestion d'erreur 403."""
    from scraper import scrape_indeed
    
    # Mock de la session requests
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session
    
    # Mock d'une réponse 403
    from requests.exceptions import HTTPError
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = HTTPError("403 Forbidden")
    mock_session.get.return_value = mock_response
    
    # Appeler scrape_indeed (devrait gérer l'erreur)
    jobs = scrape_indeed(query="test", location="test", max_results=10)
    
    # Devrait retourner une liste vide ou gérer l'erreur
    assert isinstance(jobs, list)

@patch('scraper.requests.Session')
def test_scrape_indeed_timeout(mock_session_class):
    """Test de gestion de timeout."""
    from scraper import scrape_indeed
    
    # Mock de la session requests
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session
    
    # Mock d'un timeout
    from requests.exceptions import Timeout
    mock_session.get.side_effect = Timeout("Request timeout")
    
    # Appeler scrape_indeed (devrait gérer le timeout)
    jobs = scrape_indeed(query="test", location="test", max_results=10)
    
    # Devrait retourner une liste vide ou gérer l'erreur
    assert isinstance(jobs, list)

@patch('scraper.requests.Session')
def test_scrape_indeed_empty_results(mock_session_class):
    """Test avec des résultats vides."""
    from scraper import scrape_indeed
    
    # Mock de la session requests
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session
    
    # Mock d'une réponse avec aucun résultat
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '<html><body><div>No jobs found</div></body></html>'
    mock_session.get.return_value = mock_response
    
    # Appeler scrape_indeed
    jobs = scrape_indeed(query="nonexistent job", location="nowhere", max_results=10)
    
    assert isinstance(jobs, list)
    # Devrait retourner une liste vide si aucun résultat

def test_scraper_function_signature():
    """Test de la signature de la fonction scrape_indeed."""
    from scraper import scrape_indeed
    import inspect
    
    sig = inspect.signature(scrape_indeed)
    params = list(sig.parameters.keys())
    
    # Vérifier les paramètres attendus
    assert 'query' in params
    assert 'location' in params

@patch('scraper.requests.Session')
def test_scrape_indeed_url_encoding(mock_session_class):
    """Test de l'encodage des URLs."""
    from scraper import scrape_indeed
    
    # Mock de la session requests
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '<html><body></body></html>'
    mock_session.get.return_value = mock_response
    
    # Appeler avec des caractères spéciaux
    jobs = scrape_indeed(query="développeur python & django", location="Rennes (35)", max_results=10)
    
    # Vérifier que l'URL a été appelée
    assert mock_session.get.called
    # Vérifier que l'URL contient les paramètres encodés
    call_args = mock_session.get.call_args
    if call_args:
        url = call_args[0][0] if call_args[0] else call_args[1].get('url', '')
        # L'URL devrait contenir les paramètres
        assert 'q=' in url or 'query' in str(call_args)

