"""
Gestionnaire de recherches d'emploi - Multiples recherches et tests
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class SearchManager:
    def __init__(self, searches_file="/app/searches.json"):
        self.searches_file = searches_file
        self.searches = self.load_searches()
    
    def load_searches(self) -> Dict:
        """Charge les recherches depuis le fichier JSON."""
        if not os.path.exists(self.searches_file):
            return {}
        try:
            with open(self.searches_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Erreur lors du chargement des recherches: {e}")
            return {}
    
    def save_searches(self):
        """Sauvegarde les recherches dans le fichier JSON."""
        try:
            with open(self.searches_file, 'w', encoding='utf-8') as file:
                json.dump(self.searches, file, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des recherches: {e}")
            return False
    
    def create_search(self, key: str = None, name: str = None, query: str = None, location: str = None,
                     title_keywords: List[str] = None,
                     location_keywords: List[str] = None,
                     exclude_keywords: List[str] = None,
                     search_type: str = None,
                     job_type: str = None,  # Rétrocompatibilité
                     max_results: int = 50,
                     is_active: bool = None,
                     enabled: bool = None,  # Rétrocompatibilité
                     description: str = "") -> str:
        """Crée une nouvelle recherche."""
        # Générer une clé si non fournie
        if not key:
            key = f"search{len(self.searches) + 1}"
            while key in self.searches:
                key = f"search{len(self.searches) + 1}"
        
        if key in self.searches:
            raise ValueError(f"Une recherche avec la clé '{key}' existe déjà")
        
        # Normaliser les noms de champs (support rétrocompatibilité)
        final_search_type = search_type or job_type or "développeur"
        final_is_active = is_active if is_active is not None else (enabled if enabled is not None else True)
        
        search = {
            "name": name,
            "query": query,
            "location": location,
            "title_keywords": title_keywords or [],
            "location_keywords": location_keywords or [],
            "exclude_keywords": exclude_keywords or [],
            "search_type": final_search_type,
            "max_results": max_results,
            "is_active": final_is_active,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "last_run": None,
            "run_count": 0
        }
        
        self.searches[key] = search
        self.save_searches()
        return key
    
    def get_search(self, search_key: str) -> Optional[Dict]:
        """Récupère une recherche par sa clé."""
        return self.searches.get(search_key)
    
    def update_search(self, search_key: str, **kwargs) -> bool:
        """Met à jour une recherche."""
        if search_key not in self.searches:
            return False
        
        for key, value in kwargs.items():
            if value is not None:
                self.searches[search_key][key] = value
        
        self.searches[search_key]["updated_at"] = datetime.now().isoformat()
        self.save_searches()
        return True
    
    def delete_search(self, search_key: str) -> bool:
        """Supprime une recherche."""
        if search_key not in self.searches:
            return False
        
        del self.searches[search_key]
        self.save_searches()
        return True
    
    def get_all_searches(self) -> Dict:
        """Récupère toutes les recherches."""
        return self.searches
    
    def get_enabled_searches(self) -> Dict:
        """Récupère uniquement les recherches activées."""
        return {k: v for k, v in self.searches.items() if v.get('is_active', v.get('enabled', True))}
    
    def get_active_searches(self) -> Dict:
        """Alias pour get_enabled_searches (utilise is_active)."""
        return self.get_enabled_searches()
    
    def duplicate_search(self, search_key: str, new_name: Optional[str] = None, new_key: Optional[str] = None) -> str:
        """Duplique une recherche."""
        search = self.get_search(search_key)
        if not search:
            raise ValueError(f"Recherche '{search_key}' non trouvée")
        
        new_search = search.copy()
        if new_name:
            new_search['name'] = new_name
        else:
            new_search['name'] = f"{search['name']} (Copie)"
        
        new_search['created_at'] = datetime.now().isoformat()
        new_search['last_run'] = None
        new_search['run_count'] = 0
        
        # Normaliser les champs pour la compatibilité
        search_type = new_search.get('search_type') or new_search.get('job_type', 'développeur')
        is_active = new_search.get('is_active') if 'is_active' in new_search else (new_search.get('enabled', True))
        
        return self.create_search(
            key=new_key,
            name=new_search['name'],
            query=new_search['query'],
            location=new_search['location'],
            title_keywords=new_search.get('title_keywords', []),
            location_keywords=new_search.get('location_keywords', []),
            exclude_keywords=new_search.get('exclude_keywords', []),
            search_type=search_type,
            max_results=new_search.get('max_results', 50),
            is_active=is_active,
            description=new_search.get('description', '')
        )
    
    def mark_run(self, search_key: str):
        """Marque une recherche comme exécutée."""
        if search_key in self.searches:
            self.searches[search_key]['last_run'] = datetime.now().isoformat()
            self.searches[search_key]['run_count'] = self.searches[search_key].get('run_count', 0) + 1
            self.save_searches()
    
    def get_job_types(self) -> List[str]:
        """Retourne les types de postes disponibles."""
        return [
            "développeur",
            "développeur backend",
            "développeur frontend",
            "développeur fullstack",
            "devops",
            "data scientist",
            "data engineer",
            "architecte",
            "lead developer",
            "cto",
            "product manager",
            "scrum master",
            "qa test",
            "autre"
        ]

