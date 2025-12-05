from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import threading
import time
import random
from datetime import datetime
from .cv_generator import generate_cvs_from_json, generate_cv_for_persona
from .scraper import scrape_indeed
from .auto_apply import apply_to_job
from .job_filter import filter_jobs
from .database import create_database, insert_job, get_unapplied_jobs, insert_application, update_application_status, get_db_path
from .stats import get_statistics
from .application_generator import generate_cover_letter
from .persona_manager import PersonaManager
from .search_manager import SearchManager
import os

app = Flask(__name__, template_folder='/app/templates')
app.config['SECRET_KEY'] = 'auto-apply-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# État global pour le suivi en temps réel
app_state = {
    'is_running': False,
    'current_step': 'ready',  # 'ready' au lieu de '' pour indiquer que le système est prêt
    'logs': [],
    'stats': {},
    'jobs_found': 0,
    'applications_sent': 0,
    'applications_failed': 0,
    'container_status': 'running'  # Statut du conteneur
}

# Initialiser l'état au chargement du module - FORCER l'initialisation
app_state['current_step'] = 'ready'
app_state['container_status'] = 'running'

def load_personas():
    """Charge les personas depuis le fichier JSON."""
    try:
        personas_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'personas.json')
        with open(personas_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        log_message(f"Erreur lors du chargement des personas: {e}", "error")
        return {}

# Initialiser les gestionnaires avec les bons chemins
persona_manager = PersonaManager("/app/personas.json")
search_manager = SearchManager("/app/searches.json")

def load_cvs():
    """Charge les CVs depuis le fichier JSON."""
    try:
        cvs_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cvs.json')
        with open(cvs_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        log_message(f"Erreur lors du chargement des CVs: {e}", "error")
        return {}

def log_message(message, level="info"):
    """Ajoute un message de log et l'émet via WebSocket."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {
        'timestamp': timestamp,
        'message': message,
        'level': level
    }
    app_state['logs'].append(log_entry)
    # Garder seulement les 1000 derniers logs
    if len(app_state['logs']) > 1000:
        app_state['logs'] = app_state['logs'][-1000:]
    socketio.emit('log', log_entry)
    print(f"[{timestamp}] [{level.upper()}] {message}")

def update_stats():
    """Met à jour les statistiques et les émet."""
    stats = get_statistics()
    app_state['stats'] = stats
    socketio.emit('stats_update', stats)

# Routes principales
@app.route('/')
def index():
    """Page d'accueil avec le dashboard."""
    return render_template('dashboard.html')

@app.route('/old')
def old_dashboard():
    """Ancien dashboard (pour compatibilité)."""
    return render_template('dashboard.html')

@app.route('/favicon.ico')
@app.route('/favicon.svg')
def favicon():
    """Retourne un favicon SVG."""
    from flask import Response
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="45" fill="#667eea"/>
        <text x="50" y="70" font-size="50" text-anchor="middle" fill="white">🚀</text>
    </svg>'''
    return Response(svg, mimetype='image/svg+xml', headers={'Cache-Control': 'public, max-age=3600'})

@app.route('/api/personas')
def api_personas():
    """API pour récupérer les personas."""
    personas = load_personas()
    return jsonify(personas)

@app.route('/api/personas/base')
def api_base_personas():
    """API pour récupérer uniquement les personas de base."""
    base_personas = persona_manager.get_base_personas()
    return jsonify(base_personas)

@app.route('/api/personas/<persona_key>')
def api_get_persona(persona_key):
    """API pour récupérer un persona spécifique."""
    persona = persona_manager.get_persona(persona_key)
    if persona:
        return jsonify(persona)
    return jsonify({'error': 'Persona non trouvé'}), 404

@app.route('/api/personas/<persona_key>/variants')
def api_get_variants(persona_key):
    """API pour récupérer les variantes d'un persona."""
    persona = persona_manager.get_persona(persona_key)
    if not persona:
        return jsonify({'error': 'Persona non trouvé'}), 404
    
    variants = persona_manager.get_variants_of(persona['email'])
    return jsonify(variants)

@app.route('/api/personas', methods=['POST'])
def api_create_persona():
    """API pour créer un nouveau persona."""
    data = request.json
    try:
        persona_key = persona_manager.create_persona(
            name=data.get('name'),
            email=data.get('email'),
            password=data.get('password', ''),
            alias=data.get('alias', False),
            parent=data.get('parent')
        )
        log_message(f"Persona créé: {data.get('name')} ({data.get('email')})", "success")
        return jsonify({'success': True, 'persona_key': persona_key, 'persona': persona_manager.get_persona(persona_key)})
    except Exception as e:
        log_message(f"Erreur création persona: {e}", "error")
        return jsonify({'error': str(e)}), 500

@app.route('/api/personas/<persona_key>', methods=['PUT'])
def api_update_persona(persona_key):
    """API pour mettre à jour un persona."""
    data = request.json
    try:
        success = persona_manager.update_persona(persona_key, **data)
        if success:
            log_message(f"Persona mis à jour: {persona_key}", "success")
            return jsonify({'success': True, 'persona': persona_manager.get_persona(persona_key)})
        return jsonify({'error': 'Persona non trouvé'}), 404
    except Exception as e:
        log_message(f"Erreur mise à jour persona: {e}", "error")
        return jsonify({'error': str(e)}), 500

@app.route('/api/personas/<persona_key>', methods=['DELETE'])
def api_delete_persona(persona_key):
    """API pour supprimer un persona."""
    try:
        persona = persona_manager.get_persona(persona_key)
        if not persona:
            return jsonify({'error': 'Persona non trouvé'}), 404
        
        success = persona_manager.delete_persona(persona_key)
        if success:
            log_message(f"Persona supprimé: {persona.get('name')}", "warning")
            return jsonify({'success': True})
        return jsonify({'error': 'Erreur lors de la suppression'}), 500
    except Exception as e:
        log_message(f"Erreur suppression persona: {e}", "error")
        return jsonify({'error': str(e)}), 500

@app.route('/api/personas/<persona_key>/variant', methods=['POST'])
def api_create_variant(persona_key):
    """API pour créer une variante d'un persona."""
    data = request.json
    try:
        variant_key = persona_manager.create_variant(
            base_persona_key=persona_key,
            variant_name=data.get('name'),
            email_suffix=data.get('email'),
            **{k: v for k, v in data.items() if k not in ['name', 'email']}
        )
        variant = persona_manager.get_persona(variant_key)
        log_message(f"Variante créée: {variant.get('name')} ({variant.get('email')})", "success")
        return jsonify({'success': True, 'persona_key': variant_key, 'persona': variant})
    except Exception as e:
        log_message(f"Erreur création variante: {e}", "error")
        return jsonify({'error': str(e)}), 500

@app.route('/api/personas/<persona_key>/variants', methods=['POST'])
def api_create_multiple_variants(persona_key):
    """API pour créer plusieurs variantes d'un persona."""
    data = request.json
    count = data.get('count', 1)
    name_pattern = data.get('name_pattern')
    
    try:
        created_keys = persona_manager.create_multiple_variants(
            base_persona_key=persona_key,
            count=count,
            name_pattern=name_pattern
        )
        log_message(f"{count} variantes créées pour {persona_key}", "success")
        return jsonify({'success': True, 'count': len(created_keys), 'persona_keys': created_keys})
    except Exception as e:
        log_message(f"Erreur création variantes: {e}", "error")
        return jsonify({'error': str(e)}), 500

@app.route('/api/personas/<persona_key>/test', methods=['POST'])
def api_test_persona(persona_key):
    """API pour tester un persona."""
    try:
        result = persona_manager.test_persona(persona_key)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'valid': False}), 500

@app.route('/api/personas/<persona_key>/duplicate', methods=['POST'])
def api_duplicate_persona(persona_key):
    """API pour dupliquer un persona."""
    data = request.json
    try:
        new_key = persona_manager.duplicate_persona(
            persona_key=persona_key,
            new_name=data.get('name'),
            new_email=data.get('email')
        )
        new_persona = persona_manager.get_persona(new_key)
        log_message(f"Persona dupliqué: {new_persona.get('name')}", "success")
        return jsonify({'success': True, 'persona_key': new_key, 'persona': new_persona})
    except Exception as e:
        log_message(f"Erreur duplication persona: {e}", "error")
        return jsonify({'error': str(e)}), 500

# API pour les CVs des personas
@app.route('/api/personas/<path:persona_email>/cv', methods=['GET'])
def api_get_persona_cv(persona_email):
    """Récupère le CV d'un persona."""
    import os
    from flask import send_file
    from urllib.parse import unquote
    
    # Décoder l'email depuis l'URL
    persona_email = unquote(persona_email)
    safe_email = persona_email.replace('@', '_at_').replace('.', '_')
    cv_dir = '/app/cvs'
    
    # Chercher le fichier PDF d'abord
    pdf_path = os.path.join(cv_dir, f"{safe_email}_cv.pdf")
    if os.path.exists(pdf_path):
        return send_file(pdf_path, mimetype='application/pdf', as_attachment=False)
    
    # Sinon chercher le HTML
    html_path = os.path.join(cv_dir, f"{safe_email}_cv.html")
    if os.path.exists(html_path):
        return send_file(html_path, mimetype='text/html', as_attachment=False)
    
    return jsonify({'error': 'CV non trouvé'}), 404

@app.route('/api/personas/<path:persona_email>/cv/download', methods=['GET'])
def api_download_persona_cv(persona_email):
    """Télécharge le CV d'un persona."""
    import os
    from flask import send_file
    from urllib.parse import unquote
    
    # Décoder l'email depuis l'URL
    persona_email = unquote(persona_email)
    safe_email = persona_email.replace('@', '_at_').replace('.', '_')
    cv_dir = '/app/cvs'
    
    # Chercher le fichier PDF d'abord
    pdf_path = os.path.join(cv_dir, f"{safe_email}_cv.pdf")
    if os.path.exists(pdf_path):
        return send_file(pdf_path, mimetype='application/pdf', as_attachment=True, download_name=f"{safe_email}_cv.pdf")
    
    # Sinon chercher le HTML
    html_path = os.path.join(cv_dir, f"{safe_email}_cv.html")
    if os.path.exists(html_path):
        return send_file(html_path, mimetype='text/html', as_attachment=True, download_name=f"{safe_email}_cv.html")
    
    return jsonify({'error': 'CV non trouvé'}), 404

@app.route('/api/personas/cvs', methods=['GET'])
def api_list_all_cvs():
    """Liste tous les CVs disponibles."""
    import os
    import glob
    
    cv_dir = '/app/cvs'
    cvs = []
    
    try:
        if os.path.exists(cv_dir):
            # Chercher tous les fichiers CV
            pdf_files = glob.glob(os.path.join(cv_dir, '*_cv.pdf'))
            html_files = glob.glob(os.path.join(cv_dir, '*_cv.html'))
            
            all_files = pdf_files + html_files
            
            for cv_path in all_files:
                filename = os.path.basename(cv_path)
                # Extraire l'email du nom de fichier
                safe_email = filename.replace('_cv.pdf', '').replace('_cv.html', '')
                # Convertir le safe_email en email réel
                # D'abord remplacer _at_ par @, puis les underscores restants par des points
                persona_email = safe_email.replace('_at_', '@').replace('_', '.')
                
                # Trouver le persona correspondant
                all_personas = persona_manager.get_all_personas()
                persona_name = None
                for key, persona in all_personas.items():
                    if persona.get('email') == persona_email:
                        persona_name = persona.get('name')
                        break
                
                cvs.append({
                    'persona_email': persona_email,
                    'persona_name': persona_name,
                    'filename': filename,
                    'path': cv_path,
                    'type': 'pdf' if cv_path.endswith('.pdf') else 'html',
                    'size': os.path.getsize(cv_path) if os.path.exists(cv_path) else 0
                })
    except Exception as e:
        log_message(f"Erreur lors de la liste des CVs: {e}", "error")
    
    # Toujours retourner un tableau JSON, même s'il est vide
    return jsonify(cvs)

# API pour les emails des personas
@app.route('/api/personas/<path:persona_email>/emails', methods=['GET'])
def api_get_persona_emails(persona_email):
    """Récupère les emails d'un persona."""
    import sqlite3
    from urllib.parse import unquote
    
    # Décoder l'email depuis l'URL
    persona_email = unquote(persona_email)
    
    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        
        c.execute("""SELECT id, sender, subject, body, received_at, is_read, email_type
                     FROM persona_emails
                     WHERE persona_email = ?
                     ORDER BY received_at DESC
                     LIMIT 100""", (persona_email,))
        
        emails = []
        for row in c.fetchall():
            emails.append({
                'id': row[0],
                'sender': row[1],
                'subject': row[2],
                'body': row[3],
                'received_at': row[4],
                'is_read': bool(row[5]),
                'email_type': row[6]
            })
        
        conn.close()
        return jsonify(emails)
    except Exception as e:
        log_message(f"Erreur lors de la récupération des emails pour {persona_email}: {e}", "error")
        return jsonify([])

@app.route('/api/personas/<path:persona_email>/emails/count', methods=['GET'])
def api_get_persona_emails_count(persona_email):
    """Compte les emails d'un persona."""
    import sqlite3
    from urllib.parse import unquote
    
    # Décoder l'email depuis l'URL
    persona_email = unquote(persona_email)
    
    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        
        c.execute("""SELECT COUNT(*) FROM persona_emails WHERE persona_email = ?""", (persona_email,))
        total = c.fetchone()[0]
        
        c.execute("""SELECT COUNT(*) FROM persona_emails WHERE persona_email = ? AND is_read = 0""", (persona_email,))
        unread = c.fetchone()[0]
        
        conn.close()
        return jsonify({'total': total, 'unread': unread})
    except Exception as e:
        log_message(f"Erreur lors du comptage des emails pour {persona_email}: {e}", "error")
        return jsonify({'total': 0, 'unread': 0})

@app.route('/api/personas/<path:persona_email>/emails/<int:email_id>/read', methods=['POST'])
def api_mark_email_read(persona_email, email_id):
    """Marque un email comme lu."""
    import sqlite3
    from urllib.parse import unquote
    
    # Décoder l'email depuis l'URL
    persona_email = unquote(persona_email)
    
    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        
        c.execute("""UPDATE persona_emails 
                     SET is_read = 1 
                     WHERE id = ? AND persona_email = ?""", (email_id, persona_email))
        conn.commit()
        success = c.rowcount > 0
        conn.close()
        
        if success:
            log_message(f"Email {email_id} de {persona_email} marqué comme lu.", "info")
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Email non trouvé'}), 404
    except Exception as e:
        log_message(f"Erreur lors du marquage de l'email {email_id} comme lu pour {persona_email}: {e}", "error")
        return jsonify({'success': False, 'error': str(e)}), 500

# API pour les recherches
@app.route('/api/searches')
def api_searches():
    """API pour récupérer toutes les recherches."""
    searches = search_manager.get_all_searches()
    return jsonify(searches)

@app.route('/api/searches/enabled')
def api_enabled_searches():
    """API pour récupérer les recherches activées."""
    searches = search_manager.get_enabled_searches()
    return jsonify(searches)

@app.route('/api/searches/<search_key>')
def api_get_search(search_key):
    """API pour récupérer une recherche spécifique."""
    search = search_manager.get_search(search_key)
    if search:
        return jsonify(search)
    return jsonify({'error': 'Recherche non trouvée'}), 404

@app.route('/api/searches', methods=['POST'])
def api_create_search():
    """API pour créer une nouvelle recherche."""
    data = request.json
    try:
        # Normaliser les données (support rétrocompatibilité)
        search_type = data.get('search_type') or data.get('job_type', 'développeur')
        is_active = data.get('is_active') if 'is_active' in data else (data.get('enabled', True))
        
        search_key = search_manager.create_search(
            key=data.get('key'),
            name=data.get('name'),
            query=data.get('query'),
            location=data.get('location'),
            title_keywords=data.get('title_keywords', []),
            location_keywords=data.get('location_keywords', []),
            exclude_keywords=data.get('exclude_keywords', []),
            search_type=search_type,
            max_results=data.get('max_results', 50),
            is_active=is_active,
            description=data.get('description', '')
        )
        log_message(f"Recherche créée: {data.get('name')}", "success")
        return jsonify({'success': True, 'search_key': search_key, 'search': search_manager.get_search(search_key)})
    except Exception as e:
        log_message(f"Erreur création recherche: {e}", "error")
        return jsonify({'error': str(e)}), 500

@app.route('/api/searches/<search_key>', methods=['PUT'])
def api_update_search(search_key):
    """API pour mettre à jour une recherche."""
    data = request.json
    try:
        # Normaliser les données (support rétrocompatibilité)
        update_data = data.copy()
        if 'job_type' in update_data and 'search_type' not in update_data:
            update_data['search_type'] = update_data.pop('job_type')
        if 'enabled' in update_data and 'is_active' not in update_data:
            update_data['is_active'] = update_data.pop('enabled')
        
        success = search_manager.update_search(search_key, **update_data)
        if success:
            log_message(f"Recherche mise à jour: {search_key}", "success")
            return jsonify({'success': True, 'search': search_manager.get_search(search_key)})
        return jsonify({'error': 'Recherche non trouvée'}), 404
    except Exception as e:
        log_message(f"Erreur mise à jour recherche: {e}", "error")
        return jsonify({'error': str(e)}), 500

@app.route('/api/searches/<search_key>', methods=['DELETE'])
def api_delete_search(search_key):
    """API pour supprimer une recherche."""
    try:
        search = search_manager.get_search(search_key)
        if not search:
            return jsonify({'error': 'Recherche non trouvée'}), 404
        
        success = search_manager.delete_search(search_key)
        if success:
            log_message(f"Recherche supprimée: {search.get('name')}", "warning")
            return jsonify({'success': True})
        return jsonify({'error': 'Erreur lors de la suppression'}), 500
    except Exception as e:
        log_message(f"Erreur suppression recherche: {e}", "error")
        return jsonify({'error': str(e)}), 500

@app.route('/api/searches/<search_key>/duplicate', methods=['POST'])
def api_duplicate_search(search_key):
    """API pour dupliquer une recherche."""
    data = request.json
    try:
        new_key = search_manager.duplicate_search(
            search_key=search_key,
            new_name=data.get('name')
        )
        new_search = search_manager.get_search(new_key)
        log_message(f"Recherche dupliquée: {new_search.get('name')}", "success")
        return jsonify({'success': True, 'search_key': new_key, 'search': new_search})
    except Exception as e:
        log_message(f"Erreur duplication recherche: {e}", "error")
        return jsonify({'error': str(e)}), 500

@app.route('/api/searches/job-types')
def api_job_types():
    """API pour récupérer les types de postes disponibles."""
    return jsonify(search_manager.get_job_types())

@app.route('/api/searches/run-multiple', methods=['POST'])
def api_run_multiple_searches():
    """API pour lancer plusieurs recherches."""
    data = request.json
    search_keys = data.get('search_keys', [])
    selected_personas = data.get('selected_personas', [])
    max_per_persona = data.get('max_per_persona', 3)
    delay_min = data.get('delay_min', 5)
    delay_max = data.get('delay_max', 10)
    use_cover_letter = data.get('use_cover_letter', True)
    headless = data.get('headless', True)
    
    if not search_keys:
        return jsonify({'error': 'Aucune recherche sélectionnée'}), 400
    
    if app_state['is_running']:
        return jsonify({'error': 'Le processus est déjà en cours'}), 400
    
    def run_multiple_searches_async():
        app_state['is_running'] = True
        app_state['applications_sent'] = 0
        app_state['applications_failed'] = 0
        
        try:
            log_message(f"🚀 Démarrage de {len(search_keys)} recherches", "info")
            app_state['current_step'] = 'initialisation'
            socketio.emit('status_update', {'step': 'initialisation', 'is_running': True})
            
            create_database()
            
            # Charger les personas
            all_personas = load_personas()
            if selected_personas and len(selected_personas) > 0:
                personas = {k: v for k, v in all_personas.items() if v['email'] in selected_personas}
            else:
                personas = all_personas
            
            log_message(f"   {len(personas)} personas chargés", "info")
            
            # Générer les CVs
            log_message("📄 Génération des CVs...", "info")
            app_state['current_step'] = 'generating_cvs'
            socketio.emit('status_update', {'step': 'generating_cvs', 'is_running': True})
            cv_paths = generate_cvs_from_json()
            log_message(f"   {len(cv_paths)} CVs générés", "success")
            
            # Pour chaque recherche
            for search_key in search_keys:
                if not app_state['is_running']:
                    break
                
                search = search_manager.get_search(search_key)
                if not search or not search.get('is_active', search.get('enabled', True)):
                    continue
                
                log_message(f"\n🔍 Recherche: {search['name']} ({search['query']} - {search['location']})", "info")
                app_state['current_step'] = 'scraping'
                socketio.emit('status_update', {'step': 'scraping', 'is_running': True})
                
                # Scraper les offres
                jobs = scrape_indeed(query=search['query'], location=search['location'], max_results=search.get('max_results', 50))
                log_message(f"   {len(jobs)} offres trouvées", "success")
                
                for job in jobs:
                    insert_job(job)
                
                app_state['jobs_found'] += len(jobs)
                
                # Filtrer et postuler
                log_message("🔎 Filtrage et candidature...", "info")
                app_state['current_step'] = 'applying'
                socketio.emit('status_update', {'step': 'applying', 'is_running': True})
                
                import random
                persona_list = list(personas.items())
                random.shuffle(persona_list)
                
                for persona_key, persona_info in persona_list:
                    if not app_state['is_running']:
                        break
                    
                    persona_email = persona_info['email']
                    persona_name = persona_info['name']
                    
                    if persona_email not in cv_paths:
                        continue
                    
                    cv_path = cv_paths[persona_email]
                    
                    filtered_jobs = filter_jobs(
                        title_keywords=search.get('title_keywords', []),
                        location_keywords=search.get('location_keywords', []),
                        persona_email=persona_email,
                        exclude_keywords=search.get('exclude_keywords', [])
                    )
                    
                    if not filtered_jobs:
                        continue
                    
                    jobs_to_apply = filtered_jobs[:max_per_persona]
                    
                    for job in jobs_to_apply:
                        if not app_state['is_running']:
                            break
                        
                        cover_letter = None
                        if use_cover_letter:
                            try:
                                cover_letter = generate_cover_letter(job)
                            except Exception as e:
                                pass
                        
                        application_id = insert_application(
                            job_id=job['id'],
                            persona_email=persona_email,
                            persona_name=persona_name,
                            cv_path=cv_path,
                            cover_letter=cover_letter,
                            status='pending'
                        )
                        
                        if not application_id:
                            continue
                        
                        log_message(f"   📝 {persona_name}: {job['title']} chez {job['company']}", "info")
                        
                        success = apply_to_job(
                            job=job,
                            persona_email=persona_email,
                            persona_name=persona_name,
                            cv_path=cv_path,
                            cover_letter=cover_letter,
                            headless=headless
                        )
                        
                        if success:
                            update_application_status(application_id, 'sent')
                            app_state['applications_sent'] += 1
                        else:
                            update_application_status(application_id, 'failed')
                            app_state['applications_failed'] += 1
                        
                        update_stats()
                        delay = random.uniform(delay_min, delay_max)
                        time.sleep(delay)
                
                # Marquer la recherche comme exécutée
                search_manager.mark_run(search_key)
            
            log_message("\n📊 Toutes les recherches terminées", "success")
            update_stats()
            
        except Exception as e:
            log_message(f"❌ Erreur fatale: {e}", "error")
            import traceback
            traceback.print_exc()
        finally:
            app_state['is_running'] = False
            app_state['current_step'] = 'ready'
            socketio.emit('status_update', {'step': 'ready', 'is_running': False})
    
    thread = threading.Thread(target=run_multiple_searches_async)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': f'{len(search_keys)} recherches démarrées'})

@app.route('/api/jobs')
def api_jobs():
    """API pour récupérer les offres d'emploi."""
    persona_email = request.args.get('persona_email')
    limit = request.args.get('limit', 100, type=int)
    jobs = get_unapplied_jobs(persona_email)
    # Limiter le nombre de résultats
    return jsonify(jobs[:limit])

@app.route('/api/stats')
def api_stats():
    """API pour récupérer les statistiques."""
    return jsonify(get_statistics())

@app.route('/api/logs')
def api_logs():
    """API pour récupérer les logs."""
    return jsonify(app_state['logs'])

# Routes pour les actions
@app.route('/api/generate_cvs', methods=['POST'])
def api_generate_cvs():
    """Génère tous les CVs."""
    try:
        log_message("Génération des CVs en cours...", "info")
        cv_paths = generate_cvs_from_json()
        log_message(f"{len(cv_paths)} CVs générés avec succès", "success")
        return jsonify({'success': True, 'count': len(cv_paths), 'cvs': cv_paths})
    except Exception as e:
        log_message(f"Erreur lors de la génération des CVs: {e}", "error")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scrape_jobs', methods=['POST'])
def api_scrape_jobs():
    """Scrape les offres d'emploi."""
    data = request.json
    query = data.get('query', 'développeur python')
    location = data.get('location', 'Rennes')
    max_results = data.get('max_results', 50)
    
    def scrape_async():
        try:
            log_message(f"Recherche d'offres: '{query}' à {location}...", "info")
            jobs = scrape_indeed(query, location, max_results)
            log_message(f"{len(jobs)} offres trouvées", "success")
            
            for job in jobs:
                insert_job(job)
            
            app_state['jobs_found'] = len(jobs)
            update_stats()
            socketio.emit('scrape_complete', {'count': len(jobs)})
        except Exception as e:
            log_message(f"Erreur lors du scraping: {e}", "error")
            socketio.emit('scrape_error', {'error': str(e)})
    
    thread = threading.Thread(target=scrape_async)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Scraping démarré'})

@app.route('/api/start_auto_apply', methods=['POST'])
def api_start_auto_apply():
    """Démarre le processus de candidature automatique."""
    if app_state['is_running']:
        return jsonify({'error': 'Le processus est déjà en cours'}), 400
    
    data = request.json
    search_query = data.get('query', 'développeur python')
    search_location = data.get('location', 'Rennes')
    title_keywords = data.get('title_keywords', ['Python', 'Développeur'])
    location_keywords = data.get('location_keywords', ['Rennes', 'Bretagne'])
    exclude_keywords = data.get('exclude_keywords', ['Senior', 'Lead'])
    max_per_persona = data.get('max_per_persona', 3)
    delay_min = data.get('delay_min', 5)
    delay_max = data.get('delay_max', 10)
    use_cover_letter = data.get('use_cover_letter', True)
    headless = data.get('headless', True)
    selected_personas = data.get('selected_personas', [])  # Liste des emails de personas sélectionnés
    
    def auto_apply_async():
        app_state['is_running'] = True
        app_state['applications_sent'] = 0
        app_state['applications_failed'] = 0
        
        try:
            log_message("🚀 Démarrage du système de candidature automatique", "info")
            app_state['current_step'] = 'initialisation'
            socketio.emit('status_update', {'step': 'initialisation', 'is_running': True})
            
            # Initialiser la base de données
            log_message("📊 Initialisation de la base de données...", "info")
            create_database()
            
            # Charger les personas
            log_message("👥 Chargement des personas...", "info")
            all_personas = load_personas()
            
            # Filtrer les personas si une sélection a été faite
            if selected_personas and len(selected_personas) > 0:
                personas = {k: v for k, v in all_personas.items() if v['email'] in selected_personas}
                log_message(f"   {len(selected_personas)} personas sélectionnés sur {len(all_personas)} disponibles", "info")
            else:
                personas = all_personas
                log_message(f"   {len(personas)} personas chargés (tous sélectionnés)", "info")
            
            # Générer les CVs
            log_message("📄 Génération des CVs...", "info")
            app_state['current_step'] = 'generating_cvs'
            socketio.emit('status_update', {'step': 'generating_cvs', 'is_running': True})
            cv_paths = generate_cvs_from_json()
            log_message(f"   {len(cv_paths)} CVs générés", "success")
            
            # Scraper les offres
            log_message(f"🔍 Recherche d'offres: '{search_query}' à {search_location}...", "info")
            app_state['current_step'] = 'scraping'
            socketio.emit('status_update', {'step': 'scraping', 'is_running': True})
            jobs = scrape_indeed(query=search_query, location=search_location)
            log_message(f"   {len(jobs)} offres trouvées", "success")
            
            for job in jobs:
                insert_job(job)
            
            app_state['jobs_found'] = len(jobs)
            
            # Filtrer et postuler
            log_message("🔎 Filtrage des offres...", "info")
            app_state['current_step'] = 'applying'
            socketio.emit('status_update', {'step': 'applying', 'is_running': True})
            
            import random
            persona_list = list(personas.items())
            random.shuffle(persona_list)
            
            for persona_key, persona_info in persona_list:
                if not app_state['is_running']:
                    break
                
                persona_email = persona_info['email']
                persona_name = persona_info['name']
                
                if persona_email not in cv_paths:
                    log_message(f"⚠️  Pas de CV trouvé pour {persona_name}", "warning")
                    continue
                
                cv_path = cv_paths[persona_email]
                
                filtered_jobs = filter_jobs(
                    title_keywords=title_keywords,
                    location_keywords=location_keywords,
                    persona_email=persona_email,
                    exclude_keywords=exclude_keywords
                )
                
                if not filtered_jobs:
                    log_message(f"   {persona_name}: Aucune offre disponible", "info")
                    continue
                
                jobs_to_apply = filtered_jobs[:max_per_persona]
                log_message(f"\n👤 {persona_name} ({persona_email})", "info")
                log_message(f"   {len(jobs_to_apply)} offres à traiter", "info")
                
                for job in jobs_to_apply:
                    if not app_state['is_running']:
                        break
                    
                    # Générer la lettre de motivation si activée
                    cover_letter = None
                    if use_cover_letter:
                        try:
                            cover_letter = generate_cover_letter(job)
                        except Exception as e:
                            log_message(f"   ⚠️  Erreur génération lettre: {e}", "warning")
                            cover_letter = None
                    
                    application_id = insert_application(
                        job_id=job['id'],
                        persona_email=persona_email,
                        persona_name=persona_name,
                        cv_path=cv_path,
                        cover_letter=cover_letter,
                        status='pending'
                    )
                    
                    if not application_id:
                        continue
                    
                    log_message(f"   📝 Candidature pour: {job['title']} chez {job['company']}", "info")
                    socketio.emit('application_start', {
                        'persona': persona_name,
                        'job': job['title'],
                        'company': job['company']
                    })
                    
                    success = apply_to_job(
                        job=job,
                        persona_email=persona_email,
                        persona_name=persona_name,
                        cv_path=cv_path,
                        cover_letter=cover_letter,
                        headless=headless
                    )
                    
                    if success:
                        update_application_status(job['id'], persona_email, 'sent')
                        app_state['applications_sent'] += 1
                        log_message(f"   ✅ Candidature envoyée avec succès", "success")
                        socketio.emit('application_success', {
                            'persona': persona_name,
                            'job': job['title']
                        })
                    else:
                        update_application_status(job['id'], persona_email, 'failed')
                        app_state['applications_failed'] += 1
                        log_message(f"   ❌ Échec de la candidature", "error")
                        socketio.emit('application_failed', {
                            'persona': persona_name,
                            'job': job['title']
                        })
                    
                    update_stats()
                    # Utiliser les délais configurés
                    delay = random.uniform(delay_min, delay_max)
                    time.sleep(delay)
            
            log_message("\n📊 Processus terminé", "info")
            update_stats()
            
        except Exception as e:
            log_message(f"❌ Erreur fatale: {e}", "error")
            import traceback
            traceback.print_exc()
        finally:
            app_state['is_running'] = False
            app_state['current_step'] = 'ready'  # 'ready' au lieu de 'idle' pour indiquer que le système est prêt
            socketio.emit('status_update', {'step': 'ready', 'is_running': False})
            log_message("🏁 Processus terminé - Système prêt", "info")
    
    thread = threading.Thread(target=auto_apply_async)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Processus démarré'})

@app.route('/api/stop_auto_apply', methods=['POST'])
def api_stop_auto_apply():
    """Arrête le processus de candidature automatique."""
    app_state['is_running'] = False
    log_message("Arrêt demandé...", "warning")
    return jsonify({'success': True, 'message': 'Arrêt demandé'})

@app.route('/api/status')
def api_status():
    """Récupère l'état actuel du système."""
    # S'assurer que current_step n'est jamais vide
    if not app_state.get('current_step') or app_state.get('current_step') == '':
        app_state['current_step'] = 'ready'
    
    current_step = app_state.get('current_step', 'ready')
    
    return jsonify({
        'is_running': app_state.get('is_running', False),
        'current_step': current_step,
        'jobs_found': app_state.get('jobs_found', 0),
        'applications_sent': app_state.get('applications_sent', 0),
        'applications_failed': app_state.get('applications_failed', 0),
        'container_status': 'running'  # Le conteneur fonctionne
    })

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Gère la connexion WebSocket."""
    # S'assurer que l'état est initialisé
    if not app_state.get('current_step') or app_state.get('current_step') == '':
        app_state['current_step'] = 'ready'
    
    emit('connected', {'message': 'Connecté au serveur'})
    emit('status_update', {
        'step': app_state.get('current_step', 'ready'),
        'is_running': app_state.get('is_running', False)
    })
    update_stats()

@socketio.on('disconnect')
def handle_disconnect():
    """Gère la déconnexion WebSocket."""
    pass

# Route catch-all pour le favicon (doit être après toutes les autres routes)
@app.before_request
def handle_favicon():
    if request.path == '/favicon.ico':
        from flask import Response
        svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="45" fill="#667eea"/>
            <text x="50" y="70" font-size="50" text-anchor="middle" fill="white">🚀</text>
        </svg>'''
        return Response(svg, mimetype='image/svg+xml', headers={'Cache-Control': 'public, max-age=3600'})

if __name__ == '__main__':
    # Initialiser la base de données
    create_database()
    # Initialiser l'état au démarrage
    app_state['current_step'] = 'ready'
    app_state['container_status'] = 'running'
    log_message("🚀 Serveur démarré - Système prêt", "success")
    # Démarrer le serveur
    socketio.run(app, host='0.0.0.0', port=2020, debug=True, use_reloader=False)

