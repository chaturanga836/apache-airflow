# Use the official Airflow image as the base
FROM apache/airflow:2.7.2

USER root

# 1. Install system dependencies for LDAP and SSL
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libldap2-dev libsasl2-dev gcc \
    && apt-get clean && rm -rf /var/lib/apt-get/lists/*

# 2. Add your corporate LDAP CA certificate
# Replace 'ldap-ca.crt' with your actual certificate file name
COPY ./certs/ldap-ca.crt /usr/local/share/ca-certificates/ldap-ca.crt
RUN update-ca-certificates

USER airflow

# 3. Install Python providers for Trino and LDAP
RUN pip install --no-cache-dir \
    apache-airflow-providers-trino \
    python-ldap \
    ldap3