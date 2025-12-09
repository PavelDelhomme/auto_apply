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
                  is_test_data INTEGER DEFAULT 0,
                  UNIQUE(title, company, location))''')
    
    # Table des candidatures (avec persona)
    c.execute('''CREATE TABLE IF NOT EXISTS applications
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  job_id INTEGER,
                  persona_email TEXT,
                  persona_name TEXT,
                  cv_path TEXT,
                  cv_id TEXT,
                  search_key TEXT,
                  cover_letter TEXT,
                  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  status TEXT DEFAULT 'pending',
                  is_test_data INTEGER DEFAULT 0,
                  FOREIGN KEY (job_id) REFERENCES jobs(id),
                  UNIQUE(job_id, persona_email))''')
    
    # Table des CVs par persona et recherche
    c.execute('''CREATE TABLE IF NOT EXISTS persona_cvs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  persona_email TEXT,
                  search_key TEXT,
                  cv_id TEXT,
                  cv_path TEXT,
                  cv_data TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  is_default INTEGER DEFAULT 0,
                  UNIQUE(persona_email, search_key, cv_id))''')
    
    # Table pour l'historique des recherches d'offres
    c.execute('''CREATE TABLE IF NOT EXISTS job_searches
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  query TEXT NOT NULL,
                  location TEXT NOT NULL,
                  max_results INTEGER DEFAULT 50,
                  jobs_found INTEGER DEFAULT 0,
                  platform TEXT DEFAULT 'indeed',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  is_test_data INTEGER DEFAULT 0)''')
    
    # Table des emails reçus par les personas
    c.execute('''CREATE TABLE IF NOT EXISTS persona_emails
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  persona_email TEXT,
                  sender TEXT,
                  subject TEXT,
                  body TEXT,
                  received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  is_read INTEGER DEFAULT 0,
                  email_type TEXT DEFAULT 'application',
                  is_test_data INTEGER DEFAULT 0)''')
    
    # Table des logs
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  level TEXT,
                  message TEXT,
                  category TEXT DEFAULT 'general',
                  is_test_data INTEGER DEFAULT 0)''')
    
    # Table des statistiques historiques
    c.execute('''CREATE TABLE IF NOT EXISTS historical_stats
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date DATE DEFAULT CURRENT_DATE,
                  hour INTEGER DEFAULT (CAST(strftime('%H', 'now') AS INTEGER)),
                  total_jobs INTEGER DEFAULT 0,
                  total_applications INTEGER DEFAULT 0,
                  sent_applications INTEGER DEFAULT 0,
                  failed_applications INTEGER DEFAULT 0,
                  searches_run INTEGER DEFAULT 0,
                  personas_used INTEGER DEFAULT 0,
                  is_test_data INTEGER DEFAULT 0,
                  UNIQUE(date, hour))''')
    
    # Ajouter la colonne is_test_data aux tables existantes si elle n'existe pas
    try:
        c.execute('ALTER TABLE jobs ADD COLUMN is_test_data INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # La colonne existe déjà
    
    try:
        c.execute('ALTER TABLE applications ADD COLUMN is_test_data INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # La colonne existe déjà
    
    try:
        c.execute('ALTER TABLE persona_emails ADD COLUMN is_test_data INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # La colonne existe déjà
    
    conn.commit()
    conn.close()

def insert_job(job, is_test_data=False):
    """Insère une offre d'emploi dans la base de données."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    try:
        c.execute("""INSERT OR IGNORE INTO jobs 
                     (title, company, location, url, description, is_test_data) 
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (job.get('title'), job.get('company'), job.get('location'), 
                   job.get('url', ''), job.get('description', ''), 1 if is_test_data else 0))
        conn.commit()
        return c.lastrowid
    except Exception as e:
        print(f"Erreur lors de l'insertion de l'offre: {e}")
        return None
    finally:
        conn.close()

def insert_job_search(query, location, max_results=50, jobs_found=0, platform='indeed', is_test_data=False):
    """Enregistre une recherche d'offres dans l'historique."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('''INSERT INTO job_searches (query, location, max_results, jobs_found, platform, is_test_data)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (query, location, max_results, jobs_found, platform, 1 if is_test_data else 0))
    conn.commit()
    search_id = c.lastrowid
    conn.close()
    return search_id

def get_job_searches(limit=50, offset=0):
    """Récupère l'historique des recherches d'offres."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('''SELECT id, query, location, max_results, jobs_found, platform, created_at, is_test_data
                 FROM job_searches
                 ORDER BY created_at DESC
                 LIMIT ? OFFSET ?''', (limit, offset))
    
    searches = []
    for row in c.fetchall():
        searches.append({
            'id': row[0],
            'query': row[1],
            'location': row[2],
            'max_results': row[3],
            'jobs_found': row[4],
            'platform': row[5],
            'created_at': row[6],
            'is_test_data': bool(row[7])
        })
    
    conn.close()
    return searches

def get_job_search_count():
    """Retourne le nombre total de recherches enregistrées."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM job_searches')
    count = c.fetchone()[0]
    conn.close()
    return count

def get_all_jobs(limit=None, order_by='created_at DESC', exclude_test=False):
    """Récupère toutes les offres d'emploi."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    query = "SELECT j.* FROM jobs j"
    if exclude_test:
        query += " WHERE is_test_data = 0"
    query += f" ORDER BY {order_by}"
    if limit:
        query += f" LIMIT {limit}"
    
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
            'created_at': row[6],
            'is_test_data': row[7] if len(row) > 7 else 0
        })
    
    conn.close()
    return jobs

def get_unapplied_jobs(persona_email=None, exclude_test=False):
    """Récupère les offres non candidatées pour un persona donné."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    if persona_email:
        query = """SELECT j.* FROM jobs j
                   WHERE j.id NOT IN (
                       SELECT job_id FROM applications 
                       WHERE persona_email = ? AND is_test_data = 0
                   )"""
        if exclude_test:
            query += " AND j.is_test_data = 0"
        query += " ORDER BY j.created_at DESC"
        c.execute(query, (persona_email,))
    else:
        query = """SELECT j.* FROM jobs j
                   WHERE j.id NOT IN (SELECT DISTINCT job_id FROM applications WHERE is_test_data = 0)"""
        if exclude_test:
            query += " AND j.is_test_data = 0"
        query += " ORDER BY j.created_at DESC"
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
            'created_at': row[6],
            'is_test_data': row[7] if len(row) > 7 else 0
        })
    
    conn.close()
    return jobs

def insert_application(job_id, persona_email, persona_name, cv_path, cover_letter, status='pending', is_test_data=False, cv_id=None, search_key=None):
    """Insère une candidature dans la base de données."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    try:
        c.execute("""INSERT OR IGNORE INTO applications 
                     (job_id, persona_email, persona_name, cv_path, cv_id, search_key, cover_letter, status, is_test_data) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (job_id, persona_email, persona_name, cv_path, cv_id, search_key, cover_letter, status, 1 if is_test_data else 0))
        conn.commit()
        return c.lastrowid
    except Exception as e:
        print(f"Erreur lors de l'insertion de la candidature: {e}")
        return None
    finally:
        conn.close()

def update_application_status(application_id, status):
    """Met à jour le statut d'une candidature."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    try:
        c.execute("UPDATE applications SET status = ? WHERE id = ?", (status, application_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur lors de la mise à jour du statut: {e}")
        return False
    finally:
        conn.close()

def insert_email(persona_email, sender, subject, body, email_type='application', is_test_data=False):
    """Insère un email dans la base de données."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO persona_emails 
                     (persona_email, sender, subject, body, email_type, is_test_data) 
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (persona_email, sender, subject, body, email_type, 1 if is_test_data else 0))
        conn.commit()
        return c.lastrowid
    except Exception as e:
        print(f"Erreur lors de l'insertion de l'email: {e}")
        return None
    finally:
        conn.close()

def get_persona_emails(persona_email, limit=100):
    """Récupère les emails d'un persona."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    c.execute("""SELECT id, sender, subject, body, received_at, is_read, email_type, is_test_data
                 FROM persona_emails
                 WHERE persona_email = ?
                 ORDER BY received_at DESC
                 LIMIT ?""", (persona_email, limit))
    
    emails = []
    for row in c.fetchall():
        emails.append({
            'id': row[0],
            'sender': row[1],
            'subject': row[2],
            'body': row[3],
            'received_at': row[4],
            'is_read': bool(row[5]),
            'email_type': row[6],
            'is_test_data': row[7] if len(row) > 7 else 0
        })
    
    conn.close()
    return emails

def save_persona_cv(persona_email, cv_id, cv_path, cv_data, search_key=None, is_default=False):
    """Sauvegarde un CV pour un persona (optionnellement lié à une recherche)."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    try:
        import json
        cv_data_json = json.dumps(cv_data) if isinstance(cv_data, dict) else cv_data
        
        c.execute("""INSERT OR REPLACE INTO persona_cvs 
                     (persona_email, search_key, cv_id, cv_path, cv_data, is_default) 
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (persona_email, search_key, cv_id, cv_path, cv_data_json, 1 if is_default else 0))
        conn.commit()
        return c.lastrowid
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du CV: {e}")
        return None
    finally:
        conn.close()

def get_persona_cv(persona_email, search_key=None, cv_id=None, is_default=False):
    """Récupère un CV pour un persona."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    query = "SELECT cv_id, cv_path, cv_data, search_key, is_default FROM persona_cvs WHERE persona_email = ?"
    params = [persona_email]
    
    if search_key:
        query += " AND search_key = ?"
        params.append(search_key)
    elif cv_id:
        query += " AND cv_id = ?"
        params.append(cv_id)
    elif is_default:
        query += " AND is_default = 1"
    
    query += " ORDER BY is_default DESC, created_at DESC LIMIT 1"
    
    c.execute(query, params)
    row = c.fetchone()
    conn.close()
    
    if row:
        import json
        return {
            'cv_id': row[0],
            'cv_path': row[1],
            'cv_data': json.loads(row[2]) if row[2] else {},
            'search_key': row[3],
            'is_default': bool(row[4])
        }
    return None

def get_all_persona_cvs(persona_email):
    """Récupère tous les CVs d'un persona."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    c.execute("""SELECT cv_id, cv_path, cv_data, search_key, is_default, created_at 
                 FROM persona_cvs 
                 WHERE persona_email = ? 
                 ORDER BY is_default DESC, created_at DESC""", (persona_email,))
    
    cvs = []
    for row in c.fetchall():
        import json
        cvs.append({
            'cv_id': row[0],
            'cv_path': row[1],
            'cv_data': json.loads(row[2]) if row[2] else {},
            'search_key': row[3],
            'is_default': bool(row[4]),
            'created_at': row[5]
        })
    
    conn.close()
    return cvs

def insert_log(message, level='info', category='general', is_test_data=False):
    """Insère un log dans la base de données."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO logs (message, level, category, is_test_data) 
                     VALUES (?, ?, ?, ?)""",
                  (message, level, category, 1 if is_test_data else 0))
        conn.commit()
        return c.lastrowid
    except Exception as e:
        print(f"Erreur lors de l'insertion du log: {e}")
        return None
    finally:
        conn.close()

def get_logs(limit=1000, level=None, category=None, exclude_test=False):
    """Récupère les logs depuis la base de données."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    query = "SELECT id, timestamp, level, message, category, is_test_data FROM logs"
    conditions = []
    params = []
    
    if exclude_test:
        conditions.append("is_test_data = 0")
    
    if level:
        conditions.append("level = ?")
        params.append(level)
    
    if category:
        conditions.append("category = ?")
        params.append(category)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    
    c.execute(query, params)
    
    logs = []
    for row in c.fetchall():
        logs.append({
            'id': row[0],
            'timestamp': row[1],
            'level': row[2],
            'message': row[3],
            'category': row[4],
            'is_test_data': row[5] if len(row) > 5 else 0
        })
    
    conn.close()
    return logs

def insert_historical_stat(stats, is_test_data=False):
    """Insère ou met à jour une statistique historique."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    try:
        from datetime import datetime
        now = datetime.now()
        date = now.strftime('%Y-%m-%d')
        hour = now.hour
        
        c.execute("""INSERT OR REPLACE INTO historical_stats 
                     (date, hour, total_jobs, total_applications, sent_applications, 
                      failed_applications, searches_run, personas_used, is_test_data)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (date, hour,
                   stats.get('total_jobs', 0),
                   stats.get('total_applications', 0),
                   stats.get('sent_applications', 0),
                   stats.get('failed_applications', 0),
                   stats.get('searches_run', 0),
                   stats.get('personas_used', 0),
                   1 if is_test_data else 0))
        conn.commit()
        return c.lastrowid
    except Exception as e:
        print(f"Erreur lors de l'insertion de la statistique: {e}")
        return None
    finally:
        conn.close()

def get_historical_stats(days=30, exclude_test=False):
    """Récupère les statistiques historiques."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    query = """SELECT date, hour, total_jobs, total_applications, sent_applications, 
                      failed_applications, searches_run, personas_used
               FROM historical_stats
               WHERE date >= date('now', '-' || ? || ' days')"""
    
    if exclude_test:
        query += " AND is_test_data = 0"
    
    query += " ORDER BY date DESC, hour DESC"
    
    c.execute(query, (days,))
    
    stats = []
    for row in c.fetchall():
        stats.append({
            'date': row[0],
            'hour': row[1],
            'total_jobs': row[2],
            'total_applications': row[3],
            'sent_applications': row[4],
            'failed_applications': row[5],
            'searches_run': row[6],
            'personas_used': row[7]
        })
    
    conn.close()
    return stats

def delete_test_data():
    """Supprime toutes les données marquées comme test."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    try:
        c.execute("DELETE FROM jobs WHERE is_test_data = 1")
        jobs_deleted = c.rowcount
        c.execute("DELETE FROM applications WHERE is_test_data = 1")
        apps_deleted = c.rowcount
        c.execute("DELETE FROM persona_emails WHERE is_test_data = 1")
        emails_deleted = c.rowcount
        c.execute("DELETE FROM logs WHERE is_test_data = 1")
        logs_deleted = c.rowcount
        c.execute("DELETE FROM historical_stats WHERE is_test_data = 1")
        stats_deleted = c.rowcount
        
        conn.commit()
        return {
            'jobs': jobs_deleted,
            'applications': apps_deleted,
            'emails': emails_deleted,
            'logs': logs_deleted,
            'stats': stats_deleted
        }
    except Exception as e:
        print(f"Erreur lors de la suppression des données de test: {e}")
        return None
    finally:
        conn.close()

def mark_as_test_data(table, ids, is_test=True):
    """Marque des données comme test ou non."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    try:
        if not ids:
            return 0
        
        placeholders = ','.join(['?'] * len(ids))
        query = f"UPDATE {table} SET is_test_data = ? WHERE id IN ({placeholders})"
        c.execute(query, [1 if is_test else 0] + ids)
        conn.commit()
        return c.rowcount
    except Exception as e:
        print(f"Erreur lors du marquage des données: {e}")
        return 0
    finally:
        conn.close()
