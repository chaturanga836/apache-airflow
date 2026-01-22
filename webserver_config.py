import os
from flask_appbuilder.security.manager import AUTH_LDAP

AUTH_TYPE = AUTH_LDAP
AUTH_LDAP_SERVER = f"ldap://{os.environ.get('LDAP_SERVER_IP')}:389"
AUTH_LDAP_USE_TLS = False # Set to False because we are using port 636 (Direct SSL)

# Bind Settings
AUTH_LDAP_BIND_USER = os.environ.get("LDAP_BIND_USER")
AUTH_LDAP_BIND_PASSWORD = os.environ.get("LDAP_BIND_PASSWORD")

# Search Settings
AUTH_LDAP_SEARCH = "dc=example,dc=com"
AUTH_LDAP_UID_FIELD = "uid"
AUTH_LDAP_SEARCH_SCOPE = 2 # Subtree search to find users in ou=IT and ou=Marketing

# Trust the cert we copied into the container
AUTH_LDAP_TLS_CACERTFILE = "/etc/ssl/certs/ca-certificates.crt"

# Group Mapping
AUTH_ROLES_MAPPING = {
    "cn=it_users,ou=Groups,dc=example,dc=com": ["Admin"],
    "cn=marketing_users,ou=Groups,dc=example,dc=com": ["User"],
}

AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Public"