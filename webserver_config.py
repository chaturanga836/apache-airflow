import os
import logging
import jwt
from flask_appbuilder.security.manager import AUTH_OAUTH
# In Airflow 2.x, we override the standard AirflowSecurityManager
from airflow.www.security import AirflowSecurityManager

log = logging.getLogger(__name__)

# --- STABILITY SETTINGS (HTTP/PUBLIC IP) ---
# Hardcode a static key. A dynamic key causes CSRF mismatches after restarts.
SECRET_KEY = os.environ.get('AIRFLOW__WEBSERVER__SECRET_KEY', 'datalake_static_secret_key_12345')

CSRF_ENABLED = True
SESSION_COOKIE_SECURE = False   # False for HTTP
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax' # 'Lax' is more compatible with HTTP than 'None'
ENABLE_PROXY_FIX = True

# --- AUTH SETTINGS ---
AUTH_TYPE = AUTH_OAUTH
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Viewer" 
AUTH_ROLES_SYNC_AT_LOGIN = True

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
            }
        },
    }
]

# --- ROLE MAPPING ---
AUTH_ROLES_MAPPING = {
    "Admin": ["Admin"],
    "airflow_admin": ["Admin"],
    "Viewer": ["Viewer"],
    "User": ["User"],
}

class CustomSecurityManager(AirflowSecurityManager):
    def get_oauth_user_info(self, provider, resp):
        # In 2.10.5, the method is get_oauth_user_info, not oauth_user_info
        if provider == "keycloak":
            token = resp.get("access_token")
            # verify_signature=False is fine for internal metadata mapping
            me = jwt.decode(token, options={"verify_signature": False})
            
            log.info("===== OAUTH LOGIN START =====")
            
            # Extract roles/groups from token
            groups = me.get("groups", [])
            if not groups:
                realm_roles = me.get("realm_access", {}).get("roles", [])
                groups = realm_roles
            
            if not groups:
                client_id = os.environ.get("AIRFLOW_CLIENT_ID", "airflow")
                groups = me.get("resource_access", {}).get(client_id, {}).get("roles", [])

            log.info("Final role_keys mapped for %s: %s", me.get("preferred_username"), groups)

            return {
                "username": me.get("preferred_username"),
                "email": me.get("email"),
                "first_name": me.get("given_name"),
                "last_name": me.get("family_name"),
                "role_keys": groups,
            }
        return {}

SECURITY_MANAGER_CLASS = CustomSecurityManager