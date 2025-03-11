from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def apply_to_job(job, cv_path, cover_letter):
    """
    Automatisation de la candidature à une offre via Selenium.
    :param job: Dictionnaire contenant les informations sur l'offre (title, company, location).
    :param cv_path: Chemin vers le fichier CV.
    :param cover_letter: Texte de la lettre de motivation.
    """
    driver = webdriver.Chrome()  # Assurez-vous que ChromeDriver est installé et dans le PATH
    
    # Exemple URL - remplacez par le lien réel vers l'offre
    job_url = f"https://fr.indeed.com/voir-emploi?jk={job['id']}"
    
    driver.get(job_url)
    
    # Exemple d'automatisation - ajustez selon la structure du site
    try:
        apply_button = driver.find_element(By.CLASS_NAME, 'apply-button')
        apply_button.click()
        
        time.sleep(2)
        
        # Remplir le formulaire
        cv_upload = driver.find_element(By.ID, 'cv-upload')
        cv_upload.send_keys(cv_path)
        
        cover_letter_field = driver.find_element(By.ID, 'cover-letter')
        cover_letter_field.send_keys(cover_letter)
        
        submit_button = driver.find_element(By.CLASS_NAME, 'submit-button')
        submit_button.click()
        
        print(f"Candidature envoyée pour {job['title']} chez {job['company']}")
        
        time.sleep(2)
        
    except Exception as e:
        print(f"Erreur lors de la candidature : {e}")
    
    driver.quit()
