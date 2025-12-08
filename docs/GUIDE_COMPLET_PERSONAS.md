# 📚 Guide Complet - Système de Personas

## 🎯 Vue d'Ensemble

Le système de personas permet de créer et gérer plusieurs identités virtuelles pour postuler à des offres d'emploi. Chaque persona représente un candidat avec ses propres informations, CVs, et boîte email.

## 👤 Structure d'un Persona

### Champs de Base

Un persona contient les informations suivantes :

```json
{
  "name": "Christian Gaillard",
  "email": "christian.gaillard@gmx.com",
  "password": "mot_de_passe",
  "alias": false,
  "parent": null
}
```

### Champs Détaillés (Nouveaux)

```json
{
  "skills": ["Python", "JavaScript", "Django", "React"],
  "experience_years": 5,
  "education": [
    {
      "degree": "Master Informatique",
      "school": "Université de Rennes",
      "dates": "2015-2020"
    }
  ],
  "languages": ["Français", "Anglais"],
  "location": "Rennes, France",
  "phone": "+33 6 12 34 56 78",
  "linkedin": "https://linkedin.com/in/christian-gaillard",
  "github": "https://github.com/christian-gaillard",
  "portfolio": "https://christian-gaillard.dev",
  "notes": "Spécialisé en développement web full-stack"
}
```

## 🔄 Variantes de Personas

### Qu'est-ce qu'une Variante ?

Une **variante** (ou **alias**) est un persona qui hérite des caractéristiques d'un persona de base (le **parent**), mais avec un nom et un email différents.

### Pourquoi Utiliser des Variantes ?

1. **Multiplier les candidatures** : Permet de postuler plusieurs fois à la même offre avec des identités différentes
2. **Tester différentes approches** : Tester différents CVs ou lettres de motivation
3. **Éviter la détection** : Utiliser des identités différentes pour éviter d'être détecté comme spam

### Structure d'une Variante

```json
{
  "name": "Georges Fabre",
  "email": "george.fabre@gmx.com",
  "password": "mot_de_passe",
  "alias": true,
  "parent": "christian.gaillard@gmx.com"
}
```

**Caractéristiques** :
- `alias: true` : Indique que c'est une variante
- `parent` : Email du persona de base
- Hérite automatiquement des données du parent (compétences, expérience, etc.)

### Créer des Variantes

#### Via l'Interface

1. Aller dans **Gestion des Personas**
2. Sélectionner un persona de base
3. Cliquer sur **"🔄 Variantes"**
4. Choisir le nombre de variantes à créer
5. Optionnel : Modifier le modèle de nom

#### Via l'API

```python
# Créer une variante
persona_key = persona_manager.create_variant(
    base_persona_key="persona1",
    variant_name="Georges Fabre",
    email_suffix="george.fabre@gmx.com"
)

# Créer plusieurs variantes
persona_keys = persona_manager.create_multiple_variants(
    base_persona_key="persona1",
    count=5,
    name_pattern="Variante {n}"
)
```

## 📄 Système de CVs Multiples

### Concept

Un persona peut avoir **plusieurs CVs** :
- Un CV par défaut
- Un CV par recherche spécifique
- Plusieurs CVs avec des IDs différents

### Structure

Les CVs sont stockés dans :
- **Fichiers** : `/app/cvs/{email}_{search}_{cv_id}_cv.pdf`
- **Base de données** : Table `persona_cvs`

### Créer un CV pour une Recherche Spécifique

```python
# Générer un CV pour un persona et une recherche
cv_path = generate_cv_for_persona(
    persona_email="christian.gaillard@gmx.com",
    persona_name="Christian Gaillard",
    cv_data={
        "title": "Développeur Python Senior",
        "skills": ["Python", "Django", "PostgreSQL"],
        # ... autres données
    },
    search_key="search_python_senior",
    cv_id="senior_cv"
)

# Sauvegarder dans la base de données
save_persona_cv(
    persona_email="christian.gaillard@gmx.com",
    cv_id="senior_cv",
    cv_path=cv_path,
    cv_data=cv_data,
    search_key="search_python_senior"
)
```

### Utilisation Automatique

Lors d'une candidature :
1. Le système cherche un CV spécifique à la recherche (`search_key`)
2. Si non trouvé, utilise le CV par défaut (`cv_id='default'`)
3. Si aucun CV par défaut, génère un nouveau CV

### API

```bash
# Lister tous les CVs d'un persona
GET /api/personas/{email}/cvs

# Récupérer un CV spécifique
GET /api/personas/{email}/cv?search_key=search1&cv_id=cv1

# Générer un nouveau CV
POST /api/personas/{email}/cv/generate
{
  "search_key": "search1",
  "cv_id": "cv1",
  "cv_data": { ... }
}
```

## 📧 Gestion des Emails

### Récupération des Emails

