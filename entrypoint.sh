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
#Use the new provider-based command structure
gosu airflow airflow providers fab sync-permissions

gosu airflow airflow providers fab users-create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin || echo "Admin already exists or sync-perm handled it."

# 4. HAND OFF TO AIRFLOW
# Executes the command from docker-compose (webserver, scheduler, etc.)
echo "Starting Airflow with command: $@"
exec gosu airflow airflow "$@"
