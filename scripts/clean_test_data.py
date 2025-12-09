#!/usr/bin/env python3
"""
Script pour nettoyer les données de test
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
from src.search_manager import SearchManager
from src.persona_manager import PersonaManager

def clean_test_searches():
    """Nettoie les recherches de test."""
    search_manager = SearchManager()
    all_searches = search_manager.get_all_searches()
    cleaned = 0
    invalid = []
    
    for key, search in list(all_searches.items()):
        # Supprimer les recherches invalides (sans query, name, location)
        if not search.get('query') and not search.get('name') and not search.get('location'):
            search_manager.delete_search(key)
            invalid.append(key)
            cleaned += 1
        # Supprimer les recherches de test (nom contient "test")
        elif 'test' in key.lower() or 'test' in (search.get('name', '') or '').lower():
            search_manager.delete_search(key)
            invalid.append(key)
            cleaned += 1
    
    print(f"✅ {cleaned} recherche(s) de test/invalide(s) supprimée(s)")
    return cleaned, invalid

def clean_test_personas():
    """Nettoie les personas de test."""
    persona_manager = PersonaManager()
    all_personas = persona_manager.get_all_personas()
    cleaned = 0
    invalid = []
    
    for key, persona in list(all_personas.items()):
        # Supprimer les personas de test (nom ou clé contient "test")
        if 'test' in key.lower() or 'test' in (persona.get('name', '') or '').lower():
            persona_manager.delete_persona(key)
            invalid.append(key)
            cleaned += 1
    
    print(f"✅ {cleaned} persona(s) de test supprimé(s)")
    return cleaned, invalid

if __name__ == '__main__':
    print("🧹 Nettoyage des données de test...")
    searches_cleaned, searches_invalid = clean_test_searches()
    personas_cleaned, personas_invalid = clean_test_personas()
    print(f"\n✅ Nettoyage terminé:")
    print(f"   - {searches_cleaned} recherche(s) supprimée(s)")
    print(f"   - {personas_cleaned} persona(s) supprimé(s)")

