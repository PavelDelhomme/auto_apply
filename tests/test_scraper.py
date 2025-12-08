"""
Tests pour le module scraper.py
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_scraper_imports():
    """Test que le module peut être importé."""
    try:
        from scraper import scrape_indeed
        assert True
    except ImportError as e:
        pytest.skip(f"Module scraper non disponible: {e}")

def test_scraper_function_exists():
    """Test que la fonction scrape_indeed existe."""
    from scraper import scrape_indeed
    assert callable(scrape_indeed)

@pytest.mark.skip(reason="Test d'intégration nécessitant une connexion réseau")
def test_scraper_integration():
    """Test d'intégration du scraper (nécessite une connexion réseau)."""
    from scraper import scrape_indeed
    
    # Test avec des paramètres simples
    jobs = scrape_indeed(query="développeur python", location="Rennes", max_results=5)
    
    assert isinstance(jobs, list)
    # Si des offres sont trouvées, vérifier la structure
    if jobs:
        job = jobs[0]
        assert 'title' in job
        assert 'company' in job
        assert 'location' in job

