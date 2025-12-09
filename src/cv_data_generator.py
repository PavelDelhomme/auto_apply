"""
Générateur de données CV réalistes pour les personas
"""

import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Vraies entreprises françaises par secteur
FRENCH_COMPANIES = {
    "tech": [
        "Capgemini", "Atos", "Sopra Steria", "Dassault Systèmes", "Criteo", 
        "Blablacar", "Veepee", "BlaBlaCar", "Cdiscount", "Vente-privee.com",
        "Orange", "Bouygues Telecom", "SFR", "Free", "OVHcloud",
        "Mirakl", "Doctolib", "Alan", "Back Market", "Qonto",
        "L'Occitane", "LVMH", "Kering", "Hermès", "L'Oréal"
    ],
    "finance": [
        "BNP Paribas", "Crédit Agricole", "Société Générale", "BPCE", "Crédit Mutuel",
        "Axa", "Allianz", "Groupama", "CNP Assurances", "Macif"
    ],
    "consulting": [
        "McKinsey & Company", "Boston Consulting Group", "Bain & Company",
        "Accenture", "Deloitte", "PwC", "EY", "KPMG", "Wavestone", "Mazars"
    ],
    "industrie": [
        "Airbus", "Thales", "Safran", "Schneider Electric", "Valeo",
        "Renault", "Stellantis", "Michelin", "Saint-Gobain", "Legrand"
    ],
    "retail": [
        "Carrefour", "Leclerc", "Auchan", "Casino", "Monoprix",
        "Fnac Darty", "Décathlon", "Leroy Merlin", "Castorama", "Boulanger"
    ]
}

# Titres de postes réalistes par domaine
JOB_TITLES = {
    "développeur": [
        "Développeur Full Stack", "Développeur Backend", "Développeur Frontend",
        "Développeur Python", "Développeur JavaScript", "Développeur Java",
        "Ingénieur DevOps", "Ingénieur Cloud", "Architecte Logiciel",
        "Lead Developer", "Tech Lead", "Développeur Senior"
    ],
    "devops": [
        "Ingénieur DevOps", "Ingénieur Cloud", "SRE (Site Reliability Engineer)",
        "Ingénieur Infrastructure", "DevOps Engineer", "Cloud Architect"
    ],
    "data": [
        "Data Engineer", "Data Scientist", "Data Analyst", "ML Engineer",
        "Ingénieur Big Data", "Analyste Business Intelligence"
    ],
    "general": [
        "Développeur Full Stack", "Ingénieur Logiciel", "Développeur Web",
        "Développeur Mobile", "Ingénieur Informatique", "Consultant IT"
    ]
}

# Compétences techniques par domaine
TECH_SKILLS = {
    "backend": ["Python", "Java", "C#", "Node.js", "Go", "Rust", "PHP", "Ruby"],
    "frontend": ["JavaScript", "TypeScript", "React", "Vue.js", "Angular", "HTML/CSS", "SASS"],
    "devops": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "Ansible", "Jenkins", "GitLab CI"],
    "database": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra"],
    "tools": ["Git", "Linux", "Agile", "Scrum", "JIRA", "Confluence"]
}

# Universités françaises
FRENCH_UNIVERSITIES = [
    "Université Paris-Saclay", "Sorbonne Université", "Université Paris 1 Panthéon-Sorbonne",
    "Université Paris-Dauphine", "École Polytechnique", "HEC Paris", "ESSEC", "ESCP",
    "École Centrale Paris", "INSA Lyon", "École des Mines", "Télécom Paris",
    "Université de Lyon", "Université de Rennes", "Université de Nantes",
    "Université de Bordeaux", "Université de Toulouse", "Université de Strasbourg"
]

# Diplômes
DEGREES = [
    "Bac+2 (BTS/DUT)", "Bac+3 (Licence)", "Bac+4 (Master 1)", 
    "Bac+5 (Master 2 / Ingénieur)", "Bac+6 (Doctorat)"
]

# Langues
LANGUAGES = ["Français", "Anglais", "Espagnol", "Allemand", "Italien", "Chinois"]

# Certifications
CERTIFICATIONS = [
    "AWS Certified Solutions Architect", "Google Cloud Professional", "Azure Certified",
    "Kubernetes Certified Administrator", "Scrum Master", "PMP", "ITIL"
]

