#!/bin/bash
# Script de démarrage pour Docker

echo "🚀 Démarrage d'Auto Apply..."

# Attendre que la base de données soit prête
sleep 2

# Lancer l'application
python app.py

