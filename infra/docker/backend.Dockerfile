FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# On copie uniquement le requirements pour installer les dépendances
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# On copie le code Django
COPY backend /app
COPY infra/docker/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY backend/scripts/load_secrets.py /usr/local/bin/load_secrets.py

RUN chmod +x /usr/local/bin/entrypoint.sh

CMD ["/usr/local/bin/entrypoint.sh"]

# Commande de démarrage: migrations + serveur
# CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]