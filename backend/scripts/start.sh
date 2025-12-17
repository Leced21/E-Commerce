#!/bin/bash
set -e  # Arrête le script en cas d'erreur

echo "--- Démarrage de l'Entrypoint ---"

# 1. Charger les secrets GCP
python /app/scripts/load_secrets.py

# 2. Sourcer les secrets pour le processus actuel (Gunicorn)
if [ -f /tmp/.env.secrets ]; then
    source /tmp/.env.secrets
    echo "--- Secrets injectés dans le Shell ---"
fi

# 3. Migrations
echo "--- Exécution des migrations ---"
python manage.py migrate --noinput

# 4. Lancement
echo "--- Lancement de Gunicorn ---"
exec gunicorn ecommerce.wsgi:application --bind 0.0.0.0:8000 --workers 3