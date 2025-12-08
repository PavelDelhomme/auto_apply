from jinja2 import Template

def generate_cover_letter(job, template_path="/app/templates/letters/cover_letter_template.txt"):
    """
    Génère une lettre de motivation personnalisée pour un job donné.
    :param job: Dictionnaire contenant les informations sur l'offre (title, company, location).
    :param template_path: Chemin vers le fichier modèle de lettre.
    :return: Texte de la lettre générée.
    """
    with open(template_path, 'r') as file:
        template_content = file.read()
    
    template = Template(template_content)
    
    cover_letter = template.render(
        job_title=job['title'],
        company_name=job['company'],
        location=job['location']
    )
    
    return cover_letter

# Exemple d'utilisation
if __name__ == "__main__":
    example_job = {
        "title": "Développeur Python",
        "company": "Aubépine Scop",
        "location": "Rennes"
    }
    
    print(generate_cover_letter(example_job))
