from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Détection de l'environnement de production
# Nous utilisons la variable POSTGRES_HOST comme indicateur clé d'un environnement Docker/Prod
IS_PRODUCTION = os.getenv("POSTGRES_HOST") is not None
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Sécurité: pour le dev on met une valeur par défaut. DOIT être changée en Prod.
# En Prod, cette clé sera lue par votre script load_secrets.py (via Secret Manager)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

# Le mode DEBUG est False en Production (sécurité et performance)
DEBUG = os.getenv("DEBUG", "1") == "1" and not IS_PRODUCTION  # Force False si en Prod

# Pour dev, on autorise tout. En Prod, il faut restreindre au nom de domaine.
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
    "storages",  # Nécessaire pour Google Cloud Storage
    "rest_framework",
]

# ... MIDDLEWARE, ROOT_URLCONF, TEMPLATES, WSGI_APPLICATION, AUTH_PASSWORD_VALIDATORS ...
# (Ces sections restent inchangées)
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
                "core.context_processors.cart_count",
            ],
        },
    },
]

WSGI_APPLICATION = "ecommerce.wsgi.application"

# =========================================================
# 💾 Base de Données (PostgreSQL en Prod, SQLite en Dev)
# =========================================================
if IS_PRODUCTION:
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
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
# =========================================================
# 💾 Configuration du Cache (Redis en Prod, Local en Dev)
# =========================================================

if IS_PRODUCTION:
    # URL de connexion au service Redis (typique dans un environnement Docker/K8s)
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/1")

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                # 60 secondes (max_entries par défaut)
                "MAX_ENTRIES": 1000,
            },
        }
    }
else:
    # En développement, utilise un cache local en mémoire
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-in-dev",  # Clé unique pour le cache local
        }
    }
# =========================================================
# ☁️ Stockage des Fichiers (GCS en Prod, Local en Dev)
# =========================================================

# Variables GCS
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET")  # Utilisé par django-storages
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")

if IS_PRODUCTION and GCS_BUCKET_NAME:
    # --- 🚀 PARAMÈTRES DE PRODUCTION (GCS) ---

    # 1. Stockage par défaut pour les Médias (Images de produits, uploads)
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"

    # 2. Emplacement des Médias dans le bucket GCS
    GS_MEDIA_LOCATION = "media"
    MEDIA_URL = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{GS_MEDIA_LOCATION}/"
    MEDIA_ROOT = "media/"  # Valeur symbolique pour django-storages

    # 3. Stockage des Fichiers Statiques (CSS, JS, images du thème)
    STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"

    # 4. Emplacement des Statiques dans le bucket GCS
    GS_STATIC_LOCATION = "static"
    STATIC_URL = (
        f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{GS_STATIC_LOCATION}/"
    )
    STATIC_ROOT = "static/"  # Valeur symbolique pour django-storages

    # Optionnel: Ajout de la création automatique de sous-dossiers
    GS_AUTO_CREATE_MEDIA_SUBFOLDER = True
    GS_AUTO_CREATE_STATIC_SUBFOLDER = True

else:
    # --- 💻 PARAMÈTRES DE DÉVELOPPEMENT LOCAL ---

    # Médias (uploads d'images de produits)
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "mediafiles"

    # Statiques (CSS, JS)
    STATIC_URL = "static/"
    STATIC_ROOT = BASE_DIR / "staticfiles"
    STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

# ... Autres paramètres (LANGUAGE_CODE, TIME_ZONE, DEFAULT_AUTO_FIELD) ...
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
