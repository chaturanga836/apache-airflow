#!/bin/bash
set -e

# 1. AUTOMATED PERMISSIONS FIX
# We create these in /opt/airflow (inside container). 
# Because of your volumes, this also creates/fixes them on your Ubuntu host.
mkdir -p /opt/airflow/dags /opt/airflow/logs /opt/airflow/plugins
chown -R airflow:0 /opt/airflow/dags /opt/airflow/logs /opt/airflow/plugins
chmod -R 775 /opt/airflow/dags /opt/airflow/logs /opt/airflow/plugins

# 2. AUTOMATED DB MIGRATION
# This runs the migration using the airflow user
echo "Running database migrations..."
gosu airflow airflow db migrate

# 3. AUTOMATED ADMIN CREATION
# Only runs if the user doesn't exist

echo "Ensuring Admin user exists..."
gosu airflow airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin || true

# 4. HAND OFF TO AIRFLOW
# Executes the command from docker-compose (webserver or scheduler)
echo "Starting Airflow with command: $@"
exec gosu airflow "$@"