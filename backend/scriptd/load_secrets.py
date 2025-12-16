# backend/scripts/load_secrets.py
import os
from google.cloud import secretmanager

# Le nom de votre projet GCP (peut être passé via variable d'env)
PROJECT_ID = os.environ.get("GCP_PROJECT_ID") 

# Dictionnaire de mappage: Secret GCSM -> Variable d'Env Django
SECRET_MAPPING = {
    "DJANGO_SECRET_KEY": "DJANGO_SECRET_KEY",
    "POSTGRES_PASSWORD": "POSTGRES_PASSWORD",
    "CUSTOM_API_KEY": "CUSTOM_API_KEY",
}

def load_secrets():
    """Charge les secrets depuis GCSM dans l'environnement."""
    client = secretmanager.SecretManagerServiceClient()
    
    for secret_name, env_var_name in SECRET_MAPPING.items():
        # Chemin complet vers la dernière version du secret
        secret_path = client.secret_version_path(
            PROJECT_ID, secret_name, "latest"
        )
        try:
            response = client.access_secret_version(request={"name": secret_path})
            secret_value = response.payload.data.decode("UTF-8")
            os.environ[env_var_name] = secret_value
            print(f"Secret {secret_name} chargé dans {env_var_name}")
        except Exception as e:
            print(f"Erreur lors du chargement du secret {secret_name}: {e}")
            # Lève une erreur critique si un secret est manquant
            raise EnvironmentError(f"Secret manquant: {secret_name}") from e

if __name__ == "__main__":
    if os.environ.get("DJANGO_DEBUG") == "0": # Seulement en Prod
        load_secrets()