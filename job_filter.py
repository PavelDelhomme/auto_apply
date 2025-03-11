import sqlite3

def filter_jobs(title_keywords=None, location_keywords=None):
    """
    Filtre les offres d'emploi dans la base de données en fonction des mots-clés.
    :param title_keywords: Liste de mots-clés pour filtrer par titre.
    :param location_keywords: Liste de mots-clés pour filtrer par lieu.
    :return: Liste des offres filtrées.
    """
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    
    query = "SELECT * FROM jobs WHERE applied = 0"
    conditions = []
    
    if title_keywords:
        conditions.append("(" + " OR ".join([f"title LIKE '%{keyword}%'" for keyword in title_keywords]) + ")")
    if location_keywords:
        conditions.append("(" + " OR ".join([f"location LIKE '%{keyword}%'" for keyword in location_keywords]) + ")")
    
    if conditions:
        query += " AND " + " AND ".join(conditions)
    
    c.execute(query)
    filtered_jobs = c.fetchall()
    conn.close()
    
    return filtered_jobs
