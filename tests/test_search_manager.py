"""
Tests pour le module search_manager.py
"""
import pytest
import sys
import os
import tempfile
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from search_manager import SearchManager

def test_search_manager_init(temp_config_dir):
    """Test d'initialisation du SearchManager."""
    searches_file = os.path.join(temp_config_dir, "searches.json")
    
    manager = SearchManager(searches_file)
    assert manager is not None
    assert isinstance(manager.searches, dict)

def test_create_search(temp_config_dir, sample_search):
    """Test de création d'une recherche."""
    searches_file = os.path.join(temp_config_dir, "searches.json")
    
    manager = SearchManager(searches_file)
    
    search_key = manager.create_search(
        name=sample_search['name'],
        query=sample_search['query'],
        location=sample_search['location'],
        title_keywords=sample_search['title_keywords'],
        location_keywords=sample_search['location_keywords'],
        exclude_keywords=sample_search['exclude_keywords'],
        search_type=sample_search['search_type'],
        max_results=sample_search['max_results'],
        is_active=sample_search['is_active'],
        standalone=sample_search['standalone']
    )
    
    assert search_key is not None
    assert search_key in manager.searches
    assert manager.searches[search_key]['name'] == sample_search['name']

def test_get_search(temp_config_dir, sample_search):
    """Test de récupération d'une recherche."""
    searches_file = os.path.join(temp_config_dir, "searches.json")
    
    manager = SearchManager(searches_file)
    
    search_key = manager.create_search(
        name=sample_search['name'],
        query=sample_search['query'],
        location=sample_search['location']
    )
    
    search = manager.get_search(search_key)
    assert search is not None
    assert search['name'] == sample_search['name']

def test_update_search(temp_config_dir, sample_search):
    """Test de mise à jour d'une recherche."""
    searches_file = os.path.join(temp_config_dir, "searches.json")
    
    manager = SearchManager(searches_file)
    
    search_key = manager.create_search(
        name=sample_search['name'],
        query=sample_search['query'],
        location=sample_search['location']
    )
    
    success = manager.update_search(search_key, name="Updated Search")
    assert success is True
    assert manager.searches[search_key]['name'] == "Updated Search"

def test_delete_search(temp_config_dir, sample_search):
    """Test de suppression d'une recherche."""
    searches_file = os.path.join(temp_config_dir, "searches.json")
    
    manager = SearchManager(searches_file)
    
    search_key = manager.create_search(
        name=sample_search['name'],
        query=sample_search['query'],
        location=sample_search['location']
    )
    
    success = manager.delete_search(search_key)
    assert success is True
    assert search_key not in manager.searches

def test_mark_run(temp_config_dir, sample_search):
    """Test de marquage d'une recherche comme exécutée."""
    searches_file = os.path.join(temp_config_dir, "searches.json")
    
    manager = SearchManager(searches_file)
    
    search_key = manager.create_search(
        name=sample_search['name'],
        query=sample_search['query'],
        location=sample_search['location']
    )
    
    details = {
        'jobs_found': 10,
        'jobs_filtered': 8,
        'applications_sent': 5,
        'applications_failed': 1,
        'personas_used': [],
        'errors': [],
        'steps': [],
        'duration_seconds': 60
    }
    
    manager.mark_run(search_key, details)
    
    search = manager.get_search(search_key)
    assert search['last_run'] is not None
    assert search['run_count'] == 1
    assert 'execution_history' in search
    assert len(search['execution_history']) == 1

def test_get_execution_history(temp_config_dir, sample_search):
    """Test de récupération de l'historique d'exécution."""
    searches_file = os.path.join(temp_config_dir, "searches.json")
    
    manager = SearchManager(searches_file)
    
    search_key = manager.create_search(
        name=sample_search['name'],
        query=sample_search['query'],
        location=sample_search['location']
    )
    
    manager.mark_run(search_key, {'jobs_found': 5})
    manager.mark_run(search_key, {'jobs_found': 10})
    
    history = manager.get_execution_history(search_key)
    assert len(history) == 2

def test_standalone_search(temp_config_dir):
    """Test de création d'une recherche standalone."""
    searches_file = os.path.join(temp_config_dir, "searches.json")
    
    manager = SearchManager(searches_file)
    
    search_key = manager.create_search(
        name="Standalone Test",
        query="test",
        location="test",
        standalone=True
    )
    
    search = manager.get_search(search_key)
    assert search['standalone'] is True

