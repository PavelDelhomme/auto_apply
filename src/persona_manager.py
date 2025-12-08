"""
Gestionnaire de personas - CRUD et variantes
"""

import json
import os
from typing import Dict, List, Optional
import random
import string

class PersonaManager:
    def __init__(self, personas_file="/app/config/personas.json"):
        self.personas_file = personas_file
        self.personas = self.load_personas()
    
    def load_personas(self) -> Dict:
        """Charge les personas depuis le fichier JSON."""
        if not os.path.exists(self.personas_file):
            return {}
        try:
            with open(self.personas_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Erreur lors du chargement des personas: {e}")
            return {}
    
    def save_personas(self):
        """Sauvegarde les personas dans le fichier JSON."""
        try:
            with open(self.personas_file, 'w', encoding='utf-8') as file:
                json.dump(self.personas, file, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des personas: {e}")
            return False
    
    def get_persona(self, persona_key: str) -> Optional[Dict]:
        """Récupère un persona par sa clé."""
        return self.personas.get(persona_key)
    
    def get_persona_by_email(self, email: str) -> Optional[Dict]:
        """Récupère un persona par son email."""
        for persona in self.personas.values():
            if persona.get('email') == email:
                return persona
        return None
    
    def create_persona(self, name: str, email: str, password: str = "", 
                      alias: bool = False, parent: Optional[str] = None,
                      custom_data: Optional[Dict] = None,
                      # Nouveaux champs détaillés
                      skills: Optional[List[str]] = None,
                      experience_years: Optional[int] = None,
                      education: Optional[List[Dict]] = None,
                      languages: Optional[List[str]] = None,
                      location: Optional[str] = None,
                      phone: Optional[str] = None,
                      linkedin: Optional[str] = None,
                      github: Optional[str] = None,
                      portfolio: Optional[str] = None,
                      notes: Optional[str] = None,
                      # Configuration email
                      email_config: Optional[Dict] = None) -> str:
        """Crée un nouveau persona avec des détails complets."""
        # Générer une clé unique
        persona_key = f"persona{len(self.personas) + 1}"
        while persona_key in self.personas:
            persona_key = f"persona{len(self.personas) + 1}"
        
        persona = {
            "name": name,
            "email": email,
            "password": password,
            "alias": alias,
            "parent": parent,
            # Nouveaux champs détaillés
            "skills": skills or [],
            "experience_years": experience_years,
            "education": education or [],
            "languages": languages or [],
            "location": location,
            "phone": phone,
            "linkedin": linkedin,
            "github": github,
            "portfolio": portfolio,
            "notes": notes,
            # Configuration email personnalisée
            "email_config": email_config or {}
        }
        
        if custom_data:
            persona.update(custom_data)
        
        self.personas[persona_key] = persona
        self.save_personas()
        return persona_key
    
    def update_persona(self, persona_key: str, **kwargs) -> bool:
        """Met à jour un persona."""
        if persona_key not in self.personas:
            return False
        
        for key, value in kwargs.items():
            if value is not None:
                self.personas[persona_key][key] = value
        
        self.save_personas()
        return True
    
    def delete_persona(self, persona_key: str) -> bool:
        """Supprime un persona."""
        if persona_key not in self.personas:
            return False
        
        del self.personas[persona_key]
        self.save_personas()
        return True
    
    def create_variant(self, base_persona_key: str, variant_name: Optional[str] = None,
                     email_suffix: Optional[str] = None, **overrides) -> str:
        """
        Crée une variante d'un persona de base.
        Par défaut, génère un nom et email variant.
        """
        base_persona = self.get_persona(base_persona_key)
        if not base_persona:
            raise ValueError(f"Persona de base '{base_persona_key}' non trouvé")
        
        # Générer un nom variant si non fourni
        if not variant_name:
            base_name = base_persona['name'].split()[0]  # Prénom
            surnames = ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", 
                       "Petit", "Durand", "Leroy", "Moreau", "Simon", "Laurent"]
            variant_name = f"{base_name} {random.choice(surnames)}"
        
        # Générer un email variant si non fourni
        if not email_suffix:
            # Extraire le domaine de l'email de base
            base_email = base_persona['email']
            if '@' in base_email:
                domain = base_email.split('@')[1]
                username = base_persona['name'].lower().replace(' ', '.')
                random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
                email_suffix = f"{username}.{random_suffix}@{domain}"
            else:
                email_suffix = f"{variant_name.lower().replace(' ', '.')}@gmx.com"
        
        # Créer le persona variant
        variant = base_persona.copy()
        variant['name'] = variant_name
        variant['email'] = email_suffix
        variant['alias'] = True
        variant['parent'] = base_persona['email']
        
        # Appliquer les overrides
        variant.update(overrides)
        
        # Créer le persona
        persona_key = self.create_persona(
            name=variant['name'],
            email=variant['email'],
            password=variant.get('password', ''),
            alias=variant['alias'],
            parent=variant['parent'],
            custom_data={k: v for k, v in variant.items() 
                        if k not in ['name', 'email', 'password', 'alias', 'parent']}
        )
        
        return persona_key
    
    def create_multiple_variants(self, base_persona_key: str, count: int,
                                name_pattern: Optional[str] = None) -> List[str]:
        """Crée plusieurs variantes d'un persona de base."""
        created_keys = []
        base_persona = self.get_persona(base_persona_key)
        
        if not base_persona:
            raise ValueError(f"Persona de base '{base_persona_key}' non trouvé")
        
        base_name = base_persona['name'].split()[0]
        base_email = base_persona['email']
        domain = base_email.split('@')[1] if '@' in base_email else 'gmx.com'
        
        for i in range(count):
            if name_pattern:
                variant_name = name_pattern.format(i=i+1, base=base_name)
            else:
                surnames = ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard"]
                variant_name = f"{base_name} {random.choice(surnames)}"
            
            username = variant_name.lower().replace(' ', '.').replace('é', 'e').replace('è', 'e')
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            email_variant = f"{username}.{random_suffix}@{domain}"
            
            persona_key = self.create_variant(
                base_persona_key,
                variant_name=variant_name,
                email_suffix=email_variant
            )
            created_keys.append(persona_key)
        
        return created_keys
    
    def test_persona(self, persona_key: str) -> Dict:
        """Teste un persona (vérifie la validité des données)."""
        persona = self.get_persona(persona_key)
        if not persona:
            return {"valid": False, "errors": ["Persona non trouvé"]}
        
        errors = []
        warnings = []
        
        # Vérifications
        if not persona.get('name'):
            errors.append("Le nom est requis")
        
        if not persona.get('email'):
            errors.append("L'email est requis")
        elif '@' not in persona['email']:
            errors.append("L'email n'est pas valide")
        
        if persona.get('alias') and not persona.get('parent'):
            warnings.append("Persona alias sans parent défini")
        
        if not persona.get('password') and not persona.get('alias'):
            warnings.append("Pas de mot de passe défini (OK si alias)")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "persona": persona
        }
    
    def get_all_personas(self) -> Dict:
        """Récupère tous les personas."""
        return self.personas
    
    def get_base_personas(self) -> Dict:
        """Récupère uniquement les personas de base (non alias)."""
        return {k: v for k, v in self.personas.items() if not v.get('alias', False)}
    
    def get_variants_of(self, base_email: str) -> Dict:
        """Récupère toutes les variantes d'un persona de base."""
        return {k: v for k, v in self.personas.items() 
                if v.get('parent') == base_email or v.get('email') == base_email}
    
    def duplicate_persona(self, persona_key: str, new_name: Optional[str] = None,
                          new_email: Optional[str] = None) -> str:
        """Duplique un persona avec de nouvelles données."""
        persona = self.get_persona(persona_key)
        if not persona:
            raise ValueError(f"Persona '{persona_key}' non trouvé")
        
        new_persona = persona.copy()
        if new_name:
            new_persona['name'] = new_name
        if new_email:
            new_persona['email'] = new_email
            new_persona['alias'] = False
            new_persona['parent'] = None
        
        return self.create_persona(
            name=new_persona['name'],
            email=new_persona['email'],
            password=new_persona.get('password', ''),
            alias=new_persona.get('alias', False),
            parent=new_persona.get('parent'),
            custom_data={k: v for k, v in new_persona.items() 
                        if k not in ['name', 'email', 'password', 'alias', 'parent']}
        )

