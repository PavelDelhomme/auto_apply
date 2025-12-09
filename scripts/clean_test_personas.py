#!/usr/bin/env python3
"""
Script pour nettoyer les personas de test du fichier personas.json
"""

import json
import os
import sys

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.persona_manager import PersonaManager

def is_test_persona(persona_key, persona_data):
    """Détermine si un persona est un persona de test."""
    email = persona_data.get('email', '')
    name = persona_data.get('name', '')
    
    # Emails de test
    if email and ('@example.com' in email.lower() or 
                  'test.persona.extended' in email.lower()):
        return True
    
    # Noms de test
    test_names = [
        'test persona extended',
        'test persona api',
        'duplicated persona',
        'updated name',
        'variant name',
        'test'
    ]
    
    if name and any(test_name in name.lower() for test_name in test_names):
        return True
    
    # Email null ou vide
    if not email or email == 'null' or email is None:
        return True
    
    return False

def clean_test_personas():
    """Nettoie les personas de test."""
    manager = PersonaManager("/app/config/personas.json")
    
    print("🔍 Recherche des personas de test...")
    
    personas_to_delete = []
    for key, persona in manager.personas.items():
        if is_test_persona(key, persona):
            personas_to_delete.append((key, persona.get('name', 'N/A'), persona.get('email', 'N/A')))
    
    if not personas_to_delete:
        print("✅ Aucun persona de test trouvé.")
        return
    
    print(f"\n📋 {len(personas_to_delete)} persona(s) de test trouvé(s):")
    for key, name, email in personas_to_delete:
        print(f"  - {name} ({email})")
    
    # Supprimer les personas de test
    for key, _, _ in personas_to_delete:
        if key in manager.personas:
            del manager.personas[key]
    
    # Sauvegarder
    if manager.save_personas():
        print(f"\n✅ {len(personas_to_delete)} persona(s) de test supprimé(s) avec succès.")
    else:
        print("\n❌ Erreur lors de la sauvegarde.")
        sys.exit(1)

if __name__ == '__main__':
    clean_test_personas()

