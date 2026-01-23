FROM apache/airflow:3.1.6

USER root
# Install system-level LDAP and Postgres requirements
RUN apt-get update && apt-get install -y \
    libldap2-dev libsasl2-dev gcc ca-certificates libpq-dev

# Copy and trust your LDAP SSL certificate
COPY certs/ca.crt /usr/local/share/ca-certificates/ldap-server.crt
RUN chmod 644 /usr/local/share/ca-certificates/ldap-server.crt && update-ca-certificates

USER airflow

# 1. Define the Constraint URL for your specific Airflow and Python version
ARG PYTHON_VERSION=3.12
ARG AIRFLOW_VERSION=3.1.6
# (Note: Check if your base image uses 3.8, 3.9, etc. by running 'python --version' in it)
ARG CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# 2. Install using the constraints file to prevent breaking dependencies
RUN pip install --no-cache-dir \
    "apache-airflow-providers-fab[ldap]" \
    "apache-airflow-providers-trino" \
    "apache-airflow-providers-postgres" \
    --constraint "${CONSTRAINT_URL}"

USER root

# Install gosu to safely switch from root to airflow user
RUN apt-get update && apt-get install -y gosu && apt-get clean

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Run as root initially so the script can fix permissions
USER root
ENTRYPOINT ["/entrypoint.sh"]