def generate_realistic_cv_data(persona_name: str, persona_email: str, persona_data: Optional[Dict] = None) -> Dict:
    """
    Génère des données CV réalistes pour un persona.
    
    :param persona_name: Nom du persona
    :param persona_email: Email du persona
    :param persona_data: Données du persona (optionnel, pour utiliser les compétences existantes)
    :return: Dictionnaire avec les données du CV
    """
    # Déterminer le domaine principal basé sur les compétences du persona ou aléatoirement
    if persona_data and persona_data.get('skills'):
        skills = persona_data['skills']
        if any('devops' in s.lower() or 'docker' in s.lower() or 'kubernetes' in s.lower() for s in skills):
            domain = "devops"
        elif any('data' in s.lower() or 'ml' in s.lower() or 'ai' in s.lower() for s in skills):
            domain = "data"
        else:
            domain = "développeur"
    else:
        domain = random.choice(["développeur", "devops", "data"])
    
    # Générer le titre du poste
    title = random.choice(JOB_TITLES.get(domain, JOB_TITLES["general"]))
    
    # Générer les compétences techniques
    skills = []
    if domain == "devops":
        skills.extend(random.sample(TECH_SKILLS["devops"], min(5, len(TECH_SKILLS["devops"]))))
        skills.extend(random.sample(TECH_SKILLS["tools"], min(3, len(TECH_SKILLS["tools"]))))
        skills.extend(random.sample(TECH_SKILLS["database"], min(2, len(TECH_SKILLS["database"]))))
    elif domain == "data":
        skills.extend(["Python", "SQL", "Machine Learning", "Data Analysis"])
        skills.extend(random.sample(TECH_SKILLS["database"], min(3, len(TECH_SKILLS["database"]))))
        skills.extend(random.sample(TECH_SKILLS["tools"], min(2, len(TECH_SKILLS["tools"]))))
    else:
        skills.extend(random.sample(TECH_SKILLS["backend"], min(3, len(TECH_SKILLS["backend"]))))
        skills.extend(random.sample(TECH_SKILLS["frontend"], min(2, len(TECH_SKILLS["frontend"]))))
        skills.extend(random.sample(TECH_SKILLS["database"], min(2, len(TECH_SKILLS["database"]))))
        skills.extend(random.sample(TECH_SKILLS["tools"], min(3, len(TECH_SKILLS["tools"]))))
    
    # Générer l'expérience professionnelle (2-4 postes)
    num_jobs = random.randint(2, 4)
    experience = []
    current_date = datetime.now()
    
    for i in range(num_jobs):
        # Dates décroissantes (plus récent en premier)
        if i == 0:
            # Poste actuel
            start_date = current_date - timedelta(days=random.randint(180, 730))  # 6 mois à 2 ans
            end_date = None
            dates_str = f"{start_date.strftime('%m/%Y')} - Présent"
        else:
            # Postes précédents
            duration_months = random.randint(12, 36)  # 1 à 3 ans
            end_date = current_date - timedelta(days=random.randint(30, 365))
            start_date = end_date - timedelta(days=duration_months * 30)
            dates_str = f"{start_date.strftime('%m/%Y')} - {end_date.strftime('%m/%Y')}"
            current_date = start_date
        
        # Choisir une entreprise réaliste
        company_type = random.choice(list(FRENCH_COMPANIES.keys()))
        company = random.choice(FRENCH_COMPANIES[company_type])
        
        # Titre du poste
        job_title = random.choice(JOB_TITLES.get(domain, JOB_TITLES["general"]))
        if i > 0 and random.random() > 0.5:
            # Poste précédent peut être un niveau inférieur
            job_title = random.choice(JOB_TITLES.get(domain, JOB_TITLES["general"]))
        
        # Localisation
        locations = ["Paris", "Lyon", "Rennes", "Nantes", "Bordeaux", "Toulouse", "Lille", "Marseille", "Remote"]
        location = random.choice(locations)
        
        # Détails de l'expérience
        details = generate_job_details(job_title, domain)
        
        experience.append({
            "title": job_title,
            "company": company,
            "dates": dates_str,
            "location": location,
            "details": details
        })
    
    # Générer l'éducation (1-2 diplômes)
    education = []
    num_degrees = random.randint(1, 2)
    current_year = datetime.now().year
    
    for i in range(num_degrees):
        if i == 0:
            # Diplôme principal (Bac+5)
            degree = "Bac+5 (Master 2 / Ingénieur)"
            start_year = current_year - random.randint(5, 8)
            end_year = start_year + 5
        else:
            # Diplôme secondaire (optionnel)
            degree = random.choice(["Bac+3 (Licence)", "Bac+2 (BTS/DUT)"])
            start_year = current_year - random.randint(8, 12)
            end_year = start_year + (2 if "Bac+2" in degree else 3)
        
        university = random.choice(FRENCH_UNIVERSITIES)
        education.append({
            "degree": degree,
            "school": university,
            "dates": f"{start_year}-{end_year}"
        })
    
    # Générer les langues (2-3 langues)
    languages = random.sample(LANGUAGES, min(random.randint(2, 3), len(LANGUAGES)))
    language_levels = {}
    for lang in languages:
        if lang == "Français":
            language_levels[lang] = "Natif"
        else:
            language_levels[lang] = random.choice(["Courant", "Intermédiaire", "Débutant"])
    
    # Générer les certifications (0-2)
    num_certs = random.randint(0, 2)
    certifications = random.sample(CERTIFICATIONS, min(num_certs, len(CERTIFICATIONS))) if num_certs > 0 else []
    
    # Générer des projets (2-3 projets)
    projects = generate_projects(domain, num_projects=random.randint(2, 3))
    
    # Informations de contact depuis le persona
    contact = {}
    if persona_data:
        contact['email'] = persona_email
        contact['phone'] = persona_data.get('phone', '')
        contact['linkedin'] = persona_data.get('linkedin', '')
        contact['github'] = persona_data.get('github', '')
        contact['location'] = persona_data.get('location', random.choice(["Paris", "Lyon", "Rennes"]))
    else:
        contact['email'] = persona_email
        contact['location'] = random.choice(["Paris", "Lyon", "Rennes"])
    
    return {
        "title": title,
        "skills": skills,
        "experience": experience,
        "education": education,
        "languages": language_levels,
        "certifications": certifications,
        "projects": projects,
        "contact": contact,
        "summary": generate_professional_summary(persona_name, title, domain, len(experience))
    }

