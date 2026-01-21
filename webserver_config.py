import os
from flask_appbuilder.security.manager import AUTH_LDAP

# Enable LDAP Authentication
AUTH_TYPE = AUTH_LDAP

# LDAP Server Details (Use ldaps:// for SSL)
AUTH_LDAP_SERVER = "ldaps://your-ldap-server.com:636"

# This should point to the certificate we copied in the Dockerfile
AUTH_LDAP_TLS_CACERTFILE = "/etc/ssl/certs/ldap-ca.crt"

# LDAP Search Settings
AUTH_LDAP_SEARCH = "ou=users,dc=example,dc=com"
AUTH_LDAP_UID_FIELD = "uid"  # or 'sAMAccountName' for Active Directory
AUTH_LDAP_BIND_USER = "cn=read-only-admin,dc=example,dc=com"
AUTH_LDAP_BIND_PASSWORD = "your-bind-password"

# Map LDAP groups to Airflow roles
AUTH_ROLES_MAPPING = {
    "cn=airflow_admins,ou=groups,dc=example,dc=com": ["Admin"],
    "cn=airflow_users,ou=groups,dc=example,dc=com": ["User"],
}

# Allow users to be created automatically on first login
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Public"