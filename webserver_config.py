import os
import logging
import sys
import ldap
from flask_appbuilder.security.manager import AUTH_LDAP

# --- AIRFLOW 3 FIX: Avoid conf.get attribute error ---
# Pulling the DB connection directly from the environment
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN",
    "postgresql+psycopg2://postgres:2324@144.24.127.112:5432/airflow_db"
)

CSRF_ENABLED = True

# Debug Logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
root.addHandler(handler)

logging.getLogger("flask_appbuilder.security.manager").setLevel(logging.DEBUG)
logging.getLogger("ldap").setLevel(logging.DEBUG)

SECRET_KEY = os.environ.get('AIRFLOW__WEBSERVER__SECRET_KEY', 'your-very-secure-random-string-here')
# --- LDAP SSL CONFIGURATION ---
AUTH_TYPE = AUTH_LDAP
AUTH_ROLE_ADMIN = "Admin"
AUTH_ROLE_PUBLIC = "Public"

# Updated to LDAPS per your 2026-01-19 note
AUTH_LDAP_SERVER = "ldaps://144.24.127.112:636"
AUTH_LDAP_USE_TLS = False  # Set to False when using ldaps:// (TLS is implicit)
AUTH_LDAP_ALLOW_SELF_SIGNED = True

# Search & Bind
AUTH_LDAP_SEARCH = "dc=example,dc=com"
AUTH_LDAP_UID_FIELD = "uid"
AUTH_LDAP_BIND_USER = "cn=admin,dc=example,dc=com"
AUTH_LDAP_BIND_PASSWORD = "admin123"
AUTH_LDAP_BIND_DIRECT = False

# Registration & Mapping
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Public"
AUTH_ROLES_SYNC_AT_LOGIN = True

AUTH_LDAP_FIRSTNAME_FIELD = "uid"
AUTH_LDAP_LASTNAME_FIELD = "sn"
AUTH_LDAP_EMAIL_FIELD = "mail"

# Group Membership Logic
AUTH_LDAP_GROUP_FIELD_IS_DN = True
AUTH_LDAP_GROUP_FIELD = "member" 
AUTH_LDAP_GROUP_SEARCH = "ou=Groups,dc=example,dc=com"
AUTH_LDAP_GROUP_TYPE = "groupOfNames"

# Role Mapping
AUTH_ROLES_MAPPING = {
    "ou=IT,dc=example,dc=com": ["Admin"],
    "cn=it_users,ou=Groups,dc=example,dc=com": ["Admin"],
    "cn=marketing_users,ou=Groups,dc=example,dc=com": ["User"],
}

AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_REFERRALS: 0,
    ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER # Useful for self-signed certificates
}

PERMANENT_SESSION_LIFETIME = 1800