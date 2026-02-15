import os
from flask_appbuilder.security.manager import AUTH_OAUTH
# ADD THIS
from airflow.providers.fab.auth_manager.security_manager.override import FabAirflowSecurityManagerOverride
import jwt

log = logging.getLogger(__name__)
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
            # We use verify=False because we are behind a trusted internal network
            me = jwt.decode(token, options={"verify_signature": False})
            
            log.info("me: {0}".format(me))
            # DEBUG: This is the most important line for you right now
            # Check your docker logs to see what this prints!
            print(f"DEBUG FULL TOKEN: {me}")

            # The article expects roles here: me["resource_access"]["airflow-sso"]["roles"]
            # But your config uses "groups". Let's try to find BOTH:
            groups = me.get("groups", []) # Look for Realm Groups
            if not groups:
                # Look for Client Roles as a backup (replace 'airflow' with your Client ID)
                groups = me.get("resource_access", {}).get("airflow", {}).get("roles", [])

            log.info("groups: {0}".format(groups))
            
            userinfo = {
                "username": me.get("preferred_username"),
                "email": me.get("email"),
                "first_name": me.get("given_name"),
                "last_name": me.get("family_name"),
                "role_keys": groups,
            }
            
            log.info("user info: {0}".format(userinfo))
            
            return userinfo
        return {}

SECURITY_MANAGER_CLASS = CustomSecurityManager