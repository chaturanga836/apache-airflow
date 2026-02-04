from airflow.www.security import AirflowSecurityManager
import ldap
import logging

log = logging.getLogger(__name__)

class CustomAirflowSecurityManager(AirflowSecurityManager):

    def _search_ldap(self, ldap_mod, con, username):
        """
        Override default LDAP user search
        """
        log.info("CUSTOM LDAP SEARCH ENABLED")

        filter_str = f"({self.auth_ldap_uid_field}={username})"

        # ⚠️ IMPORTANT: request ALL attributes you want
        request_fields = [
            "uid",
            "cn",
            "sn",
            "givenName",
            "mail",
            "memberOf",        # if exists
            "description",    # custom
        ]

        result = con.search_s(
            self.auth_ldap_search,
            ldap.SCOPE_SUBTREE,
            filter_str,
            request_fields,
        )

        if not result:
            return None, None

        user_dn, user_attrs = result[0]

        log.info("LDAP USER ATTRS: %s", user_attrs)
        return user_dn, user_attrs

    def _ldap_get_nested_groups(self, ldap_mod, con, user_dn):
        """
        Custom group resolution for OpenLDAP
        """
        log.info("CUSTOM GROUP SEARCH ENABLED")

        group_filter = f"(member={user_dn})"

        result = con.search_s(
            "ou=groups,dc=crypto,dc=lake",
            ldap.SCOPE_SUBTREE,
            group_filter,
            ["cn"],
        )

        groups = []
        for dn, attrs in result:
            if "cn" in attrs:
                groups.extend([g.decode() for g in attrs["cn"]])

        log.info("LDAP GROUPS FOUND: %s", groups)
        return groups
