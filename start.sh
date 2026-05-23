#!/bin/bash
cd "$(dirname "$0")"
echo "Installation des dépendances..."
pip3 install -r requirements.txt -q
echo "Démarrage de l'application..."
python3 app.py