def generate_job_details(job_title: str, domain: str) -> List[str]:
    """Génère des détails réalistes pour une expérience professionnelle."""
    details_templates = {
        "devops": [
            "Mise en place et maintenance de pipelines CI/CD avec Jenkins et GitLab CI",
            "Déploiement et orchestration de conteneurs Docker sur Kubernetes",
            "Gestion de l'infrastructure cloud AWS/Azure avec Terraform",
            "Monitoring et optimisation des performances applicatives",
            "Automatisation des processus de déploiement et de scaling",
            "Mise en place de stratégies de backup et de disaster recovery",
            "Collaboration avec les équipes de développement pour améliorer la qualité du code"
        ],
        "data": [
            "Développement de modèles de machine learning pour la prédiction",
            "Traitement et analyse de grandes quantités de données (Big Data)",
            "Création de dashboards et rapports business intelligence",
            "Optimisation de requêtes SQL et gestion de bases de données",
            "Mise en place de pipelines ETL pour la transformation de données",
            "Collaboration avec les équipes métier pour identifier les besoins analytiques"
        ],
        "développeur": [
            "Développement d'applications web full stack avec Python/Django et React",
            "Conception et développement d'APIs REST pour des services microservices",
            "Refactoring et optimisation de code legacy",
            "Participation aux code reviews et amélioration continue des pratiques",
            "Collaboration en équipe agile (Scrum) avec livraisons itératives",
            "Mise en place de tests unitaires et d'intégration",
            "Développement de fonctionnalités backend et frontend",
            "Intégration avec des services tiers et APIs externes"
        ]
    }
    
    templates = details_templates.get(domain, details_templates["développeur"])
    # Sélectionner 3-5 détails aléatoires
    num_details = random.randint(3, min(5, len(templates)))
    return random.sample(templates, num_details)

def generate_projects(domain: str, num_projects: int = 2) -> List[Dict]:
    """Génère des projets réalistes."""
    project_templates = {
        "devops": [
            {"name": "Migration vers Kubernetes", "description": "Migration de l'infrastructure legacy vers Kubernetes avec automatisation complète"},
            {"name": "Pipeline CI/CD multi-environnements", "description": "Mise en place d'un pipeline CI/CD pour 10+ microservices"},
            {"name": "Monitoring centralisé", "description": "Déploiement d'une solution de monitoring avec Prometheus et Grafana"}
        ],
        "data": [
            {"name": "Système de recommandation", "description": "Développement d'un système de recommandation avec machine learning"},
            {"name": "Dashboard analytique", "description": "Création d'un dashboard interactif pour l'analyse de données business"},
            {"name": "Pipeline de traitement de données", "description": "Conception d'un pipeline ETL pour le traitement de données en temps réel"}
        ],
        "développeur": [
            {"name": "Application e-commerce", "description": "Développement d'une plateforme e-commerce full stack avec paiement en ligne"},
            {"name": "API REST microservices", "description": "Conception et développement d'une architecture microservices avec API REST"},
            {"name": "Application mobile", "description": "Développement d'une application mobile cross-platform avec React Native"}
        ]
    }
    
    templates = project_templates.get(domain, project_templates["développeur"])
    # Sélectionner des projets aléatoires
    return random.sample(templates, min(num_projects, len(templates)))

def generate_professional_summary(name: str, title: str, domain: str, years_exp: int) -> str:
    """Génère un résumé professionnel."""
    summaries = {
        "devops": f"{name} est un {title} avec {years_exp} ans d'expérience dans la mise en place et la maintenance d'infrastructures cloud, l'automatisation des déploiements et l'optimisation des performances. Passionné par les technologies cloud et l'infrastructure as code.",
        "data": f"{name} est un {title} avec {years_exp} ans d'expérience dans l'analyse de données, le machine learning et la création de solutions data-driven. Expert en Python, SQL et outils de Big Data.",
        "développeur": f"{name} est un {title} avec {years_exp} ans d'expérience dans le développement d'applications web et mobiles. Passionné par les technologies modernes et les bonnes pratiques de développement logiciel."
    }
    
    return summaries.get(domain, summaries["développeur"])

