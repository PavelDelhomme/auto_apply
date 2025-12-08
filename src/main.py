import json
import random
from scraper import scrape_indeed
from .database import create_database, insert_job, insert_application, update_application_status
from job_filter import filter_jobs
from auto_apply import apply_to_job
from stats import get_statistics
from cv_generator import generate_cvs_from_json
from application_generator import generate_cover_letter

def load_personas(personas_file="config/personas.json"):
    """Charge les personas depuis le fichier JSON."""
    with open(personas_file, 'r', encoding='utf-8') as file:
        return json.load(file)

def main():
    """
    Fonction principale pour automatiser les candidatures avec plusieurs personas.
    """
    print("🚀 Démarrage du système de candidature automatique")
    
    # Créer la base de données
    print("📊 Initialisation de la base de données...")
    create_database()
    
    # Charger les personas
    print("👥 Chargement des personas...")
    personas = load_personas()
    print(f"   {len(personas)} personas chargés")
    
    # Générer les CVs pour tous les personas
    print("📄 Génération des CVs...")
    cv_paths = generate_cvs_from_json()
    print(f"   {len(cv_paths)} CVs générés")
    
    # Configuration de la recherche
    search_query = "développeur python"
    search_location = "Rennes"
    title_keywords = ["Python", "Développeur", "Developer"]
    location_keywords = ["Rennes", "Bretagne", "Remote", "Télétravail"]
    exclude_keywords = ["Senior", "Lead", "Manager"]  # Exclure certains postes
    
    # Scraper des offres d'emploi
    print(f"🔍 Recherche d'offres: '{search_query}' à {search_location}...")
    jobs = scrape_indeed(query=search_query, location=search_location)
    print(f"   {len(jobs)} offres trouvées")
    
    # Insérer les offres dans la base de données
    for job in jobs:
        insert_job(job)
    
    # Filtrer les offres
    print("🔎 Filtrage des offres...")
    
    # Pour chaque persona, candidater à des offres différentes
    persona_list = list(personas.items())
    random.shuffle(persona_list)  # Mélanger pour varier les candidatures
    
    total_applications = 0
    
    for persona_key, persona_info in persona_list:
        persona_email = persona_info['email']
        persona_name = persona_info['name']
        
        # Récupérer les CVs pour ce persona
        if persona_email not in cv_paths:
            print(f"⚠️  Pas de CV trouvé pour {persona_name} ({persona_email})")
            continue
        
        cv_path = cv_paths[persona_email]
        
        # Filtrer les offres non candidatées pour ce persona
        filtered_jobs = filter_jobs(
            title_keywords=title_keywords,
            location_keywords=location_keywords,
            persona_email=persona_email,
            exclude_keywords=exclude_keywords
        )
        
        if not filtered_jobs:
            print(f"   {persona_name}: Aucune offre disponible")
            continue
        
        # Limiter le nombre de candidatures par persona pour éviter la surcharge
        max_applications_per_persona = 3
        jobs_to_apply = filtered_jobs[:max_applications_per_persona]
        
        print(f"\n👤 {persona_name} ({persona_email})")
        print(f"   {len(jobs_to_apply)} offres à traiter")
        
        for job in jobs_to_apply:
            # Générer une lettre de motivation personnalisée
            try:
                cover_letter = generate_cover_letter(job)
            except Exception as e:
                print(f"   ⚠️  Erreur génération lettre de motivation: {e}")
                cover_letter = None
            
            # Enregistrer la candidature dans la base de données
            application_id = insert_application(
                job_id=job['id'],
                persona_email=persona_email,
                persona_name=persona_name,
                cv_path=cv_path,
                cover_letter=cover_letter,
                status='pending'
            )
            
            if not application_id:
                print(f"   ⚠️  Candidature déjà enregistrée pour cette offre")
                continue
            
            # Postuler automatiquement
            success = apply_to_job(
                job=job,
                persona_email=persona_email,
                persona_name=persona_name,
                cv_path=cv_path,
                cover_letter=cover_letter,
                headless=False  # Mettre à True pour exécuter en arrière-plan
            )
            
            # Mettre à jour le statut
            if success:
                update_application_status(job['id'], persona_email, 'sent')
                total_applications += 1
            else:
                update_application_status(job['id'], persona_email, 'failed')
            
            # Pause entre les candidatures pour éviter d'être détecté
            import time
            time.sleep(random.uniform(5, 10))
    
    # Afficher les statistiques
    print("\n📊 Statistiques finales:")
    stats = get_statistics()
    print(f"   Total d'offres: {stats['total_jobs']}")
    print(f"   Candidatures envoyées: {total_applications}")
    print(f"   Offres restantes: {stats['remaining_jobs']}")

if __name__ == "__main__":
    main()
