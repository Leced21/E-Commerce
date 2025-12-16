#!/bin/sh

# Fichier: infra/docker/entrypoint.sh (CORRIGÉ)
echo "Démarrage de l'entrypoint..."

# Si DJANGO_DEBUG est explicitement désactivé (mode production)
if [ "$DJANGO_DEBUG" = "0" ]; then
    echo "Mode PRODUCTION détecté. Chargement des secrets via Secret Manager."
    
    # Exécuter le script Python depuis son nouvel emplacement
    # Le script Python va lire les secrets et les injecter dans l'environnement du shell
    python /usr/local/bin/load_secrets.py

    # IMPORTANT: Exécuter les migrations avant de lancer le serveur Gunicorn
    echo "Exécution des migrations de base de données."
    python manage.py migrate --noinput
else
    echo "Mode DÉVELOPPEMENT détecté. Pas de chargement de secrets ni de migrations ici."
fi

# Exécuter l'application principale (Gunicorn)
# L'utilisation de 'exec' remplace le processus shell actuel par Gunicorn, 
# ce qui permet à Docker de mieux gérer les signaux (ex: arrêt)
echo "Lancement de Gunicorn avec $GUNICORN_WORKERS workers."
exec gunicorn ecommerce.wsgi:application --bind 0.0.0.0:8000 --workers $GUNICORN_WORKERS