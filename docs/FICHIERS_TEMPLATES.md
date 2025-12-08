# 📁 Organisation des Fichiers Templates

## Fichiers actuellement utilisés

### `templates/dashboard.html`
- **Statut**: ✅ Actif
- **Utilisation**: Interface web principale
- **Référencé dans**: `src/app.py` (routes `/` et `/dashboard`)
- **Description**: Dashboard complet avec gestion des personas, recherches, statistiques, etc.

### `templates/cv/cv_template.html`
- **Statut**: ✅ Actif
- **Utilisation**: Template pour génération de CVs
- **Référencé dans**: `src/cv_generator.py`
- **Description**: Template Jinja2 pour générer les CVs en HTML/PDF

### `templates/letters/cover_letter_template.txt`
- **Statut**: ✅ Actif
- **Utilisation**: Template pour lettres de motivation
- **Référencé dans**: `src/application_generator.py`
- **Description**: Template de lettre de motivation

## Fichiers archivés

### `docs/archive/dashboard_v2.html`
- **Statut**: ❌ Archivé
- **Raison**: Ancienne version du dashboard, remplacée par `dashboard.html`
- **Action**: Déplacé dans `docs/archive/` pour référence historique

### `docs/archive/index.html`
- **Statut**: ❌ Archivé
- **Raison**: Ancien template utilisé par `src/server.py` (ancien serveur non utilisé)
- **Action**: Déplacé dans `docs/archive/` car `server.py` n'est plus utilisé

### `docs/archive/server.py`
- **Statut**: ❌ Archivé
- **Raison**: Ancien serveur Flask basique, remplacé par `src/app.py`
- **Action**: Déplacé dans `docs/archive/` pour référence historique

## Structure actuelle

```
templates/
├── dashboard.html              # ✅ Interface principale
├── cv/
│   └── cv_template.html        # ✅ Template CV
└── letters/
    └── cover_letter_template.txt # ✅ Template lettre
```

## Recommandations

1. **Ne pas supprimer les fichiers archivés** : Ils peuvent servir de référence
2. **Utiliser uniquement `dashboard.html`** : C'est le fichier actif
3. **Si besoin de restaurer** : Les fichiers sont dans `docs/archive/`

## Vérification

Pour vérifier quels fichiers sont utilisés :

```bash
# Chercher les références à dashboard.html
grep -r "dashboard.html" src/

# Chercher les références à index.html
grep -r "index.html" src/

# Chercher les références à dashboard_v2.html
grep -r "dashboard_v2" src/
```

