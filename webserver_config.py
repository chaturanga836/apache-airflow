import os
import logging
import jwt
from flask_appbuilder.security.manager import AUTH_OAUTH
from airflow.providers.fab.auth_manager.security_manager.override import FabAirflowSecurityManagerOverride

log = logging.getLogger(__name__)

# --- CORE SETTINGS ---
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN",
    "postgresql+psycopg2://postgres:2324@144.24.127.112:5432/airflow_db"
)
CSRF_ENABLED = True
SECRET_KEY = os.environ.get('AIRFLOW__API__SECRET_KEY', 'secure_static_key_here')

# --- OIDC / KEYCLOAK ---
AUTH_TYPE = AUTH_OAUTH
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Public"
AUTH_ROLES_SYNC_AT_LOGIN = True

# Ensure this matches your Keycloak Realm URL
OIDC_ISSUER = os.environ.get("AIRFLOW_OIDC_ISSUER", "http://144.24.127.112:8081/realms/datalake") 
OIDC_BASE_URL = f"{OIDC_ISSUER}/protocol/openid-connect"

OAUTH_PROVIDERS = [
    {
        "name": "keycloak",
        "icon": "fa-key",
        "token_key": "access_token",
        "remote_app": {
            "client_id": os.environ.get("AIRFLOW_CLIENT_ID", "airflow"),
            "client_secret": os.environ.get("AIRFLOW_CLIENT_SECRET"),
            "api_base_url": OIDC_BASE_URL,
            "access_token_url": f"{OIDC_BASE_URL}/token",
            "authorize_url": f"{OIDC_BASE_URL}/auth",
            "server_metadata_url": f"{OIDC_ISSUER}/.well-known/openid-configuration",
            "client_kwargs": {
                "scope": "openid email profile groups",
                "verify": False # Set to True if you have valid SSL certs
            }
        },
    }
]

# --- ROLE MAPPING ---
AUTH_ROLES_MAPPING = {
    "Viewer": ["Viewer"],
    "Admin": ["Admin"],
    "User": ["User"],
    "Public": ["Public"],
    "Op": ["Op"],
}

class CustomSecurityManager(FabAirflowSecurityManagerOverride):
    def oauth_user_info(self, provider, response):
        if provider == "keycloak":
            token = response.get("access_token")
            # Decode without signature check because we trust the internal network issuer
            me = jwt.decode(token, options={"verify_signature": False})
            
            # CRITICAL: Check these logs to see the 'groups' or 'resource_access' keys!
            print(f"DEBUG FULL TOKEN: {me}")

            # 1. Try to get Realm-level Groups
            groups = me.get("groups", []) 
            
            # 2. If empty, try to get Client-level Roles (resource_access)
            if not groups:
                client_id = os.environ.get("AIRFLOW_CLIENT_ID", "airflow")
                groups = me.get("resource_access", {}).get(client_id, {}).get("roles", [])

            return {
                "username": me.get("preferred_username"),
                "email": me.get("email"),
                "first_name": me.get("given_name"),
                "last_name": me.get("family_name"),
                "role_keys": groups,
            }
        return {}

SECURITY_MANAGER_CLASS = CustomSecurityManager