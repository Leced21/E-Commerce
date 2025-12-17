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
    print(f"Connexion à Secret Manager pour le projet : {PROJECT_ID}")
    client = secretmanager.SecretManagerServiceClient()
    secrets_to_write = []

    for secret_name, env_var_name in SECRET_MAPPING.items():
        secret_path = client.secret_version_path(PROJECT_ID, secret_name, "latest")
        try:
            response = client.access_secret_version(request={"name": secret_path})
            secret_value = response.payload.data.decode("UTF-8")

            # On prépare la ligne pour le fichier .env
            secrets_to_write.append(f"export {env_var_name}='{secret_value}'")
            print(f"Secret {secret_name} récupéré.")
        except Exception as e:
            print(f"Erreur lors du chargement du secret {secret_name}: {e}")
            raise EnvironmentError(f"Secret manquant: {secret_name}") from e

    # On écrit tout dans un fichier que le Shell pourra lire
    with open("/tmp/.env.secrets", "w") as f:
        f.write("\n".join(secrets_to_write))
    print("Fichier de secrets temporaire généré.")


if __name__ == "__main__":
    if os.environ.get("DJANGO_DEBUG") == "0":  # Seulement en Prod
        load_secrets()
