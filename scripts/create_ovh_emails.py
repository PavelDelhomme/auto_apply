#!/usr/bin/env python3
"""
Script pour créer automatiquement des emails OVH via l'API
et les ajouter dans personas.json
"""

import json
import os
import sys
import random
import string
import time
from typing import List, Dict

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

# Configuration
OVH_ENDPOINT = 'ovh-eu'  # ou 'ovh-ca', 'ovh-us'
DOMAIN = 'maily.ovh'
EMAIL_SIZE_GB = 5  # Taille de la boîte mail en GB

def generate_password(length=16):
    """Génère un mot de passe aléatoire."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def create_ovh_client(app_key=None, app_secret=None, consumer_key=None):
    """Crée un client OVH."""
    if not OVH_AVAILABLE:
        raise ImportError("Module 'ovh' non installé. Installez-le avec: pip install ovh")
    
    # Essayer de charger depuis un fichier de configuration
    config_file = os.path.join(project_root, 'config', 'ovh_config.json')
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            app_key = config.get('application_key', app_key)
            app_secret = config.get('application_secret', app_secret)
            consumer_key = config.get('consumer_key', consumer_key)
    
    if not all([app_key, app_secret, consumer_key]):
        print("❌ Configuration OVH manquante!")
        print("\n📋 Pour obtenir vos clés API:")
        print("1. Allez sur https://eu.api.ovh.com/createApp/")
        print("2. Créez une application")
        print("3. Récupérez:")
        print("   - Application Key")
        print("   - Application Secret")
        print("   - Consumer Key")
        print("\n💾 Créez un fichier config/ovh_config.json avec:")
        print('''{
    "application_key": "VOTRE_APP_KEY",
    "application_secret": "VOTRE_APP_SECRET",
    "consumer_key": "VOTRE_CONSUMER_KEY"
}''')
        return None
    
    return ovh.Client(
        endpoint=OVH_ENDPOINT,
        application_key=app_key,
        application_secret=app_secret,
        consumer_key=consumer_key
    )

def create_email_account(client, domain, username, password, size_gb=5):
    """Crée un compte email sur OVH."""
    try:
        size_bytes = size_gb * 1024 * 1024 * 1024
        result = client.post(
            f'/email/domain/{domain}/account',
            accountName=username,
            password=password,
            size=size_bytes
        )
        return result
    except Exception as e:
        error_msg = str(e)
        if 'already exists' in error_msg.lower() or 'already registered' in error_msg.lower():
            return {'status': 'exists', 'message': f'Le compte {username}@{domain} existe déjà'}
        print(f"❌ Erreur création {username}@{domain}: {error_msg}")
        return None

def create_persona_from_email(persona_manager, email, password, name=None):
    """Crée un persona dans personas.json à partir d'un email."""
    if not name:
        # Extraire le nom depuis l'email
        username = email.split('@')[0]
        name = username.replace('.', ' ').replace('_', ' ').title()
    
    # Générer une clé unique
    existing_keys = list(persona_manager.personas.keys())
    max_num = 0
    for key in existing_keys:
        if key.startswith('persona') and key[7:].isdigit():
            num = int(key[7:])
            max_num = max(max_num, num)
    
    persona_key = f"persona{max_num + 1}"
    
    persona_data = {
        "name": name,
        "email": email,
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
    
    persona_manager.personas[persona_key] = persona_data
    return persona_key

def main():
    print("🚀 Création automatique d'emails OVH pour personas")
    print("="*60)
    
    if not OVH_AVAILABLE:
        print("\n❌ Module 'ovh' non installé.")
        print("📦 Installez-le avec: pip install ovh")
        print("   Ou dans Docker: docker-compose exec auto-apply pip install ovh")
        return
    
    # Demander le nombre d'emails à créer
    try:
        count = int(input("\n📧 Combien d'emails voulez-vous créer? "))
        if count <= 0:
            print("❌ Le nombre doit être positif")
            return
    except ValueError:
        print("❌ Nombre invalide")
        return
    
    # Demander le préfixe
    prefix = input("📝 Préfixe pour les emails (ex: 'persona', 'test'): ").strip() or "persona"
    
    # Créer le client OVH
    client = create_ovh_client()
    if not client:
        return
    
    print(f"\n🔍 Vérification du domaine {DOMAIN}...")
    try:
        # Vérifier que le domaine existe
        domains = client.get('/email/domain')
        if DOMAIN not in domains:
            print(f"❌ Le domaine {DOMAIN} n'est pas configuré dans votre compte OVH")
            return
        print(f"✅ Domaine {DOMAIN} trouvé")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return
    
    # Charger le PersonaManager
    if os.path.exists('/app/config/personas.json'):
        personas_file = '/app/config/personas.json'
    else:
        personas_file = os.path.join(project_root, 'config', 'personas.json')
    
    persona_manager = PersonaManager(personas_file)
    
    print(f"\n📧 Création de {count} email(s)...")
    print("="*60)
    
    created = []
    failed = []
    existing = []
    
    for i in range(1, count + 1):
        username = f"{prefix}{i}"
        email = f"{username}@{DOMAIN}"
        password = generate_password(16)
        
        print(f"\n[{i}/{count}] Création de {email}...")
        
        # Créer l'email sur OVH
        result = create_email_account(client, DOMAIN, username, password, EMAIL_SIZE_GB)
        
        if result:
            if isinstance(result, dict) and result.get('status') == 'exists':
                print(f"⚠️  {email} existe déjà")
                existing.append((email, username))
            else:
                print(f"✅ {email} créé avec succès")
                
                # Créer le persona
                persona_key = create_persona_from_email(persona_manager, email, password)
                created.append((persona_key, email, password))
                
                # Délai pour éviter de surcharger l'API OVH
                if i < count:
                    time.sleep(1)
        else:
            print(f"❌ Échec de la création de {email}")
            failed.append(email)
    
    # Sauvegarder les personas
    if created:
        print(f"\n💾 Sauvegarde de {len(created)} persona(s) dans personas.json...")
        if persona_manager.save_personas():
            print("✅ Personas sauvegardés avec succès")
        else:
            print("❌ Erreur lors de la sauvegarde")
    
    # Résumé
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ")
    print(f"{'='*60}")
    print(f"✅ Créés: {len(created)}")
    print(f"⚠️  Existants: {len(existing)}")
    print(f"❌ Échoués: {len(failed)}")
    
    if created:
        print(f"\n📋 Emails créés:")
        for persona_key, email, password in created[:10]:  # Afficher les 10 premiers
            print(f"  - {persona_key}: {email} (mot de passe: {password})")
        if len(created) > 10:
            print(f"  ... et {len(created) - 10} autres")
        
        print(f"\n💾 Les mots de passe sont sauvegardés dans personas.json")
        print(f"⚠️  IMPORTANT: Sauvegardez ces mots de passe dans un gestionnaire de mots de passe!")
    
    if existing:
        print(f"\n⚠️  Emails existants (non modifiés):")
        for email, username in existing[:5]:
            print(f"  - {email}")
        if len(existing) > 5:
            print(f"  ... et {len(existing) - 5} autres")
    
    if failed:
        print(f"\n❌ Emails en échec:")
        for email in failed:
            print(f"  - {email}")

if __name__ == '__main__':
    main()

