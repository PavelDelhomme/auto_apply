#!/usr/bin/env python3
"""
Script pour tester les connexions email de tous les personas
et générer un rapport détaillé
"""

import json
import os
import sys
import imaplib
import socket
import time
import threading
import random
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ajouter le répertoire parent au path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.join(project_root, 'src'))

# Ajouter le chemin dotfiles pour utiliser progress_utils
dotfiles_utils = os.path.expanduser('~/dotfiles/core/utils')
if os.path.exists(dotfiles_utils):
    sys.path.insert(0, dotfiles_utils)

# Définir le chemin du fichier personas.json
# Dans Docker, le chemin est /app, localement c'est le répertoire parent
if os.path.exists('/app/config/personas.json'):
    # On est dans Docker
    personas_file = '/app/config/personas.json'
    project_root = '/app'
else:
    # On est en local
    personas_file = os.path.join(project_root, 'config', 'personas.json')

from persona_manager import PersonaManager

# Importer ProgressBar depuis dotfiles si disponible, sinon utiliser la fonction locale
# Le module progress_utils est dans ~/dotfiles/core/utils/
try:
    from progress_utils import ProgressBar
    USE_PROGRESS_BAR = True
except ImportError:
    # Fallback: utiliser la fonction locale si dotfiles n'est pas disponible (ex: dans Docker)
    USE_PROGRESS_BAR = False

# Créer une instance avec le bon chemin
persona_manager = PersonaManager(personas_file=personas_file)

def get_imap_server(email_domain, email_config=None):
    """Détermine le serveur IMAP selon le domaine."""
    if email_config and email_config.get('imap_server'):
        return email_config.get('imap_server'), email_config.get('imap_port', 993)
    
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
        'numericable.fr': 'imap.numericable.fr',
        'protonmail.com': '127.0.0.1',  # ProtonMail nécessite ProtonMail Bridge
        'proton.me': '127.0.0.1'
    }
    
    imap_server = imap_servers.get(email_domain)
    if not imap_server:
        imap_server = f'imap.{email_domain}'
    
    return imap_server, 993

def get_password_for_persona(persona, persona_manager, all_personas):
    """Récupère le mot de passe pour un persona, en gérant les alias."""
    password = persona.get('password')
    email = persona.get('email', '')
    email_domain = email.split('@')[1].lower() if '@' in email else ''
    
    if not password and persona.get('alias'):
        parent_email = persona.get('parent')
        
        if email_domain in ['gmx.com', 'gmx.fr', 'caramail.com', 'caramail.fr'] and parent_email:
            parent_domain = parent_email.split('@')[1].lower() if '@' in parent_email else ''
            if parent_domain in ['gmx.com', 'gmx.fr', 'caramail.com', 'caramail.fr']:
                parent_persona = persona_manager.get_persona_by_email(parent_email)
                if parent_persona:
                    parent_password = parent_persona.get('password')
                    if not parent_password and parent_persona.get('alias') and parent_persona.get('parent'):
                        # Remonter la chaîne
                        current_parent = parent_persona.get('parent')
                        max_depth = 10
                        depth = 0
                        while current_parent and depth < max_depth:
                            current_parent_persona = persona_manager.get_persona_by_email(current_parent)
                            if current_parent_persona:
                                current_parent_password = current_parent_persona.get('password')
                                if current_parent_password:
                                    return current_parent_password, f"parent chain ({current_parent})"
                                if current_parent_persona.get('alias') and current_parent_persona.get('parent'):
                                    current_parent = current_parent_persona.get('parent')
                                else:
                                    break
                            else:
                                break
                            depth += 1
                    elif parent_password:
                        return parent_password, f"parent GMX/CaraMail ({parent_email})"
            else:
                # Chercher un persona principal GMX/CaraMail
                gmx_principals = []
                for p in all_personas.values():
                    if (not p.get('alias', False) and 
                        p.get('email', '').split('@')[1].lower() in ['gmx.com', 'gmx.fr', 'caramail.com', 'caramail.fr'] and 
                        p.get('password')):
                        gmx_principals.append(p)
                
                if gmx_principals:
                    return gmx_principals[0].get('password'), f"principal GMX/CaraMail ({gmx_principals[0].get('email')})"
        else:
            if parent_email:
                parent_persona = persona_manager.get_persona_by_email(parent_email)
                if parent_persona:
                    return parent_persona.get('password'), f"parent ({parent_email})"
    
    if password:
        return password, "direct"
    return None, "none"

