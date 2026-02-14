import os
from flask_appbuilder.security.manager import AUTH_OAUTH
from airflow.www.security import AirflowSecurityManager
import jwt
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
# ... existing imports ...

# Match Trino's logic: No HTTPS, no Verify False needed (but safe to keep)
OIDC_ISSUER = os.environ.get("AIRFLOW_OIDC_ISSUER") 
OIDC_BASE_URL = f"{OIDC_ISSUER}/protocol/openid-connect"

OAUTH_PROVIDERS = [
    {
        "name": "keycloak",
        "icon": "fa-key",
        "token_key": "access_token",
        "remote_app": {
            "client_id": os.environ.get("AIRFLOW_CLIENT_ID"),
            "client_secret": os.environ.get("AIRFLOW_CLIENT_SECRET"),
            "api_base_url": OIDC_BASE_URL,
            "access_token_url": f"{OIDC_BASE_URL}/token",
            "authorize_url": f"{OIDC_BASE_URL}/auth",
            "server_metadata_url": f"{OIDC_ISSUER}/.well-known/openid-configuration",
            "client_kwargs": {
                "scope": "openid email profile groups"
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


class CustomSecurityManager(AirflowSecurityManager):
    def oauth_user_info(self, provider, response):
        if provider == "keycloak":
            token = response.get("access_token")
            # Decode the token (no signature check needed as we trust the internal OIDC_ISSUER)
            me = jwt.decode(token, options={"verify_signature": False})
            
            # Print to docker logs so you can see what's happening
            # docker logs -f airflow-webserver
            groups = me.get("groups", [])
            print(f"DEBUG: Keycloak Groups found: {groups}")
            
            return {
                "username": me.get("preferred_username"),
                "email": me.get("email"),
                "first_name": me.get("given_name"),
                "last_name": me.get("family_name"),
                "role_keys": groups, 
            }
        return {}

# Crucial: Tell Airflow to use your custom class
SECURITY_MANAGER_CLASS = CustomSecurityManager