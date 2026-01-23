#!/bin/bash
set -e

# 1. AUTOMATED PERMISSIONS FIX
mkdir -p /opt/airflow/dags /opt/airflow/logs /opt/airflow/plugins
chown -R airflow:0 /opt/airflow/dags /opt/airflow/logs /opt/airflow/plugins
chmod -R 775 /opt/airflow/dags /opt/airflow/logs /opt/airflow/plugins

# 2. AUTOMATED DB MIGRATION
echo "Running database migrations..."
gosu airflow airflow db migrate

# 3. AUTOMATED ADMIN CREATION
echo "Ensuring Admin user exists..."

# In Airflow 3, sync-perm is a top-level command
gosu airflow airflow sync-perm || true

# In your build, 'users' is also a top-level command group
gosu airflow airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin || echo "Admin already exists or user creation skipped."

# 4. HAND OFF TO AIRFLOW
echo "Starting Airflow with command: $@"
# Ensure we use 'api-server' for the webserver service
exec gosu airflow airflow "$@"