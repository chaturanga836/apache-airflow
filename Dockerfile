FROM apache/airflow:3.0.0

USER root
# Install system-level requirements
# We keep libpq-dev for Postgres and ca-certificates for SSL trust with Keycloak
RUN apt-get update && apt-get install -y \
    gcc ca-certificates libpq-dev curl \
    && apt-get clean

USER airflow

# 1. Define the Constraint URL
# Note: Using 3.0.0 as 3.1.6 is a future release for 2026; ensure this matches your base
ARG PYTHON_VERSION=3.12
ARG AIRFLOW_VERSION=3.0.0
ARG CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# 2. Install providers
# Removed [ldap] extra from FAB as we are using OIDC/OAuth2
RUN pip install --no-cache-dir \
    "apache-airflow-providers-fab" \
    "apache-airflow-providers-trino" \
    "apache-airflow-providers-postgres" \
    --constraint "${CONSTRAINT_URL}"

USER root

# Install gosu to safely switch from root to airflow user
RUN apt-get update && apt-get install -y gosu && apt-get clean

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Entrypoint handles initialization
ENTRYPOINT ["/entrypoint.sh"]