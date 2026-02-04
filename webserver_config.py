import os
import logging
import ldap
from flask_appbuilder.security.manager import AUTH_LDAP

# -------------------------------
# GENERAL AIRFLOW SETTINGS
# -------------------------------
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN",
    "postgresql+psycopg2://postgres:2324@144.24.127.112:5432/airflow_db"
)

CSRF_ENABLED = True
SECRET_KEY = os.environ.get('AIRFLOW__API__SECRET_KEY', 'secure_static_key_here')
PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes

# -------------------------------
# LDAP AUTHENTICATION SETTINGS
# -------------------------------
AUTH_TYPE = AUTH_LDAP
AUTH_ROLE_ADMIN = "Admin"
AUTH_ROLE_PUBLIC = "Public"
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Public"
AUTH_ROLES_SYNC_AT_LOGIN = True

# LDAP server connection
AUTH_LDAP_SERVER = "ldaps://144.24.127.112:636"
AUTH_LDAP_USE_TLS = False
AUTH_LDAP_ALLOW_SELF_SIGNED = True

# Bind (search) user
AUTH_LDAP_BIND_USER = "uid=admin,ou=users,dc=crypto,dc=lake"
AUTH_LDAP_BIND_PASSWORD = "SuperSecretCryptoPassword2026"
AUTH_LDAP_BIND_DIRECT = False  # indirect bind

# Search user in LDAP
AUTH_LDAP_SEARCH = "ou=users,dc=crypto,dc=lake"
AUTH_LDAP_UID_FIELD = "uid"
AUTH_LDAP_SEARCH_FILTER = "(objectClass=inetOrgPerson)"
AUTH_LDAP_SEARCH_ATTRS = ["uid", "givenName", "sn", "mail"]

# Map LDAP attributes to Airflow user fields
AUTH_LDAP_FIRSTNAME_FIELD = "givenName"
AUTH_LDAP_LASTNAME_FIELD = "sn"
AUTH_LDAP_EMAIL_FIELD = "mail"

# -------------------------------
# LDAP GROUP SETTINGS
# -------------------------------
# Use the field in the LDAP group object that contains the user DN (for OpenLDAP: usually 'member')
AUTH_LDAP_GROUP_FIELD = "sn"
AUTH_LDAP_GROUP_FIELD_IS_DN = True

# LDAP group search
AUTH_LDAP_GROUP_SEARCH = "ou=groups,dc=crypto,dc=lake"
AUTH_LDAP_GROUP_OBJECT_CLASS = "groupOfNames"
AUTH_LDAP_GROUP_SEARCH_FILTER = "(objectClass=groupOfNames)"
AUTH_LDAP_GROUP_SEARCH_SCOPE = 2  # SUBTREE

# Optional: if your LDAP supports nested groups (Microsoft AD style)
AUTH_LDAP_USE_NESTED_GROUPS_FOR_ROLES = False

# Map LDAP group cn to Airflow roles
AUTH_ROLES_MAPPING = {
    "Administrator": ["Admin"],
    "HR_DEP": ["User"],
    "FOX_COMP": ["Viewer"],
}

# -------------------------------
# LDAP CONNECTION OPTIONS
# -------------------------------
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_REFERRALS: 0,
    ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER,
    ldap.OPT_DEBUG_LEVEL: 255,  # enable for debug
}

# -------------------------------
# DEBUGGING HELPERS
# -------------------------------
# Optional print/debug
import sys
print("Airflow LDAP Webserver Config Loaded", file=sys.stderr)