def test_email_connection(persona_key, persona, persona_manager, all_personas):
    """Teste la connexion email pour un persona."""
    email = persona.get('email')
    if not email:
        return {
            'persona_key': persona_key,
            'name': persona.get('name', 'N/A'),
            'email': 'N/A',
            'success': False,
            'error': 'Email non configuré',
            'is_alias': persona.get('alias', False),
            'parent': persona.get('parent'),
            'password_source': 'none',
            'requires_imap_activation': False
        }
    
    email_domain = email.split('@')[1].lower()
    start_time = time.time()
    
    # Récupérer le mot de passe
    password, password_source = get_password_for_persona(persona, persona_manager, all_personas)
    
    if not password:
        return {
            'persona_key': persona_key,
            'name': persona.get('name', 'N/A'),
            'email': email,
            'success': False,
            'error': 'Mot de passe non configuré',
            'is_alias': persona.get('alias', False),
            'parent': persona.get('parent'),
            'password_source': password_source,
            'requires_imap_activation': False
        }
    
    # Déterminer le serveur IMAP
    email_config = persona.get('email_config', {})
    imap_server, imap_port = get_imap_server(email_domain, email_config)
    
    try:
        # Essayer avec SSL d'abord avec timeout
        try:
            mail = imaplib.IMAP4_SSL(imap_server, imap_port, timeout=10)
        except Exception as ssl_error:
            # Si SSL échoue, essayer sans SSL (port 143)
            try:
                mail = imaplib.IMAP4(imap_server, 143, timeout=10)
                imap_port = 143
            except Exception as e:
                return {
                    'persona_key': persona_key,
                    'name': persona.get('name', 'N/A'),
                    'email': email,
                    'success': False,
                    'error': f'Impossible de se connecter au serveur {imap_server}: {str(e)}',
                    'is_alias': persona.get('alias', False),
                    'parent': persona.get('parent'),
                    'password_source': password_source,
                    'server': imap_server,
                    'port': imap_port,
                    'requires_imap_activation': False
                }
        
        # Timeout pour les opérations IMAP
        mail.sock.settimeout(10)
        mail.login(email, password)
        mail.select('inbox')
        mail.close()
        mail.logout()
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            'persona_key': persona_key,
            'name': persona.get('name', 'N/A'),
            'email': email,
            'success': True,
            'message': 'Connexion réussie',
            'is_alias': persona.get('alias', False),
            'parent': persona.get('parent'),
            'password_source': password_source,
            'server': imap_server,
            'port': imap_port,
            'response_time': response_time,
            'requires_imap_activation': False
        }
        
    except imaplib.IMAP4.error as e:
        error_msg = str(e)
        response_time = round((time.time() - start_time) * 1000, 2)
        
        requires_imap_activation = email_domain in ['gmx.com', 'gmx.fr', 'caramail.com', 'caramail.fr']
        
        if 'authentication failed' in error_msg.lower() or 'invalid credentials' in error_msg.lower():
            error = 'Identifiants incorrects'
        elif 'login' in error_msg.lower() or 'auth' in error_msg.lower():
            error = f'Erreur d\'authentification: {error_msg}'
            if requires_imap_activation:
                error += ' (IMAP peut être désactivé)'
        else:
            error = f'Erreur IMAP: {error_msg}'
        
        return {
            'persona_key': persona_key,
            'name': persona.get('name', 'N/A'),
            'email': email,
            'success': False,
            'error': error,
            'is_alias': persona.get('alias', False),
            'parent': persona.get('parent'),
            'password_source': password_source,
            'server': imap_server,
            'port': imap_port,
            'response_time': response_time,
            'requires_imap_activation': requires_imap_activation
        }
    except socket.timeout as e:
        return {
            'persona_key': persona_key,
            'name': persona.get('name', 'N/A'),
            'email': email,
            'success': False,
            'error': f'Timeout: connexion au serveur {imap_server} a pris trop de temps (>10s)',
            'is_alias': persona.get('alias', False),
            'parent': persona.get('parent'),
            'password_source': password_source,
            'server': imap_server,
            'port': imap_port,
            'requires_imap_activation': False
        }
    except socket.gaierror as e:
        return {
            'persona_key': persona_key,
            'name': persona.get('name', 'N/A'),
            'email': email,
            'success': False,
            'error': f'Impossible de résoudre le nom du serveur {imap_server}',
            'is_alias': persona.get('alias', False),
            'parent': persona.get('parent'),
            'password_source': password_source,
            'server': imap_server,
            'port': imap_port,
            'requires_imap_activation': False
        }
    except Exception as e:
        error_msg = str(e)
        if 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
            error_msg = f'Timeout: {error_msg}'
        return {
            'persona_key': persona_key,
            'name': persona.get('name', 'N/A'),
            'email': email,
            'success': False,
            'error': f'Erreur: {error_msg}',
            'is_alias': persona.get('alias', False),
            'parent': persona.get('parent'),
            'password_source': password_source,
            'server': imap_server,
            'port': imap_port,
            'requires_imap_activation': False
        }

