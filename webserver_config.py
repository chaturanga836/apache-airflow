import os
import logging
import jwt
from flask_appbuilder.security.manager import AUTH_OAUTH
from airflow.www.security import AirflowSecurityManager

log = logging.getLogger(__name__)

# --- STABILITY SETTINGS ---
SECRET_KEY = os.environ.get('AIRFLOW__WEBSERVER__SECRET_KEY', 'datalake_static_secret_key_12345')
CSRF_ENABLED = True
SESSION_COOKIE_SECURE = False 
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
ENABLE_PROXY_FIX = True

# --- AUTH SETTINGS ---
AUTH_TYPE = AUTH_OAUTH
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Viewer" 
AUTH_ROLES_SYNC_AT_LOGIN = True

# Use your actual Keycloak IP and Realm
OIDC_ISSUER = os.environ.get("AIRFLOW_OIDC_ISSUER", "http://13.200.160.10:8081/realms/etl-dev") 
OIDC_BASE_URL = f"{OIDC_ISSUER}/protocol/openid-connect"

OAUTH_PROVIDERS = [{
    "name": "keycloak",
    "icon": "fa-key",
    "token_key": "access_token",
    "remote_app": {
        "client_id": os.environ.get("AIRFLOW_CLIENT_ID", "airflow-cluster"),
        "client_secret": os.environ.get("AIRFLOW_CLIENT_SECRET"),
        "api_base_url": OIDC_BASE_URL,
        "access_token_url": f"{OIDC_BASE_URL}/token",
        "authorize_url": f"{OIDC_BASE_URL}/auth",
        "server_metadata_url": f"{OIDC_ISSUER}/.well-known/openid-configuration",
        "client_kwargs": {"scope": "openid email profile groups"}
    }
}]

# --- ROLE MAPPING ---
AUTH_ROLES_MAPPING = {
    "Admin": ["Admin"],
    "airflow_admin": ["Admin"],
    "Viever": ["Viewer"], # Keycloak 'Viever' -> Airflow 'Viewer'
    "User": ["User"],
}

class CustomSecurityManager(AirflowSecurityManager):
    def get_oauth_user_info(self, provider, resp):
        if provider == "keycloak":
            token = resp.get("access_token")
            # This requires 'PyJWT' to be installed
            me = jwt.decode(token, options={"verify_signature": False})
            
            log.info("===== OAUTH LOGIN ATTEMPT: %s =====", me.get("preferred_username"))
            
            # Extract roles from realm_access (matches your Mapper setup)
            groups = me.get("realm_access", {}).get("roles", [])
            
            if not groups:
                groups = me.get("groups", [])

            return {
                "username": me.get("preferred_username"),
                "email": me.get("email"),
                "first_name": me.get("given_name"),
                "last_name": me.get("family_name"),
                "role_keys": groups,
            }
        return {}

SECURITY_MANAGER_CLASS = CustomSecurityManager