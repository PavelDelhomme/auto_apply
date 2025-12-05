from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
from cv_generator import generate_cvs_from_json, generate_cv_for_persona
from scraper import scrape_indeed
from auto_apply import apply_to_job
from job_filter import filter_jobs
from database import create_database, insert_job, get_unapplied_jobs
from stats import get_statistics
from application_generator import generate_cover_letter

app = Flask(__name__)

# Initialiser la base de données au démarrage
create_database()

def load_personas():
    """Charge les personas depuis le fichier JSON."""
    with open('personas.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def load_cvs():
    """Charge les CVs depuis le fichier JSON."""
    with open('cvs.json', 'r', encoding='utf-8') as file:
        return json.load(file)

# Route pour la page d'accueil
@app.route('/')
def index():
    stats = get_statistics()
    return render_template('index.html', stats=stats)

# Route pour afficher les personas
@app.route('/personas')
def personas():
    personas_data = load_personas()
    personas_list = [{'key': k, **v} for k, v in personas_data.items()]
    return render_template('personas.html', personas=personas_list)

# Route pour générer un CV
@app.route('/generate_cv', methods=['POST'])
def generate_cv_route():
    persona_email = request.form.get('persona_email')
    persona_name = request.form.get('persona_name')
    
    if not persona_email or not persona_name:
        return jsonify({'error': 'Email et nom du persona requis'}), 400
    
    cvs_data = load_cvs()
    # Utiliser le premier CV disponible (vous pouvez améliorer cette logique)
    cv_data = list(cvs_data.values())[0]
    
    cv_path = generate_cv_for_persona(
        persona_email=persona_email,
        persona_name=persona_name,
        cv_data=cv_data
    )
    
    if cv_path:
        return jsonify({'success': True, 'cv_path': cv_path})
    else:
        return jsonify({'error': 'Erreur lors de la génération du CV'}), 500

# Route pour générer tous les CVs
@app.route('/generate_all_cvs', methods=['POST'])
def generate_all_cvs_route():
    try:
        cv_paths = generate_cvs_from_json()
        return jsonify({'success': True, 'count': len(cv_paths), 'cvs': cv_paths})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route pour la recherche d'offres d'emploi
@app.route('/search_jobs', methods=['POST'])
def search_jobs():
    query = request.form.get('query', '')
    location = request.form.get('location', '')
    
    if not query or not location:
        return jsonify({'error': 'Query et location requis'}), 400
    
    try:
        jobs = scrape_indeed(query, location)
        
        # Insérer les offres dans la base de données
        for job in jobs:
            insert_job(job)
        
        return render_template('jobs.html', jobs=jobs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route API pour récupérer les offres
@app.route('/api/jobs')
def api_jobs():
    persona_email = request.args.get('persona_email')
    jobs = get_unapplied_jobs(persona_email)
    return jsonify(jobs)

# Route pour postuler à une offre
@app.route('/apply_job', methods=['POST'])
def apply_job():
    job_id = request.form.get('job_id')
    persona_email = request.form.get('persona_email')
    persona_name = request.form.get('persona_name')
    
    if not all([job_id, persona_email, persona_name]):
        return jsonify({'error': 'Données incomplètes'}), 400
    
    # Récupérer l'offre depuis la base de données
    jobs = get_unapplied_jobs(persona_email)
    job = next((j for j in jobs if j['id'] == int(job_id)), None)
    
    if not job:
        return jsonify({'error': 'Offre non trouvée ou déjà candidatée'}), 404
    
    # Récupérer le CV approprié pour la persona
    import os
    safe_email = persona_email.replace('@', '_at_').replace('.', '_')
    cv_path = os.path.join('cvs', f"{safe_email}_cv.pdf")
    
    if not os.path.exists(cv_path):
        return jsonify({'error': 'CV non trouvé. Veuillez générer le CV d\'abord.'}), 404
    
    # Générer la lettre de motivation
    try:
        cover_letter = generate_cover_letter(job)
    except Exception as e:
        cover_letter = None
    
    # Appliquer automatiquement
    try:
        success = apply_to_job(
            job=job,
            persona_email=persona_email,
            persona_name=persona_name,
            cv_path=cv_path,
            cover_letter=cover_letter,
            headless=False
        )
        
        if success:
            from database import insert_application, update_application_status
            insert_application(
                job_id=job['id'],
                persona_email=persona_email,
                persona_name=persona_name,
                cv_path=cv_path,
                cover_letter=cover_letter,
                status='sent'
            )
            return jsonify({'success': True, 'message': 'Candidature envoyée avec succès'})
        else:
            from database import insert_application
            insert_application(
                job_id=job['id'],
                persona_email=persona_email,
                persona_name=persona_name,
                cv_path=cv_path,
                cover_letter=cover_letter,
                status='failed'
            )
            return jsonify({'error': 'Échec de la candidature'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route pour afficher les statistiques
@app.route('/stats')
def stats_route():
    stats = get_statistics()
    return render_template('stats.html', stats=stats)

# Route API pour les statistiques
@app.route('/api/stats')
def api_stats():
    return jsonify(get_statistics())

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
