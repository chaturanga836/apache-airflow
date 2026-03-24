import os
import logging
import jwt
from flask_appbuilder.security.manager import AUTH_OAUTH
from airflow.www.security import AirflowSecurityManager

log = logging.getLogger(__name__)

# --- STABILITY & SESSION SETTINGS ---
SECRET_KEY = os.environ.get('AIRFLOW__WEBSERVER__SECRET_KEY', 'datalake_static_secret_key_12345')
CSRF_ENABLED = True
SESSION_COOKIE_SECURE = False 
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
ENABLE_PROXY_FIX = True

# --- AUTH TYPE SETTINGS ---
AUTH_TYPE = AUTH_OAUTH
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Viewer" 
AUTH_ROLES_SYNC_AT_LOGIN = True

OIDC_ISSUER = os.environ.get("AIRFLOW_OIDC_ISSUER", "http://13.200.160.10:8081/realms/etl-dev") 
OIDC_BASE_URL = f"{OIDC_ISSUER}/protocol/openid-connect"

OAUTH_PROVIDERS = [{
    "name": "keycloak",
    "icon": "fa-key",
    "token_key": "access_token",
    "remote_app": {
        "client_id": os.environ.get("AIRFLOW_CLIENT_ID", "airflow-cluster"),
        "client_secret": os.environ.get("AIRFLOW_CLIENT_SECRET", "R07bsffOmZU2sOSmm7LJsGNJKWnnCTZw"),
        "api_base_url": OIDC_BASE_URL,
        "access_token_url": f"{OIDC_BASE_URL}/token",
        "authorize_url": f"{OIDC_BASE_URL}/auth",
        "server_metadata_url": f"{OIDC_ISSUER}/.well-known/openid-configuration",
        "client_kwargs": {"scope": "openid email profile groups"}
    }
}]

# --- IMPROVED ROLE MAPPING ---
# We map the Keycloak role string to the Airflow role list
AUTH_ROLES_MAPPING = {
    "Admin": ["Admin"],
    "admin": ["Admin"], # Added lowercase fallback
    "airflow_admin": ["Admin"],
    "Viewer": ["Viewer"],
    "User": ["User"],
}

class CustomSecurityManager(AirflowSecurityManager):
    def get_oauth_user_info(self, provider, resp):
        if provider == "keycloak":
            token = resp.get("access_token")
            if not token:
                log.error("No access_token received from Keycloak")
                return {}

            try:
                # Decode without verification for debugging roles
                me = jwt.decode(token, options={"verify_signature": False})
                username = me.get("preferred_username")
                
                log.info(f"===== OAUTH LOGIN ATTEMPT: {username} =====")
                
                # Extract Realm Roles
                realm_roles = me.get("realm_access", {}).get("roles", [])
                
                # Extract Client Roles for 'airflow-cluster'
                res_access = me.get("resource_access", {})
                client_roles = res_access.get("airflow-cluster", {}).get("roles", [])
                
                # Log the structure to see if Keycloak is nesting them differently
                log.debug(f"Resource Access Keys found: {list(res_access.keys())}")
                
                # Merge lists
                all_roles = list(set(realm_roles + client_roles))

                log.info(f"Detected Keycloak Roles for {username}: {all_roles}")

                return {
                    "username": username,
                    "email": me.get("email"),
                    "first_name": me.get("given_name", ""),
                    "last_name": me.get("family_name", ""),
                    "role_keys": all_roles,
                }
            except Exception as e:
                log.error(f"Error decoding Keycloak token: {e}")
                return {}
        
        return super().get_oauth_user_info(provider, resp)

SECURITY_MANAGER_CLASS = CustomSecurityManager