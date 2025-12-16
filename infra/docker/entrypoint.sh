#!/bin/sh

# Fichier: infra/docker/entrypoint.sh

# Charger les variables d'environnement nécessaires pour l'authentification GCP
# (Ces variables sont injectées via Docker Compose / .env)
# La librairie Google Cloud utilise l'environnement pour s'authentifier.

# Importer la librairie Python Secret Manager
python /app/scripts/load_secrets.py

# Exécuter l'application principale (Gunicorn)
exec gunicorn ecommerce.wsgi:application -b 0.0.0.0:8000 --workers $GUNICORN_WORKERS