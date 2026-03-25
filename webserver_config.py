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
AUTH_USER_REGISTRATION_ROLE = "Admin" 
AUTH_ROLES_SYNC_AT_LOGIN = True
AUTH_USER_OID_FIELD_NAME = 'preferred_username'

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
                
                # 1. Get Realm Roles (usually default-roles)
                realm_roles = me.get("realm_access", {}).get("roles", [])
                
                # 2. Get the TOP-LEVEL roles (where your 'Admin' is currently sitting)
                top_level_roles = me.get("roles", [])
                
                # 3. Get Group Roles (if any)
                group_roles = me.get("groups", [])
                
                # 4. Get Client Roles (Fallback for standard Keycloak structure)
                client_roles = me.get("resource_access", {}).get("airflow-cluster", {}).get("roles", [])
                
                # Merge EVERYTHING into one list
                all_roles = list(set(realm_roles + top_level_roles + group_roles + client_roles))

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
    
    def before_request(self):
        """
        Force the REST API to recognize the Bearer token for OIDC users.
        """
        from flask import g, request
        
        # 1. If user is already authenticated (UI), let them through
        if g.get("user") and g.user.is_authenticated:
            return super().before_request()

        # 2. Check for Bearer token in the Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                # Decode to find the username (we already trust the sig via Keycloak)
                payload = jwt.decode(token, options={"verify_signature": False})
                username = payload.get("preferred_username")
                
                if username:
                    # Look up the user 'service-account-airflow-worker' in the DB
                    user = self.find_user(username=username)
                    if user:
                        g.user = user  # Manually sign them in for this request
                        log.info(f"API AUTH SUCCESS: {username}")
            except Exception as e:
                log.error(f"API JWT Error: {e}")
        
        return super().before_request()

SECURITY_MANAGER_CLASS = CustomSecurityManager