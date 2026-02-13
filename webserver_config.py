import os
from flask_appbuilder.security.manager import AUTH_OAUTH

# --- CORE SETTINGS ---
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN",
    "postgresql+psycopg2://postgres:2324@144.24.127.112:5432/airflow_db"
)
CSRF_ENABLED = True
SECRET_KEY = os.environ.get('AIRFLOW__API__SECRET_KEY', 'secure_static_key_here')

# --- OIDC / KEYCLOAK ONLY ---
AUTH_TYPE = AUTH_OAUTH
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Public"
AUTH_ROLES_SYNC_AT_LOGIN = True

# Issuer from .env (e.g., https://144.24.127.112:8443/realms/datalake)
OIDC_ISSUER = os.environ.get("AIRFLOW_OIDC_ISSUER")
OIDC_BASE_URL = f"{OIDC_ISSUER}/protocol/openid-connect"

OAUTH_PROVIDERS = [
    {
        "name": "keycloak",
        "icon": "fa-key",
        "token_key": "access_token",
        "remote_app": {
            "client_id": "airflow_admin",  # Matches your Keycloak Client ID
            "client_secret": os.environ.get("AIRFLOW_CLIENT_SECRET"),
            "api_base_url": OIDC_BASE_URL,
            "access_token_url": f"{OIDC_BASE_URL}/token",
            "authorize_url": f"{OIDC_BASE_URL}/auth",
            "request_token_params": {"scope": "openid email profile groups"},
            "server_metadata_url": f"{OIDC_ISSUER}/.well-known/openid-configuration",
            "client_kwargs": {
                "verify": False  # Use False only if your 144.24.x.x SSL is self-signed
            }
        },
    }
]

# --- ROLE MAPPING ---
# Keycloak Groups -> Airflow Roles
AUTH_ROLES_MAPPING = {
    "airflow_admin": ["Admin"],
    "trino_admin": ["Admin"]
}