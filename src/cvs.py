import json
from jinja2 import Template
import pdfkit

# Chargement des données depuis le fichier JSON
with open('cvs.json', 'r') as file:
    cvs_data = json.load(file)

# Charger le motdèle HTML
with open('cv_template.html', 'r') as file:
    template_content = file.read()

# Créer un rendu HTML pour chaque CV
for cv_name, cv_data in cvs_data.items():
    template = Template(template_content)
    rendered_html = template.render(cv_data)

    # Convertir le HTML en PDF
    output_file = f"{cv_name}.pdf"
    pdfkit.from_string(rendered_html, output_file)
    print(f"CV généré : {output_file}")