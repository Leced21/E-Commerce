from .base import *
import os

DEBUG = True

# Toolbar activable seulement si on le demande ET si le package est installé
if os.getenv("DJANGO_USE_DEBUG_TOOLBAR", "0") == "1":
    try:
        import debug_toolbar  # noqa: F401

        INSTALLED_APPS += ["debug_toolbar"]
        MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
        INTERNAL_IPS = ["127.0.0.1"]
    except ImportError:
        # On ne casse pas le démarrage si le paquet n'est pas installé
        pass
