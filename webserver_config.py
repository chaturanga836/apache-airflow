import os
import logging
import jwt  # Note: Ensure 'PyJWT' is installed in your Airflow environment
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

# --- KEYCLOAK CONNECTION SETTINGS ---
# Using the information from your Keycloak Console URLs
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

# --- ROLE MAPPING ---
# These keys on the left must match the ROLES defined in Keycloak exactly.
# The values on the right are standard Airflow roles.
AUTH_ROLES_MAPPING = {
    "Admin": ["Admin"],
    "airflow_admin": ["Admin"],
    "Viewer": ["Viewer"],  # Fixed typo from 'Viever'
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
                # Decode the JWT to read roles and user info without verifying signature 
                # (Verification is handled by the OAuth flow internally)
                me = jwt.decode(token, options={"verify_signature": False})
                
                username = me.get("preferred_username")
                log.info(f"===== OAUTH LOGIN ATTEMPT: {username} =====")
                
                # 1. Try to get roles from 'realm_access' (Standard Keycloak location)
                # 2. Fallback to 'groups' if you are using a Group Mapper
                # 3. Fallback to 'resource_access' for client-specific roles
                roles = me.get("realm_access", {}).get("roles", [])
                if not roles:
                    roles = me.get("groups", [])
                if not roles:
                    roles = me.get("resource_access", {}).get("airflow-cluster", {}).get("roles", [])

                log.info(f"Detected Keycloak Roles for {username}: {roles}")

                return {
                    "username": username,
                    "email": me.get("email"),
                    "first_name": me.get("given_name", ""),
                    "last_name": me.get("family_name", ""),
                    "role_keys": roles,
                }
            except Exception as e:
                log.error(f"Error decoding Keycloak token: {e}")
                return {}
        
        return super().get_oauth_user_info(provider, resp)

SECURITY_MANAGER_CLASS = CustomSecurityManager