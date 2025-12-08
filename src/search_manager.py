"""
Gestionnaire de recherches d'emploi - Multiples recherches et tests
"""

import json
import os
import uuid
from typing import Dict, List, Optional
from datetime import datetime

class SearchManager:
    def __init__(self, searches_file="/app/config/searches.json"):
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
                     description: str = "",
                     standalone: bool = False,
                     # Nouveaux champs détaillés
                     salary_min: int = None,
                     salary_max: int = None,
                     contract_type: List[str] = None,  # CDI, CDD, Stage, Freelance, etc.
                     experience_level: str = None,  # Junior, Mid, Senior, etc.
                     remote: bool = None,  # Télétravail
                     full_time: bool = None,  # Temps plein
                     company_size: str = None,  # Startup, PME, Grande entreprise
                     tags: List[str] = None,  # Tags personnalisés
                     notes: str = None,  # Notes personnelles
                     priority: int = 1,  # Priorité de la recherche (1-5)
                     personas_assigned: List[str] = None,  # Personas assignés à cette recherche (emails)
                     personas_excluded: List[str] = None) -> str:  # Personas exclus de cette recherche (emails)
        """Crée une nouvelle recherche.
        
        Args:
            standalone: Si True, la recherche ne postule pas avec des personas, elle ne fait que scraper les offres.
        """
        # Générer une clé si non fournie
        if not key:
            # Générer un ID unique basé sur UUID
            search_id = str(uuid.uuid4())[:8]  # 8 premiers caractères de l'UUID
            key = f"search_{search_id}"
            # S'assurer que la clé est unique
            while key in self.searches:
                search_id = str(uuid.uuid4())[:8]
                key = f"search_{search_id}"
        
        if key in self.searches:
            raise ValueError(f"Une recherche avec la clé '{key}' existe déjà")
        
        # Normaliser les noms de champs (support rétrocompatibilité)
        final_search_type = search_type or job_type or "développeur"
        final_is_active = is_active if is_active is not None else (enabled if enabled is not None else True)
        
        search = {
            "id": key,  # ID unique de la recherche
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
            "standalone": standalone,  # Recherche standalone (sans personas)
            # Nouveaux champs détaillés
            "salary_min": salary_min,
            "salary_max": salary_max,
            "contract_type": contract_type or [],
            "experience_level": experience_level,
            "remote": remote,
            "full_time": full_time,
            "company_size": company_size,
            "tags": tags or [],
            "notes": notes,
            "priority": priority,
            "personas_assigned": personas_assigned or [],  # Personas spécifiques pour cette recherche
            "personas_excluded": personas_excluded or [],  # Personas à exclure de cette recherche
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
            description=new_search.get('description', ''),
            standalone=new_search.get('standalone', False),
            salary_min=new_search.get('salary_min'),
            salary_max=new_search.get('salary_max'),
            contract_type=new_search.get('contract_type', []),
            experience_level=new_search.get('experience_level'),
            remote=new_search.get('remote'),
            full_time=new_search.get('full_time'),
            company_size=new_search.get('company_size'),
            tags=new_search.get('tags', []),
            notes=new_search.get('notes'),
            priority=new_search.get('priority', 1)
        )
    
    def mark_run(self, search_key: str, details: Dict = None):
        """Marque une recherche comme exécutée avec des détails."""
        if search_key in self.searches:
            self.searches[search_key]['last_run'] = datetime.now().isoformat()
            self.searches[search_key]['run_count'] = self.searches[search_key].get('run_count', 0) + 1
            
            # Initialiser l'historique si nécessaire
            if 'execution_history' not in self.searches[search_key]:
                self.searches[search_key]['execution_history'] = []
            
            # Ajouter les détails de cette exécution
            execution_record = {
                'timestamp': datetime.now().isoformat(),
                'jobs_found': details.get('jobs_found', 0) if details else 0,
                'jobs_filtered': details.get('jobs_filtered', 0) if details else 0,
                'applications_sent': details.get('applications_sent', 0) if details else 0,
                'applications_failed': details.get('applications_failed', 0) if details else 0,
                'personas_used': details.get('personas_used', []) if details else [],
                'errors': details.get('errors', []) if details else [],
                'steps': details.get('steps', []) if details else [],
                'duration_seconds': details.get('duration_seconds', 0) if details else 0
            }
            
            self.searches[search_key]['execution_history'].append(execution_record)
            
            # Garder seulement les 50 dernières exécutions
            if len(self.searches[search_key]['execution_history']) > 50:
                self.searches[search_key]['execution_history'] = self.searches[search_key]['execution_history'][-50:]
            
            self.save_searches()
    
    def get_execution_history(self, search_key: str) -> List[Dict]:
        """Récupère l'historique d'exécution d'une recherche."""
        if search_key in self.searches:
            return self.searches[search_key].get('execution_history', [])
        return []
    
    def get_last_execution(self, search_key: str) -> Optional[Dict]:
        """Récupère les détails de la dernière exécution."""
        history = self.get_execution_history(search_key)
        return history[-1] if history else None
    
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

