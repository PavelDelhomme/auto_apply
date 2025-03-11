import sqlite3

def get_statistics():
    """
    Génère des statistiques sur les candidatures.
    :return: Dictionnaire contenant les statistiques.
    """
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    
    total_jobs = c.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    applied_jobs = c.execute("SELECT COUNT(*) FROM jobs WHERE applied = 1").fetchone()[0]
    
    conn.close()
    
    return {
        "total_jobs": total_jobs,
        "applied_jobs": applied_jobs,
        "remaining_jobs": total_jobs - applied_jobs
    }

if __name__ == "__main__":
    stats = get_statistics()
    print(f"Total d'offres trouvées : {stats['total_jobs']}")
    print(f"Nombre de candidatures envoyées : {stats['applied_jobs']}")
    print(f"Offres restantes à postuler : {stats['remaining_jobs']}")
