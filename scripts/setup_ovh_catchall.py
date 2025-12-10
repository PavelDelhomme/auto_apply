#!/usr/bin/env python3
"""
Script pour configurer le catch-all email sur OVH
et créer le compte catchall@maily.ovh
"""

import json
import os
import sys
import random
import string

try:
    import ovh
    OVH_AVAILABLE = True
except ImportError:
    OVH_AVAILABLE = False
    print("⚠️  Module 'ovh' non installé. Installez-le avec: pip install ovh")

# Ajouter le répertoire parent au path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.join(project_root, 'src'))

from persona_manager import PersonaManager

DOMAIN = 'maily.ovh'
CATCHALL_EMAIL = 'catchall@maily.ovh'

def create_ovh_client():
    """Crée un client OVH."""
    if not OVH_AVAILABLE:
        raise ImportError("Module 'ovh' non installé")
    
    config_file = os.path.join(project_root, 'config', 'ovh_config.json')
    if not os.path.exists(config_file):
        print("❌ Fichier config/ovh_config.json non trouvé!")
        print("\n📋 Créez ce fichier avec vos clés API OVH:")
        print('''{
    "application_key": "VOTRE_APP_KEY",
    "application_secret": "VOTRE_APP_SECRET",
    "consumer_key": "VOTRE_CONSUMER_KEY"
}''')
        return None
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    return ovh.Client(
        endpoint='ovh-eu',
        application_key=config['application_key'],
        application_secret=config['application_secret'],
        consumer_key=config['consumer_key']
    )

def setup_catchall(client, domain, catchall_email, redirect_to=None):
    """Configure le catch-all email."""
    if not redirect_to:
        redirect_to = catchall_email
    
    try:
        # Vérifier si le catch-all existe déjà
        try:
            existing = client.get(f'/email/domain/{domain}/redirection')
            for redir in existing:
                if redir.get('from') == f'*@{domain}':
                    print(f"⚠️  Catch-all existe déjà: {redir.get('to')}")
                    return True
        except:
            pass
        
        # Créer le catch-all
        result = client.post(
            f'/email/domain/{domain}/redirection',
            from_=f'*@{domain}',
            to=redirect_to,
            localCopy=True  # Garder une copie locale
        )
        print(f"✅ Catch-all configuré: *@{domain} → {redirect_to}")
        return True
    except Exception as e:
        print(f"❌ Erreur configuration catch-all: {e}")
        return False

def create_catchall_account(client, domain, username='catchall', password=None):
    """Crée le compte catch-all."""
    if not password:
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    try:
        # Vérifier si le compte existe
        try:
            accounts = client.get(f'/email/domain/{domain}/account')
            if username in [acc.split('@')[0] for acc in accounts]:
                print(f"⚠️  Le compte {username}@{domain} existe déjà")
                return True, password
        except:
            pass
        
        # Créer le compte
        result = client.post(
            f'/email/domain/{domain}/account',
            accountName=username,
            password=password,
            size=5000000000  # 5 GB
        )
        print(f"✅ Compte {username}@{domain} créé")
        return True, password
    except Exception as e:
        error_msg = str(e)
        if 'already exists' in error_msg.lower():
            print(f"⚠️  Le compte {username}@{domain} existe déjà")
            return True, password
        print(f"❌ Erreur création compte: {e}")
        return False, None

def main():
    print("🚀 Configuration du Catch-All Email OVH")
    print("="*60)
    
    if not OVH_AVAILABLE:
        print("\n❌ Module 'ovh' non installé.")
        print("📦 Installez-le avec: pip install ovh")
        return
    
    client = create_ovh_client()
    if not client:
        return
    
    print(f"\n📧 Configuration pour le domaine {DOMAIN}")
    print("="*60)
    
    # Étape 1: Créer le compte catch-all
    print(f"\n1️⃣  Création du compte {CATCHALL_EMAIL}...")
    success, password = create_catchall_account(client, DOMAIN, 'catchall')
    
    if not success:
        print("❌ Impossible de créer le compte catch-all")
        return
    
    print(f"✅ Compte créé. Mot de passe: {password}")
    print("⚠️  IMPORTANT: Sauvegardez ce mot de passe!")
    
    # Étape 2: Configurer le catch-all
    print(f"\n2️⃣  Configuration de la redirection catch-all...")
    if setup_catchall(client, DOMAIN, CATCHALL_EMAIL):
        print("✅ Catch-all configuré avec succès")
    else:
        print("❌ Erreur lors de la configuration du catch-all")
        return
    
    # Étape 3: Ajouter dans personas.json
    print(f"\n3️⃣  Ajout dans personas.json...")
    if os.path.exists('/app/config/personas.json'):
        personas_file = '/app/config/personas.json'
    else:
        personas_file = os.path.join(project_root, 'config', 'personas.json')
    
    persona_manager = PersonaManager(personas_file)
    
    # Vérifier si le persona existe déjà
    catchall_persona = None
    for key, persona in persona_manager.personas.items():
        if persona.get('email') == CATCHALL_EMAIL:
            catchall_persona = key
            break
    
    if catchall_persona:
        print(f"⚠️  Le persona {catchall_persona} existe déjà pour {CATCHALL_EMAIL}")
        print("💡 Mise à jour du mot de passe...")
        persona_manager.personas[catchall_persona]['password'] = password
    else:
        # Créer un nouveau persona
        existing_keys = list(persona_manager.personas.keys())
        max_num = 0
        for key in existing_keys:
            if key.startswith('persona') and key[7:].isdigit():
                num = int(key[7:])
                max_num = max(max_num, num)
        
        persona_key = f"persona{max_num + 1}"
        persona_manager.personas[persona_key] = {
            "name": "Catch-All Email",
            "email": CATCHALL_EMAIL,
            "password": password,
            "alias": False,
            "parent": None,
            "email_config": {
                "imap_server": "ssl0.ovh.net",
                "imap_port": 993,
                "smtp_server": "ssl0.ovh.net",
                "smtp_port": 465
            }
        }
        print(f"✅ Persona {persona_key} créé")
    
    if persona_manager.save_personas():
        print("✅ Configuration sauvegardée dans personas.json")
    else:
        print("❌ Erreur lors de la sauvegarde")
        return
    
    # Instructions
    print(f"\n{'='*60}")
    print("✅ CONFIGURATION TERMINÉE")
    print(f"{'='*60}")
    print(f"\n📧 Compte catch-all: {CATCHALL_EMAIL}")
    print(f"🔑 Mot de passe: {password}")
    print(f"\n💡 Utilisation:")
    print(f"   - Tous les emails à *@{DOMAIN} arriveront dans {CATCHALL_EMAIL}")
    print(f"   - Vous pouvez créer des personas avec n'importe quelle adresse @{DOMAIN}")
    print(f"   - Exemple: persona1@{DOMAIN}, persona2@{DOMAIN}, etc.")
    print(f"   - Tous utiliseront le même compte IMAP ({CATCHALL_EMAIL})")
    print(f"\n⚠️  IMPORTANT: Sauvegardez le mot de passe dans un gestionnaire de mots de passe!")

if __name__ == '__main__':
    main()

