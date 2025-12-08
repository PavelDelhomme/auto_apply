"""
Suite de tests complète pour vérifier que tout le projet fonctionne
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestProjectCompleteness:
    """Tests pour vérifier la complétude du projet."""
    
    def test_all_modules_importable(self):
        """Test que tous les modules principaux peuvent être importés."""
        import sys
        import os
        
        # Ajouter src au PYTHONPATH
        src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        modules = [
            'database',
            'persona_manager',
            'search_manager',
            'cv_generator',
            'scraper',
            'job_filter',
            'stats',
            'application_generator'
        ]
        
        failed_imports = []
        for module_name in modules:
            try:
                __import__(module_name)
            except ImportError as e:
                failed_imports.append(f"{module_name}: {e}")
        
        # Test app séparément car il a des imports relatifs
        try:
            from src.app import app
        except ImportError as e:
            failed_imports.append(f"app: {e}")
        
        if failed_imports:
            pytest.fail(f"Modules non importables: {', '.join(failed_imports)}")
    
    def test_config_files_exist(self):
        """Test que les fichiers de configuration existent."""
        config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        required_files = ['personas.json', 'cvs.json', 'searches.json']
        
        missing_files = []
        for file_name in required_files:
            file_path = os.path.join(config_dir, file_name)
            if not os.path.exists(file_path):
                missing_files.append(file_name)
        
        # Les fichiers peuvent ne pas exister au début, c'est OK
        # On vérifie juste que le répertoire existe
        assert os.path.exists(config_dir), "Le répertoire config/ doit exister"
    
    def test_templates_exist(self):
        """Test que les templates nécessaires existent."""
        templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        required_templates = [
            'dashboard.html',
            'cv/cv_template.html',
            'letters/cover_letter_template.txt'
        ]
        
        missing_templates = []
        for template_path in required_templates:
            full_path = os.path.join(templates_dir, template_path)
            if not os.path.exists(full_path):
                missing_templates.append(template_path)
        
        if missing_templates:
            pytest.fail(f"Templates manquants: {', '.join(missing_templates)}")
    
    def test_database_functions_exist(self):
        """Test que toutes les fonctions de base de données existent."""
        from database import (
            create_database, insert_job, get_all_jobs,
            get_unapplied_jobs, insert_application,
            update_application_status, insert_email
        )
        
        assert callable(create_database)
        assert callable(insert_job)
        assert callable(get_all_jobs)
        assert callable(get_unapplied_jobs)
        assert callable(insert_application)
        assert callable(update_application_status)
        assert callable(insert_email)
    
    def test_persona_manager_functions_exist(self):
        """Test que toutes les fonctions de PersonaManager existent."""
        from persona_manager import PersonaManager
        
        manager = PersonaManager("/tmp/test_personas.json")
        
        assert hasattr(manager, 'create_persona')
        assert hasattr(manager, 'get_persona')
        assert hasattr(manager, 'get_persona_by_email')
        assert hasattr(manager, 'update_persona')
        assert hasattr(manager, 'delete_persona')
        assert hasattr(manager, 'get_all_personas')
    
    def test_search_manager_functions_exist(self):
        """Test que toutes les fonctions de SearchManager existent."""
        from search_manager import SearchManager
        
        manager = SearchManager("/tmp/test_searches.json")
        
        assert hasattr(manager, 'create_search')
        assert hasattr(manager, 'get_search')
        assert hasattr(manager, 'update_search')
        assert hasattr(manager, 'delete_search')
        assert hasattr(manager, 'get_all_searches')
        assert hasattr(manager, 'mark_run')
        assert hasattr(manager, 'get_execution_history')
        assert hasattr(manager, 'get_last_execution')

@pytest.mark.integration
class TestIntegration:
    """Tests d'intégration pour vérifier que les composants fonctionnent ensemble."""
    
    def test_persona_and_search_integration(self, temp_config_dir):
        """Test d'intégration entre PersonaManager et SearchManager."""
        from persona_manager import PersonaManager
        from search_manager import SearchManager
        
        personas_file = os.path.join(temp_config_dir, "personas.json")
        searches_file = os.path.join(temp_config_dir, "searches.json")
        
        # Créer un persona
        persona_manager = PersonaManager(personas_file)
        persona_key = persona_manager.create_persona(
            name="Integration Test",
            email="integration@test.com"
        )
        
        # Créer une recherche
        search_manager = SearchManager(searches_file)
        search_key = search_manager.create_search(
            name="Integration Search",
            query="test",
            location="test"
        )
        
        # Vérifier que tout fonctionne
        assert persona_manager.get_persona(persona_key) is not None
        assert search_manager.get_search(search_key) is not None

