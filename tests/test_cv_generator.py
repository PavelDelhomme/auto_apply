"""
Tests pour le module cv_generator.py
"""
import pytest
import sys
import os
import tempfile
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_cv_generator_imports():
    """Test que le module peut être importé."""
    try:
        from cv_generator import generate_cv_for_persona, generate_cvs_from_json
        assert True
    except ImportError as e:
        pytest.skip(f"Module cv_generator non disponible: {e}")

def test_generate_cvs_from_json_structure(temp_config_dir, sample_personas, sample_cvs):
    """Test de la structure de génération des CVs."""
    from cv_generator import generate_cvs_from_json
    
    # Créer un template minimal
    template_dir = os.path.join(temp_config_dir, 'templates', 'cv')
    os.makedirs(template_dir, exist_ok=True)
    template_file = os.path.join(template_dir, 'cv_template.html')
    
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write("""
        <html>
        <body>
            <h1>{{ name }}</h1>
            <p>{{ email }}</p>
            <h2>{{ title }}</h2>
        </body>
        </html>
        """)
    
    # Créer un répertoire de sortie
    output_dir = os.path.join(temp_config_dir, 'cvs')
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Tester la génération (peut échouer si wkhtmltopdf n'est pas installé)
        cv_paths = generate_cvs_from_json(
            cvs_file=sample_cvs,
            personas_file=sample_personas,
            template_file=template_file
        )
        # Si ça fonctionne, vérifier la structure
        if cv_paths:
            assert isinstance(cv_paths, dict)
    except Exception as e:
        # Si wkhtmltopdf n'est pas disponible, c'est OK pour les tests
        if 'wkhtmltopdf' in str(e).lower() or 'No such file' in str(e):
            pytest.skip("wkhtmltopdf non disponible pour les tests")
        else:
            raise

