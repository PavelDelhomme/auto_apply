from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import json
import threading
import time
import random
import logging
import sqlite3
from datetime import datetime
from .cv_generator import generate_cvs_from_json, generate_cv_for_persona
from .scraper import scrape_indeed
from .auto_apply import apply_to_job
from .job_filter import filter_jobs
from .database import (create_database, insert_job, get_unapplied_jobs, insert_application, 
                      update_application_status, get_db_path, insert_email, insert_log, 
                      get_logs, insert_historical_stat, get_historical_stats, 
                      delete_test_data, mark_as_test_data, save_persona_cv, get_persona_cv, 
                      get_all_persona_cvs, get_all_jobs)
from .stats import get_statistics
from .application_generator import generate_cover_letter
from .persona_manager import PersonaManager
from .search_manager import SearchManager
import os

logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='/app/templates', static_folder='/app/static')
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
        personas_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'personas.json')
        with open(personas_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        log_message(f"Erreur lors du chargement des personas: {e}", "error")
        return {}

# Initialiser les gestionnaires avec les bons chemins
persona_manager = PersonaManager("/app/config/personas.json")
search_manager = SearchManager("/app/config/searches.json")

def load_cvs():
    """Charge les CVs depuis le fichier JSON."""
    try:
        cvs_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'cvs.json')
        with open(cvs_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        log_message(f"Erreur lors du chargement des CVs: {e}", "error")
        return {}

def log_message(message, level="info", category="general", is_test_data=False):
    """Ajoute un message de log et l'émet via WebSocket."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {
        'timestamp': timestamp,
        'message': message,
        'level': level,
        'category': category
    }
    app_state['logs'].append(log_entry)
    # Garder seulement les 1000 derniers logs en mémoire
    if len(app_state['logs']) > 1000:
        app_state['logs'] = app_state['logs'][-1000:]
    
    # Stocker dans la base de données
    try:
        insert_log(message, level, category, is_test_data)
    except Exception as e:
        logger.error(f"Erreur lors de l'insertion du log: {e}")
    
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
    return render_template('pages/dashboard.html')

@app.route('/personas')
def personas_page():
    """Page de gestion des personas."""
    return render_template('pages/personas.html')

@app.route('/searches')
def searches_page():
    """Page de gestion des recherches."""
    return render_template('pages/searches.html')

@app.route('/jobs')
def jobs_page():
    """Page des offres d'emploi."""
    return render_template('pages/jobs.html')

@app.route('/emails')
def emails_page():
    """Page de gestion des emails."""
    return render_template('pages/emails.html')

@app.route('/stats')
def stats_page():
    """Page des statistiques."""
    return render_template('pages/stats.html')

@app.route('/settings')
def settings_page():
    """Page des paramètres."""
    return render_template('pages/settings.html')

@app.route('/logs')
def logs_page():
    """Page des logs et historique."""
    return render_template('pages/logs.html')

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
            parent=data.get('parent'),
            skills=data.get('skills', []),
            experience_years=data.get('experience_years'),
            education=data.get('education', []),
            languages=data.get('languages', []),
            location=data.get('location'),
            phone=data.get('phone'),
            linkedin=data.get('linkedin'),
            github=data.get('github'),
            portfolio=data.get('portfolio'),
            notes=data.get('notes'),
            email_config=data.get('email_config', {})
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
    """Récupère le CV d'un persona (par défaut ou pour une recherche spécifique)."""
    import os
    from flask import send_file
    from urllib.parse import unquote
    
    # Décoder l'email depuis l'URL
    persona_email = unquote(persona_email)
    search_key = request.args.get('search_key')
    cv_id = request.args.get('cv_id')
    
    # Chercher dans la base de données d'abord
    cv_info = get_persona_cv(persona_email, search_key=search_key, cv_id=cv_id)
    if cv_info and os.path.exists(cv_info['cv_path']):
        if cv_info['cv_path'].endswith('.pdf'):
            return send_file(cv_info['cv_path'], mimetype='application/pdf', as_attachment=False)
        else:
            return send_file(cv_info['cv_path'], mimetype='text/html', as_attachment=False)
    
    # Fallback: chercher le fichier par défaut
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

@app.route('/api/personas/<path:persona_email>/cvs', methods=['GET'])
def api_list_persona_cvs(persona_email):
    """Liste tous les CVs d'un persona."""
    from urllib.parse import unquote
    persona_email = unquote(persona_email)
    cvs = get_all_persona_cvs(persona_email)
    return jsonify(cvs)

@app.route('/api/personas/<path:persona_email>/cv/generate', methods=['POST'])
def api_generate_persona_cv(persona_email):
    """Génère un CV pour un persona (optionnellement pour une recherche spécifique)."""
    from urllib.parse import unquote
    from .cv_generator import generate_cv_for_persona
    import json
    
    persona_email = unquote(persona_email)
    data = request.json
    search_key = data.get('search_key')
    cv_id = data.get('cv_id', 'default')
    cv_data = data.get('cv_data', {})
    
    try:
        persona = persona_manager.get_persona_by_email(persona_email)
        if not persona:
            return jsonify({'error': 'Persona non trouvé'}), 404
        
        # Générer le CV
        cv_path = generate_cv_for_persona(
            persona_email=persona_email,
            persona_name=persona.get('name'),
            cv_data=cv_data,
            search_key=search_key,
            cv_id=cv_id
        )
        
        if cv_path:
            # Sauvegarder dans la base de données
            save_persona_cv(
                persona_email=persona_email,
                cv_id=cv_id,
                cv_path=cv_path,
                cv_data=cv_data,
                search_key=search_key,
                is_default=(search_key is None and cv_id == 'default')
            )
            return jsonify({'success': True, 'cv_path': cv_path, 'cv_id': cv_id})
        else:
            return jsonify({'error': 'Erreur lors de la génération du CV'}), 500
    except Exception as e:
        logger.error(f"Erreur génération CV: {e}")
        return jsonify({'error': str(e)}), 500

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

@app.route('/api/personas/<path:persona_email>/emails/test-connection', methods=['POST'])
def api_test_email_connection(persona_email):
    """Teste la connexion IMAP pour un persona."""
    from urllib.parse import unquote
    import imaplib
    
    persona_email = unquote(persona_email)
    
    try:
        # Récupérer les informations du persona
        persona = persona_manager.get_persona_by_email(persona_email)
        if not persona:
            return jsonify({'success': False, 'error': 'Persona non trouvé'}), 404
        
        # Récupérer le mot de passe
        password = persona.get('password')
        if not password:
            return jsonify({'success': False, 'error': 'Mot de passe non configuré pour ce persona'}), 400
        
        # Déterminer le serveur IMAP selon le domaine
        email_domain = persona_email.split('@')[1].lower()
        
        # Vérifier si le persona a une configuration email personnalisée
        imap_server = persona.get('email_config', {}).get('imap_server')
        imap_port = persona.get('email_config', {}).get('imap_port', 993)
        
        if not imap_server:
            # Utiliser la liste par défaut des serveurs IMAP
            imap_servers = {
                'gmx.com': 'imap.gmx.com',
                'gmx.fr': 'imap.gmx.com',
                'gmail.com': 'imap.gmail.com',
                'outlook.com': 'outlook.office365.com',
                'hotmail.com': 'outlook.office365.com',
                'live.com': 'outlook.office365.com',
                'yahoo.com': 'imap.mail.yahoo.com',
                'yahoo.fr': 'imap.mail.yahoo.com',
                'caramail.com': 'imap.caramail.com',
                'caramail.fr': 'imap.caramail.com',
                'orange.fr': 'imap.orange.fr',
                'wanadoo.fr': 'imap.orange.fr',
                'free.fr': 'imap.free.fr',
                'laposte.net': 'imap.laposte.net',
                'sfr.fr': 'imap.sfr.fr',
                'numericable.fr': 'imap.numericable.fr'
            }
            
            imap_server = imap_servers.get(email_domain)
            if not imap_server:
                # Essayer avec le format standard
                imap_server = f'imap.{email_domain}'
        
        # Tester la connexion
        try:
            # Essayer avec SSL d'abord
            try:
                mail = imaplib.IMAP4_SSL(imap_server, imap_port)
            except Exception as ssl_error:
                # Si SSL échoue, essayer sans SSL (port 143)
                logger.warning(f"SSL échoué pour {imap_server}, tentative sans SSL: {ssl_error}")
                imap_server = imap_server.replace('imap.', '')  # Retirer le préfixe si présent
                try:
                    mail = imaplib.IMAP4(imap_server, 143)
                except Exception as e:
                    return jsonify({
                        'success': False, 
                        'error': f'Impossible de se connecter au serveur {imap_server}: {str(e)}'
                    }), 500
            
            mail.login(persona_email, password)
            mail.select('inbox')
            mail.close()
            mail.logout()
            
            log_message(f"Test connexion email réussi pour {persona_email} ({imap_server}:{imap_port})", "success")
            return jsonify({
                'success': True,
                'message': f'Connexion réussie au serveur {imap_server}:{imap_port}',
                'server': imap_server,
                'port': imap_port
            })
        except imaplib.IMAP4.error as e:
            error_msg = str(e)
            logger.error(f"Erreur IMAP pour {persona_email} sur {imap_server}: {error_msg}")
            if 'authentication failed' in error_msg.lower() or 'invalid credentials' in error_msg.lower():
                return jsonify({
                    'success': False, 
                    'error': 'Identifiants incorrects. Vérifiez le mot de passe.',
                    'server': imap_server,
                    'port': imap_port
                }), 401
            elif 'login' in error_msg.lower():
                return jsonify({
                    'success': False, 
                    'error': f'Erreur d\'authentification: {error_msg}. Vérifiez que l\'accès IMAP est activé pour ce compte.',
                    'server': imap_server,
                    'port': imap_port
                }), 401
            else:
                return jsonify({
                    'success': False, 
                    'error': f'Erreur IMAP: {error_msg}',
                    'server': imap_server,
                    'port': imap_port,
                    'hint': 'Vérifiez que le serveur IMAP est correct et que l\'accès IMAP est activé pour ce compte.'
                }), 500
        except socket.gaierror as e:
            return jsonify({
                'success': False, 
                'error': f'Impossible de résoudre le nom du serveur {imap_server}. Vérifiez la configuration.',
                'server': imap_server,
                'port': imap_port
            }), 500
        except Exception as e:
            logger.error(f"Erreur inattendue lors du test de connexion pour {persona_email}: {e}")
            return jsonify({
                'success': False, 
                'error': f'Erreur de connexion: {str(e)}',
                'server': imap_server,
                'port': imap_port,
                'hint': 'Vérifiez la configuration email du persona et que l\'accès IMAP est activé.'
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur test connexion email pour {persona_email}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/personas/<path:persona_email>/emails/fetch', methods=['POST'])
def api_fetch_emails_from_imap(persona_email):
    """Récupère les emails depuis IMAP pour un persona."""
    from urllib.parse import unquote
    import imaplib
    import email
    from email.header import decode_header
    
    persona_email = unquote(persona_email)
    
    try:
        # Récupérer les informations du persona
        persona = persona_manager.get_persona_by_email(persona_email)
        if not persona:
            return jsonify({'success': False, 'error': 'Persona non trouvé'}), 404
        
        password = persona.get('password')
        if not password:
            return jsonify({'success': False, 'error': 'Mot de passe non configuré'}), 400
        
        # Déterminer le serveur IMAP
        email_domain = persona_email.split('@')[1].lower()
        
        # Vérifier si le persona a une configuration email personnalisée
        imap_server = persona.get('email_config', {}).get('imap_server')
        imap_port = persona.get('email_config', {}).get('imap_port', 993)
        
        if not imap_server:
            # Utiliser la liste par défaut des serveurs IMAP
            imap_servers = {
                'gmx.com': 'imap.gmx.com',
                'gmx.fr': 'imap.gmx.com',
                'gmail.com': 'imap.gmail.com',
                'outlook.com': 'outlook.office365.com',
                'hotmail.com': 'outlook.office365.com',
                'live.com': 'outlook.office365.com',
                'yahoo.com': 'imap.mail.yahoo.com',
                'yahoo.fr': 'imap.mail.yahoo.com',
                'caramail.com': 'imap.caramail.com',
                'caramail.fr': 'imap.caramail.com',
                'orange.fr': 'imap.orange.fr',
                'wanadoo.fr': 'imap.orange.fr',
                'free.fr': 'imap.free.fr',
                'laposte.net': 'imap.laposte.net',
                'sfr.fr': 'imap.sfr.fr',
                'numericable.fr': 'imap.numericable.fr'
            }
            
            imap_server = imap_servers.get(email_domain)
            if not imap_server:
                # Essayer avec le format standard
                imap_server = f'imap.{email_domain}'
        
        # Connexion IMAP
        try:
            mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        except Exception as ssl_error:
            # Si SSL échoue, essayer sans SSL (port 143)
            logger.warning(f"SSL échoué pour {imap_server}, tentative sans SSL: {ssl_error}")
            try:
                mail = imaplib.IMAP4(imap_server, 143)
            except Exception as e:
                log_message(f"Impossible de se connecter au serveur {imap_server}: {str(e)}", "error")
                return jsonify({'success': False, 'error': f'Impossible de se connecter au serveur: {str(e)}'}), 500
        
        mail.login(persona_email, password)
        mail.select('inbox')
        
        # Rechercher les emails non lus
        status, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()
        
        fetched_count = 0
        
        for email_id in email_ids[:50]:  # Limiter à 50 emails
            try:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                # Extraire les informations
                subject = email_message['Subject']
                if subject:
                    decoded_subject = decode_header(subject)[0]
                    if decoded_subject[1]:
                        subject = decoded_subject[0].decode(decoded_subject[1])
                    else:
                        subject = decoded_subject[0] if isinstance(decoded_subject[0], str) else decoded_subject[0].decode()
                
                sender = email_message['From']
                date = email_message['Date']
                
                # Extraire le corps du message
                body = ''
                if email_message.is_multipart():
                    for part in email_message.walk():
                        content_type = part.get_content_type()
                        if content_type == 'text/plain':
                            try:
                                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            except:
                                pass
                else:
                    try:
                        body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        body = str(email_message.get_payload())
                
                # Insérer dans la base de données
                insert_email(
                    persona_email=persona_email,
                    sender=sender or 'Inconnu',
                    subject=subject or '(Sans objet)',
                    body=body[:5000],  # Limiter la taille
                    email_type='application'
                )
                fetched_count += 1
                
            except Exception as e:
                logger.error(f"Erreur lors de la récupération d'un email: {e}")
                continue
        
        mail.close()
        mail.logout()
        
        log_message(f"{fetched_count} email(s) récupéré(s) pour {persona_email}", "success")
        return jsonify({'success': True, 'count': fetched_count})
        
    except imaplib.IMAP4.error as e:
        error_msg = str(e)
        if 'authentication failed' in error_msg.lower():
            return jsonify({'success': False, 'error': 'Identifiants incorrects'}), 401
        else:
            return jsonify({'success': False, 'error': f'Erreur IMAP: {error_msg}'}), 500
    except Exception as e:
        logger.error(f"Erreur récupération emails IMAP pour {persona_email}: {e}")
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

@app.route('/api/searches/<search_key>/history')
def api_get_search_history(search_key):
    """API pour récupérer l'historique d'exécution d'une recherche."""
    try:
        history = search_manager.get_execution_history(search_key)
        last_execution = search_manager.get_last_execution(search_key)
        return jsonify({
            'success': True,
            'history': history,
            'last_execution': last_execution,
            'total_executions': len(history)
        })
    except Exception as e:
        logger.error(f"Erreur récupération historique recherche {search_key}: {e}")
        return jsonify({'error': str(e)}), 500

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
            description=data.get('description', ''),
            standalone=data.get('standalone', False),
            salary_min=data.get('salary_min'),
            salary_max=data.get('salary_max'),
            contract_type=data.get('contract_type', []),
            experience_level=data.get('experience_level'),
            remote=data.get('remote'),
            full_time=data.get('full_time'),
            company_size=data.get('company_size'),
            tags=data.get('tags', []),
            notes=data.get('notes'),
            priority=data.get('priority', 1),
            personas_assigned=data.get('personas_assigned', []),
            personas_excluded=data.get('personas_excluded', [])
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

@app.route('/api/test-application', methods=['POST'])
def api_test_application():
    """API pour tester une candidature sur une plateforme."""
    data = request.json
    try:
        platform = data.get('platform')
        job_url = data.get('job_url')
        persona_email = data.get('persona_email')
        use_cover_letter = data.get('use_cover_letter', True)
        headless = data.get('headless', False)
        dry_run = data.get('dry_run', True)
        
        if not platform or not job_url or not persona_email:
            return jsonify({'success': False, 'error': 'Paramètres manquants'}), 400
        
        # Récupérer le persona
        persona = persona_manager.get_persona_by_email(persona_email)
        if not persona:
            return jsonify({'success': False, 'error': 'Persona non trouvé'}), 404
        
        # Récupérer ou générer le CV
        import os
        from .cv_generator import generate_cv_for_persona, load_cvs
        
        safe_email = persona_email.replace('@', '_at_').replace('.', '_')
        cv_dir = '/app/cvs'
        cv_path = os.path.join(cv_dir, f"{safe_email}_cv.pdf")
        
        if not os.path.exists(cv_path):
            # Générer le CV
            cvs_data = load_cvs()
            if cvs_data:
                cv_key = list(cvs_data.keys())[0]
                cv_data = cvs_data[cv_key]
                cv_path = generate_cv_for_persona(
                    persona_email=persona_email,
                    persona_name=persona.get('name'),
                    cv_data=cv_data
                )
        
        if not cv_path or not os.path.exists(cv_path):
            return jsonify({'success': False, 'error': 'CV non disponible'}), 400
        
        # Générer la lettre de motivation si nécessaire
        cover_letter = None
        if use_cover_letter:
            try:
                from .application_generator import generate_cover_letter
                cover_letter = generate_cover_letter(
                    job_title="Test",
                    company_name="Test Company",
                    persona_name=persona.get('name')
                )
            except Exception as e:
                logger.warning(f"Impossible de générer la lettre de motivation: {e}")
        
        # Créer un job de test
        test_job = {
            'id': 'test_' + str(int(time.time())),
            'title': 'Test Application',
            'company': 'Test Company',
            'location': 'Test Location',
            'url': job_url
        }
        
        if dry_run:
            # Mode test : simuler sans envoyer
            log_message(f"🧪 Test de candidature (DRY RUN) pour {persona.get('name')} sur {platform}", "info")
            log_message(f"   URL: {job_url}", "info")
            log_message(f"   CV: {cv_path}", "info")
            log_message(f"   Lettre de motivation: {'Oui' if cover_letter else 'Non'}", "info")
            
            return jsonify({
                'success': True,
                'message': 'Test simulé avec succès (mode DRY RUN)',
                'details': {
                    'platform': platform,
                    'persona': persona.get('name'),
                    'cv_path': cv_path,
                    'has_cover_letter': bool(cover_letter),
                    'job_url': job_url
                }
            })
        else:
            # Mode réel : tester la candidature
            from .auto_apply import apply_to_job
            
            success = apply_to_job(
                job=test_job,
                persona_email=persona_email,
                persona_name=persona.get('name'),
                cv_path=cv_path,
                cover_letter=cover_letter,
                headless=headless,
                platform=platform
            )
            
            if success:
                log_message(f"✅ Test de candidature réussi pour {persona.get('name')} sur {platform}", "success")
                return jsonify({
                    'success': True,
                    'message': 'Candidature testée avec succès',
                    'details': {
                        'platform': platform,
                        'persona': persona.get('name'),
                        'cv_path': cv_path,
                        'has_cover_letter': bool(cover_letter)
                    }
                })
            else:
                log_message(f"❌ Test de candidature échoué pour {persona.get('name')} sur {platform}", "error")
                return jsonify({
                    'success': False,
                    'error': 'La candidature a échoué. Vérifiez les logs pour plus de détails.',
                    'details': {
                        'platform': platform,
                        'persona': persona.get('name')
                    }
                }), 500
                
    except Exception as e:
        logger.error(f"Erreur test candidature: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

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
            
            # Vérifier si toutes les recherches sont standalone
            all_standalone = all(search_manager.get_search(key).get('standalone', False) 
                               for key in search_keys 
                               if search_manager.get_search(key))
            
            # Charger les personas seulement si nécessaire
            personas = {}
            cv_paths = {}
            if not all_standalone:
                all_personas = load_personas()
                if selected_personas and len(selected_personas) > 0:
                    personas = {k: v for k, v in all_personas.items() if v['email'] in selected_personas}
                else:
                    personas = all_personas
                
                log_message(f"   {len(personas)} personas chargés", "info")
                
                # Générer les CVs seulement si nécessaire
                log_message("📄 Génération des CVs...", "info")
                app_state['current_step'] = 'generating_cvs'
                socketio.emit('status_update', {'step': 'generating_cvs', 'is_running': True})
                cv_paths = generate_cvs_from_json()
                log_message(f"   {len(cv_paths)} CVs générés", "success")
            else:
                log_message("   🔍 Mode standalone: pas de personas nécessaires", "info")
            
            # Pour chaque recherche
            for search_key in search_keys:
                if not app_state['is_running']:
                    break
                
                search = search_manager.get_search(search_key)
                if not search or not search.get('is_active', search.get('enabled', True)):
                    continue
                
                # Initialiser le suivi de cette recherche
                import time as time_module
                search_start_time = time_module.time()
                search_steps = []
                search_errors = []
                search_jobs_found = 0
                search_jobs_filtered = 0
                search_applications_sent = 0
                search_applications_failed = 0
                search_personas_used = []
                
                try:
                    log_message(f"\n{'='*60}", "info")
                    log_message(f"🔍 DÉBUT RECHERCHE: {search['name']}", "info")
                    log_message(f"   Requête: {search['query']} | Localisation: {search['location']}", "info")
                    search_steps.append({'step': 'start', 'message': f"Début de la recherche: {search['name']}", 'timestamp': datetime.now().isoformat()})
                    
                    app_state['current_step'] = 'scraping'
                    socketio.emit('status_update', {'step': 'scraping', 'is_running': True, 'search_name': search['name']})
                    
                    # Étape 1: Scraping des offres
                    log_message("📡 Étape 1/4: Scraping des offres d'emploi...", "info")
                    search_steps.append({'step': 'scraping', 'message': "Scraping des offres d'emploi", 'timestamp': datetime.now().isoformat()})
                    
                    jobs = scrape_indeed(query=search['query'], location=search['location'], max_results=search.get('max_results', 50))
                    search_jobs_found = len(jobs)
                    log_message(f"   ✅ {len(jobs)} offres trouvées et enregistrées", "success")
                    search_steps.append({'step': 'scraping_complete', 'message': f"{len(jobs)} offres trouvées", 'timestamp': datetime.now().isoformat()})
                    
                    for job in jobs:
                        insert_job(job)
                    
                    app_state['jobs_found'] += len(jobs)
                    
                    # Si c'est une recherche standalone, on arrête ici
                    if search.get('standalone', False):
                        log_message("   ✅ Recherche standalone terminée: offres ajoutées à la base de données", "success")
                        search_steps.append({'step': 'standalone_complete', 'message': 'Recherche standalone terminée', 'timestamp': datetime.now().isoformat()})
                        
                        search_duration = time_module.time() - search_start_time
                        search_manager.mark_run(search_key, {
                            'jobs_found': search_jobs_found,
                            'jobs_filtered': 0,
                            'applications_sent': 0,
                            'applications_failed': 0,
                            'personas_used': [],
                            'errors': search_errors,
                            'steps': search_steps,
                            'duration_seconds': int(search_duration)
                        })
                        continue
                    
                    # Étape 2: Filtrage des offres
                    log_message("🔎 Étape 2/4: Filtrage des offres...", "info")
                    search_steps.append({'step': 'filtering', 'message': 'Filtrage des offres', 'timestamp': datetime.now().isoformat()})
                    app_state['current_step'] = 'filtering'
                    socketio.emit('status_update', {'step': 'filtering', 'is_running': True, 'search_name': search['name']})
                    
                    # Étape 3: Génération des CVs (déjà fait, mais on le note)
                    log_message("📄 Étape 3/4: CVs prêts pour candidature", "info")
                    search_steps.append({'step': 'cvs_ready', 'message': f"{len(cv_paths)} CVs disponibles", 'timestamp': datetime.now().isoformat()})
                    
                    # Étape 4: Candidatures
                    log_message("📝 Étape 4/4: Envoi des candidatures...", "info")
                    search_steps.append({'step': 'applying', 'message': 'Début des candidatures', 'timestamp': datetime.now().isoformat()})
                    app_state['current_step'] = 'applying'
                    socketio.emit('status_update', {'step': 'applying', 'is_running': True, 'search_name': search['name']})
                    
                    # Déterminer les personas à utiliser pour cette recherche
                    search_personas = personas.copy()
                    
                    # Si des personas sont assignés à cette recherche, n'utiliser que ceux-là
                    if search.get('personas_assigned') and len(search.get('personas_assigned', [])) > 0:
                        assigned_emails = search.get('personas_assigned', [])
                        search_personas = {k: v for k, v in personas.items() if v['email'] in assigned_emails}
                        log_message(f"   👥 {len(search_personas)} personas assignés à cette recherche", "info")
                    
                    # Exclure les personas spécifiés
                    if search.get('personas_excluded') and len(search.get('personas_excluded', [])) > 0:
                        excluded_emails = search.get('personas_excluded', [])
                        search_personas = {k: v for k, v in search_personas.items() if v['email'] not in excluded_emails}
                        log_message(f"   🚫 {len(excluded_emails)} personas exclus de cette recherche", "info")
                    
                    if not search_personas:
                        log_message(f"   ⚠️  Aucun persona disponible pour cette recherche", "warning")
                        continue
                    
                    import random
                    persona_list = list(search_personas.items())
                    random.shuffle(persona_list)
                    
                    for persona_key, persona_info in persona_list:
                        if not app_state['is_running']:
                            break
                        
                        persona_email = persona_info['email']
                        persona_name = persona_info['name']
                        
                        # Chercher un CV spécifique à la recherche
                        import os
                        cv_info = get_persona_cv(persona_email, search_key=search_key)
                        if cv_info and os.path.exists(cv_info['cv_path']):
                            cv_path = cv_info['cv_path']
                            cv_id = cv_info['cv_id']
                        elif persona_email in cv_paths:
                            # Utiliser le CV par défaut
                            cv_path = cv_paths[persona_email]
                            cv_id = 'default'
                        else:
                            log_message(f"   ⚠️  {persona_name}: CV non disponible", "warning")
                            continue
                        
                        log_message(f"   👤 Traitement de {persona_name} ({persona_email})...", "info")
                        
                        filtered_jobs = filter_jobs(
                            title_keywords=search.get('title_keywords', []),
                            location_keywords=search.get('location_keywords', []),
                            persona_email=persona_email,
                            exclude_keywords=search.get('exclude_keywords', [])
                        )
                        
                        search_jobs_filtered += len(filtered_jobs)
                        
                        if not filtered_jobs:
                            log_message(f"      ℹ️  Aucune offre correspondante après filtrage", "info")
                            continue
                        
                        jobs_to_apply = filtered_jobs[:max_per_persona]
                        log_message(f"      📋 {len(jobs_to_apply)} offre(s) à traiter (sur {len(filtered_jobs)} filtrées)", "info")
                        
                        persona_applications_sent = 0
                        persona_applications_failed = 0
                        
                        for job in jobs_to_apply:
                            if not app_state['is_running']:
                                break
                            
                            try:
                                cover_letter = None
                                if use_cover_letter:
                                    try:
                                        cover_letter = generate_cover_letter(job)
                                        log_message(f"      📄 Lettre de motivation générée pour: {job['title']}", "info")
                                    except Exception as e:
                                        log_message(f"      ⚠️  Erreur génération lettre: {str(e)}", "warning")
                                        search_errors.append(f"Génération lettre pour {job['title']}: {str(e)}")
                                
                                application_id = insert_application(
                                    job_id=job['id'],
                                    persona_email=persona_email,
                                    persona_name=persona_name,
                                    cv_path=cv_path,
                                    cv_id=cv_id,
                                    search_key=search_key,
                                    cover_letter=cover_letter,
                                    status='pending'
                                )
                                
                                if not application_id:
                                    log_message(f"      ❌ Erreur: Impossible d'enregistrer la candidature", "error")
                                    search_errors.append(f"Enregistrement candidature {job['title']} échoué")
                                    continue
                                
                                log_message(f"      📝 Candidature: {job['title']} chez {job['company']} ({job.get('location', 'N/A')})", "info")
                                
                                # Détecter la plateforme depuis l'URL
                                from .platform_handlers import detect_platform
                                job_platform = detect_platform(job.get('url', ''))
                                
                                success = apply_to_job(
                                    job=job,
                                    persona_email=persona_email,
                                    persona_name=persona_name,
                                    cv_path=cv_path,
                                    cover_letter=cover_letter,
                                    headless=headless,
                                    platform=job_platform
                                )
                                
                                if success:
                                    update_application_status(job['id'], persona_email, 'sent')
                                    search_applications_sent += 1
                                    persona_applications_sent += 1
                                    app_state['applications_sent'] += 1
                                    log_message(f"      ✅ Candidature envoyée avec succès", "success")
                                else:
                                    update_application_status(job['id'], persona_email, 'failed')
                                    search_applications_failed += 1
                                    persona_applications_failed += 1
                                    app_state['applications_failed'] += 1
                                    log_message(f"      ❌ Échec de l'envoi de la candidature", "error")
                                    search_errors.append(f"Échec candidature {persona_name} - {job['title']}")
                                
                                update_stats()
                                delay = random.uniform(delay_min, delay_max)
                                time.sleep(delay)
                                
                            except Exception as e:
                                log_message(f"      ❌ Erreur lors de la candidature: {str(e)}", "error")
                                search_errors.append(f"Erreur candidature {persona_name} - {job.get('title', 'N/A')}: {str(e)}")
                                search_applications_failed += 1
                                app_state['applications_failed'] += 1
                                continue
                        
                        if persona_applications_sent > 0 or persona_applications_failed > 0:
                            search_personas_used.append({
                                'email': persona_email,
                                'name': persona_name,
                                'applications_sent': persona_applications_sent,
                                'applications_failed': persona_applications_failed
                            })
                            log_message(f"      📊 Résumé {persona_name}: {persona_applications_sent} envoyées, {persona_applications_failed} échouées", "info")
                    
                    search_steps.append({'step': 'applying_complete', 'message': f'Candidatures terminées: {search_applications_sent} envoyées, {search_applications_failed} échouées', 'timestamp': datetime.now().isoformat()})
                    
                    search_duration = time_module.time() - search_start_time
                    log_message(f"\n📊 RÉSUMÉ RECHERCHE: {search['name']}", "info")
                    log_message(f"   ⏱️  Durée: {int(search_duration)} secondes", "info")
                    log_message(f"   📡 Offres trouvées: {search_jobs_found}", "info")
                    log_message(f"   🔎 Offres filtrées: {search_jobs_filtered}", "info")
                    log_message(f"   ✅ Candidatures envoyées: {search_applications_sent}", "success")
                    log_message(f"   ❌ Candidatures échouées: {search_applications_failed}", "error" if search_applications_failed > 0 else "info")
                    log_message(f"   👥 Personas utilisés: {len(search_personas_used)}", "info")
                    if search_errors:
                        log_message(f"   ⚠️  Erreurs: {len(search_errors)}", "warning")
                    log_message(f"{'='*60}\n", "info")
                    
                    # Enregistrer les détails de l'exécution
                    search_manager.mark_run(search_key, {
                        'jobs_found': search_jobs_found,
                        'jobs_filtered': search_jobs_filtered,
                        'applications_sent': search_applications_sent,
                        'applications_failed': search_applications_failed,
                        'personas_used': search_personas_used,
                        'errors': search_errors,
                        'steps': search_steps,
                        'duration_seconds': int(search_duration)
                    })
                    
                except Exception as e:
                    log_message(f"❌ ERREUR lors de l'exécution de la recherche {search['name']}: {str(e)}", "error")
                    search_errors.append(f"Erreur fatale: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    
                    search_duration = time_module.time() - search_start_time
                    search_manager.mark_run(search_key, {
                        'jobs_found': search_jobs_found,
                        'jobs_filtered': search_jobs_filtered,
                        'applications_sent': search_applications_sent,
                        'applications_failed': search_applications_failed,
                        'personas_used': search_personas_used,
                        'errors': search_errors,
                        'steps': search_steps,
                        'duration_seconds': int(search_duration)
                    })
            
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
    try:
        unapplied = request.args.get('unapplied', 'false').lower() == 'true'
        persona_email = request.args.get('persona_email')
        limit = request.args.get('limit', 1000, type=int)
        
        if unapplied:
            # Récupérer seulement les offres non candidatées
            jobs = get_unapplied_jobs(persona_email)
            if limit:
                jobs = jobs[:limit]
        else:
            # Récupérer toutes les offres
            jobs = get_all_jobs(limit=limit)
        
        # S'assurer que les jobs sont au format dictionnaire
        jobs_list = []
        for job in jobs:
            if isinstance(job, dict):
                # Vérifier si le job a déjà été candidaté
                job_id = job.get('id')
                applied = False
                if job_id:
                    conn = sqlite3.connect(get_db_path())
                    c = conn.cursor()
                    c.execute("SELECT COUNT(*) FROM applications WHERE job_id = ?", (job_id,))
                    applied = c.fetchone()[0] > 0
                    conn.close()
                
                job_dict = {
                    'id': job.get('id'),
                    'title': job.get('title'),
                    'company': job.get('company'),
                    'location': job.get('location'),
                    'url': job.get('url'),
                    'platform': job.get('platform', 'indeed'),
                    'description': job.get('description'),
                    'created_at': job.get('created_at'),
                    'applied': applied
                }
                jobs_list.append(job_dict)
            else:
                # Format tuple (ancien format)
                job_dict = {
                    'id': job[0] if len(job) > 0 else None,
                    'title': job[1] if len(job) > 1 else None,
                    'company': job[2] if len(job) > 2 else None,
                    'location': job[3] if len(job) > 3 else None,
                    'url': job[4] if len(job) > 4 else None,
                    'platform': job[5] if len(job) > 5 else 'indeed',
                    'description': job[5] if len(job) > 5 else None,
                    'created_at': job[6] if len(job) > 6 else None,
                    'applied': False
                }
                # Vérifier si le job a été candidaté
                if job_dict['id']:
                    conn = sqlite3.connect(get_db_path())
                    c = conn.cursor()
                    c.execute("SELECT COUNT(*) FROM applications WHERE job_id = ?", (job_dict['id'],))
                    job_dict['applied'] = c.fetchone()[0] > 0
                    conn.close()
                jobs_list.append(job_dict)
        
        return jsonify(jobs_list)
    except Exception as e:
        logger.error(f"Erreur API jobs: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """Retourne les statistiques globales et de session."""
    # Récupérer les stats de la base de données
    db_stats = get_statistics()
    
    # Ajouter les stats de session depuis app_state
    stats = {
        **db_stats,
        # Statistiques de session actuelle
        'jobs_found': app_state.get('jobs_found', 0),
        'applications_sent': app_state.get('applications_sent', 0),
        'applications_failed': app_state.get('applications_failed', 0)
    }
    
    # Sauvegarder dans l'historique
    try:
        insert_historical_stat(db_stats)
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des stats: {e}")
    
    return jsonify(stats)

@app.route('/api/stats/historical')
def api_historical_stats():
    """Récupère les statistiques historiques."""
    try:
        days = request.args.get('days', 30, type=int)
        exclude_test = request.args.get('exclude_test', 'false').lower() == 'true'
        
        stats = get_historical_stats(days=days, exclude_test=exclude_test)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stats historiques: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs')
def api_logs():
    """Récupère les logs depuis la base de données."""
    try:
        limit = request.args.get('limit', 1000, type=int)
        level = request.args.get('level', None)
        category = request.args.get('category', None)
        exclude_test = request.args.get('exclude_test', 'false').lower() == 'true'
        
        logs = get_logs(limit=limit, level=level, category=category, exclude_test=exclude_test)
        return jsonify(logs)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des logs: {e}")
        return jsonify({'error': str(e)}), 500

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

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Sert les fichiers statiques."""
    try:
        static_dir = '/app/static'
        file_path = os.path.join(static_dir, filename)
        
        # Vérifier que le fichier existe et est un fichier (pas un dossier)
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            logger.warning(f"Fichier statique non trouvé: {file_path}")
            return "Fichier statique non trouvé", 404
        
        # Déterminer le type MIME selon l'extension
        mimetype = None
        if filename.endswith('.js'):
            mimetype = 'application/javascript; charset=utf-8'
        elif filename.endswith('.css'):
            mimetype = 'text/css; charset=utf-8'
        elif filename.endswith('.png'):
            mimetype = 'image/png'
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            mimetype = 'image/jpeg'
        elif filename.endswith('.svg'):
            mimetype = 'image/svg+xml'
        elif filename.endswith('.json'):
            mimetype = 'application/json'
        
        return send_from_directory(static_dir, filename, mimetype=mimetype)
    except Exception as e:
        logger.error(f"Erreur serveur fichier statique {filename}: {e}")
        return f"Erreur: {str(e)}", 500

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

@app.route('/api/test-data/delete', methods=['POST'])
def api_delete_test_data():
    """Supprime toutes les données de test."""
    try:
        result = delete_test_data()
        if result:
            log_message(f"Données de test supprimées: {result}", "info")
            return jsonify({'success': True, 'deleted': result})
        return jsonify({'error': 'Erreur lors de la suppression'}), 500
    except Exception as e:
        logger.error(f"Erreur lors de la suppression des données de test: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-data/mark', methods=['POST'])
def api_mark_test_data():
    """Marque des données comme test ou non."""
    try:
        data = request.json
        table = data.get('table')  # 'jobs', 'applications', 'emails', 'logs'
        ids = data.get('ids', [])
        is_test = data.get('is_test', True)
        
        if not table or not ids:
            return jsonify({'error': 'Table et ids requis'}), 400
        
        count = mark_as_test_data(table, ids, is_test)
        log_message(f"{count} enregistrement(s) marqué(s) comme {'test' if is_test else 'production'}", "info")
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        logger.error(f"Erreur lors du marquage des données: {e}")
        return jsonify({'error': str(e)}), 500

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

