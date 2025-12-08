"""
Tests pour le module job_filter.py
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_job_filter_imports():
    """Test que le module peut être importé."""
    try:
        from job_filter import filter_jobs
        assert True
    except ImportError as e:
        pytest.skip(f"Module job_filter non disponible: {e}")

def test_filter_jobs_function_exists():
    """Test que la fonction filter_jobs existe."""
    from job_filter import filter_jobs
    assert callable(filter_jobs)

def test_filter_jobs_with_keywords(temp_db):
    """Test du filtrage avec des mots-clés."""
    import sqlite3
    import database
    
    original_get_db_path = database.get_db_path
    database.get_db_path = lambda: temp_db
    
    try:
        from job_filter import filter_jobs
        
        # Insérer des offres de test
        jobs = [
            {'title': 'Développeur Python Senior', 'company': 'C1', 'location': 'Rennes', 'url': '', 'description': ''},
            {'title': 'Développeur Java', 'company': 'C2', 'location': 'Paris', 'url': '', 'description': ''},
            {'title': 'Développeur Python Junior', 'company': 'C3', 'location': 'Rennes', 'url': '', 'description': ''}
        ]
        
        for job in jobs:
            database.insert_job(job)
        
        # Filtrer avec des mots-clés
        filtered = filter_jobs(
            title_keywords=['Python'],
            location_keywords=['Rennes'],
            exclude_keywords=['Senior']
        )
        
        # Devrait trouver seulement "Développeur Python Junior" à Rennes
        assert len(filtered) >= 1
        job_titles = [j['title'] for j in filtered]
        assert any('Python' in title and 'Junior' in title for title in job_titles)
        assert not any('Senior' in title for title in job_titles)
    finally:
        database.get_db_path = original_get_db_path

