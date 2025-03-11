from scraper import scrape_indeed
from database import create_database, insert_job
from job_filter import filter_jobs
from auto_apply import apply_to_job
from stats import get_statistics
from cv_generator import generate_cv

def main():
    create_database()

    # Générer automatiquement un CV avant de postuler
    generate_cv()

    # Scraper des offres d'emploi (personnalisez ici)
    jobs = scrape_indeed(query="développeur python", location="Rennes")
    
    for job in jobs:
        insert_job(job)

    # Filtrer les offres selon vos critères
    filtered_jobs = filter_jobs(title_keywords=["Python", "Développeur"], location_keywords=["Rennes", "Bretagne"])
    
    # Postuler automatiquement sans lettre de motivation
    for job in filtered_jobs:
        apply_to_job(job, cv_path="generated_cv.pdf", cover_letter=None)

if __name__ == "__main__":
    main()
