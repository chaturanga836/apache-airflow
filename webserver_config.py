import os
import logging
import sys
import ldap
from flask_appbuilder.security.manager import AUTH_LDAP

# Global LDAP Options - This is crucial for SSL stability
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN",
    "postgresql+psycopg2://postgres:2324@144.24.127.112:5432/airflow_db"
)

CSRF_ENABLED = True
SECRET_KEY = os.environ.get('AIRFLOW__API__SECRET_KEY', 'secure_static_key_here')

# --- LDAP SSL CONFIGURATION ---
AUTH_TYPE = AUTH_LDAP
AUTH_ROLE_ADMIN = "Admin"
AUTH_ROLE_PUBLIC = "Public"
AUTH_LDAP_SERVER = "ldaps://144.24.127.112:636"
AUTH_LDAP_USE_TLS = False 
AUTH_LDAP_ALLOW_SELF_SIGNED = True

# Search & Bind
AUTH_LDAP_SEARCH = "ou=users,dc=crypto,dc=lake"
AUTH_LDAP_UID_FIELD = "uid"
AUTH_LDAP_BIND_USER = "cn=admin,dc=crypto,dc=lake"
AUTH_LDAP_BIND_PASSWORD = "SuperSecretCryptoPassword2026"
AUTH_LDAP_BIND_DIRECT = False

# Registration & Mapping
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Public"
AUTH_ROLES_SYNC_AT_LOGIN = True

AUTH_LDAP_FIRSTNAME_FIELD = "uid"
AUTH_LDAP_LASTNAME_FIELD = "sn"
AUTH_LDAP_EMAIL_FIELD = "mail"
AUTH_LDAP_GROUP_PULL_ALL_SEARCH = True
# --- THE CRITICAL GROUP SEARCH FIXES ---
AUTH_LDAP_GROUP_FIELD_IS_DN = True  # Your search used the full User DN
AUTH_LDAP_GROUP_FIELD = "member" 
AUTH_LDAP_GROUP_SEARCH = "ou=groups,dc=crypto,dc=lake" # Broaden to root to ensure we don't miss ou=Groups
AUTH_LDAP_GROUP_TYPE = "groupOfNames"
AUTH_LDAP_GROUP_OBJECT_CLASS = "groupOfNames"
AUTH_LDAP_GROUP_SEARCH_SCOPE = 2 # Subtree search
AUTH_LDAP_SEARCH_FILTER = "(objectClass=inetOrgPerson)" # Or whatever Anna's objectClass is
AUTH_LDAP_GROUP_SEARCH_FILTER = "(objectClass=groupOfNames)"

AUTH_LDAP_USER_REGISTRATION_FIELDS = ["uid", "mail", "givenName", "sn", "description"]
AUTH_LDAP_SEARCH_ATTRS = ["uid", "mail", "givenName", "sn", "description"]
AUTH_LDAP_USE_NESTED_GROUPS_FOR_ROLES = False
# Use EXACT strings from your successful ldapsearch
AUTH_ROLES_MAPPING = {
    "admins": ["Admin"],
    "HR_DEP": ["User"],
    "FOX_COMP": ["Viewer"],
}

AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_REFERRALS: 0,
    ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER,
    ldap.OPT_DEBUG_LEVEL: 255 # Only if you need extreme LDAP tracing
}

PERMANENT_SESSION_LIFETIME = 1800