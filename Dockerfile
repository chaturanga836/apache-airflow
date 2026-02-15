# Use the stable 2.10.5 image
FROM apache/airflow:2.10.5

USER root

# Install system-level requirements
# GCC and libpq-dev are essential for the Postgres/Trino drivers
RUN apt-get update && apt-get install -y \
    gcc \
    ca-certificates \
    libpq-dev \
    curl \
    gosu \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# 1. Define the Constraint URL for 2.10.5
# This ensures we don't install incompatible library versions
ARG PYTHON_VERSION=3.12
ARG AIRFLOW_VERSION=2.10.5
ARG CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# 2. Install providers (Removed LDAP, added OIDC support)
# We add 'authlib' and 'python-jose' to handle the Keycloak JWTs properly
RUN pip install --no-cache-dir \
    "apache-airflow-providers-trino" \
    "apache-airflow-providers-postgres" \
    "authlib" \
    "python-jose" \
    --constraint "${CONSTRAINT_URL}"

USER root

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Revert to airflow user for safety before finishing
USER airflow

ENTRYPOINT ["/entrypoint.sh"]