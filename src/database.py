import sqlite3
import os
from datetime import datetime

def get_db_path():
    """Retourne le chemin de la base de données."""
    db_dir = 'data'
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, 'jobs.db')

def create_database():
    """Crée la base de données avec les tables nécessaires."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Table des offres d'emploi
    c.execute('''CREATE TABLE IF NOT EXISTS jobs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  company TEXT,
                  location TEXT,
                  url TEXT,
                  description TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  UNIQUE(title, company, location))''')
    
    # Table des candidatures (avec persona)
    c.execute('''CREATE TABLE IF NOT EXISTS applications
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  job_id INTEGER,
                  persona_email TEXT,
                  persona_name TEXT,
                  cv_path TEXT,
                  cover_letter TEXT,
                  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  status TEXT DEFAULT 'pending',
                  FOREIGN KEY (job_id) REFERENCES jobs(id),
                  UNIQUE(job_id, persona_email))''')
    
    # Table des emails reçus par les personas
    c.execute('''CREATE TABLE IF NOT EXISTS persona_emails
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  persona_email TEXT,
                  sender TEXT,
                  subject TEXT,
                  body TEXT,
                  received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  is_read INTEGER DEFAULT 0,
                  email_type TEXT DEFAULT 'application')''')
    
    conn.commit()
    conn.close()

def insert_job(job):
    """Insère une offre d'emploi dans la base de données."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    try:
        c.execute("""INSERT OR IGNORE INTO jobs 
                     (title, company, location, url, description) 
                     VALUES (?, ?, ?, ?, ?)""",
                  (job.get('title'), job.get('company'), job.get('location'), 
                   job.get('url', ''), job.get('description', '')))
        conn.commit()
        return c.lastrowid
    except Exception as e:
        print(f"Erreur lors de l'insertion de l'offre: {e}")
        return None
    finally:
        conn.close()

def get_unapplied_jobs(persona_email=None):
    """Récupère les offres non candidatées pour un persona donné."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    if persona_email:
        # Offres non candidatées par ce persona spécifique
        query = """SELECT j.* FROM jobs j
                   LEFT JOIN applications a ON j.id = a.job_id AND a.persona_email = ?
                   WHERE a.id IS NULL"""
        c.execute(query, (persona_email,))
    else:
        # Toutes les offres non candidatées
        query = """SELECT j.* FROM jobs j
                   LEFT JOIN applications a ON j.id = a.job_id
                   WHERE a.id IS NULL"""
        c.execute(query)
    
    jobs = []
    for row in c.fetchall():
        jobs.append({
            'id': row[0],
            'title': row[1],
            'company': row[2],
            'location': row[3],
            'url': row[4],
            'description': row[5],
            'created_at': row[6]
        })
    
    conn.close()
    return jobs

def insert_application(job_id, persona_email, persona_name, cv_path, cover_letter=None, status='pending'):
    """Enregistre une candidature."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    try:
        c.execute("""INSERT OR REPLACE INTO applications 
                     (job_id, persona_email, persona_name, cv_path, cover_letter, status) 
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (job_id, persona_email, persona_name, cv_path, cover_letter, status))
        conn.commit()
        return c.lastrowid
    except Exception as e:
        print(f"Erreur lors de l'enregistrement de la candidature: {e}")
        return None
    finally:
        conn.close()

def update_application_status(job_id, persona_email, status):
    """Met à jour le statut d'une candidature."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("""UPDATE applications 
                 SET status = ? 
                 WHERE job_id = ? AND persona_email = ?""",
              (status, job_id, persona_email))
    conn.commit()
    conn.close()
