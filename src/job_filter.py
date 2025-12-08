import sqlite3
from .database import get_unapplied_jobs

def filter_jobs(title_keywords=None, location_keywords=None, persona_email=None, exclude_keywords=None):
    """
    Filtre les offres d'emploi dans la base de données en fonction des mots-clés.
    :param title_keywords: Liste de mots-clés pour filtrer par titre.
    :param location_keywords: Liste de mots-clés pour filtrer par lieu.
    :param persona_email: Email du persona pour exclure les offres déjà candidatées.
    :param exclude_keywords: Liste de mots-clés à exclure.
    :return: Liste des offres filtrées.
    """
    # Récupérer les offres non candidatées pour ce persona
    jobs = get_unapplied_jobs(persona_email)
    filtered_jobs = []
    
    for job in jobs:
        # Filtre par mots-clés dans le titre
        if title_keywords:
            title_match = any(keyword.lower() in job['title'].lower() for keyword in title_keywords)
            if not title_match:
                continue
        
        # Filtre par mots-clés dans la localisation
        if location_keywords:
            location_match = any(keyword.lower() in job['location'].lower() for keyword in location_keywords)
            if not location_match:
                continue
        
        # Exclusion par mots-clés
        if exclude_keywords:
            excluded = any(keyword.lower() in job['title'].lower() or 
                          keyword.lower() in job.get('description', '').lower() 
                          for keyword in exclude_keywords)
            if excluded:
                continue
        
        filtered_jobs.append(job)
    
    return filtered_jobs
