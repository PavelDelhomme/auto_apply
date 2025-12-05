import requests
from bs4 import BeautifulSoup
import time
import random

def scrape_indeed(query, location, max_results=50):
    """
    Scrape les offres d'emploi depuis Indeed.
    :param query: Terme de recherche.
    :param location: Localisation.
    :param max_results: Nombre maximum de résultats à récupérer.
    :return: Liste de dictionnaires contenant les informations des offres.
    """
    jobs = []
    # Headers plus complets pour éviter les blocages
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.google.com/'
    }
    
    # Session pour maintenir les cookies
    session = requests.Session()
    session.headers.update(headers)
    
    start = 0
    while len(jobs) < max_results:
        # Encoder correctement l'URL
        from urllib.parse import quote_plus
        encoded_query = quote_plus(query)
        encoded_location = quote_plus(location)
        url = f"https://fr.indeed.com/emplois?q={encoded_query}&l={encoded_location}&start={start}"
        
        try:
            response = session.get(url, timeout=15, allow_redirects=True)
            
            # Gérer les erreurs 403
            if response.status_code == 403:
                print(f"   ⚠️  Accès refusé (403) - Tentative avec différents headers...")
                # Essayer avec un autre User-Agent
                headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                session.headers.update(headers)
                time.sleep(random.uniform(2, 4))
                response = session.get(url, timeout=15, allow_redirects=True)
            
            if response.status_code != 200:
                print(f"   ⚠️  Erreur HTTP {response.status_code} - Arrêt du scraping")
                break
                
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Trouver tous les éléments d'offres d'emploi
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            
            if not job_cards:
                # Essayer d'autres sélecteurs possibles
                job_cards = soup.find_all('div', {'data-jk': True})
            
            if not job_cards:
                print(f"   Aucune offre trouvée à la page {start // 10 + 1}")
                break
            
            for card in job_cards:
                try:
                    # Extraire le titre
                    title_elem = card.find('h2', class_='jobTitle')
                    if not title_elem:
                        title_elem = card.find('a', {'data-jk': True})
                    title = title_elem.get_text(strip=True) if title_elem else "Titre non disponible"
                    
                    # Extraire le lien
                    link_elem = card.find('a', {'data-jk': True})
                    job_id = link_elem.get('data-jk', '') if link_elem else ''
                    url = f"https://fr.indeed.com/voir-emploi?jk={job_id}" if job_id else ''
                    
                    # Extraire le nom de l'entreprise
                    company_elem = card.find('span', class_='companyName')
                    if not company_elem:
                        company_elem = card.find('a', class_='companyName')
                    company = company_elem.get_text(strip=True) if company_elem else "Entreprise non spécifiée"
                    
                    # Extraire la localisation
                    location_elem = card.find('div', class_='companyLocation')
                    if not location_elem:
                        location_elem = card.find('span', class_='companyLocation')
                    location_text = location_elem.get_text(strip=True) if location_elem else location
                    
                    # Extraire la description (si disponible)
                    description_elem = card.find('div', class_='job-snippet')
                    description = description_elem.get_text(strip=True) if description_elem else ''
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': location_text,
                        'url': url,
                        'description': description,
                        'id': job_id
                    }
                    
                    # Éviter les doublons
                    if job not in jobs:
                        jobs.append(job)
                    
                    if len(jobs) >= max_results:
                        break
                        
                except Exception as e:
                    print(f"   Erreur lors de l'extraction d'une offre: {e}")
                    continue
            
            # Vérifier s'il y a une page suivante
            next_button = soup.find('a', {'aria-label': 'Suivant'})
            if not next_button:
                break
            
            start += 10
            time.sleep(random.uniform(1, 3))  # Pause pour éviter d'être bloqué
            
        except requests.RequestException as e:
            print(f"   Erreur lors de la requête: {e}")
            break
        except Exception as e:
            print(f"   Erreur inattendue: {e}")
            break
    
    print(f"   {len(jobs)} offres extraites")
    return jobs[:max_results]
