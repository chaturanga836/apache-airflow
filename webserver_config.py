import os
from airflow import configuration as conf
from flask_appbuilder.security.manager import AUTH_LDAP

SQLALCHEMY_DATABASE_URI = conf.get("core", "SQL_ALCHEMY_CONN")
CSRF_ENABLED = True

AUTH_TYPE = AUTH_LDAP
AUTH_ROLE_ADMIN = "Admin"

# Use your actual server IP and LDAP SSL port if applicable
# Since your note says LDAP SSL, ensure this matches your requirement
AUTH_LDAP_SERVER = f"ldap://{os.environ.get('LDAP_SERVER_IP')}:389"

# Registration configs
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Public" # Fallback role
AUTH_LDAP_FIRSTNAME_FIELD = "cn"       # Based on your LDIF
AUTH_LDAP_LASTNAME_FIELD = "sn"
AUTH_LDAP_EMAIL_FIELD = "mail"

# Search configs - MUST be the top level to see ou=IT and ou=Groups
AUTH_LDAP_SEARCH = os.environ.get("AUTH_LDAP_SEARCH")
AUTH_LDAP_UID_FIELD = os.environ.get("AUTH_LDAP_UID_FIELD") 
AUTH_LDAP_BIND_USER = os.environ.get("LDAP_BIND_USER")
AUTH_LDAP_BIND_PASSWORD = os.environ.get("LDAP_BIND_PASSWORD")

# --- THE KEY FIXES ---

# 1. Match your LDIF attribute name exactly
AUTH_LDAP_GROUP_FIELD = "member" 

# 2. Use the exact DNs from your successful ldapsearch
AUTH_ROLES_MAPPING = {
    "cn=it_users,ou=Groups,dc=example,dc=com": ["Admin"],
    "cn=marketing_users,ou=Groups,dc=example,dc=com": ["User"],
}

AUTH_ROLES_SYNC_AT_LOGIN = True
PERMANENT_SESSION_LIFETIME = 1800

# TLS / SSL Settings
# If using port 636, set AUTH_LDAP_USE_TLS = True or use ldaps://
AUTH_LDAP_USE_TLS = False 
AUTH_LDAP_ALLOW_SELF_SIGNED = True