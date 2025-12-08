"""
Tests pour le module persona_manager.py
"""
import pytest
import sys
import os
import tempfile
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from persona_manager import PersonaManager

def test_persona_manager_init(temp_config_dir):
    """Test d'initialisation du PersonaManager."""
    personas_file = os.path.join(temp_config_dir, "personas.json")
    
    # Créer un fichier personas.json vide
    with open(personas_file, 'w', encoding='utf-8') as f:
        json.dump({}, f)
    
    manager = PersonaManager(personas_file)
    assert manager is not None
    assert isinstance(manager.personas, dict)

def test_create_persona(temp_config_dir):
    """Test de création d'un persona."""
    personas_file = os.path.join(temp_config_dir, "personas.json")
    
    with open(personas_file, 'w', encoding='utf-8') as f:
        json.dump({}, f)
    
    manager = PersonaManager(personas_file)
    
    persona_key = manager.create_persona(
        name="Test Persona",
        email="test@example.com",
        password="testpass123"
    )
    
    assert persona_key is not None
    assert persona_key in manager.personas
    assert manager.personas[persona_key]['name'] == "Test Persona"
    assert manager.personas[persona_key]['email'] == "test@example.com"

def test_get_persona(temp_config_dir):
    """Test de récupération d'un persona."""
    personas_file = os.path.join(temp_config_dir, "personas.json")
    
    manager = PersonaManager(personas_file)
    
    persona_key = manager.create_persona(
        name="Test",
        email="test@example.com"
    )
    
    persona = manager.get_persona(persona_key)
    assert persona is not None
    assert persona['name'] == "Test"

def test_get_persona_by_email(temp_config_dir):
    """Test de récupération d'un persona par email."""
    personas_file = os.path.join(temp_config_dir, "personas.json")
    
    manager = PersonaManager(personas_file)
    
    manager.create_persona(
        name="Test",
        email="test@example.com"
    )
    
    persona = manager.get_persona_by_email("test@example.com")
    assert persona is not None
    assert persona['email'] == "test@example.com"

def test_update_persona(temp_config_dir):
    """Test de mise à jour d'un persona."""
    personas_file = os.path.join(temp_config_dir, "personas.json")
    
    manager = PersonaManager(personas_file)
    
    persona_key = manager.create_persona(
        name="Test",
        email="test@example.com"
    )
    
    success = manager.update_persona(persona_key, name="Updated Test")
    assert success is True
    assert manager.personas[persona_key]['name'] == "Updated Test"

def test_delete_persona(temp_config_dir):
    """Test de suppression d'un persona."""
    personas_file = os.path.join(temp_config_dir, "personas.json")
    
    manager = PersonaManager(personas_file)
    
    persona_key = manager.create_persona(
        name="Test",
        email="test@example.com"
    )
    
    success = manager.delete_persona(persona_key)
    assert success is True
    assert persona_key not in manager.personas

