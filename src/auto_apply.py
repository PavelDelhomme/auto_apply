from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os

def apply_to_job(job, persona_email, persona_name, cv_path, cover_letter=None, headless=False):
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
        
        driver.get(job_url)
        time.sleep(3)  # Attendre le chargement de la page
        
        # Chercher le bouton de candidature (plusieurs sélecteurs possibles)
        apply_button = None
        selectors = [
            (By.CLASS_NAME, 'apply-button'),
            (By.ID, 'applyButton'),
            (By.XPATH, "//button[contains(text(), 'Postuler')]"),
            (By.XPATH, "//a[contains(text(), 'Postuler')]"),
            (By.XPATH, "//button[contains(text(), 'Apply')]"),
            (By.XPATH, "//a[contains(text(), 'Apply')]"),
        ]
        
        for selector_type, selector_value in selectors:
            try:
                apply_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                break
            except TimeoutException:
                continue
        
        if not apply_button:
            print("Bouton de candidature non trouvé. La structure de la page a peut-être changé.")
            return False
        
        apply_button.click()
        time.sleep(2)
        
        # Remplir le formulaire de candidature
        # Upload du CV
        try:
            cv_upload_selectors = [
                (By.ID, 'cv-upload'),
                (By.NAME, 'cv'),
                (By.XPATH, "//input[@type='file']"),
            ]
            
            cv_upload = None
            for selector_type, selector_value in cv_upload_selectors:
                try:
                    cv_upload = driver.find_element(selector_type, selector_value)
                    break
                except NoSuchElementException:
                    continue
            
            if cv_upload:
                absolute_cv_path = os.path.abspath(cv_path)
                cv_upload.send_keys(absolute_cv_path)
                print("CV uploadé avec succès")
                time.sleep(1)
        except Exception as e:
            print(f"Attention: Impossible d'uploader le CV automatiquement: {e}")
        
        # Remplir la lettre de motivation si fournie
        if cover_letter:
            try:
                cover_letter_selectors = [
                    (By.ID, 'cover-letter'),
                    (By.NAME, 'cover-letter'),
                    (By.TAG_NAME, 'textarea'),
                ]
                
                cover_letter_field = None
                for selector_type, selector_value in cover_letter_selectors:
                    try:
                        cover_letter_field = driver.find_element(selector_type, selector_value)
                        break
                    except NoSuchElementException:
                        continue
                
                if cover_letter_field:
                    cover_letter_field.clear()
                    cover_letter_field.send_keys(cover_letter)
                    print("Lettre de motivation remplie")
                    time.sleep(1)
            except Exception as e:
                print(f"Attention: Impossible de remplir la lettre de motivation: {e}")
        
        # Soumettre le formulaire
        try:
            submit_selectors = [
                (By.CLASS_NAME, 'submit-button'),
                (By.ID, 'submit'),
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Envoyer')]"),
                (By.XPATH, "//button[contains(text(), 'Submit')]"),
            ]
            
            submit_button = None
            for selector_type, selector_value in submit_selectors:
                try:
                    submit_button = driver.find_element(selector_type, selector_value)
                    break
                except NoSuchElementException:
                    continue
            
            if submit_button:
                submit_button.click()
                print(f"✅ Candidature envoyée avec succès pour {job['title']} chez {job['company']}")
                time.sleep(2)
                return True
            else:
                print("Bouton de soumission non trouvé. La candidature n'a peut-être pas été envoyée.")
                return False
        except Exception as e:
            print(f"Erreur lors de la soumission: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Erreur lors de la candidature: {e}")
        return False
    finally:
        if driver:
            driver.quit()
    
    return False
