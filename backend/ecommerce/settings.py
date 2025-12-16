from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Sécurité: pour le dev on met une valeur par défaut
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

# Dev par défaut
DEBUG = os.getenv("DEBUG", "1") == "1"

# Pour dev, on autorise tout (tu pourras restreindre en prod)
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Tes apps
    "core",
    "storages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ecommerce.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ecommerce.wsgi.application"

# Pour l’instant, DB simple en SQLite pour dev
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

# Configuration de la base de données (PostgreSQL ou SQLite)
# Si POSTGRES_HOST est défini (dans l'environnement Docker Prod), on utilise PostgreSQL
if os.getenv("POSTGRES_HOST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB"),
            "USER": os.getenv("POSTGRES_USER"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
            "HOST": os.getenv("POSTGRES_HOST"),
            "PORT": os.getenv("POSTGRES_PORT"),
        }
    }
else:
    # Pour l’instant, DB simple en SQLite pour dev (si non défini)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
# =========================================================
# ☁️ Configuration des Fichiers Médias (Google Cloud Storage)
# =========================================================

GCS_BUCKET = os.getenv("GCS_BUCKET")
DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"

# Configuration supplémentaire (Utiliser les IDs et régions réels)
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "VOTRE_PROJET_ID")
GCP_LOCATION = os.getenv("GCP_LOCATION", "VOTRE_REGION")

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# Configuration pour les Fichiers Statiques
if os.getenv("GCS_BUCKET") and not DEBUG:
    # 1. Utiliser GCS pour les statiques en Production
    STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"

    # 2. Définir le chemin de base des statiques sur le CDN GCS
    STATIC_URL = f"https://storage.googleapis.com/{os.getenv('GCS_BUCKET')}/static/"

    # Optional: Ajouter des paramètres spécifiques si nécessaire (ex: cache)
    GS_STATIC_LOCATION = (
        "static"  # Les fichiers statiques seront stockés sous ce chemin
    )
else:
    # 3. Maintenir le comportement local en Dev (ou si les variables GCS sont absentes)
    STATIC_URL = "static/"
    # STATIC_ROOT et STATICFILES_DIRS restent inchangés
