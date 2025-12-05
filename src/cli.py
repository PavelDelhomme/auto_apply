#!/usr/bin/env python3
"""
Interface en ligne de commande pour Auto Apply
"""

import argparse
import json
import sys
from database import create_database
from scraper import scrape_indeed
from job_filter import filter_jobs
from cv_generator import generate_cvs_from_json
from auto_apply import apply_to_job
from stats import print_statistics, get_statistics
from application_generator import generate_cover_letter
import random
import time

def load_personas(personas_file="personas.json"):
    """Charge les personas depuis le fichier JSON."""
    with open(personas_file, 'r', encoding='utf-8') as file:
        return json.load(file)

def main():
    parser = argparse.ArgumentParser(description='Auto Apply - Candidature automatique avec personas')
    
    # Arguments de recherche
    parser.add_argument('--query', '-q', default='développeur python', help='Terme de recherche')
    parser.add_argument('--location', '-l', default='Rennes', help='Localisation')
    parser.add_argument('--max-results', '-m', type=int, default=50, help='Nombre max de résultats')
    
    # Arguments de filtrage
    parser.add_argument('--title-keywords', nargs='+', default=['Python', 'Développeur'], 
                       help='Mots-clés dans le titre')
    parser.add_argument('--location-keywords', nargs='+', default=['Rennes', 'Bretagne'],
                       help='Mots-clés dans la localisation')
    parser.add_argument('--exclude-keywords', nargs='+', default=['Senior', 'Lead'],
                       help='Mots-clés à exclure')
    
    # Arguments de candidature
    parser.add_argument('--max-per-persona', type=int, default=3, 
                       help='Max candidatures par persona')
    parser.add_argument('--delay-min', type=int, default=5, 
                       help='Délai minimum entre candidatures (secondes)')
    parser.add_argument('--delay-max', type=int, default=10,
                       help='Délai maximum entre candidatures (secondes)')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Mode headless pour le navigateur')
    parser.add_argument('--no-cover-letter', action='store_true',
                       help='Ne pas utiliser de lettres de motivation')
    
    # Sélection de personas
    parser.add_argument('--personas', '-p', nargs='+',
                       help='Emails des personas à utiliser (sinon tous)')
    
    # Actions
    parser.add_argument('--generate-cvs', action='store_true',
                       help='Générer les CVs uniquement')
    parser.add_argument('--scrape-only', action='store_true',
                       help='Scraper les offres uniquement')
    parser.add_argument('--stats', action='store_true',
                       help='Afficher les statistiques')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simulation sans candidater réellement')
    
    args = parser.parse_args()
    
    # Initialiser la base de données
    create_database()
    
    # Afficher les statistiques uniquement
    if args.stats:
        print_statistics()
        return
    
    # Générer les CVs uniquement
    if args.generate_cvs:
        print("📄 Génération des CVs...")
        cv_paths = generate_cvs_from_json()
        print(f"✅ {len(cv_paths)} CVs générés")
        return
    
    # Charger les personas
    print("👥 Chargement des personas...")
    all_personas = load_personas()
    
    if args.personas:
        personas = {k: v for k, v in all_personas.items() if v['email'] in args.personas}
        print(f"   {len(personas)} personas sélectionnés sur {len(all_personas)} disponibles")
    else:
        personas = all_personas
        print(f"   {len(personas)} personas chargés (tous)")
    
    # Générer les CVs
    print("📄 Génération des CVs...")
    cv_paths = generate_cvs_from_json()
    print(f"   {len(cv_paths)} CVs générés")
    
    # Scraper les offres
    if not args.scrape_only:
        print(f"🔍 Recherche d'offres: '{args.query}' à {args.location}...")
        jobs = scrape_indeed(query=args.query, location=args.location, max_results=args.max_results)
        print(f"   {len(jobs)} offres trouvées")
        
        from database import insert_job
        for job in jobs:
            insert_job(job)
        
        if args.scrape_only:
            return
        
        # Filtrer et postuler
        print("🔎 Filtrage des offres...")
        
        persona_list = list(personas.items())
        random.shuffle(persona_list)
        
        total_applications = 0
        
        for persona_key, persona_info in persona_list:
            persona_email = persona_info['email']
            persona_name = persona_info['name']
            
            if persona_email not in cv_paths:
                print(f"⚠️  Pas de CV trouvé pour {persona_name}")
                continue
            
            cv_path = cv_paths[persona_email]
            
            filtered_jobs = filter_jobs(
                title_keywords=args.title_keywords,
                location_keywords=args.location_keywords,
                persona_email=persona_email,
                exclude_keywords=args.exclude_keywords
            )
            
            if not filtered_jobs:
                print(f"   {persona_name}: Aucune offre disponible")
                continue
            
            jobs_to_apply = filtered_jobs[:args.max_per_persona]
            print(f"\n👤 {persona_name} ({persona_email})")
            print(f"   {len(jobs_to_apply)} offres à traiter")
            
            for job in jobs_to_apply:
                # Générer la lettre de motivation
                cover_letter = None
                if not args.no_cover_letter:
                    try:
                        cover_letter = generate_cover_letter(job)
                    except Exception as e:
                        print(f"   ⚠️  Erreur génération lettre: {e}")
                
                from database import insert_application, update_application_status
                
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
                
                print(f"   📝 Candidature pour: {job['title']} chez {job['company']}")
                
                if args.dry_run:
                    print(f"   [DRY RUN] Candidature simulée")
                    update_application_status(job['id'], persona_email, 'sent')
                    total_applications += 1
                else:
                    success = apply_to_job(
                        job=job,
                        persona_email=persona_email,
                        persona_name=persona_name,
                        cv_path=cv_path,
                        cover_letter=cover_letter,
                        headless=args.headless
                    )
                    
                    if success:
                        update_application_status(job['id'], persona_email, 'sent')
                        total_applications += 1
                        print(f"   ✅ Candidature envoyée avec succès")
                    else:
                        update_application_status(job['id'], persona_email, 'failed')
                        print(f"   ❌ Échec de la candidature")
                
                # Délai entre candidatures
                delay = random.uniform(args.delay_min, args.delay_max)
                time.sleep(delay)
        
        print(f"\n📊 Processus terminé: {total_applications} candidatures envoyées")
        print_statistics()

if __name__ == '__main__':
    main()

