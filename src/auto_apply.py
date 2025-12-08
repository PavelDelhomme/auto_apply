from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
from .platform_handlers import detect_platform, PLATFORM_HANDLERS

def apply_to_job(job, persona_email, persona_name, cv_path, cover_letter=None, headless=False, platform=None):
    """
    Automatisation de la candidature à une offre via Selenium.
    :param job: Dictionnaire contenant les informations sur l'offre (id, title, company, location, url).
    :param persona_email: Email du persona qui postule.
    :param persona_name: Nom du persona qui postule.
    :param cv_path: Chemin vers le fichier CV.
    :param cover_letter: Texte de la lettre de motivation (optionnel).
    :param headless: Mode headless pour le navigateur.
    :return: True si la candidature a réussi, False sinon.
    """
    if not os.path.exists(cv_path):
        print(f"Erreur: Le fichier CV {cv_path} n'existe pas")
        return False
    
    # Configuration du navigateur
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Pour Docker, utiliser chromium si disponible
    import os
    if os.path.exists('/usr/bin/chromium'):
        options.binary_location = '/usr/bin/chromium'
    
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Utiliser l'URL de l'offre si disponible, sinon construire une URL Indeed
        if job.get('url'):
            job_url = job['url']
        else:
            job_url = f"https://fr.indeed.com/voir-emploi?jk={job.get('id', '')}"
        
        print(f"Tentative de candidature pour {persona_name} ({persona_email})")
        print(f"Offre: {job['title']} chez {job['company']} - {job['location']}")
        print(f"URL: {job_url}")
        
        # Détecter la plateforme si non spécifiée
        if not platform:
            platform = detect_platform(job_url)
        
        print(f"Plateforme détectée: {platform}")
        
        driver.get(job_url)
        time.sleep(3)  # Attendre le chargement de la page
        
        # Utiliser le gestionnaire spécifique à la plateforme
        handler = PLATFORM_HANDLERS.get(platform, PLATFORM_HANDLERS['other'])
        success, message = handler(driver, job, persona_name, persona_email, cv_path, cover_letter)
        
        if success:
            print(f"✅ {message}")
            return True
        else:
            print(f"❌ {message}")
            return False
        
    except Exception as e:
        print(f"❌ Erreur lors de la candidature: {e}")
        return False
    finally:
        if driver:
            driver.quit()
    
    return False
