"""
Gestionnaires spécifiques pour différentes plateformes d'emploi
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re

def detect_platform(url):
    """Détecte la plateforme à partir de l'URL."""
    url_lower = url.lower()
    if 'indeed.com' in url_lower or 'indeed.fr' in url_lower:
        return 'indeed'
    elif 'linkedin.com' in url_lower:
        return 'linkedin'
    elif 'welcometothejungle.com' in url_lower:
        return 'welcometothejungle'
    elif 'hellowork.com' in url_lower or 'hellowork.fr' in url_lower:
        return 'hellowork'
    elif 'apec.fr' in url_lower:
        return 'apec'
    else:
        return 'other'

def apply_indeed(driver, job, persona_name, persona_email, cv_path, cover_letter=None):
    """Gère la candidature sur Indeed."""
    try:
        # Chercher le bouton de candidature
        apply_selectors = [
            (By.XPATH, "//button[contains(text(), 'Postuler')]"),
            (By.XPATH, "//a[contains(text(), 'Postuler')]"),
            (By.XPATH, "//button[contains(text(), 'Apply')]"),
            (By.XPATH, "//a[contains(text(), 'Apply')]"),
            (By.ID, 'apply-button'),
            (By.CLASS_NAME, 'apply-button'),
        ]
        
        apply_button = None
        for selector_type, selector_value in apply_selectors:
            try:
                apply_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                break
            except TimeoutException:
                continue
        
        if not apply_button:
            return False, "Bouton de candidature non trouvé"
        
        apply_button.click()
        time.sleep(2)
        
        # Remplir le formulaire
        # Upload du CV
        try:
            file_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
            file_input.send_keys(cv_path)
            time.sleep(1)
        except NoSuchElementException:
            pass
        
        # Remplir la lettre de motivation si disponible
        if cover_letter:
            try:
                cover_letter_input = driver.find_element(By.CSS_SELECTOR, 'textarea[name*="cover"], textarea[id*="cover"], textarea[placeholder*="motivation"]')
                cover_letter_input.clear()
                cover_letter_input.send_keys(cover_letter)
                time.sleep(1)
            except NoSuchElementException:
                pass
        
        # Soumettre
        try:
            submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"], button[class*="submit"]')
            submit_button.click()
            time.sleep(2)
            return True, "Candidature envoyée avec succès"
        except NoSuchElementException:
            return False, "Bouton de soumission non trouvé"
            
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def apply_linkedin(driver, job, persona_name, persona_email, cv_path, cover_letter=None):
    """Gère la candidature sur LinkedIn."""
    try:
        # LinkedIn nécessite souvent une connexion
        # Chercher le bouton "Easy Apply" ou "Postuler facilement"
        apply_selectors = [
            (By.XPATH, "//button[contains(@aria-label, 'Easy Apply')]"),
            (By.XPATH, "//button[contains(text(), 'Postuler facilement')]"),
            (By.XPATH, "//button[contains(text(), 'Easy Apply')]"),
            (By.CSS_SELECTOR, 'button[data-control-name="job_apply"]'),
        ]
        
        apply_button = None
        for selector_type, selector_value in apply_selectors:
            try:
                apply_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                break
            except TimeoutException:
                continue
        
        if not apply_button:
            return False, "Bouton Easy Apply non trouvé (connexion LinkedIn requise?)"
        
        apply_button.click()
        time.sleep(2)
        
        # LinkedIn Easy Apply - remplir le formulaire
        # Upload du CV
        try:
            file_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
            file_input.send_keys(cv_path)
            time.sleep(1)
        except NoSuchElementException:
            pass
        
        # Continuer les étapes
        try:
            next_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Continue')] | //button[contains(text(), 'Continuer')]")
            next_button.click()
            time.sleep(1)
        except NoSuchElementException:
            pass
        
        # Soumettre
        try:
            submit_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Submit')] | //button[contains(text(), 'Envoyer')]")
            submit_button.click()
            time.sleep(2)
            return True, "Candidature envoyée avec succès"
        except NoSuchElementException:
            return False, "Bouton de soumission non trouvé"
            
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def apply_welcometothejungle(driver, job, persona_name, persona_email, cv_path, cover_letter=None):
    """Gère la candidature sur Welcome to the Jungle."""
    try:
        # Chercher le bouton de candidature
        apply_selectors = [
            (By.XPATH, "//button[contains(text(), 'Postuler')]"),
            (By.XPATH, "//a[contains(text(), 'Postuler')]"),
            (By.CSS_SELECTOR, 'button[data-testid="apply-button"]'),
        ]
        
        apply_button = None
        for selector_type, selector_value in apply_selectors:
            try:
                apply_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                break
            except TimeoutException:
                continue
        
        if not apply_button:
            return False, "Bouton de candidature non trouvé"
        
        apply_button.click()
        time.sleep(2)
        
        # Upload du CV
        try:
            file_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
            file_input.send_keys(cv_path)
            time.sleep(1)
        except NoSuchElementException:
            pass
        
        # Lettre de motivation
        if cover_letter:
            try:
                cover_letter_input = driver.find_element(By.CSS_SELECTOR, 'textarea[name*="cover"], textarea[id*="cover"]')
                cover_letter_input.clear()
                cover_letter_input.send_keys(cover_letter)
                time.sleep(1)
            except NoSuchElementException:
                pass
        
        # Soumettre
        try:
            submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            time.sleep(2)
            return True, "Candidature envoyée avec succès"
        except NoSuchElementException:
            return False, "Bouton de soumission non trouvé"
            
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def apply_hellowork(driver, job, persona_name, persona_email, cv_path, cover_letter=None):
    """Gère la candidature sur HelloWork."""
    try:
        # Chercher le bouton de candidature
        apply_selectors = [
            (By.XPATH, "//button[contains(text(), 'Postuler')]"),
            (By.XPATH, "//a[contains(text(), 'Postuler')]"),
            (By.CSS_SELECTOR, 'button.apply-button'),
        ]
        
        apply_button = None
        for selector_type, selector_value in apply_selectors:
            try:
                apply_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                break
            except TimeoutException:
                continue
        
        if not apply_button:
            return False, "Bouton de candidature non trouvé"
        
        apply_button.click()
        time.sleep(2)
        
        # Upload du CV
        try:
            file_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
            file_input.send_keys(cv_path)
            time.sleep(1)
        except NoSuchElementException:
            pass
        
        # Lettre de motivation
        if cover_letter:
            try:
                cover_letter_input = driver.find_element(By.CSS_SELECTOR, 'textarea[name*="cover"], textarea[id*="cover"]')
                cover_letter_input.clear()
                cover_letter_input.send_keys(cover_letter)
                time.sleep(1)
            except NoSuchElementException:
                pass
        
        # Soumettre
        try:
            submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            time.sleep(2)
            return True, "Candidature envoyée avec succès"
        except NoSuchElementException:
            return False, "Bouton de soumission non trouvé"
            
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def apply_generic(driver, job, persona_name, persona_email, cv_path, cover_letter=None):
    """Gestionnaire générique pour les autres plateformes."""
    try:
        # Chercher le bouton de candidature avec plusieurs sélecteurs
        apply_selectors = [
            (By.XPATH, "//button[contains(text(), 'Postuler')]"),
            (By.XPATH, "//a[contains(text(), 'Postuler')]"),
            (By.XPATH, "//button[contains(text(), 'Apply')]"),
            (By.XPATH, "//a[contains(text(), 'Apply')]"),
            (By.ID, 'apply-button'),
            (By.CLASS_NAME, 'apply-button'),
            (By.CSS_SELECTOR, 'button[type="submit"]'),
        ]
        
        apply_button = None
        for selector_type, selector_value in apply_selectors:
            try:
                apply_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                break
            except TimeoutException:
                continue
        
        if not apply_button:
            return False, "Bouton de candidature non trouvé"
        
        apply_button.click()
        time.sleep(2)
        
        # Upload du CV
        try:
            file_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
            file_input.send_keys(cv_path)
            time.sleep(1)
        except NoSuchElementException:
            pass
        
        # Lettre de motivation
        if cover_letter:
            try:
                cover_letter_input = driver.find_element(By.CSS_SELECTOR, 'textarea')
                cover_letter_input.clear()
                cover_letter_input.send_keys(cover_letter)
                time.sleep(1)
            except NoSuchElementException:
                pass
        
        # Soumettre
        try:
            submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            time.sleep(2)
            return True, "Candidature envoyée avec succès"
        except NoSuchElementException:
            return False, "Bouton de soumission non trouvé"
            
    except Exception as e:
        return False, f"Erreur: {str(e)}"

PLATFORM_HANDLERS = {
    'indeed': apply_indeed,
    'linkedin': apply_linkedin,
    'welcometothejungle': apply_welcometothejungle,
    'hellowork': apply_hellowork,
    'apec': apply_generic,
    'other': apply_generic
}