Les emails sont récupérés depuis la boîte IMAP du persona et stockés dans la base de données.

### Types d'Emails

- `application` : Réponses aux candidatures
- `notification` : Notifications diverses
- `other` : Autres emails

### API Email

```bash
# Récupérer les emails
GET /api/personas/{email}/emails

# Compter les emails
GET /api/personas/{email}/emails/count

# Marquer comme lu
POST /api/personas/{email}/emails/{id}/read

# Tester la connexion IMAP
POST /api/personas/{email}/emails/test-connection

# Récupérer depuis IMAP
POST /api/personas/{email}/emails/fetch
```

### Tests des Emails

Des tests automatisés vérifient :
- La connexion IMAP
- La récupération des emails
- Le stockage en base de données
- Le marquage comme lu

## 🔍 Recherches et Personas

### Assignation de Personas

Chaque recherche peut avoir :
- **Personas assignés** : Seuls ces personas seront utilisés
- **Personas exclus** : Ces personas ne seront pas utilisés

### CVs par Recherche

Si un persona a un CV spécifique pour une recherche, ce CV sera utilisé automatiquement lors de la candidature.

### Exemple

```json
{
  "search_key": "python_rennes",
  "name": "Développeur Python Rennes",
  "personas_assigned": ["christian.gaillard@gmx.com"],
  "personas_excluded": []
}
```

Lors de cette recherche :
1. Seul `christian.gaillard@gmx.com` sera utilisé
2. Si un CV existe pour `search_key="python_rennes"`, il sera utilisé
3. Sinon, le CV par défaut sera utilisé

## 🧪 Tests

### Tests des Emails

```bash
# Lancer les tests d'emails
pytest tests/test_persona_emails.py -v

# Tests spécifiques
pytest tests/test_persona_emails.py::test_api_test_email_connection -v
```

### Tests des Personas

```bash
# Lancer tous les tests de personas
pytest tests/test_persona_manager.py -v
```

## 📊 Statistiques

Chaque persona a ses propres statistiques :
- Nombre de candidatures envoyées
- Nombre de candidatures réussies/échouées
- Emails reçus
- CVs générés

## 🔐 Sécurité

### Mots de Passe

- Les mots de passe sont stockés en clair dans `personas.json`
- **Recommandation** : Utiliser un gestionnaire de mots de passe
- **Future amélioration** : Chiffrement des mots de passe

### Emails

- Les emails sont stockés en base de données
- Les mots de passe IMAP ne sont pas exposés via l'API
- Les tests de connexion sont sécurisés

## 🚀 Bonnes Pratiques

### Création de Personas

1. **Un persona de base** avec toutes les informations
2. **Plusieurs variantes** pour multiplier les candidatures
3. **CVs adaptés** pour chaque type de recherche

### Gestion des CVs

1. **CV par défaut** : CV généraliste
2. **CVs spécialisés** : Un CV par domaine (Python, JavaScript, etc.)
3. **CVs par recherche** : CV ultra-spécialisé pour une recherche précise

### Tests

1. **Tester les emails** régulièrement pour vérifier la connexion
2. **Vérifier les CVs** avant de lancer les candidatures
3. **Surveiller les statistiques** pour optimiser les candidatures

## 📝 Exemples Complets

### Exemple 1 : Persona avec Variantes

```json
{
  "persona1": {
    "name": "Christian Gaillard",
    "email": "christian.gaillard@gmx.com",
    "password": "pass123",
    "alias": false,
    "parent": null,
    "skills": ["Python", "Django"],
    "experience_years": 5
  },
  "persona2": {
    "name": "Georges Fabre",
    "email": "george.fabre@gmx.com",
    "password": "pass123",
    "alias": true,
    "parent": "christian.gaillard@gmx.com",
    "skills": ["Python", "Django"],
    "experience_years": 5
  }
}
```

### Exemple 2 : CVs Multiples

```python
# CV par défaut
generate_cv_for_persona(
    persona_email="christian.gaillard@gmx.com",
    persona_name="Christian Gaillard",
    cv_data={"title": "Développeur Full Stack"},
    cv_id="default"
)

# CV pour recherche Python
generate_cv_for_persona(
    persona_email="christian.gaillard@gmx.com",
    persona_name="Christian Gaillard",
    cv_data={"title": "Développeur Python Senior"},
    search_key="python_senior",
    cv_id="python_cv"
)

# CV pour recherche Django
generate_cv_for_persona(
    persona_email="christian.gaillard@gmx.com",
    persona_name="Christian Gaillard",
    cv_data={"title": "Développeur Django"},
    search_key="django_dev",
    cv_id="django_cv"
)
```

## 🔗 Ressources

- [Guide des Recherches](AMELIORATIONS_RECHERCHES_PERSONAS.md)
- [Guide des Logs et Statistiques](AMELIORATIONS_LOGS_STATS.md)
- [API Documentation](API.md)

