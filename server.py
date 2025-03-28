from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import json
from cv_generator import generate_cv
from scraper import scrape_indeed
from auto_apply import apply_to_job
from job_filter import filter_jobs

app = Flask(__name__)

# Route pour la page d'accueil
@app.route('/')
def index():
    return render_template('index.html')

# Route pour afficher les personas
@app.route('/personas')
def personas():
    with open('data.json', 'r') as file:
        data = json.load(file)
    
    personas = list(data.values())
    return render_template('personas.html', personas=personas)

# Route pour générer un CV
@app.route('/generate_cv', methods=['POST'])
def generate_cv_route():
    persona_name = request.form['persona_name']
    generate_cv(data_file="data.json", template_file="cv_template.html", output_file=f"{persona_name}_cv.pdf")
    return redirect(url_for('index'))

# Route pour la recherche d'offres d'emploi
@app.route('/search_jobs', methods=['POST'])
def search_jobs():
    query = request.form['query']
    location = request.form['location']
    jobs = scrape_indeed(query, location)
    
    # INsérer les offres dans la base de données
    for job in jobs:
        insert_job(job)
    
    return render_template('jobs.html', jobs=jobs)

# Route pour postuler à une offre
@app.route('/apply_job', methods=['POST'])
def apply_job():
    job_title = request.form['job_title']
    persona_email = request.form['persona_email']

    # Récupérer le CV approprié pour la persona
    cv_path = f"{persona_email}_cv.pdf"

    # Appliquer automatiquement
    filtered_jobs = filter_jobs(title_keywords=[job_title], location_keywords=[])
    for job in filtered_jobs:
        apply_to_job(job, cv_path=cv_path, cover_letter=None)
    
    return redirect(url_for('index'))

# Route pour afficher les statistiques
@app.route('/stats')
def stats():
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    total_jobs = c.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    applied_jobs = c.execute("SELECT COUNT(*) FROM jobs WHERE applied = 1").fetchone()[0]
    conn.close()

    return render_template('stats.html', total_jobs=total_jobs, applied_jobs=applied_jobs)

if __name__ == "__main__":
    app.run(debug=True)
