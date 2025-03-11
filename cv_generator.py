import json
from jinja2 import Template
import pdfkit

def generate_cv(data_file="data.json", template_file="cv_template.html", output_file="generated_cv.pdf"):
    """
    Génère un CV au format PDF à partir d'un fichier JSON contenant les données.
    :param data_file: Chemin du fichier JSON contenant les données.
    :param template_file: Chemin du fichier HTML servant de modèle.
    :param output_file: Nom du fichier PDF généré.
    """
    # Charger les données depuis le fichier JSON
    with open(data_file, 'r') as file:
        data = json.load(file)

    # Charger le modèle HTML
    with open(template_file,  'r') as file:
        template_content = file.read()
    
    # Créer le rendu HTML avec Jinja2
    template = Template(template_content)
    rendered_html = template.render(data)

    # Convertir le HTML en PDF
    pdfkit.from_string(rendered_html, output_file)
    print(f"CV généré : {output_file}")

