# 🚀 Améliorations - Recherches avec Personas et Templates Réutilisables

## ✅ Fonctionnalités Ajoutées

### 1. Assignation de Personas aux Recherches

**Nouveaux champs dans les recherches** :
- `personas_assigned` : Liste des emails de personas assignés à cette recherche
- `personas_excluded` : Liste des emails de personas à exclure de cette recherche

**Comportement** :
- Si `personas_assigned` est défini et non vide, **seuls ces personas** seront utilisés pour cette recherche
- Si `personas_excluded` est défini, ces personas seront **exclus** même s'ils sont assignés globalement
- Si aucun persona n'est assigné, **tous les personas disponibles** seront utilisés

### 2. Interface de Création/Édition de Recherche Améliorée

**Dans le modal de recherche** :
- ✅ Section "Personas assignés" avec bouton de sélection
- ✅ Section "Personas exclus" avec bouton de sélection
- ✅ Affichage visuel des personas sélectionnés
- ✅ Possibilité de retirer des personas de la liste
- ✅ Checkbox "Standalone" pour les recherches sans personas

### 3. Interface dans les Paramètres

**Nouvelle section "Lancer plusieurs recherches avec personas"** :
- ✅ Liste de toutes les recherches avec checkboxes
- ✅ Indication visuelle des personas assignés/exclus pour chaque recherche
- ✅ Sélection de personas globaux (optionnel)
- ✅ Configuration des paramètres de lancement (max candidatures, délais, etc.)
- ✅ Bouton pour lancer toutes les recherches sélectionnées

**Logique de lancement** :
1. Si des personas sont sélectionnés dans les paramètres, ils sont utilisés pour toutes les recherches
2. Si une recherche a des personas assignés, ceux-ci sont prioritaires
3. Les personas exclus sont toujours exclus, même s'ils sont assignés

### 4. Extraction des Styles CSS

**Fichiers créés** :
- `static/css/dashboard.css` : Styles principaux du dashboard
- `static/css/components.css` : Styles des composants réutilisables (déjà existant)
- `static/js/components.js` : Fonctions JavaScript réutilisables (déjà existant)

**Avantages** :
- ✅ Code plus maintenable
- ✅ Styles réutilisables
- ✅ Chargement plus rapide (cache du navigateur)
- ✅ Séparation des préoccupations

### 5. Templates Réutilisables

**Composants disponibles** :
- `templates/components/persona_card.html` : Carte persona réutilisable
- `templates/components/search_card.html` : Carte recherche réutilisable

**Utilisation** :
```python
from flask import render_template_string

# Dans votre code Python
with open('templates/components/persona_card.html') as f:
    template = f.read()
    html = render_template_string(template, persona=persona, ...)
```

## 📋 Utilisation

### Assigner des Personas à une Recherche

1. **Créer/Modifier une recherche** :
   - Cliquez sur "Créer une recherche" ou "Modifier"
   - Dans le modal, section "Personas pour cette recherche"
   - Cliquez sur "👥 Sélectionner des personas assignés"
   - Sélectionnez les personas souhaités
   - Cliquez sur "✅ Confirmer"

2. **Exclure des Personas** :
   - Cliquez sur "🚫 Sélectionner des personas à exclure"
   - Sélectionnez les personas à exclure
   - Cliquez sur "✅ Confirmer"

### Lancer Plusieurs Recherches depuis les Paramètres

1. **Accéder aux paramètres** :
   - Menu → "⚙️ Paramètres"
   - Section "🚀 Lancer plusieurs recherches avec personas"

2. **Sélectionner les recherches** :
   - Cochez les recherches à lancer
   - Chaque recherche affiche ses personas assignés/exclus

3. **Sélectionner des personas globaux (optionnel)** :
   - Cliquez sur "👥 Sélectionner des personas"
   - Sélectionnez les personas à utiliser pour toutes les recherches

4. **Configurer les paramètres** :
   - Max candidatures par persona
   - Délais entre candidatures
   - Utilisation des lettres de motivation

5. **Lancer** :
   - Cliquez sur "🚀 Lancer les recherches"

## 🔧 Structure du Code

### Backend

**`src/search_manager.py`** :
- `create_search()` : Accepte `personas_assigned` et `personas_excluded`
- `update_search()` : Met à jour ces champs

**`src/app.py`** :
- `api_create_search()` : Gère les personas assignés/exclus
- `api_update_search()` : Met à jour les personas
- `api_run_multiple_searches()` : Utilise les personas assignés de chaque recherche

### Frontend

**`templates/dashboard.html`** :
- Modal de recherche avec sélecteurs de personas
- Section paramètres avec interface de lancement multiple
- Fonctions JavaScript :
  - `showPersonaSelector(type)` : Affiche le sélecteur de personas
  - `updatePersonasDisplay(type, personasSet)` : Met à jour l'affichage
  - `loadSettingsSearches()` : Charge les recherches dans les paramètres
  - `startMultipleSearchesFromSettings()` : Lance les recherches

## 🎯 Exemples d'Utilisation

### Scénario 1 : Recherche avec Personas Spécifiques

```javascript
// Créer une recherche avec seulement 2 personas
{
  "name": "Développeur Python Senior",
  "query": "développeur python senior",
  "location": "Paris",
  "personas_assigned": ["persona1@example.com", "persona2@example.com"],
  "personas_excluded": []
}
```

### Scénario 2 : Recherche Excluant Certains Personas

```javascript
// Recherche qui utilise tous les personas sauf certains
{
  "name": "Développeur Junior",
  "query": "développeur junior",
  "location": "Rennes",
  "personas_assigned": [],  // Tous les personas
  "personas_excluded": ["senior@example.com"]  // Exclure le persona senior
}
```

### Scénario 3 : Lancer Plusieurs Recherches

1. Aller dans Paramètres
2. Sélectionner 3 recherches
3. Sélectionner 2 personas globaux
4. Configurer : max 5 candidatures, délai 5-10s
5. Lancer → Chaque recherche utilisera ses personas assignés ou les personas globaux

## 📝 Notes Techniques

### Priorité des Personas

1. **Personas assignés à la recherche** (priorité la plus haute)
2. **Personas sélectionnés dans les paramètres** (si aucun assigné)
3. **Tous les personas disponibles** (si aucun sélectionné)
4. **Personas exclus** (toujours exclus, quelle que soit la priorité)

### Compatibilité

- ✅ Rétrocompatible : Les recherches existantes sans `personas_assigned` fonctionnent normalement
- ✅ Les recherches standalone ignorent les personas
- ✅ Les personas exclus sont toujours respectés

## 🚀 Prochaines Améliorations Possibles

1. **Templates Jinja2** : Utiliser `{% include %}` pour les composants
2. **Composants Vue/React** : Migrer vers un framework moderne
3. **Graphiques** : Visualisation des statistiques par recherche/persona
4. **Planification** : Programmer des recherches à des heures spécifiques
5. **Notifications** : Alertes quand des recherches sont terminées

