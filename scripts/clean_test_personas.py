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
    
    # Noms de test (plus complets)
    test_names = [
        'test persona extended',
        'test persona api',
        'duplicated persona',
        'updated name',
        'variant name',
        'test',
        'test persona',
        'persona test'
    ]
    
    if name and any(test_name in name.lower() for test_name in test_names):
        return True
    
    # Email null ou vide ou "N/A"
    if not email or email == 'null' or email is None or email.upper() == 'N/A':
        return True
    
    # Clés de persona qui commencent par "test" ou contiennent "test"
    if persona_key and 'test' in persona_key.lower():
        return True
    
    return False

def clean_test_personas():
    """Nettoie les personas de test."""
    # Déterminer le chemin du fichier personas.json
    if os.path.exists('/app/config/personas.json'):
        personas_file = '/app/config/personas.json'
    else:
        personas_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'personas.json')
    
    manager = PersonaManager(personas_file)
    
    print("🔍 Recherche des personas de test...")
    
    personas_to_delete = []
    for key, persona in manager.personas.items():
        if is_test_persona(key, persona):
            personas_to_delete.append((key, persona.get('name', 'N/A'), persona.get('email', 'N/A')))
    
    if not personas_to_delete:
        print("✅ Aucun persona de test trouvé.")
        return
    
    print(f"\n📋 {len(personas_to_delete)} persona(s) de test trouvé(s):")
    for key, name, email in personas_to_delete[:20]:  # Afficher les 20 premiers
        print(f"  - {key}: {name} ({email})")
    if len(personas_to_delete) > 20:
        print(f"  ... et {len(personas_to_delete) - 20} autres")
    
    # Supprimer les personas de test
    for key, _, _ in personas_to_delete:
        if key in manager.personas:
            del manager.personas[key]
    
    # Sauvegarder
    if manager.save_personas():
        print(f"\n✅ {len(personas_to_delete)} persona(s) de test supprimé(s) avec succès.")
        print(f"📊 Il reste {len(manager.personas)} persona(s) valide(s).")
    else:
        print("\n❌ Erreur lors de la sauvegarde.")
        sys.exit(1)

if __name__ == '__main__':
    clean_test_personas()

