import json
import os
import hashlib
import requests
from jinja2 import Template
import pdfkit

def get_persona_photo(persona_email, photos_dir="/app/photos"):
    """
    Récupère ou génère une photo pour un persona depuis thispersondoesnotexist.com.
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
        # Utiliser le hash comme seed pour obtenir une photo différente par persona
        # thispersondoesnotexist.com génère des photos aléatoires, mais on peut utiliser l'ID
        # On utilise le hash modulo un grand nombre pour avoir un ID
        photo_id = int(email_hash[:8], 16) % 1000000
        photo_url = f"https://thispersondoesnotexist.com/"
        
        # Télécharger la photo
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(photo_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            with open(photo_path, 'wb') as f:
                f.write(response.content)
            print(f"Photo téléchargée pour {persona_email}: {photo_path}")
            return photo_path
        else:
            print(f"⚠️  Impossible de télécharger la photo (HTTP {response.status_code})")
            return None
    except Exception as e:
        print(f"⚠️  Erreur lors du téléchargement de la photo: {e}")
        return None

def generate_cv_for_persona(persona_email, persona_name, cv_data, template_file="/app/cv_template.html", output_dir="/app/cvs"):
    """
    Génère un CV au format PDF pour un persona spécifique.
    :param persona_email: Email du persona.
    :param persona_name: Nom du persona.
    :param cv_data: Dictionnaire contenant les données du CV.
    :param template_file: Chemin du fichier HTML servant de modèle.
    :param output_dir: Dossier de sortie pour les CVs.
    :return: Chemin du fichier PDF généré.
    """
    # Créer le dossier de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    # Récupérer ou générer la photo du persona
    photo_path = get_persona_photo(persona_email)
    if photo_path:
        # Convertir le chemin absolu en chemin relatif pour le template
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

def generate_cvs_from_json(cvs_file="/app/cvs.json", personas_file="/app/personas.json", template_file="/app/cv_template.html"):
    """
    Génère des CVs pour tous les personas à partir des données JSON.
    :param cvs_file: Fichier JSON contenant les données des CVs.
    :param personas_file: Fichier JSON contenant les personas.
    :param template_file: Fichier template HTML pour les CVs.
    :return: Dictionnaire {persona_email: cv_path}
    """
    # Charger les CVs
    with open(cvs_file, 'r', encoding='utf-8') as file:
        cvs_data = json.load(file)
    
    # Charger les personas
    with open(personas_file, 'r', encoding='utf-8') as file:
        personas_data = json.load(file)
    
    cv_paths = {}
    cv_keys = list(cvs_data.keys())
    
    # Générer un CV pour chaque persona
    for i, (persona_key, persona_info) in enumerate(personas_data.items()):
        # Utiliser un CV de manière cyclique
        cv_key = cv_keys[i % len(cv_keys)]
        cv_data = cvs_data[cv_key]
        
        cv_path = generate_cv_for_persona(
            persona_info['email'],
            persona_info['name'],
            cv_data,
            template_file
        )
        
        if cv_path:
            cv_paths[persona_info['email']] = cv_path
    
    return cv_paths