def main():
    print("🔍 Test de connexion email pour tous les personas")
    print("="*60)
    
    # Utiliser l'instance globale
    all_personas = persona_manager.get_all_personas()
    
    if not all_personas:
        print("❌ Aucun persona trouvé")
        return
    
    total = len(all_personas)
    print(f"📊 {total} persona(s) à tester\n")
    
    results = []
    start_time = time.time()
    
    # Variables partagées pour la progression (protégées par un lock)
    progress_lock = threading.Lock()
    completed = 0
    successful_count = 0
    failed_count = 0
    
    # Utiliser ProgressBar depuis dotfiles si disponible
    if USE_PROGRESS_BAR:
        progress = ProgressBar(total, "Test de connexions email")
    else:
        # Fonction locale de fallback si dotfiles n'est pas disponible
        def print_progress(completed, total, successful, failed, elapsed_time):
            percentage = (completed / total) * 100
            bar_length = 40
            filled = int(bar_length * completed / total)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            # Estimation du temps restant
            if completed > 0:
                avg_time_per_persona = elapsed_time / completed
                remaining = total - completed
                estimated_remaining = avg_time_per_persona * remaining
                eta = timedelta(seconds=int(estimated_remaining))
                elapsed_str = timedelta(seconds=int(elapsed_time))
                time_info = f"⏱️  {elapsed_str} écoulé | ~{eta} restant"
            else:
                time_info = "⏱️  Calcul en cours..."
            
            # Statistiques
            stats = f"✅ {successful} | ❌ {failed}"
            
            # Afficher la barre de progression
            sys.stdout.write(f"\r[{completed}/{total}] {percentage:.1f}% |{bar}| {stats} | {time_info}")
            sys.stdout.flush()
    
    # Thread pour mettre à jour la barre de progression régulièrement (toutes les secondes)
    update_stop = threading.Event()
    
    def update_progress_periodically():
        """Met à jour la barre de progression toutes les secondes."""
        while not update_stop.is_set():
            time.sleep(1.0)  # Mettre à jour toutes les secondes
            if update_stop.is_set():
                break
            
            with progress_lock:
                current_completed = completed
                current_successful = successful_count
                current_failed = failed_count
                current_elapsed = time.time() - start_time
            
            if USE_PROGRESS_BAR:
                # Utiliser ProgressBar depuis dotfiles
                progress.update(current_completed, current_successful, current_failed, force=True)
            else:
                # Utiliser la fonction locale
                print_progress(current_completed, total, current_successful, current_failed, current_elapsed)
    
    # Démarrer le thread de mise à jour périodique
    progress_thread = threading.Thread(target=update_progress_periodically, daemon=True)
    progress_thread.start()
    
    # Tester tous les personas en parallèle (max 3 simultanés pour éviter les blocages GMX)
    # Réduit à 3 pour éviter les blocages de comptes après trop de tentatives
    # Ajout d'un délai aléatoire entre les soumissions pour espacer les connexions
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}
        for idx, (persona_key, persona) in enumerate(all_personas.items()):
            # Ajouter un petit délai aléatoire (0-0.5s) pour espacer les connexions
            if idx > 0:
                time.sleep(random.uniform(0.1, 0.5))
            future = executor.submit(test_email_connection, persona_key, persona, persona_manager, all_personas)
            futures[future] = (persona_key, persona.get('name', 'N/A'))
        
        for future in as_completed(futures):
            persona_key, persona_name = futures[future]
            elapsed_time = time.time() - start_time
            
            try:
                result = future.result()
                results.append(result)
                with progress_lock:
                    completed += 1
                    if result['success']:
                        successful_count += 1
                    else:
                        failed_count += 1
                    
                    # Mettre à jour immédiatement à chaque complétion
                    if USE_PROGRESS_BAR:
                        # Utiliser ProgressBar depuis dotfiles
                        progress.update(completed, successful_count, failed_count, force=True)
                    else:
                        # Utiliser la fonction locale
                        print_progress(completed, total, successful_count, failed_count, elapsed_time)
            except Exception as e:
                with progress_lock:
                    completed += 1
                    failed_count += 1
                results.append({
                    'persona_key': persona_key,
                    'name': persona_name,
                    'email': 'N/A',
                    'success': False,
                    'error': str(e),
                    'is_alias': False,
                    'parent': None,
                    'password_source': 'none',
                    'requires_imap_activation': False
                })
                # Mettre à jour après l'erreur aussi
                with progress_lock:
                    if USE_PROGRESS_BAR:
                        progress.update(completed, successful_count, failed_count, force=True)
                    else:
                        print_progress(completed, total, successful_count, failed_count, time.time() - start_time)
    
    # Arrêter le thread de mise à jour périodique
    update_stop.set()
    progress_thread.join(timeout=2.0)  # Attendre max 2 secondes
    
    # Afficher la progression finale
    with progress_lock:
        if USE_PROGRESS_BAR:
            progress.finish(show_summary=False)  # On affichera le résumé nous-mêmes
        else:
            print_progress(completed, total, successful_count, failed_count, time.time() - start_time)
            print()  # Nouvelle ligne après la barre de progression
    
    # Générer le rapport
    report_path = generate_report(results)
    
    # Afficher le résumé
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    requires_imap = [r for r in failed if r.get('requires_imap_activation')]
    no_password = [r for r in failed if 'Mot de passe non configuré' in r.get('error', '')]
    wrong_credentials = [r for r in failed if 'Identifiants incorrects' in r.get('error', '')]
    
    total_time = time.time() - start_time
    total_time_str = timedelta(seconds=int(total_time))
    
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ")
    print(f"{'='*60}")
    print(f"⏱️  Temps total: {total_time_str}")
    print(f"✅ Réussis: {len(successful)} ({len(successful)/total*100:.1f}%)")
    print(f"❌ Échoués: {len(failed)} ({len(failed)/total*100:.1f}%)")
    print(f"\n📋 Détail des échecs:")
    print(f"   🔒 IMAP désactivé (GMX/CaraMail): {len(requires_imap)}")
    print(f"   🔑 Mot de passe manquant: {len(no_password)}")
    print(f"   ❌ Identifiants incorrects: {len(wrong_credentials)}")
    print(f"   ⚠️  Autres erreurs: {len(failed) - len(requires_imap) - len(no_password) - len(wrong_credentials)}")
    print(f"\n📄 Rapport détaillé généré dans: {report_path}")

