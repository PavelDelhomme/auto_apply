"""
Tests pour le module database.py
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import (
    create_database, insert_job, get_all_jobs, 
    get_unapplied_jobs, insert_application, 
    update_application_status, insert_email
)

def test_create_database(temp_db):
    """Test de création de la base de données."""
    # La base de données est déjà créée par la fixture
    import sqlite3
    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    
    # Vérifier que les tables existent
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c.fetchall()]
    
    assert 'jobs' in tables
    assert 'applications' in tables
    assert 'persona_emails' in tables
    
    conn.close()

def test_insert_job(temp_db):
    """Test d'insertion d'une offre d'emploi."""
    import sqlite3
    import database
    
    # Sauvegarder le chemin original
    original_get_db_path = database.get_db_path
    
    # Remplacer temporairement get_db_path
    database.get_db_path = lambda: temp_db
    
    try:
        job = {
            'title': 'Développeur Python',
            'company': 'Test Company',
            'location': 'Rennes',
            'url': 'https://example.com/job1',
            'description': 'Description du poste'
        }
        
        job_id = insert_job(job, is_test_data=True)
        assert job_id is not None
        
        # Vérifier que l'offre a été insérée
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        result = c.fetchone()
        conn.close()
        
        assert result is not None
        assert result[1] == 'Développeur Python'
        assert result[2] == 'Test Company'
    finally:
        database.get_db_path = original_get_db_path

def test_get_all_jobs(temp_db):
    """Test de récupération de toutes les offres."""
    import sqlite3
    import database
    
    original_get_db_path = database.get_db_path
    database.get_db_path = lambda: temp_db
    
    try:
        # Insérer quelques offres
        jobs = [
            {'title': 'Job 1', 'company': 'Company 1', 'location': 'Paris', 'url': '', 'description': ''},
            {'title': 'Job 2', 'company': 'Company 2', 'location': 'Lyon', 'url': '', 'description': ''}
        ]
        
        for job in jobs:
            insert_job(job)
        
        all_jobs = get_all_jobs()
        assert len(all_jobs) >= 2
        assert any(j['title'] == 'Job 1' for j in all_jobs)
        assert any(j['title'] == 'Job 2' for j in all_jobs)
    finally:
        database.get_db_path = original_get_db_path

def test_insert_application(temp_db):
    """Test d'insertion d'une candidature."""
    import sqlite3
    import database
    
    original_get_db_path = database.get_db_path
    database.get_db_path = lambda: temp_db
    
    try:
        # Insérer une offre d'abord
        job = {'title': 'Test Job', 'company': 'Test', 'location': 'Test', 'url': '', 'description': ''}
        job_id = insert_job(job)
        
        # Insérer une candidature
        app_id = insert_application(
            job_id=job_id,
            persona_email='test@example.com',
            persona_name='Test Persona',
            cv_path='/path/to/cv.pdf',
            cover_letter='Test cover letter',
            status='pending'
        )
        
        assert app_id is not None
        
        # Vérifier
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
        result = c.fetchone()
        conn.close()
        
        assert result is not None
        assert result[2] == 'test@example.com'
    finally:
        database.get_db_path = original_get_db_path

def test_insert_email(temp_db):
    """Test d'insertion d'un email."""
    import sqlite3
    import database
    
    original_get_db_path = database.get_db_path
    database.get_db_path = lambda: temp_db
    
    try:
        email_id = insert_email(
            persona_email='test@example.com',
            sender='sender@example.com',
            subject='Test Subject',
            body='Test body',
            email_type='application',
            is_test_data=True
        )
        
        assert email_id is not None
        
        # Vérifier
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        c.execute("SELECT * FROM persona_emails WHERE id = ?", (email_id,))
        result = c.fetchone()
        conn.close()
        
        assert result is not None
        assert result[1] == 'test@example.com'
        assert result[2] == 'sender@example.com'
    finally:
        database.get_db_path = original_get_db_path

def test_get_unapplied_jobs(temp_db):
    """Test de récupération des offres non candidatées."""
    import sqlite3
    import database
    
    original_get_db_path = database.get_db_path
    database.get_db_path = lambda: temp_db
    
    try:
        # Insérer des offres
        job1 = {'title': 'Job 1', 'company': 'C1', 'location': 'L1', 'url': '', 'description': ''}
        job2 = {'title': 'Job 2', 'company': 'C2', 'location': 'L2', 'url': '', 'description': ''}
        
        job1_id = insert_job(job1)
        job2_id = insert_job(job2)
        
        # Candidater à job1 seulement
        insert_application(job1_id, 'test@example.com', 'Test', '/cv.pdf', 'Cover letter test')
        
        # Récupérer les offres non candidatées
        unapplied = get_unapplied_jobs('test@example.com')
        
        # Job2 devrait être dans la liste, pas job1
        job_titles = [j['title'] for j in unapplied]
        assert 'Job 2' in job_titles
        assert 'Job 1' not in job_titles
    finally:
        database.get_db_path = original_get_db_path

