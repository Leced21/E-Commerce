#!/bin/bash

# Fichier: backend/start.sh
# Script de démarrage pour le conteneur Gunicorn/Django en Production

# Terminer immédiatement si une commande échoue
set -e

# Configuration des variables
HOST=$POSTGRES_HOST
PORT=$POSTGRES_PORT
DB=$POSTGRES_DB

# =========================================================
# 1. ATTENDRE LA BASE DE DONNÉES (DB)
# =========================================================
echo "⏳ Attente de la disponibilité de PostgreSQL ($HOST:$PORT)..."
# Utilise 'nc' (netcat) ou 'wait-for-it' si disponible, ici on simule avec un loop simple
# Ceci est crucial pour éviter que les migrations ne se lancent sur une DB non prête.
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$HOST" -U "$POSTGRES_USER" -d "$DB" -c '\q'; do
  >&2 echo "Postgres n'est pas encore disponible - attente de 1 seconde"
  sleep 1
done

>&2 echo "✅ PostgreSQL est disponible. Démarrage de l'application..."

# =========================================================
# 2. CHARGER LES SECRETS (via le script Python)
# =========================================================
# Ceci exécute le script Python qui lit GCP Secret Manager et exporte les variables (SECRET_KEY, STRIPE_SECRET_KEY)
echo "🔑 Chargement des secrets depuis GCP Secret Manager..."
python manage.py runscript load_secrets # Assurez-vous que load_secrets est un runscript ou un script Python simple
echo "✅ Secrets chargés."

# =========================================================
# 3. PRÉPARATION DE L'APPLICATION
# =========================================================

# Appliquer les migrations de la base de données
echo "🚀 Application des migrations de la base de données..."
python manage.py migrate --noinput
echo "✅ Migrations appliquées."

# Collecter les fichiers statiques (pour GCS en Prod)
echo "📁 Collection des fichiers statiques pour GCS..."
python manage.py collectstatic --noinput
echo "✅ Fichiers statiques collectés."

# =========================================================
# 4. LANCEMENT DE GUNICORN
# =========================================================

# Configuration de Gunicorn (ajustez le nombre de workers selon vos ressources)
WORKERS=${GUNICORN_WORKERS:-4}
TIMEOUT=${GUNICORN_TIMEOUT:-30}

echo "Starting Gunicorn with $WORKERS workers..."
exec gunicorn ecommerce.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers $WORKERS \
  --timeout $TIMEOUT \
  --log-level info