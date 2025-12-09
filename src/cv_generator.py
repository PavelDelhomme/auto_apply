import json
import os
import hashlib
import requests
from jinja2 import Template
import pdfkit
from .cv_data_generator import generate_realistic_cv_data

def get_persona_photo(persona_email, photos_dir="/app/photos"):
    """
    Récupère ou génère une photo pour un persona.
    Utilise randomuser.me avec filtrage par âge pour éviter les enfants et personnes très âgées.
    Utilise un hash de l'email pour avoir toujours la même photo pour le même persona.
    :param persona_email: Email du persona.
    :param photos_dir: Dossier pour stocker les photos.
    :return: Chemin local de la photo.
    """
    os.makedirs(photos_dir, exist_ok=True)
    
    # Créer un hash de l'email pour avoir une photo stable par persona
    email_hash = hashlib.md5(persona_email.encode()).hexdigest()
    photo_filename = f"{email_hash}.jpg"
    photo_path = os.path.join(photos_dir, photo_filename)
    
    # Si la photo existe déjà, la retourner
    if os.path.exists(photo_path):
        return photo_path
    
    # Sinon, télécharger une nouvelle photo
    try:
        # Utiliser randomuser.me avec seed pour avoir une photo stable par persona
        # Filtrage par âge : entre 25 et 55 ans (adultes professionnels)
        # Le seed est basé sur le hash de l'email pour avoir toujours la même photo
        seed = email_hash[:16]  # Utiliser les 16 premiers caractères du hash comme seed
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Essayer plusieurs fois avec des seeds différents jusqu'à trouver une photo avec un âge approprié
        max_attempts = 10
        for attempt in range(max_attempts):
            # Générer un seed unique pour chaque tentative
            if attempt == 0:
                current_seed = seed
            else:
                # Modifier le seed pour chaque tentative
                current_seed = hashlib.md5((email_hash + str(attempt)).encode()).hexdigest()[:16]
            
            randomuser_url = f"https://randomuser.me/api/?seed={current_seed}&results=1"
            
            try:
                # Récupérer les données de l'utilisateur
                response = requests.get(randomuser_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('results') and len(data['results']) > 0:
                        user = data['results'][0]
                        age = user.get('dob', {}).get('age', 0)
                        
                        # Vérifier que l'âge est approprié (25-55 ans)
                        if 25 <= age <= 55:
                            photo_url = user.get('picture', {}).get('large', '')
                            if photo_url:
                                # Télécharger la photo
                                photo_response = requests.get(photo_url, headers=headers, timeout=10)
                                if photo_response.status_code == 200:
                                    # Vérifier que c'est bien une image (pas une erreur HTML)
                                    content_type = photo_response.headers.get('content-type', '')
                                    if 'image' in content_type:
                                        with open(photo_path, 'wb') as f:
                                            f.write(photo_response.content)
                                        print(f"✅ Photo téléchargée pour {persona_email} (âge: {age} ans, tentative {attempt + 1}): {photo_path}")
                                        return photo_path
                                    else:
                                        print(f"⚠️  Réponse n'est pas une image pour {persona_email} (tentative {attempt + 1})")
                        else:
                            print(f"⚠️  Photo avec âge inapproprié ({age} ans) pour {persona_email} (tentative {attempt + 1})")
            except Exception as e:
                print(f"⚠️  Erreur lors de la tentative {attempt + 1} pour {persona_email}: {e}")
                continue
        
        # Si aucune photo appropriée n'a été trouvée après toutes les tentatives
        print(f"⚠️  Impossible de trouver une photo avec un âge approprié pour {persona_email} après {max_attempts} tentatives")
        return None
            
    except Exception as e:
        print(f"⚠️  Erreur lors du téléchargement de la photo: {e}")
        return None

def generate_cv_for_persona(persona_email, persona_name, cv_data=None, template_file="/app/templates/cv/cv_template.html", 
                            output_dir="/app/cvs", search_key=None, cv_id=None, persona_data=None):
    """
    Génère un CV au format PDF pour un persona spécifique.
    :param persona_email: Email du persona.
    :param persona_name: Nom du persona.
    :param cv_data: Dictionnaire contenant les données du CV (optionnel, sera généré si non fourni).
    :param template_file: Chemin du fichier HTML servant de modèle.
    :param output_dir: Dossier de sortie pour les CVs.
    :param search_key: Clé de la recherche (optionnel, pour CV spécifique à une recherche).
    :param cv_id: ID du CV (optionnel, pour identifier le CV).
    :param persona_data: Données complètes du persona (optionnel, pour générer un CV réaliste).
    :return: Chemin du fichier PDF généré.
    """
    # Créer le dossier de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    # Si cv_data n'est pas fourni, générer des données réalistes
    if not cv_data:
        cv_data = generate_realistic_cv_data(persona_name, persona_email, persona_data)
    
    # Récupérer ou générer la photo du persona
    photo_path = get_persona_photo(persona_email)
    if photo_path:
        # Convertir le chemin absolu en chemin relatif pour le template
        # Pour PDF, on doit utiliser le chemin absolu avec file://
        cv_data['photo_path'] = photo_path
    
    # Charger le modèle HTML
    with open(template_file, 'r', encoding='utf-8') as file:
        template_content = file.read()
    
    # Ajouter les informations du persona aux données du CV
    cv_data['name'] = persona_name
    cv_data['email'] = persona_email
    
    # Créer le rendu HTML avec Jinja2
    template = Template(template_content)
    rendered_html = template.render(**cv_data)
    
    # Nom du fichier de sortie
    safe_email = persona_email.replace('@', '_at_').replace('.', '_')
    if search_key and cv_id:
        # CV spécifique à une recherche
        safe_search = search_key.replace(' ', '_').replace('/', '_')
        output_file = os.path.join(output_dir, f"{safe_email}_{safe_search}_{cv_id}_cv.pdf")
    elif cv_id:
        # CV avec ID spécifique
        output_file = os.path.join(output_dir, f"{safe_email}_{cv_id}_cv.pdf")
    else:
        # CV par défaut
        output_file = os.path.join(output_dir, f"{safe_email}_cv.pdf")
    
    try:
        # Convertir le HTML en PDF
        # Configuration pour wkhtmltopdf
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        pdfkit.from_string(rendered_html, output_file, options=options)
        print(f"CV généré pour {persona_name} ({persona_email}): {output_file}")
        return output_file
    except OSError as e:
        # wkhtmltopdf n'est pas installé ou non trouvé
        print(f"⚠️  wkhtmltopdf non disponible: {e}")
        print(f"   Le CV HTML a été généré mais pas converti en PDF")
        # Sauvegarder le HTML à la place
        html_file = output_file.replace('.pdf', '.html')
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        print(f"   Fichier HTML sauvegardé: {html_file}")
        return html_file
    except Exception as e:
        print(f"Erreur lors de la génération du CV pour {persona_email}: {e}")
        # Sauvegarder le HTML en fallback
        html_file = output_file.replace('.pdf', '.html')
        try:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(rendered_html)
            print(f"   Fichier HTML sauvegardé en fallback: {html_file}")
            return html_file
        except:
            return None

def generate_cvs_from_json(cvs_file="/app/config/cvs.json", personas_file="/app/config/personas.json", template_file="/app/templates/cv/cv_template.html", use_realistic_data=True):
    """
    Génère des CVs pour tous les personas.
    :param cvs_file: Fichier JSON contenant les données des CVs (utilisé si use_realistic_data=False).
    :param personas_file: Fichier JSON contenant les personas.
    :param template_file: Fichier template HTML pour les CVs.
    :param use_realistic_data: Si True, génère des CVs réalistes avec vraies entreprises. Sinon, utilise cvs_file.
    :return: Dictionnaire {persona_email: cv_path}
    """
    # Charger les personas
    with open(personas_file, 'r', encoding='utf-8') as file:
        personas_data = json.load(file)
    
    cv_paths = {}
    
    # Générer un CV pour chaque persona
    for persona_key, persona_info in personas_data.items():
        if use_realistic_data:
            # Générer des données CV réalistes
            cv_data = None  # Sera généré dans generate_cv_for_persona
            persona_data = persona_info
        else:
            # Utiliser les données du fichier JSON
            try:
                with open(cvs_file, 'r', encoding='utf-8') as file:
                    cvs_data = json.load(file)
                cv_keys = list(cvs_data.keys())
                cv_key = cv_keys[hash(persona_key) % len(cv_keys)]
                cv_data = cvs_data[cv_key]
                persona_data = None
            except FileNotFoundError:
                # Si le fichier n'existe pas, utiliser les données réalistes
                cv_data = None
                persona_data = persona_info
        
        cv_path = generate_cv_for_persona(
            persona_info['email'],
            persona_info['name'],
            cv_data,
            template_file,
            persona_data=persona_data
        )
        
        if cv_path:
            cv_paths[persona_info['email']] = cv_path
    
    return cv_paths