def generate_report(results):
    """Génère un rapport Markdown détaillé."""
    # Dans Docker, sauvegarder dans /app, sinon dans le répertoire parent
    if os.path.exists('/app'):
        report_path = '/app/EMAIL_STATUS_REPORT.md'
    else:
        report_path = os.path.join(os.path.dirname(__file__), '..', 'EMAIL_STATUS_REPORT.md')
    
    return report_path
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    requires_imap = [r for r in failed if r.get('requires_imap_activation')]
    no_password = [r for r in failed if 'Mot de passe non configuré' in r.get('error', '')]
    wrong_credentials = [r for r in failed if 'Identifiants incorrects' in r.get('error', '')]
    other_errors = [r for r in failed if r not in requires_imap and r not in no_password and r not in wrong_credentials]
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 📧 Rapport de Statut des Connexions Email\n\n")
        f.write(f"**Date de génération:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Résumé
        f.write("## 📊 Résumé\n\n")
        f.write(f"- ✅ **Réussis:** {len(successful)} persona(s)\n")
        f.write(f"- ❌ **Échoués:** {len(failed)} persona(s)\n")
        f.write(f"  - 🔒 IMAP désactivé (GMX/CaraMail): {len(requires_imap)}\n")
        f.write(f"  - 🔑 Mot de passe manquant: {len(no_password)}\n")
        f.write(f"  - ❌ Identifiants incorrects: {len(wrong_credentials)}\n")
        f.write(f"  - ⚠️ Autres erreurs: {len(other_errors)}\n\n")
        f.write("---\n\n")
        
        # Personas fonctionnels
        f.write("## ✅ Personas avec Connexion Fonctionnelle\n\n")
        if successful:
            f.write("| Nom | Email | Type | Parent | Serveur | Temps (ms) |\n")
            f.write("|-----|-------|------|--------|---------|------------|\n")
            for r in sorted(successful, key=lambda x: x['name']):
                persona_type = "Alias" if r['is_alias'] else "Principal"
                parent = r.get('parent', '-')
                server = f"{r.get('server', 'N/A')}:{r.get('port', 'N/A')}"
                response_time = r.get('response_time', 'N/A')
                f.write(f"| {r['name']} | {r['email']} | {persona_type} | {parent} | {server} | {response_time} |\n")
        else:
            f.write("Aucun persona avec connexion fonctionnelle.\n")
        f.write("\n---\n\n")
        
        # Personas nécessitant activation IMAP
        if requires_imap:
            f.write("## 🔒 Personas Nécessitant l'Activation IMAP (GMX/CaraMail)\n\n")
            f.write("⚠️ **IMPORTANT:** Ces personas nécessitent l'activation manuelle de IMAP dans les paramètres de la boîte mail.\n\n")
            f.write("### 📋 Instructions pour Activer IMAP:\n\n")
            f.write("1. Connectez-vous à https://www.gmx.fr ou https://www.caramail.com\n")
            f.write("2. Allez dans **Paramètres** / **Réglages** de votre boîte mail\n")
            f.write("3. Cherchez **\"Accès par programme\"** ou **\"IMAP/POP3\"** ou **\"Paramètres de messagerie\"**\n")
            f.write("4. Activez l'accès **IMAP** et **SMTP**\n")
            f.write("5. Réessayez la connexion\n\n")
            f.write("| Nom | Email | Type | Parent | Source Mot de Passe |\n")
            f.write("|-----|-------|------|--------|---------------------|\n")
            for r in sorted(requires_imap, key=lambda x: x['name']):
                persona_type = "Alias" if r['is_alias'] else "Principal"
                parent = r.get('parent', '-')
                password_source = r.get('password_source', 'N/A')
                f.write(f"| {r['name']} | {r['email']} | {persona_type} | {parent} | {password_source} |\n")
            f.write("\n---\n\n")
        
        # Personas sans mot de passe
        if no_password:
            f.write("## 🔑 Personas Sans Mot de Passe Configuré\n\n")
            f.write("| Nom | Email | Type | Parent |\n")
            f.write("|-----|-------|------|--------|\n")
            for r in sorted(no_password, key=lambda x: x['name']):
                persona_type = "Alias" if r['is_alias'] else "Principal"
                parent = r.get('parent', '-')
                f.write(f"| {r['name']} | {r['email']} | {persona_type} | {parent} |\n")
            f.write("\n---\n\n")
        
        # Personas avec identifiants incorrects
        if wrong_credentials:
            f.write("## ❌ Personas avec Identifiants Incorrects\n\n")
            f.write("| Nom | Email | Type | Parent | Source Mot de Passe | Serveur |\n")
            f.write("|-----|-------|------|--------|---------------------|----------|\n")
            for r in sorted(wrong_credentials, key=lambda x: x['name']):
                persona_type = "Alias" if r['is_alias'] else "Principal"
                parent = r.get('parent', '-')
                password_source = r.get('password_source', 'N/A')
                server = f"{r.get('server', 'N/A')}:{r.get('port', 'N/A')}"
                f.write(f"| {r['name']} | {r['email']} | {persona_type} | {parent} | {password_source} | {server} |\n")
            f.write("\n---\n\n")
        
        # Autres erreurs
        if other_errors:
            f.write("## ⚠️ Autres Erreurs\n\n")
            f.write("| Nom | Email | Type | Erreur | Serveur |\n")
            f.write("|-----|-------|------|--------|----------|\n")
            for r in sorted(other_errors, key=lambda x: x['name']):
                persona_type = "Alias" if r['is_alias'] else "Principal"
                error = r.get('error', 'Erreur inconnue')
                server = f"{r.get('server', 'N/A')}:{r.get('port', 'N/A')}"
                f.write(f"| {r['name']} | {r['email']} | {persona_type} | {error[:50]}... | {server} |\n")
            f.write("\n---\n\n")
    
    print(f"\n✅ Rapport généré: {report_path}")
    return report_path

if __name__ == '__main__':
    main()

