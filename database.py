import sqlite3

def create_database():
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs
                 (id INTEGER PRIMARY KEY,
                  title TEXT,
                  company TEXT,
                  location TEXT,
                  applied INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def insert_job(job):
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute("INSERT INTO jobs (title, company, location) VALUES (?, ?, ?)",
              (job['title'], job['company'], job['location']))
    conn.commit()
    conn.close()
