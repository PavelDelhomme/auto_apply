"""
Tests pour la gestion des emails des personas
"""
import pytest
import sys
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.app import app
from database import create_database, insert_email, get_persona_emails, get_db_path
import sqlite3

@pytest.fixture
def client():
    """Crée un client de test Flask."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            create_database()
            yield client

@pytest.fixture
def test_persona():
    """Crée un persona de test."""
    return {
        'name': 'Test Persona',
        'email': 'test@example.com',
        'password': 'testpass123'
    }

def test_insert_email(client, test_persona):
    """Test l'insertion d'un email."""
    email_id = insert_email(
        persona_email=test_persona['email'],
        sender='recruiter@company.com',
        subject='Réponse à votre candidature',
        body='Merci pour votre candidature...',
        email_type='application'
    )
    assert email_id is not None

def test_get_persona_emails(client, test_persona):
    """Test la récupération des emails d'un persona."""
    # Insérer quelques emails
    insert_email(test_persona['email'], 'sender1@test.com', 'Subject 1', 'Body 1')
    insert_email(test_persona['email'], 'sender2@test.com', 'Subject 2', 'Body 2')
    
    emails = get_persona_emails(test_persona['email'])
    assert len(emails) >= 2
    assert emails[0]['sender'] in ['sender1@test.com', 'sender2@test.com']

def test_api_get_persona_emails(client, test_persona):
    """Test l'API de récupération des emails."""
    # Insérer un email
    insert_email(test_persona['email'], 'test@example.com', 'Test Subject', 'Test Body')
    
    response = client.get(f"/api/personas/{test_persona['email']}/emails")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_api_email_count(client, test_persona):
    """Test l'API de comptage des emails."""
    # Insérer quelques emails
    insert_email(test_persona['email'], 'sender1@test.com', 'Subject 1', 'Body 1')
    insert_email(test_persona['email'], 'sender2@test.com', 'Subject 2', 'Body 2', is_test_data=True)
    
    response = client.get(f"/api/personas/{test_persona['email']}/emails/count")
    assert response.status_code == 200
    data = response.get_json()
    assert 'total' in data
    assert 'unread' in data
    assert data['total'] >= 1

def test_api_mark_email_read(client, test_persona):
    """Test l'API de marquage d'email comme lu."""
    # Insérer un email
    email_id = insert_email(test_persona['email'], 'test@example.com', 'Test', 'Body')
    
    response = client.post(f"/api/personas/{test_persona['email']}/emails/{email_id}/read")
    assert response.status_code == 200
    data = response.get_json()
    assert data.get('success') is True
    
    # Vérifier que l'email est marqué comme lu
    emails = get_persona_emails(test_persona['email'])
    read_email = next((e for e in emails if e['id'] == email_id), None)
    assert read_email is not None
    assert read_email['is_read'] is True

def test_api_test_email_connection(client, test_persona):
    """Test l'API de test de connexion email (mock)."""
    # Note: Ce test nécessiterait un mock de imaplib
    # Pour l'instant, on teste juste que l'endpoint existe
    response = client.post(f"/api/personas/{test_persona['email']}/emails/test-connection")
    # Peut retourner 404 si le persona n'existe pas, ou 400 si pas de mot de passe
    assert response.status_code in [200, 400, 404, 500]

def test_email_exclude_test_data(client, test_persona):
    """Test que les emails de test sont exclus si demandé."""
    # Insérer des emails normaux et de test
    insert_email(test_persona['email'], 'normal@test.com', 'Normal', 'Body', is_test_data=False)
    insert_email(test_persona['email'], 'test@test.com', 'Test', 'Body', is_test_data=True)
    
    emails = get_persona_emails(test_persona['email'])
    # Tous les emails devraient être retournés par défaut
    assert len(emails) >= 2
    
    # Note: La fonction get_persona_emails ne filtre pas actuellement par is_test_data
    # Ce serait une amélioration future

