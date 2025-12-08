# Configuration d'exemple pour Auto Apply
# Copiez ce fichier en config.py et personnalisez-le selon vos besoins

# Configuration de la recherche d'emploi
SEARCH_CONFIG = {
    "query": "développeur python",
    "location": "Rennes",
    "max_results": 50,
    "title_keywords": ["Python", "Développeur", "Developer", "Backend", "Full Stack"],
    "location_keywords": ["Rennes", "Bretagne", "Remote", "Télétravail", "France"],
    "exclude_keywords": ["Senior", "Lead", "Manager", "Architecte"],  # Mots-clés à exclure
}

# Configuration des candidatures
APPLICATION_CONFIG = {
    "max_applications_per_persona": 3,  # Nombre maximum de candidatures par persona
    "delay_between_applications": (5, 10),  # Délai aléatoire entre candidatures (secondes)
    "headless": False,  # Mode headless pour le navigateur
    "timeout": 30,  # Timeout pour les opérations Selenium (secondes)
}

# Configuration des CVs
CV_CONFIG = {
    "template_file": "templates/cv/cv_template.html",
    "output_dir": "cvs",
    "cvs_file": "config/cvs.json",
}

# Configuration des personas
PERSONAS_CONFIG = {
    "personas_file": "config/personas.json",
}

# Configuration de la base de données
DATABASE_CONFIG = {
    "database_file": "jobs.db",
}

# Configuration du serveur web (optionnel)
SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": True,
}

